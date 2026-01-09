import json
import random
from datetime import datetime

from agents.listening_agent import ListeningAgent
from agents.reading_agent import ReadingAgent
from utils.curriculum_manager import CurriculumManager
from utils.drive_client import DriveClient
from utils.episode_manager import EpisodeManager
from utils.gemini_client import GeminiClient
from utils.prompts import get_brainstorm_prompt
from utils.rss_generator import RSSGenerator
from utils.state_manager import StateManager

# Listening draws from literature OR philosophy
LISTENING_CATEGORIES = ["literature", "philosophy"]
# Reading draws from physics OR mathematics
READING_CATEGORIES = ["physics", "mathematics"]


def brainstorm_new_topic(gemini_client, curriculum_manager, category: str) -> dict:
    """Use Gemini to brainstorm a new topic when curriculum runs out."""
    print(f"Brainstorming new {category} topic...")
    existing = curriculum_manager.get_existing_topics(category)
    prompt = get_brainstorm_prompt(category, existing)

    try:
        response = gemini_client.generate_content(prompt, model="gemini-3-pro-preview")
        # Clean up response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        topic_data = json.loads(response)

        # Add to curriculum
        if curriculum_manager.add_brainstormed_topic(category, topic_data):
            print(f"Added new brainstormed topic: {topic_data.get('topic_name')}")
            return topic_data
    except Exception as e:
        print(f"Error brainstorming topic: {e}")

    return None


def get_topic_with_fallback(
    gemini_client, curriculum_manager, progress, categories, allow_advanced
):
    """Try to get a topic from curriculum, brainstorm if empty."""
    # Shuffle categories to add variety
    shuffled = categories.copy()
    random.shuffle(shuffled)

    for category in shuffled:
        result = curriculum_manager.get_next_topic(progress, category, allow_advanced)
        if result:
            topic_name, subtopic_id, subtopic = result
            topic_progress = progress.get(category, {}).get(topic_name, {})
            subtopic_progress = topic_progress.get(subtopic_id, {})
            episode = subtopic_progress.get("completed_episodes", 0) + 1
            total = subtopic["episodes"]
            return category, topic_name, subtopic_id, subtopic, episode, total

    # All categories exhausted - brainstorm new content
    for category in shuffled:
        new_topic = brainstorm_new_topic(gemini_client, curriculum_manager, category)
        if new_topic and new_topic.get("subtopics"):
            subtopic = new_topic["subtopics"][0]
            return (
                category,
                new_topic["topic_name"],
                subtopic["id"],
                subtopic,
                1,
                subtopic["episodes"],
            )

    # Ultimate fallback
    return (
        shuffled[0],
        "General French",
        "fallback",
        {"title": "Open Discussion", "description": "Free-form lesson", "episodes": 1},
        1,
        1,
    )


