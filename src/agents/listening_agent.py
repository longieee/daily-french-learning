import json
import os
from datetime import datetime
from typing import Dict
from utils.gemini_client import GeminiClient

class ListeningAgent:
    def __init__(self, client: GeminiClient):
        self.client = client

    def generate_episode(self, level: str, topic: str, date_str: str) -> str:
        """
        Generates the audio file for the given topic and level.
        Returns the path to the generated file.
        """
        print(f"ListeningAgent: Generating script for level {level}, topic {topic}...")

        # 1. Generate Script
        prompt = f"""
        You are an expert French Literature Tutor.
        Input Level: {level}
        Topic: {topic} (Classical French Philosophy/Literature)

        Task:
        1. Select a grounded passage (Quote/Excerpt) relevant to the topic.
        2. Adapt the text strictly to {level} vocabulary/grammar.
        3. Generate a script JSON.

        Constraint for Level {level}:
        - Break text sentence-by-sentence.
        - Insert an English Tutor explaining grammar/meaning between sentences.
        - End with full recitation.

        Output Format (JSON ONLY):
        [
            {{"role": "tutor_en", "text": "English context..."}},
            {{"role": "actor_fr", "text": "French sentence..."}},
            {{"role": "tutor_en", "text": "English explanation..."}}
        ]
        """

        script_text = self.client.generate_content(prompt, model="gemini-3-pro-preview")

        # Clean up script_text if it contains markdown code blocks
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
            print(f"Raw text: {script_text}")
            # Fallback or retry logic could go here. For now, raise.
            raise

        # 2. Generate Audio
        print("ListeningAgent: Synthesizing audio...")
        audio_data = self.client.generate_audio(script_json)

        # 3. Save Audio
        filename = f"daily_drill_{date_str}.mp3"
        filepath = os.path.join("content/audio", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(audio_data)

        print(f"ListeningAgent: Audio saved to {filepath}")
        return filepath
