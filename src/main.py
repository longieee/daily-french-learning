import os
import json
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

    # Check for level up
    if state_manager.check_level_up():
        print(f"Congratulations! Level upgraded to {state_manager.get_current_level()}")

    current_level = state_manager.get_current_level()
    topics_covered = state_manager.get_topics_covered()

    # Brainstorm Topics
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

    # Run Agents
    print(f"Today's Topics: Listening='{listening_topic}', Reading='{reading_topic}'")

    try:
        # 1. Listening (Audio -> Drive URL)
        audio_url = listening_agent.generate_episode(current_level, listening_topic, today_str)
        print(f"Audio available at: {audio_url}")

        # 2. Reading (Essay Text)
        essay_text = reading_agent.generate_essay(current_level, reading_topic, today_str)

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
        state_manager.add_topics([listening_topic, reading_topic])
        state_manager.update_streak()
        state_manager.save_state()

        print("Daily Drill completed successfully.")

    except Exception as e:
        print(f"Critical Error during execution: {e}")
        exit(1)

if __name__ == "__main__":
    main()
