import json
import os
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

        # 3. Save to Temporary File
        filename = f"daily_drill_{date_str}.mp3"
        temp_dir = "content/temp"
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, filename)

        with open(filepath, "wb") as f:
            f.write(audio_data)

        # 4. Upload to Drive
        print(f"ListeningAgent: Uploading {filename} to Google Drive...")
        drive_url = self.drive_client.upload_file(filepath, filename)

        # 5. Delete Local File
        try:
            os.remove(filepath)
            print(f"ListeningAgent: Deleted local file {filepath}")
        except OSError as e:
            print(f"Warning: Could not delete temp file: {e}")

        return drive_url
