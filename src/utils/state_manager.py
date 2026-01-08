import json
import os
from datetime import datetime, timedelta
from typing import List

STATE_FILE = "user_state.json"
LEVELS = ["A2", "B1", "B2"]

class StateManager:
    def __init__(self, filepath: str = STATE_FILE):
        self.filepath = filepath
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if not os.path.exists(self.filepath):
            return {
                "current_level": "A2",
                "day_streak": 0,
                "topics_covered": [],
                "last_run_date": "1970-01-01"
            }
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save_state(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_current_level(self) -> str:
        return self.state.get("current_level", "A2")

    def get_topics_covered(self) -> List[str]:
        return self.state.get("topics_covered", [])

    def update_streak(self):
        last_date_str = self.state.get("last_run_date", "1970-01-01")
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        except ValueError:
            last_date = datetime(1970, 1, 1).date()

        today = datetime.utcnow().date()

        if last_date == today:
            return
        elif last_date == today - timedelta(days=1):
            self.state["day_streak"] += 1
        else:
            self.state["day_streak"] = 1

        self.state["last_run_date"] = today.strftime("%Y-%m-%d")

    def check_level_up(self) -> bool:
        streak = self.state.get("day_streak", 0)
        current_level = self.state.get("current_level", "A2")

        if streak > 0 and streak % 30 == 0:
            try:
                current_idx = LEVELS.index(current_level)
                if current_idx < len(LEVELS) - 1:
                    new_level = LEVELS[current_idx + 1]
                    self.state["current_level"] = new_level
                    return True
            except ValueError:
                pass
        return False

    def add_topics(self, new_topics: List[str]):
        current_topics = set(self.state.get("topics_covered", []))
        for t in new_topics:
            current_topics.add(t)
        self.state["topics_covered"] = list(current_topics)
