# L'Obsédé - Automated French Learning System

This project generates daily French study materials (Audio & Text) using Google Gemini models.

## Architecture
- **Agents**: Listening (TTS) and Reading (Text/Essay).
- **Manager**: State machine that tracks progress and orchestrates daily runs.
- **Automation**: GitHub Actions runs daily at 06:00 UTC.

## Usage
1.  **Dependencies**: `pip install -r requirements.txt`
2.  **Environment**: Set `GEMINI_API_KEY`.
3.  **Run**: `python src/main.py`

## Storage Note
The system currently commits generated content (`.mp3` and `.md`) to the repository to serve via GitHub Pages.
**Future Upgrade**: To use Google Drive for storage (as requested), we will need to implement Google Drive API authentication (OAuth/Service Account) and update the `save_state` and file handling logic. This is deferred for the MVP to avoid complexity with credential management in the initial setup.
