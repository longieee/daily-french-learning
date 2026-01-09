import json
import os
import random
from typing import Dict, List, Optional, Tuple

CURRICULUM_FILE = "curriculum.json"


class CurriculumManager:
    def __init__(self, filepath: str = CURRICULUM_FILE):
        self.filepath = filepath
        self.curriculum = self._load_curriculum()

    def _load_curriculum(self) -> Dict:
        if not os.path.exists(self.filepath):
            return {
                "literature": {},
                "philosophy": {},
                "physics": {},
                "mathematics": {},
            }
        with open(self.filepath, "r") as f:
            return json.load(f)

    def _save_curriculum(self):
        """Save curriculum back to file (used when brainstorming new content)."""
        with open(self.filepath, "w") as f:
            json.dump(self.curriculum, f, indent=2, ensure_ascii=False)

    def get_existing_topics(self, category: str) -> str:
        """Get list of existing topics in a category for brainstorming prompt."""
        topics = self.curriculum.get(category, {})
        return ", ".join(topics.keys()) if topics else "None"

    def add_brainstormed_topic(self, category: str, topic_data: Dict) -> bool:
        """Add a new brainstormed topic to the curriculum."""
        try:
            topic_name = topic_data.get("topic_name")
            if not topic_name:
                return False

            if category not in self.curriculum:
                self.curriculum[category] = {}

            self.curriculum[category][topic_name] = {
                "description": topic_data.get("description", ""),
                "subtopics": topic_data.get("subtopics", []),
                "brainstormed": True,  # Mark as AI-generated
            }
            self._save_curriculum()
            return True
        except Exception as e:
            print(f"Error adding brainstormed topic: {e}")
            return False

    def get_next_topic(
        self, progress: Dict, category: str, allow_advanced: bool = False
    ) -> Optional[Tuple[str, str, Dict]]:
        """
        Returns (topic_name, subtopic_id, subtopic_info) for the next topic to study.
        Prioritizes continuing an existing chain, then picks new topics.
        """
        category_curriculum = self.curriculum.get(category, {})
        category_progress = progress.get(category, {})

        # Find all available subtopics
        available = []
        for topic_name, topic_data in category_curriculum.items():
            topic_progress = category_progress.get(topic_name, {})

            for subtopic in topic_data.get("subtopics", []):
                subtopic_id = subtopic["id"]
                is_advanced = subtopic.get("advanced", False)

                # Skip advanced topics if not allowed
                if is_advanced and not allow_advanced:
                    continue

                # Check progress
                subtopic_progress = topic_progress.get(subtopic_id, {})
                completed_episodes = subtopic_progress.get("completed_episodes", 0)
                total_episodes = subtopic["episodes"]

                if completed_episodes < total_episodes:
                    available.append(
                        {
                            "topic_name": topic_name,
                            "subtopic_id": subtopic_id,
                            "subtopic": subtopic,
                            "completed": completed_episodes,
                            "total": total_episodes,
                            "is_advanced": is_advanced,
                        }
                    )

        if not available:
            return None

        # Prioritize in-progress subtopics (episode chains)
        in_progress = [s for s in available if s["completed"] > 0]
        if in_progress:
            # Continue the one with most progress
            chosen = max(in_progress, key=lambda x: x["completed"])
        else:
            # Start a new topic - prefer non-advanced first
            non_advanced = [s for s in available if not s["is_advanced"]]
            pool = non_advanced if non_advanced else available
            chosen = random.choice(pool)

        return (chosen["topic_name"], chosen["subtopic_id"], chosen["subtopic"])

    def get_subtopic_info(
        self, category: str, topic_name: str, subtopic_id: str
    ) -> Optional[Dict]:
        """Get detailed info about a specific subtopic."""
        category_curriculum = self.curriculum.get(category, {})
        topic_data = category_curriculum.get(topic_name, {})

        for subtopic in topic_data.get("subtopics", []):
            if subtopic["id"] == subtopic_id:
                return {
                    "topic_name": topic_name,
                    "topic_description": topic_data.get("description", ""),
                    "subtopic": subtopic,
                }
        return None

    def get_topics_for_review(self, progress: Dict, count: int = 10) -> List[str]:
        """Get recently completed subtopics for gauntlet review."""
        completed = []

        for category, topics in progress.items():
            for topic_name, topic_progress in topics.items():
                for subtopic_id, subtopic_data in topic_progress.items():
                    if subtopic_data.get("completed_episodes", 0) > 0:
                        completed.append(
                            {
                                "category": category,
                                "topic": topic_name,
                                "subtopic_id": subtopic_id,
                                "last_studied": subtopic_data.get(
                                    "last_studied", "1970-01-01"
                                ),
                            }
                        )

        # Sort by last studied (most recent first) and take top N
        completed.sort(key=lambda x: x["last_studied"], reverse=True)
        return [
            f"{item['topic']} - {item['subtopic_id']}" for item in completed[:count]
        ]

    def format_topic_for_prompt(
        self,
        category: str,
        topic_name: str,
        subtopic: Dict,
        episode_number: int,
        total_episodes: int,
    ) -> str:
        """Format topic info for inclusion in prompts."""
        return f"""
TOPIC: {topic_name}
SUBTOPIC: {subtopic["title"]} (Episode {episode_number} of {total_episodes})
FOCUS: {subtopic["description"]}
CATEGORY: {category}

This is part of an EPISODE CHAIN. Maintain continuity with previous episodes if this is not episode 1.
{"This is the FINAL episode of this subtopic - include a summary and conclusion." if episode_number == total_episodes else ""}
{"This is an ADVANCED topic - go deeper into philosophical/theoretical aspects." if subtopic.get("advanced", False) else ""}
"""
