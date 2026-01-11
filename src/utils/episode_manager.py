import json
import os
import shutil
from typing import Dict, List

EPISODES_FILE = "episodes.json"

class EpisodeManager:
    def __init__(self, filepath: str = EPISODES_FILE):
        self.filepath = filepath
        self.episodes = self._load_episodes()

    def _load_episodes(self) -> List[Dict]:
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_episodes(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.episodes, f, indent=2)
        # Also copy to docs folder for GitHub Pages reading interface
        docs_dir = "docs"
        if os.path.exists(docs_dir):
            shutil.copy(self.filepath, os.path.join(docs_dir, EPISODES_FILE))
            print(f"Episodes JSON copied to {docs_dir}/")

    def add_episode(self, date: str, listening_topic: str, reading_topic: str,
                   audio_url: str, description_text: str, reading_content: str = "", file_size: int = 0):
        episode = {
            "date": date,
            "listening_topic": listening_topic,
            "reading_topic": reading_topic,
            "audio_url": audio_url,
            "description": description_text,
            "reading_content": reading_content,
            "file_size": file_size
        }
        # Prepend to list (newest first)
        self.episodes.insert(0, episode)
        self.save_episodes()

    def get_episodes(self) -> List[Dict]:
        return self.episodes
