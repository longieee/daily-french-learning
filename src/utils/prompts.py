from typing import List

def get_brainstorm_prompt(topics_history: str) -> str:
    return f"""
    I need two distinct topics for a French learning session.
    1. A Classical French Philosophy or Literature topic (e.g., specific work by Camus, Sartre, Voltaire).
    2. A Math or Physics concept (e.g., Entropy, Vectors, Calculus).

    History of covered topics: {topics_history}

    Task: output a JSON object with two fields: "listening_topic" and "reading_topic".
    Ensure they are NOT in the history.
    """

def get_listening_prompt(level: str, topic: str) -> str:
    return f"""
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

def get_reading_prompt(level: str, topic: str) -> str:
    return f"""
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
