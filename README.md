# L'Obsédé - Automated French Learning System

This project generates daily French study materials (Audio & Text) using Google Gemini models, stores the audio in Google Drive, and publishes an RSS feed via GitHub Pages.

## Architecture

### Components

1. **Manager (`src/main.py`)**: The central orchestrator. It runs daily, checks user state (level, streak), and triggers the agents.
2. **Listening Agent (`src/agents/listening_agent.py`)**:
   - Generates a French-immersive podcast script (Literature/Philosophy) using `gemini-3-pro-preview`.
   - Synthesizes multi-speaker audio (Tutor + Acteur) using `gemini-2.5-pro-preview-tts` (Voices: Zephyr & Puck).
   - Uploads the MP3 to **Google Drive** via `DriveClient`.
   - Returns a public link, file size, and transcript.
3. **Reading Agent (`src/agents/reading_agent.py`)**:
   - Generates structured JSON with essay, vocabulary annotations, and exercises with answers.
   - Output stored in `reading_content` field for the interactive web interface.
4. **Episode Manager (`src/utils/episode_manager.py`)**:
   - Maintains a database of past episodes in `episodes.json`.
   - Stores Date, Topics, Audio URL, Transcript, and Reading Content (JSON).
5. **RSS Generator (`src/utils/rss_generator.py`)**:
   - Reads `episodes.json` and generates a valid Podcast RSS feed (`feed.xml`).
6. **Reading Web Interface (`/read/`)**:
   - Mobile-friendly static site at `https://longieee.github.io/daily-french-learning/read/`
   - Vocabulary words are clickable → popup with definition and grammar notes
   - Interactive exercises with answer checking (fill-in-blank, true/false, multiple choice, translation)
   - Dark mode support

### Data Flow

1. **GitHub Actions** triggers `src/main.py` daily at 06:00 UTC.
2. `main.py` loads `user_state.json`.
3. Gemini generates content based on curriculum.
4. Audio is uploaded to Drive.
5. `episodes.json` is updated with the new episode.
6. `feed.xml` is regenerated.
7. All files are committed back to the repo.

## Workflow

The system is fully automated via `.github/workflows/daily_drill.yml`.

### Daily Routine

1. **Checkout Code**: Pulls the latest state.
2. **Install Dependencies**: `google-api-python-client`, `feedgen`, etc.
3. **Run Application**: Executes the Python logic.
   - Authenticates with Google Drive using OAuth2.
   - Authenticates with Gemini using API Key.
4. **Commit Artifacts**: Pushes updated JSON databases and XML feed.
5. **Deploy to GitHub Pages**: Serves from repo root.

## Setup & Configuration

### Environment Variables

The following secrets must be set in the GitHub Repository settings:

- `GEMINI_API_KEY`: API Key for Google Gemini (AI Studio).
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`: OAuth2 credentials for Google Drive.
- `GOOGLE_DRIVE_FOLDER_ID`: The ID of the Google Drive folder for audio files.

### Local Development

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables in your shell or `.env` file.
3. Run the manager:

   ```bash
   python src/main.py
   ```

## Storage Strategy

- **Audio (.mp3)**: Stored in **Google Drive** to avoid git repository bloat.
- **Metadata (JSON/XML)**: Stored in **Git** to drive the RSS feed and reading interface.
- **Hosting**: GitHub Pages serves from repo root. RSS feed at `/feed.xml`, reading at `/read/`.

