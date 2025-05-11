import json
from google_connector.google_sheet_download import GoogleDriveDownloader
import os

def clean_applicants_dataframe(dataframe):
     # Strip whitespace from all cells in latest_data
    dataframe = dataframe.map(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
    # Clean column names
    dataframe.columns = dataframe.columns.str.strip()
    dataframe = dataframe.rename(columns=json.load(open("database/schemas/renaming_convention.json")))
    return dataframe

def download_resumes(dataframe, session_name, category):
    downloader = GoogleDriveDownloader()
    for name, resume in dataframe[["name", "CV"]].values:
        file_path = f"./database/{session_name}/applicants_resume/{name.replace(' ', '_')}_resume_{category}.pdf"
        if not os.path.exists(file_path):
            downloader.download_pdf(resume, file_path)
            dataframe.loc[dataframe.name == name, "path_to_pdf"] = file_path