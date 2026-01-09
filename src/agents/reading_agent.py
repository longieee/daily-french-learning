from utils.gemini_client import GeminiClient
from utils.prompts import get_gauntlet_reading_prompt, get_reading_prompt


class ReadingAgent:
    def __init__(self, client: GeminiClient):
        self.client = client

    def generate_essay(self, level: str, topic: str, date_str: str, is_gauntlet: bool = False, topics_summary: str = "") -> str:
        """
        Generates the reading essay for the given topic and level.
        Returns the essay text (Markdown string).
        """
        print(f"ReadingAgent: Generating essay for level {level}, topic {topic} (Gauntlet={is_gauntlet})...")

        if is_gauntlet:
            prompt = get_gauntlet_reading_prompt(level, topics_summary)
        else:
            prompt = get_reading_prompt(level, topic)

        essay_text = self.client.generate_content(prompt, model="gemini-3-pro-preview")

        return essay_text
        return essay_text
