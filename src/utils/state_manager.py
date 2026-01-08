import json
import os
from datetime import datetime, timedelta
from typing import List

STATE_FILE = "user_state.json"
LEVEL_THRESHOLDS = {"A2": 60, "B1": 120, "B2": 200}

class StateManager:
    def __init__(self, filepath: str = STATE_FILE):
        self.filepath = filepath
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if not os.path.exists(self.filepath):
            return {
                "current_level": "A2",
                "xp_in_level": 0,
                "status": "TRAINING",
                "topics_covered": [],
                "last_run_date": "1970-01-01"
            }
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            # Migration logic
            if "xp_in_level" not in data:
                data["xp_in_level"] = 0
            if "status" not in data:
                data["status"] = "TRAINING"
            return data

    def save_state(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_current_level(self) -> str:
        return self.state.get("current_level", "A2")

    def get_status(self) -> str:
        return self.state.get("status", "TRAINING")

    def get_xp(self) -> int:
        return self.state.get("xp_in_level", 0)

    def get_topics_covered(self) -> List[str]:
        return self.state.get("topics_covered", [])

    def update_streak_and_date(self):
        # We still track date to prevent double runs, but streak is less relevant for promotion now.
        # However, keeping streak for user vanity is fine.
        # The prompt didn't ask to delete streak, just change promotion logic.
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
        """
        Checks if the user has reached the XP threshold for the Gauntlet.
        """
        level = self.get_current_level()
        xp = self.get_xp()
        threshold = LEVEL_THRESHOLDS.get(level, 200)

        if xp >= threshold:
            self.state["status"] = "GAUNTLET"
        else:
            # Ensure we are in TRAINING if below threshold (e.g. after manual level up reset)
            self.state["status"] = "TRAINING"

    def increment_xp(self):
        if self.state["status"] == "TRAINING":
            self.state["xp_in_level"] += 1

    def add_topics(self, new_topics: List[str]):
        current_topics = set(self.state.get("topics_covered", []))
        for t in new_topics:
            current_topics.add(t)
        self.state["topics_covered"] = list(current_topics)
