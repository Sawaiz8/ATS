import os
from main.database import mongo_store
import asyncio
import json
import tempfile
from utilities.utils import clean_applicants_dataframe, download_resumes
from google_connector.google_sheet_download import GoogleDriveDownloader
import streamlit as st
import pandas as pd


def update_data(session_name, chess_sheet_url, it_sheet_url, sel_sheet_url):
    downloader = GoogleDriveDownloader()
    os.makedirs(f"./database/{session_name}", exist_ok=True)
    os.makedirs(f"./database/{session_name}/applicants_form_data", exist_ok=True)
    os.makedirs(f"./database/{session_name}/applicants_resume", exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Define the categories and their URLs
        categories = {
            "it": it_sheet_url,
            "chess": chess_sheet_url, 
            "sel": sel_sheet_url
        }

        # Process each category
        for category, sheet_url in categories.items():
            if len(sheet_url) != 0:
                downloaded_file = downloader.download_google_sheet(sheet_url, f"{temp_dir}/{category}_file.csv")
                if downloaded_file:
                    # Update MongoDB
                    asyncio.run(mongo_store.update_sheet_url(session_name, category, sheet_url))
                    asyncio.run(mongo_store.delete_volunteers_by_category(session_name=session_name, category=category))

                    # Remove category specific resumes
                    resume_dir = f"./database/{session_name}/applicants_resume"
                    for file in os.listdir(resume_dir):
                        if file.split(".")[0].endswith(f"_{category}"):
                            os.remove(os.path.join(resume_dir, file))

                    # Process and save new data
                    latest_data = pd.read_csv(f"{temp_dir}/{category}_file.csv", dtype={'Phone Number': str})
                    latest_data = clean_applicants_dataframe(latest_data)
                    latest_data["applicant_status"] = "Under Review"
                    latest_data.to_csv(f"./database/{session_name}/applicants_form_data/{category}_applicant_data.csv", index=False)
                    download_resumes(latest_data, session_name, category)
                    st.success(f"Updated {category.upper()} file")