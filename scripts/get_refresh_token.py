#!/usr/bin/env python3
"""
One-time script to get a refresh token for Google Drive OAuth 2.0.

Usage:
1. Create OAuth 2.0 credentials in Google Cloud Console:
   - Go to https://console.cloud.google.com/apis/credentials
   - Create OAuth 2.0 Client ID (choose "Desktop app")
   - Download the JSON file and save as 'client_secrets.json' in this folder

2. Run this script:
   python scripts/get_refresh_token.py

3. Copy the refresh token and add it to your GitHub secrets as GOOGLE_REFRESH_TOKEN
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    # Load client secrets
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'scripts/client_secrets.json',
            scopes=SCOPES
        )
    except FileNotFoundError:
        print("Error: client_secrets.json not found!")
        print("\nPlease download your OAuth 2.0 credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download JSON and save as 'scripts/client_secrets.json'")
        return

    # Run local server for auth
    creds = flow.run_local_server(port=0)  # Use any available port

    print("\n" + "="*60)
    print("SUCCESS! Here are your credentials:")
    print("="*60)
    print(f"\nGOOGLE_CLIENT_ID:\n{creds.client_id}")
    print(f"\nGOOGLE_CLIENT_SECRET:\n{creds.client_secret}")
    print(f"\nGOOGLE_REFRESH_TOKEN:\n{creds.refresh_token}")
    print("\n" + "="*60)
    print("Add these as GitHub secrets (Settings → Secrets → Actions)")
    print("="*60)

if __name__ == '__main__':
    main()