def main():
    print("Starting L'Obsédé Daily Drill...")

    # Initialize components
    state_manager = StateManager()
    curriculum_manager = CurriculumManager()
    gemini_client = GeminiClient()
    drive_client = DriveClient()
    rss_generator = RSSGenerator()
    episode_manager = EpisodeManager()

    listening_agent = ListeningAgent(gemini_client, drive_client)
    reading_agent = ReadingAgent(gemini_client)

    # Check Gauntlet Threshold
    state_manager.check_gauntlet_entry()

    current_level = state_manager.get_current_level()
    status = state_manager.get_status()
    xp = state_manager.get_xp()
    progress = state_manager.get_progress()
    current_chain = state_manager.get_current_chain()

    print(f"Status: {status} | Level: {current_level} | XP: {xp}")

    is_gauntlet = status == "GAUNTLET"
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Determine if we should allow advanced topics (after some XP)
    allow_advanced = xp >= 30

    if is_gauntlet:
        # Gauntlet Mode: Review recent topics
        topics_for_review = curriculum_manager.get_topics_for_review(progress, count=10)
        topics_summary = (
            ", ".join(topics_for_review) if topics_for_review else "General French"
        )
        listening_topic = "THE GAUNTLET: Review"
        reading_topic = listening_topic
        listening_context = f"Review topics: {topics_summary}"
        reading_context = listening_context
        print(f"Entering GAUNTLET MODE. Reviewing: {topics_summary}")

        # Generate content
        audio_url = listening_agent.generate_episode(
            current_level,
            listening_context,
            today_str,
            is_gauntlet=True,
            topics_summary=topics_summary,
        )
        essay_text = reading_agent.generate_essay(
            current_level,
            reading_context,
            today_str,
            is_gauntlet=True,
            topics_summary=topics_summary,
        )
    else:
        # Training Mode: Use curriculum
        print("Selecting topics from curriculum...")

        # LISTENING: Check for existing chain first
        if current_chain:
            lit_category = current_chain["category"]
            lit_topic = current_chain["topic_name"]
            lit_subtopic_id = current_chain["subtopic_id"]
            lit_episode = current_chain["current_episode"]
            lit_total = current_chain["total_episodes"]
            lit_subtopic_info = curriculum_manager.get_subtopic_info(
                lit_category, lit_topic, lit_subtopic_id
            )
            if lit_subtopic_info:
                lit_subtopic = lit_subtopic_info["subtopic"]
            else:
                # Chain info invalid (maybe curriculum changed), reset and pick new
                state_manager.clear_current_chain()
                current_chain = None

        if not current_chain:
            # Pick from literature or philosophy
            (
                lit_category,
                lit_topic,
                lit_subtopic_id,
                lit_subtopic,
                lit_episode,
                lit_total,
            ) = get_topic_with_fallback(
                gemini_client,
                curriculum_manager,
                progress,
                LISTENING_CATEGORIES,
                allow_advanced,
            )

        # READING: Pick from physics or mathematics (no chains, single episodes)
        (
            sci_category,
            sci_topic,
            sci_subtopic_id,
            sci_subtopic,
            sci_episode,
            sci_total,
        ) = get_topic_with_fallback(
            gemini_client,
            curriculum_manager,
            progress,
            READING_CATEGORIES,
            allow_advanced,
        )

        # Format topic context for prompts
        listening_context = curriculum_manager.format_topic_for_prompt(
            lit_category, lit_topic, lit_subtopic, lit_episode, lit_total
        )
        reading_context = curriculum_manager.format_topic_for_prompt(
            sci_category, sci_topic, sci_subtopic, sci_episode, sci_total
        )

        listening_topic = (
            f"{lit_topic}: {lit_subtopic['title']} ({lit_episode}/{lit_total})"
        )
        reading_topic = (
            f"{sci_topic}: {sci_subtopic['title']} ({sci_episode}/{sci_total})"
        )

        print(f"Listening: {listening_topic}")
        print(f"Reading: {reading_topic}")

        try:
            # 1. Generate Listening (Audio -> Drive URL)
            audio_url = listening_agent.generate_episode(
                current_level, listening_context, today_str
            )
            print(f"Audio available at: {audio_url}")

            # 2. Generate Reading (Essay Text)
            essay_text = reading_agent.generate_essay(
                current_level, reading_context, today_str
            )

            # 3. Update progress for listening topic (episode chain)
            state_manager.update_progress(
                lit_category, lit_topic, lit_subtopic_id, lit_episode
            )

            # Update or clear chain
            if lit_episode < lit_total:
                state_manager.set_current_chain(
                    lit_category,
                    lit_topic,
                    lit_subtopic_id,
                    lit_episode + 1,
                    lit_total,
                )
                print(f"Episode chain continues: {lit_episode + 1}/{lit_total} next")
            else:
                state_manager.clear_current_chain()
                print(f"Episode chain completed for: {lit_subtopic['title']}")

            # 4. Update progress for reading topic
            state_manager.update_progress(
                sci_category, sci_topic, sci_subtopic_id, sci_episode
            )

        except Exception as e:
            print(f"Critical Error during content generation: {e}")
            raise

    # Save Episode Metadata
    episode_manager.add_episode(
        date=today_str,
        listening_topic=listening_topic,
        reading_topic=reading_topic,
        audio_url=audio_url,
        description_text=essay_text,
    )

    # Update Feed
    episodes = episode_manager.get_episodes()
    rss_generator.generate_feed(episodes)

    # Update State
    if not is_gauntlet:
        state_manager.increment_xp()

    state_manager.update_streak_and_date()
    state_manager.save_state()

    print("Daily Drill completed successfully.")


if __name__ == "__main__":
    main()
