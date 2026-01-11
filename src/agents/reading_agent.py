import json

from utils.gemini_client import GeminiClient
from utils.prompts import get_gauntlet_reading_prompt, get_reading_prompt


class ReadingAgent:
    def __init__(self, client: GeminiClient):
        self.client = client

    def generate_essay(self, level: str, topic: str, date_str: str, is_gauntlet: bool = False, topics_summary: str = "") -> str:
        """
        Generates the reading essay for the given topic and level.
        Returns JSON string with structured reading content.
        """
        print(f"ReadingAgent: Generating essay for level {level}, topic {topic} (Gauntlet={is_gauntlet})...")

        if is_gauntlet:
            prompt = get_gauntlet_reading_prompt(level, topics_summary)
        else:
            prompt = get_reading_prompt(level, topic)

        response_text = self.client.generate_content(prompt, model="gemini-3-pro-preview")

        # Clean up JSON response
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        # Validate it's valid JSON, but return as string for storage
        try:
            json.loads(response_text)  # Validate
        except json.JSONDecodeError as e:
            print(f"Warning: Reading content is not valid JSON: {e}")
            # Return as-is for backward compatibility
        
        return response_text

