# L'Obsédé - Automated French Learning System

This project generates daily French study materials (Audio & Text) using Google Gemini models, stores the audio in Google Drive, and publishes an RSS feed via GitHub Pages.

## Architecture

### Components
1.  **Manager (`src/main.py`)**: The central orchestrator. It runs daily, checks user state (level, streak), brainstorms new topics, and triggers the agents.
2.  **Listening Agent (`src/agents/listening_agent.py`)**:
    - Generates a French-immersive podcast script (Literature/Philosophy) using `gemini-3-pro-preview`.
    - Synthesizes multi-speaker audio (Tutor + Acteur) using `gemini-2.5-pro-preview-tts` (Voices: Zephyr & Puck).
    - Uploads the MP3 to **Google Drive** via `DriveClient`.
    - Returns a public link, file size, and transcript.
3. **Reading Agent (`src/agents/reading_agent.py`)**:
    - Generates a technical essay (Math/Physics) using `gemini-3-pro-preview`.
    - Output is stored separately for web access.
4. **Episode Manager (`src/utils/episode_manager.py`)**:
    - Maintains a database of past episodes in `episodes.json`.
    - Stores Date, Topics, Audio URL (Drive), Transcript (podcast description), and Reading Content.
5. **RSS Generator (`src/utils/rss_generator.py`)**:
    - Reads `episodes.json` and generates a valid Podcast RSS feed (`feed.xml`).
    - Uses the Google Drive public link for the audio enclosure.
6. **Reading Web Interface (`docs/read/`)**:
    - Mobile-friendly static site for reading practice on iPhone/MacBook.
    - Loads `episodes.json` and displays reading content with dark mode support.


### Data Flow
1.  **GitHub Actions** triggers `src/main.py` daily at 06:00 UTC.
2.  `main.py` loads `user_state.json`.
3.  Gemini brainstorms unique topics based on history.
4.  Agents generate content. Audio is uploaded to Drive.
5.  `episodes.json` is updated with the new episode.
6.  `feed.xml` is regenerated.
7.  `user_state.json`, `episodes.json`, and `feed.xml` are committed back to the repo.

## Workflow

The system is fully automated via `.github/workflows/daily_drill.yml`.

### Daily Routine
1.  **Checkout Code**: Pulls the latest state.
2.  **Install Dependencies**: `google-api-python-client`, `feedgen`, etc.
3.  **Run Application**: Executes the Python logic.
    -   Authenticates with Google Drive using Service Account.
    -   Authenticates with Gemini using API Key.
4.  **Commit Artifacts**: Pushes updated JSON databases and XML feed to the repository.
    -   *Note*: Generated media files are **not** committed to the repo.

## Setup & Configuration

### Environment Variables
The following secrets must be set in the GitHub Repository settings:

-   `GEMINI_API_KEY`: API Key for Google Gemini (AI Studio).
-   `GOOGLE_SERVICE_ACCOUNT_JSON`: The full JSON string of your Google Cloud Service Account key.
-   `GOOGLE_DRIVE_FOLDER_ID`: The ID of the Google Drive folder where audio files will be stored.
    -   *Permissions*: The Service Account must have **Editor** access to this folder.

### Local Development
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set environment variables in your shell or `.env` file.
3.  Run the manager:
    ```bash
    python src/main.py
    ```

## Storage Strategy
-   **Audio (.mp3)**: Stored in **Google Drive** to handle large file sizes and avoid git repository bloat.
-   **Metadata (JSON/XML)**: Stored in **Git** to drive the GitHub Pages site and RSS feed.
-   **Hosting**: The RSS feed is accessible via GitHub Pages (e.g., `https://<user>.github.io/<repo>/feed.xml`).
