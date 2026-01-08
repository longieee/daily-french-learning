import json
import os
import random
from datetime import datetime
from utils.state_manager import StateManager
from utils.rss_generator import RSSGenerator
from utils.gemini_client import GeminiClient
from utils.drive_client import DriveClient
from utils.episode_manager import EpisodeManager
from utils.prompts import get_brainstorm_prompt
from agents.listening_agent import ListeningAgent
from agents.reading_agent import ReadingAgent

def main():
    print("Starting L'Obsédé Daily Drill (Drive Edition)...")

    # Initialize components
    state_manager = StateManager()
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
    topics_covered = state_manager.get_topics_covered()

    print(f"Status: {status} | Level: {current_level} | XP: {xp}")

    is_gauntlet = (status == "GAUNTLET")
    listening_topic = ""
    reading_topic = ""
    topics_summary = ""

    if is_gauntlet:
        # Gauntlet Mode: Review recent topics
        recent_topics = topics_covered[-10:] if topics_covered else ["General French"]
        topics_summary = ", ".join(recent_topics)
        listening_topic = f"THE GAUNTLET: Review of {len(recent_topics)} topics"
        reading_topic = listening_topic
        print(f"Entering GAUNTLET MODE. Reviewing: {topics_summary}")
    else:
        # Training Mode: Brainstorm new topics
        print("Brainstorming new topics...")
        brainstorm_prompt = get_brainstorm_prompt(json.dumps(topics_covered))
        try:
            topics_json_str = gemini_client.generate_content(brainstorm_prompt, model="gemini-3-pro-preview")
            if topics_json_str.startswith("```json"):
                topics_json_str = topics_json_str[7:]
            if topics_json_str.startswith("```"):
                topics_json_str = topics_json_str[3:]
            if topics_json_str.endswith("```"):
                topics_json_str = topics_json_str[:-3]

            topics = json.loads(topics_json_str)
            listening_topic = topics.get("listening_topic", "Camus_Stranger_Default")
            reading_topic = topics.get("reading_topic", "Entropy_Default")
        except Exception as e:
            print(f"Error brainstorming topics: {e}. Using fallbacks.")
            listening_topic = f"Philosophy_{random.randint(1, 100)}"
            reading_topic = f"Physics_{random.randint(1, 100)}"

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    print(f"Today's Topics: Listening='{listening_topic}', Reading='{reading_topic}'")

    try:
        # 1. Listening (Audio -> Drive URL)
        audio_url = listening_agent.generate_episode(
            current_level, listening_topic, today_str,
            is_gauntlet=is_gauntlet, topics_summary=topics_summary
        )
        print(f"Audio available at: {audio_url}")

        # 2. Reading (Essay Text)
        essay_text = reading_agent.generate_essay(
            current_level, reading_topic, today_str,
            is_gauntlet=is_gauntlet, topics_summary=topics_summary
        )

        # 3. Save Episode Metadata
        episode_manager.add_episode(
            date=today_str,
            listening_topic=listening_topic,
            reading_topic=reading_topic,
            audio_url=audio_url,
            description_text=essay_text
        )

        # 4. Update Feed
        episodes = episode_manager.get_episodes()
        rss_generator.generate_feed(episodes)

        # 5. Update State
        if not is_gauntlet:
            state_manager.add_topics([listening_topic, reading_topic])
            state_manager.increment_xp()

        state_manager.update_streak_and_date()
        state_manager.save_state()

        print("Daily Drill completed successfully.")

    except Exception as e:
        print(f"Critical Error during execution: {e}")
        exit(1)

if __name__ == "__main__":
    main()
