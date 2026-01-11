LEVEL_DURATION = {"A1": 10, "A2": 10, "B1": 15, "B2": 20, "C1": 20, "C2": 20}
LEVEL_WORD_COUNT = {
    "A1": 800,
    "A2": 900,
    "B1": 1200,
    "B2": 1600,
    "C1": 1800,
    "C2": 2000,
}


def get_listening_prompt(level: str, topic_context: str) -> str:
    duration = LEVEL_DURATION.get(level, 10)
    word_count = LEVEL_WORD_COUNT.get(level, 900)

    return f"""
You are creating a {duration}-MINUTE French immersion audio lesson.
Input Level: {level}

{topic_context}

CRITICAL PHILOSOPHY: Push the learner UP. Less English hand-holding, more French immersion.
The goal is authentic listening practice, not translation exercises.

Task:
1. Create an engaging lesson on this specific subtopic.
2. Adapt vocabulary to {level}, but aim slightly higher to stretch the learner.
3. Generate script JSON (~{word_count}-{word_count + 200} words total).
4. Include philosophical discussion and textual analysis.

Structure:
- Tutor provides BRIEF English context (1-2 sentences max) only when absolutely necessary
- Actor reads extended French passages (multiple sentences at a time)
- Tutor may briefly clarify key vocabulary, but NOT translate everything
- Include French comprehension questions that Actor asks and answers
- End with French summary of key points

MINIMIZE ENGLISH. If the learner struggles, that's growth. French Actor should speak 70%+ of the content.

Output Format (JSON ONLY):
[
    {{"role": "tutor_en", "text": "Brief context..."}},
    {{"role": "actor_fr", "text": "Extended French passage..."}},
    {{"role": "actor_fr", "text": "Continuation in French..."}},
    {{"role": "tutor_en", "text": "One key insight only..."}}
]
"""



def get_reading_prompt(level: str, topic_context: str) -> str:
    return f"""
You are a French Physics/Mathematics Professor with a dramatic, intense teaching style.
You speak as if lecturing passionate students who MUST understand these concepts.
Input Level: {level}

{topic_context}

Task:
1. Write an engaging technical essay (400-500 words) in French.
2. Grammar Constraint: Use ONLY {level} allowed tenses.
3. Make it feel like an exciting lecture - use rhetorical questions, exclamations, vivid examples.
4. Include the mathematical/physical intuition, not just formulas.

CRITICAL: Output as JSON with the following structure.

Output Format (JSON ONLY):
{{
    "title": "Subtopic Title",
    "level": "{level}",
    "text": "The full essay text in French. Mark vocabulary words with [[word]] brackets.",
    "vocabulary": [
        {{"term": "word", "gender": "m/f", "definition": "English definition", "grammar_note": "optional grammar tip"}}
    ],
    "exercises": [
        {{
            "type": "fill_blank",
            "question": "L'énergie est ______ dans l'univers.",
            "answer": "conservée",
            "hint": "Think about the first law"
        }},
        {{
            "type": "true_false",
            "question": "L'entropie diminue toujours.",
            "answer": false,
            "explanation": "L'entropie augmente toujours selon la deuxième loi."
        }},
        {{
            "type": "multiple_choice",
            "question": "Quelle loi parle de la conservation?",
            "options": ["Première", "Deuxième", "Troisième"],
            "answer": "Première",
            "explanation": "La première loi traite de la conservation de l'énergie."
        }},
        {{
            "type": "translation",
            "question": "Energy cannot be destroyed.",
            "answer": "L'énergie ne peut pas être détruite.",
            "accept_variations": ["L'énergie ne peut être détruite"]
        }}
    ]
}}

Guidelines:
- Mark 10-15 vocabulary words in the text using [[word]] brackets
- Include exactly those words in the vocabulary array with definitions
- Include 5-6 exercises with correct answers
- For fill_blank: leave exactly one ____ blank in the question
- For multiple_choice: include 3-4 options
- Vary exercise types for engagement
"""



def get_gauntlet_listening_prompt(level: str, topics_summary: str) -> str:
    return f"""
You are the Gatekeeper of French Mastery.
Input Level: {level} (Testing for promotion to next level)
Topics to Review: {topics_summary}

Task:
1. Generate a rigorous, 10-minute test covering these topics at high speed.
2. NO ENGLISH SUPPORT in the main content after the intro.
3. The tone should be intense and challenging.
4. Test both comprehension and recall of key concepts.

Intro Constraint:
- Start with this English line: "This is a test. If you understand 90 percent of this, you are ready for the next level."

Output Format (JSON ONLY):
[
    {{"role": "tutor_en", "text": "This is a test. If you understand 90 percent of this, you are ready for the next level."}},
    {{"role": "actor_fr", "text": "Complex French summary/test content..."}},
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

CRITICAL: Output in PLAIN TEXT only. NO markdown symbols.

Output Format (PLAIN TEXT):

THE GAUNTLET: REVIEW ({level})

L'EPREUVE (The Trial)

[Full French Text - Dense synthesis of all reviewed topics]

QUESTIONS DE VIE OU DE MORT

1. Hard question in French
2. Hard question in French
3. Hard question in French
4. Hard question in French
5. Hard question in French
"""


def get_brainstorm_prompt(category: str, existing_topics: str) -> str:
    """Generate a prompt to brainstorm new curriculum content when curriculum runs out."""
    category_descriptions = {
        "literature": "Classical French Literature (novels, plays, poetry from French authors)",
        "philosophy": "French Philosophy (existentialism, enlightenment, postmodernism, ethics)",
        "physics": "Physics concepts explained in French",
        "mathematics": "Mathematics concepts explained in French",
    }
    cat_desc = category_descriptions.get(category, category)

    return f"""
You are a curriculum designer for French language learning.
Category: {cat_desc}

Existing topics already in curriculum (DO NOT repeat these):
{existing_topics}

Task: Create a NEW topic with subtopics for the curriculum.

Output Format (JSON ONLY):
{{
    "topic_name": "Name of the work/concept in French",
    "description": "Brief English description of the topic",
    "subtopics": [
        {{
            "id": "unique-id-1",
            "title": "Subtopic title in French",
            "episodes": 2,
            "description": "What this subtopic covers"
        }},
        {{
            "id": "unique-id-2",
            "title": "Another subtopic",
            "episodes": 3,
            "description": "What this covers"
        }}
    ]
}}

Guidelines:
- For literature: Choose a specific French literary work (novel, play, collection)
- For philosophy: Choose a specific philosopher or philosophical movement
- For physics/math: Choose a coherent topic area
- Each topic should have 3-6 subtopics
- Each subtopic should have 2-4 episodes
- Include one "advanced" subtopic for deeper exploration
"""
