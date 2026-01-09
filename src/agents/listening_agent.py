import json
import os
import subprocess
from datetime import datetime
from typing import Dict
from utils.gemini_client import GeminiClient
from utils.drive_client import DriveClient
from utils.prompts import get_listening_prompt, get_gauntlet_listening_prompt

class ListeningAgent:
    def __init__(self, client: GeminiClient, drive_client: DriveClient):
        self.client = client
        self.drive_client = drive_client

    def generate_episode(self, level: str, topic: str, date_str: str, is_gauntlet: bool = False, topics_summary: str = "") -> str:
        """
        Generates the audio, uploads to Drive, deletes local file.
        Returns the Drive URL.
        """
        print(f"ListeningAgent: Generating script for level {level}, topic {topic} (Gauntlet={is_gauntlet})...")

        # 1. Generate Script
        if is_gauntlet:
            prompt = get_gauntlet_listening_prompt(level, topics_summary)
        else:
            prompt = get_listening_prompt(level, topic)

        script_text = self.client.generate_content(prompt, model="gemini-3-pro-preview")

        # Clean up script_text
        script_text = script_text.strip()
        if script_text.startswith("```json"):
            script_text = script_text[7:]
        if script_text.startswith("```"):
            script_text = script_text[3:]
        if script_text.endswith("```"):
            script_text = script_text[:-3]
        script_text = script_text.strip()

        try:
            script_json = json.loads(script_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding script JSON: {e}")
            raise

        # 2. Generate Audio
        print("ListeningAgent: Synthesizing audio...")
        audio_data = self.client.generate_audio(script_json)

        # 3. Save to Temporary File and Convert to MP3
        temp_dir = "content/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Gemini TTS returns raw PCM audio (24kHz, 16-bit, little-endian, mono)
        raw_filename = f"daily_drill_{date_str}.pcm"
        raw_filepath = os.path.join(temp_dir, raw_filename)
        
        mp3_filename = f"daily_drill_{date_str}.mp3"
        mp3_filepath = os.path.join(temp_dir, mp3_filename)

        with open(raw_filepath, "wb") as f:
            f.write(audio_data)

        # Convert raw PCM to MP3 using ffmpeg
        print("ListeningAgent: Converting audio to MP3...")
        try:
            result = subprocess.run([
                "ffmpeg", "-y",
                "-f", "s16le",        # Input format: signed 16-bit little-endian
                "-ar", "24000",       # Sample rate: 24kHz
                "-ac", "1",           # Channels: mono
                "-i", raw_filepath,
                "-codec:a", "libmp3lame",
                "-qscale:a", "2",
                mp3_filepath
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting audio: {e.stderr.decode()}")
            raise
        finally:
            # Clean up raw PCM file
            if os.path.exists(raw_filepath):
                os.remove(raw_filepath)

        # 4. Upload to Drive
        print(f"ListeningAgent: Uploading {mp3_filename} to Google Drive...")
        drive_url = self.drive_client.upload_file(mp3_filepath, mp3_filename)

        # 5. Delete Local File
        try:
            os.remove(mp3_filepath)
            print(f"ListeningAgent: Deleted local file {mp3_filepath}")
        except OSError as e:
            print(f"Warning: Could not delete temp file: {e}")

        return drive_url
