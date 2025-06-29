
from google_connector.google_sheet_download import GoogleDriveDownloader
from os import makedirs
from main.database import mongo_store
import pandas as pd
import streamlit as st
import os
import asyncio
from utilities.mongo_db.streamlit_mongo_wrapper import upsert_volunteers_data, get_all_session_names
import json
import tempfile

def save_project(session_name, category_files):
    downloader = GoogleDriveDownloader()

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Download all files
            for category, file_url in category_files.items():
                downloader.download_google_sheet(file_url, f"{temp_dir}/{category}_file.csv")
        except:
            st.error("Error downloading files")
            return
        
        session_names = get_all_session_names()
        if session_name in session_names:
            st.error("Project with same name already exists!")
            return
        
        makedirs(f"./database/{session_name}", exist_ok=True)
        makedirs(f"./database/{session_name}/applicants_form_data", exist_ok=True)
        makedirs(f"./database/{session_name}/applicants_resume", exist_ok=True)

        dataframes = {}
        # Read all CSV files
        for category in category_files.keys():
            df = pd.read_csv(f"{temp_dir}/{category}_file.csv", dtype={'Phone Number': str})
            # Strip spaces from string values
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            # Rename columns according to convention
            df.rename(columns=json.load(open("database/schemas/renaming_convention.json")), inplace=True)
            dataframes[category] = df

        def download_resumes_and_update_paths(df, session_name, category):
            for name, resume in df[["name", "CV"]].values:
                file_path = f"./database/{session_name}/applicants_resume/{name.replace(' ', '_')}_resume_{category}.pdf"
                downloader.download_pdf(resume, file_path)
                df.loc[df.name == name, "path_to_pdf"] = file_path

        # Process each dataframe
        for category, df in dataframes.items():
            download_resumes_and_update_paths(df, session_name, category)
            df["applicant_status"] = "Under_Review"
            upsert_volunteers_data(df=df, session_name=session_name, category=category)
            df.to_csv(f"./database/{session_name}/applicants_form_data/{category}.csv", index=False)

        session_data_mongo = json.load(open("database/schemas/session_data_schema.json"))
        session_data_mongo["session_name"] = session_name
        
        # Update session data for each category
        for category, file_url in category_files.items():
            session_data_mongo["categories"][category] = {"sheet_url": file_url, "dataframe_path": f"./database/{session_name}/applicants_form_data/{category}.csv"}

        asyncio.run(mongo_store.upsert_session_data(session_data_mongo))
        st.toast(f"{session_name} created successfully!")
