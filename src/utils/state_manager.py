import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

STATE_FILE = "user_state.json"
LEVEL_THRESHOLDS = {"A2": 60, "B1": 120, "B2": 200}


class StateManager:
    def __init__(self, filepath: str = STATE_FILE):
        self.filepath = filepath
        self.state = self._load_state()

    def _load_state(self) -> dict:
        default_progress = {
            "literature": {},
            "philosophy": {},
            "physics": {},
            "mathematics": {},
        }
        if not os.path.exists(self.filepath):
            return {
                "current_level": "A2",
                "xp_in_level": 0,
                "status": "TRAINING",
                "last_run_date": "1970-01-01",
                "day_streak": 0,
                "current_chain": None,
                "progress": default_progress,
            }
        with open(self.filepath, "r") as f:
            data = json.load(f)
            # Migration logic
            if "xp_in_level" not in data:
                data["xp_in_level"] = 0
            if "status" not in data:
                data["status"] = "TRAINING"
            if "progress" not in data:
                data["progress"] = default_progress
            else:
                # Ensure all categories exist
                for cat in default_progress:
                    if cat not in data["progress"]:
                        data["progress"][cat] = {}
            if "current_chain" not in data:
                data["current_chain"] = None
            # Remove old topics_covered if exists
            if "topics_covered" in data:
                del data["topics_covered"]
            return data

    def save_state(self):
        with open(self.filepath, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_current_level(self) -> str:
        return self.state.get("current_level", "A2")

    def get_status(self) -> str:
        return self.state.get("status", "TRAINING")

    def get_xp(self) -> int:
        return self.state.get("xp_in_level", 0)

    def get_progress(self) -> Dict:
        return self.state.get("progress", {})

    def get_current_chain(self) -> Optional[Dict]:
        return self.state.get("current_chain")

    def set_current_chain(
        self,
        category: str,
        topic_name: str,
        subtopic_id: str,
        current_episode: int,
        total_episodes: int,
    ):
        """Set or update the current episode chain."""
        self.state["current_chain"] = {
            "category": category,
            "topic_name": topic_name,
            "subtopic_id": subtopic_id,
            "current_episode": current_episode,
            "total_episodes": total_episodes,
        }

    def clear_current_chain(self):
        """Clear the current chain when a subtopic is completed."""
        self.state["current_chain"] = None

    def update_progress(
        self, category: str, topic_name: str, subtopic_id: str, episode_completed: int
    ):
        """Update progress for a specific subtopic."""
        if category not in self.state["progress"]:
            self.state["progress"][category] = {}
        if topic_name not in self.state["progress"][category]:
            self.state["progress"][category][topic_name] = {}
        if subtopic_id not in self.state["progress"][category][topic_name]:
            self.state["progress"][category][topic_name][subtopic_id] = {
                "completed_episodes": 0,
                "last_studied": None,
            }

        self.state["progress"][category][topic_name][subtopic_id][
            "completed_episodes"
        ] = episode_completed
        self.state["progress"][category][topic_name][subtopic_id]["last_studied"] = (
            datetime.utcnow().strftime("%Y-%m-%d")
        )

    def update_streak_and_date(self):
        last_date_str = self.state.get("last_run_date", "1970-01-01")
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        except ValueError:
            last_date = datetime(1970, 1, 1).date()

        today = datetime.utcnow().date()

        if last_date == today:
            return
        elif last_date == today - timedelta(days=1):
            self.state["day_streak"] = self.state.get("day_streak", 0) + 1
        else:
            self.state["day_streak"] = 1

        self.state["last_run_date"] = today.strftime("%Y-%m-%d")

    def check_gauntlet_entry(self):
        """Checks if the user has reached the XP threshold for the Gauntlet."""
        level = self.get_current_level()
        xp = self.get_xp()
        threshold = LEVEL_THRESHOLDS.get(level, 200)

        if xp >= threshold:
            self.state["status"] = "GAUNTLET"
        else:
            self.state["status"] = "TRAINING"

    def increment_xp(self):
        if self.state["status"] == "TRAINING":
            self.state["xp_in_level"] += 1
