import os
from utils.gemini_client import GeminiClient

class ReadingAgent:
    def __init__(self, client: GeminiClient):
        self.client = client

    def generate_essay(self, level: str, topic: str, date_str: str) -> str:
        """
        Generates the reading essay for the given topic and level.
        Returns the path to the generated file.
        """
        print(f"ReadingAgent: Generating essay for level {level}, topic {topic}...")

        prompt = f"""
        You are a ruthless French Physics Professor.
        Input Level: {level}
        Topic: {topic} (Math/Physics Concept)

        Task:
        1. Write a technical essay (approx 200 words) on the topic.
        2. Grammar Constraint: Use ONLY {level} allowed tenses.
        3. Vocabulary: Highlight technical terms (e.g., 'la dérivée').

        Output Format (Markdown):
        # {topic} ({level})

        ## Section 1: Le Texte
        [The Essay in French]

        ## Section 2: Laboratoire de Vocabulaire
        - Term (FR): Definition (EN)

        ## Section 3: Rappel Actif (Active Recall)
        1. Fill-in-the-blank question based on the text.
        2. Fill-in-the-blank question based on the text.
        3. Fill-in-the-blank question based on the text.
        """

        essay_text = self.client.generate_content(prompt, model="gemini-3-pro-preview")

        # Save Text
        filename = f"{date_str}.md"
        filepath = os.path.join("content/text", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(essay_text)

        print(f"ReadingAgent: Essay saved to {filepath}")
        return filepath
