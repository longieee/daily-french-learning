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

    def generate_audio(self, script: List[Dict[str, str]], model: str = "gemini-2.5-pro-preview-tts") -> bytes:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        url = f"{self.base_url}/{model}:streamGenerateContent?key={self.api_key}"

        parts = []
        parts.append(
            "Read the following dialogue aloud at a natural, conversational pace. Do not slow down for language learners - speak at normal native speed. Speaker 1 is an English Tutor (Voice: Zephyr). Speaker 2 is a French Actor (Voice: Puck)."
        )

        for turn in script:
            speaker_label = "Speaker 1" if turn["role"] == "tutor_en" else "Speaker 2"
            parts.append(f"{speaker_label}: {turn['text']}")

        full_prompt_text = "\n".join(parts)

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
                "responseModalities": ["audio"],
                "speech_config": {
                    "multi_speaker_voice_config": {
                        "speaker_voice_configs": [
                            {
                                "speaker": "Speaker 1",
                                "voice_config": {
                                    "prebuilt_voice_config": {
                                        "voice_name": "Zephyr"
                                    }
                                }
                            },
                            {
                                "speaker": "Speaker 2",
                                "voice_config": {
                                    "prebuilt_voice_config": {
                                        "voice_name": "Puck"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        # TTS can take longer, use extended timeout with manual retry for connection errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.post(url, json=payload, timeout=300)
                response.raise_for_status()
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"TTS request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"TTS request failed after {max_retries} attempts")
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
            print(f"Error parsing Gemini Audio response: {e}")
            raise
            print(f"Error parsing Gemini Audio response: {e}")
            raise
