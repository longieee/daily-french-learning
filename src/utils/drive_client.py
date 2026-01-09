import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveClient:
    def __init__(self):
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
        self.folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            print("Warning: OAuth credentials not fully configured.")
            print("Required: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN")
            self.service = None
            return

        try:
            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=SCOPES
            )
            # Refresh to get a valid access token
            creds.refresh(Request())
            self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error initializing Drive Client: {e}")
            self.service = None

    def upload_file(self, filepath: str, filename: str) -> str:
        """
        Uploads a file to the configured Google Drive folder.
        Returns the webContentLink (direct download link).
        """
        if not self.service:
            print("Drive service not initialized. Skipping upload.")
            return "http://mock-drive-url.com/file.mp3"

        file_metadata = {
            'name': filename,
            'parents': [self.folder_id] if self.folder_id else []
        }

        media = MediaFileUpload(filepath, resumable=True)

        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

            file_id = file.get('id')
            print(f"File ID: {file_id}")

            # Make public (Anyone with link can read)
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id',
                supportsAllDrives=True
            ).execute()

            # Get the webContentLink
            result = self.service.files().get(
                fileId=file_id,
                fields='webContentLink, webViewLink, size',
                supportsAllDrives=True
            ).execute()

            # webContentLink is for downloading/streaming
            url = result.get('webContentLink') or result.get('webViewLink')
            file_size = int(result.get('size', 0))
            
            return url, file_size

        except Exception as e:
            print(f"Error uploading to Drive: {e}")
            raise