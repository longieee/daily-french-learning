import os
from datetime import datetime
from typing import Dict, List

from feedgen.feed import FeedGenerator

FEED_FILE = "feed.xml"
# We keep the BASE_URL for the feed link itself, but audio links will come from Drive
BASE_URL = "https://longieee.github.io/daily-french-learning"
# Placeholder image - you should replace this with a real 1400x1400+ image
PODCAST_IMAGE = "https://longieee.github.io/daily-french-learning/artwork.jpg"

class RSSGenerator:
    def __init__(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('podcast')
        self.fg.title("L'Obsédé - Daily French Drill")
        self.fg.description("Automated French learning: Literature, Philosophy, Math, and Physics.")
        self.fg.link(href=BASE_URL, rel='alternate')
        self.fg.language('fr')
        self.fg.author({'name': 'The Machine', 'email': 'bot@machine.com'})
        
        # Required for Apple Podcasts
        self.fg.logo(PODCAST_IMAGE)
        self.fg.image(PODCAST_IMAGE)

        # Podcast specific settings (iTunes)
        self.fg.podcast.itunes_category('Education', 'Language Courses')
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_author('The Machine')
        self.fg.podcast.itunes_summary("Daily automated French learning podcast covering Literature, Philosophy, Mathematics, and Physics. Each episode features listening comprehension and vocabulary building.")
        self.fg.podcast.itunes_image(PODCAST_IMAGE)
        self.fg.podcast.itunes_owner(name='The Machine', email='bot@machine.com')

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

            # Enclosure - use file_size if available, otherwise estimate based on duration
            # Most podcast apps require a non-zero length
            file_size = ep.get("file_size", 0)
            if file_size == 0:
                # Estimate: ~128kbps MP3 = 16KB/sec, 10 min episode = ~10MB
                file_size = 10000000  # 10MB default estimate
            fe.enclosure(ep.get("audio_url"), str(file_size), 'audio/mpeg')

        # Generate feed file
        self.fg.rss_file(FEED_FILE)

