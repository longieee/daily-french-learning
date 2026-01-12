import base64
import os
import time
from typing import Dict, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY environment variable is not set")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # Create session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def generate_content(self, prompt: str, model: str = "gemini-3-pro-preview") -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        url = f"{self.base_url}/{model}:streamGenerateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "thinkingConfig": {
                    "thinkingLevel": "HIGH",
                }
            },
            "tools": [
                {
                    "googleSearch": {}
                }
            ]
        }

        response = self.session.post(url, json=payload, timeout=120)
        response.raise_for_status()

        try:
            data = response.json()
            full_text = ""
            candidates_list = []

            if isinstance(data, list):
                for chunk in data:
                    if "candidates" in chunk:
                        candidates_list.extend(chunk["candidates"])
            else:
                if "candidates" in data:
                    candidates_list.extend(data["candidates"])

            for candidate in candidates_list:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        full_text += part.get("text", "")

            return full_text
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            raise

    def _chunk_script(self, script: List[Dict[str, str]], max_turns_per_chunk: int = 20) -> List[List[Dict[str, str]]]:
        """Split script into smaller chunks for TTS processing."""
        chunks = []
        for i in range(0, len(script), max_turns_per_chunk):
            chunks.append(script[i:i + max_turns_per_chunk])
        return chunks

    def _generate_audio_chunk(self, script_chunk: List[Dict[str, str]], model: str) -> bytes:
        """Generate audio for a single chunk of the script."""
        url = f"{self.base_url}/{model}:streamGenerateContent?key={self.api_key}"

        # Build structured prompt with director's notes for better TTS control
        director_notes = """# AUDIO PROFILES

## Tutor (Voice: Zephyr)
Concise English instructor. Keep English brief - only essential context.

## Acteur (Voice: Puck)
Native French speaker reading French text with authentic Parisian accent.

### DIRECTOR'S NOTES
Pacing: Fast, natural conversational speed. No slow dictation. Speak as natives would in real conversation.
Tutor: American English accent. Brief and efficient delivery.
Acteur: Native French (Parisian) accent. Speak French passages at authentic native speed with proper French phonetics.

### DIALOGUE
"""
        dialogue_lines = []
        for turn in script_chunk:
            speaker_label = "Tutor" if turn["role"] == "tutor_en" else "Acteur"
            dialogue_lines.append(f"{speaker_label}: {turn['text']}")

        full_prompt_text = director_notes + "\n".join(dialogue_lines)

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": full_prompt_text}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "multiSpeakerVoiceConfig": {
                        "speakerVoiceConfigs": [
                            {
                                "speaker": "Tutor",
                                "voiceConfig": {
                                    "prebuiltVoiceConfig": {
                                        "voiceName": "Achernar"
                                    }
                                }
                            },
                            {
                                "speaker": "Acteur",
                                "voiceConfig": {
                                    "prebuiltVoiceConfig": {
                                        "voiceName": "Alnilam"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }


        # TTS with retry logic for connection errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.post(url, json=payload, timeout=180)
                response.raise_for_status()
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"TTS chunk request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"TTS chunk request failed after {max_retries} attempts")
                    raise

        audio_data = b""
        try:
            data = response.json()
            candidates_list = []
            if isinstance(data, list):
                for chunk in data:
                    if "candidates" in chunk:
                        candidates_list.extend(chunk["candidates"])
            else:
                if "candidates" in data:
                    candidates_list.extend(data["candidates"])

            for candidate in candidates_list:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            audio_data += base64.b64decode(part["inlineData"]["data"])

            return audio_data
        except Exception as e:
            print(f"Error parsing Gemini Audio chunk response: {e}")
            raise

    def generate_audio(self, script: List[Dict[str, str]], model: str = "gemini-2.5-pro-preview-tts") -> bytes:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        # Split script into chunks to avoid TTS timeout issues
        chunks = self._chunk_script(script, max_turns_per_chunk=20)
        print(f"Generating audio in {len(chunks)} chunk(s)...")

        all_audio_data = b""
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)} ({len(chunk)} turns)...")
            chunk_audio = self._generate_audio_chunk(chunk, model)
            all_audio_data += chunk_audio
            # Small delay between chunks to avoid rate limiting
            if i < len(chunks) - 1:
                time.sleep(2)

        return all_audio_data