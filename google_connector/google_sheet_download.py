import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

class GoogleDriveDownloader:
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    def __init__(self, creds_file='token.json', client_secret_file='credentials.json'):
        """Initializes the downloader with paths to credentials and client secret files."""
        self.creds_file = creds_file
        self.client_secret_file = client_secret_file
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates the user and saves/loads credentials."""
        # Load saved credentials from file if available
        if os.path.exists(self.creds_file):
            self.creds = Credentials.from_authorized_user_file(self.creds_file, self.SCOPES)
        
        # If there are no valid credentials, prompt the user to log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save credentials for future use
            with open(self.creds_file, "w") as token:
                token.write(self.creds.to_json())

        # Initialize the Drive API client
        self.service = build("drive", "v3", credentials=self.creds)

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

# # Example usage:
# if __name__ == "__main__":
#     downloader = GoogleDriveDownloader()

#     # Download a Google Sheet as a CSV file
#     sheet_url = "https://docs.google.com/spreadsheets/d/1hRe35C02f6AzvcsNb8PkBjgAAh1krZU1-YlSuDNG8Ow/edit?resourcekey=&gid=983807525#gid=983807525"
#     downloader.download_google_sheet(sheet_url)

#     # # Download a PDF file from Google Drive
#     pdf_url = "https://drive.google.com/open?id=1e0X3QpqD7ZMy_bdkYiW4r9QAhMe_eG4D"
#     downloader.download_pdf(pdf_url)
