import os
from datetime import datetime
from feedgen.feed import FeedGenerator
import glob

FEED_FILE = "feed.xml"
AUDIO_DIR = "content/audio"
TEXT_DIR = "content/text"
# Base URL for the podcast files (GitHub Pages)
# Ideally this should be configurable, but for now we use the user's repo structure
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

    def generate_feed(self):
        # We need to scan existing files to rebuild the feed or load the existing one and append?
        # Rebuilding from file system is safer to ensure sync.

        # Find all mp3 files
        audio_files = sorted(glob.glob(f"{AUDIO_DIR}/*.mp3"), reverse=True)

        for audio_path in audio_files:
            filename = os.path.basename(audio_path)
            # Filename format expected: daily_drill_YYYY-MM-DD.mp3
            # Extract date
            try:
                date_str = filename.replace("daily_drill_", "").replace(".mp3", "")
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            fe = self.fg.add_entry()
            fe.id(f"{BASE_URL}/{audio_path}")
            fe.title(f"Drill: {date_str}")
            fe.link(href=f"{BASE_URL}/{audio_path}")

            # Try to find corresponding text file for description
            text_path = f"{TEXT_DIR}/{date_str}.md"
            description = "Daily French Drill."
            if os.path.exists(text_path):
                with open(text_path, 'r') as f:
                    description = f.read()

            # If description is markdown, we might want to convert to HTML or just plain text.
            # RSS readers usually handle HTML in description.
            fe.description(description)
            fe.pubDate(dt.replace(hour=6, minute=0, second=0, microsecond=0).astimezone())

            # Enclosure
            file_size = os.path.getsize(audio_path)
            fe.enclosure(f"{BASE_URL}/{audio_path}", str(file_size), 'audio/mpeg')

        self.fg.rss_file(FEED_FILE)
