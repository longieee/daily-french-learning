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

def get_gauntlet_listening_prompt(level: str, topics_summary: str) -> str:
    return f"""
    You are the Gatekeeper of French Mastery.
    Input Level: {level} (Testing for promotion to next level)
    Topics to Review: {topics_summary}

    Task:
    1. Generate a rigorous, high-speed test script summarizing these topics.
    2. NO ENGLISH SUPPORT allowed in the main content.
    3. The tone should be intense and challenging.

    Intro Constraint:
    - Start EXACTLY with this English line: "This is a test. If you understand 90% of this, edit your config file to Level [Next Level]. Until then, you remain here."

    Output Format (JSON ONLY):
    [
        {{"role": "tutor_en", "text": "This is a test. If you understand 90% of this, edit your config file to Level [Next Level]. Until then, you remain here."}},
        {{"role": "actor_fr", "text": "Complex French summary/test sentence 1...", "speed": 1.1}},
        {{"role": "actor_fr", "text": "Complex French summary/test sentence 2...", "speed": 1.1}},
        ...
    ]
    """

def get_gauntlet_reading_prompt(level: str, topics_summary: str) -> str:
    return f"""
    You are the Gatekeeper of French Mastery.
    Input Level: {level} (Testing for promotion)
    Topics to Review: {topics_summary}

    Task:
    1. Write a complex, high-density essay synthesizing the review topics.
    2. NO GLOSSARY. NO ENGLISH HELP.
    3. Use complex sentence structures suitable for testing mastery of {level}.

    Output Format (Markdown):
    # THE GAUNTLET: REVIEW ({level})

    ## L'Épreuve (The Trial)
    [Full French Text - Dense and Fast-Paced Style]

    ## Questions de Vie ou de Mort (Active Recall)
    1. Hard question 1 (in French).
    2. Hard question 2 (in French).
    3. Hard question 3 (in French).
    """
