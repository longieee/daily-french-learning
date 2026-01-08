from datetime import datetime
from feedgen.feed import FeedGenerator
from typing import List, Dict

FEED_FILE = "feed.xml"
# We keep the BASE_URL for the feed link itself, but audio links will come from Drive
BASE_URL = "https://longieee.github.io/daily-french-learning"

class RSSGenerator:
    def __init__(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('podcast')
        self.fg.title("L'Obsédé - Daily French Drill")
        self.fg.description("Automated French learning: Literature, Philosophy, Math, and Physics.")
        self.fg.link(href=BASE_URL, rel='alternate')
        self.fg.language('fr')
        self.fg.author({'name': 'The Machine', 'email': 'bot@machine.com'})

        # Podcast specific settings
        self.fg.podcast.itunes_category('Education', 'Language Courses')
        self.fg.podcast.itunes_explicit('no')

    def generate_feed(self, episodes: List[Dict]):
        # episodes is a list of dicts from EpisodeManager

        for ep in episodes:
            date_str = ep.get("date")
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            fe = self.fg.add_entry()
            fe.id(f"daily-drill-{date_str}")
            fe.title(f"Drill: {date_str} - {ep.get('listening_topic')}")
            fe.link(href=ep.get("audio_url"))

            fe.description(ep.get("description", "Daily French Drill."))
            fe.pubDate(dt.replace(hour=6, minute=0, second=0, microsecond=0).astimezone())

            # Enclosure
            # We don't know the exact size without querying Drive, using 0 or mock is risky for some players.
            # But we can try to use a default.
            fe.enclosure(ep.get("audio_url"), "0", 'audio/mpeg')

        self.fg.rss_file(FEED_FILE)
