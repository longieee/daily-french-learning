import os
import json
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class DriveClient:
    def __init__(self):
        self.service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

        if not self.service_account_json:
            print("Warning: GOOGLE_SERVICE_ACCOUNT_JSON not set.")
            self.service = None
            return

        try:
            # Parse the JSON string
            creds_dict = json.loads(self.service_account_json)
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
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
                fields='id'
            ).execute()

            file_id = file.get('id')
            print(f"File ID: {file_id}")

            # Make public (Anyone with link can read)
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()

            # Get the webContentLink
            result = self.service.files().get(
                fileId=file_id,
                fields='webContentLink, webViewLink'
            ).execute()

            # webContentLink is for downloading/streaming
            return result.get('webContentLink') or result.get('webViewLink')

        except Exception as e:
            print(f"Error uploading to Drive: {e}")
            raise
