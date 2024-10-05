import os
import io
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import json

class GoogleDriveDownloader:
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    def __init__(self):
        """Initializes the downloader using Streamlit secrets for Google Drive credentials."""
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates using the service account credentials from Streamlit secrets and initializes the Drive API client."""
        try:
            # Retrieve credentials from Streamlit secrets
            credentials_info = st.secrets["google_drive_credentials"]["credentials"]
            self.creds = Credentials.from_service_account_info(json.loads(credentials_info), scopes=self.SCOPES)

            # Initialize the Drive API client
            self.service = build("drive", "v3", credentials=self.creds)

        except Exception as e:
            print(f"Failed to authenticate using service account: {e}")

    def download_google_sheet(self, sheet_url, output_file='sheet.csv'):
        """Downloads a Google Sheet as a CSV file (.csv).
        
        Args:
            sheet_url: URL of the Google Sheet to download.
            output_file: Path to save the downloaded file.
        """
        try:
            # Extract file ID from the Google Sheet URL
            file_id = sheet_url.split("/d/")[1].split("/")[0]

            # Request to export the Google Sheet as a CSV file
            request = self.service.files().export_media(fileId=file_id, mimeType='text/csv')
            
            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}% complete.")

            # Write the downloaded content to a CSV file
            with open(output_file, "wb") as output:
                output.write(file_data.getvalue())

            print(f"Download complete! File saved as '{output_file}'.")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def _extract_file_id(self, url):
        """Extracts the file ID from a Google Drive URL."""
        return url.split("id=")[-1] if "id=" in url else url.split("/d/")[1].split("/")[0]

    def download_pdf(self, pdf_url, output_file='file.pdf'):
        """Downloads a PDF from Google Drive.
        
        Args:
            pdf_url: URL of the PDF file on Google Drive.
            output_file: Path to save the downloaded PDF file.
        """
        try:
            # Extract file ID from the Google Drive URL
            file_id = self._extract_file_id(pdf_url)

            # Request to download the PDF file
            request = self.service.files().get_media(fileId=file_id)

            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}% complete.")

            # Write the downloaded content to a PDF file
            with open(output_file, "wb") as output:
                output.write(file_data.getvalue())

            print(f"Download complete! File saved as '{output_file}'.")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
