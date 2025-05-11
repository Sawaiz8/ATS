import pandas as pd
import os
from google_connector.google_sheet_download import GoogleDriveDownloader
import json
import tempfile
from utilities.mongo_db.streamlit_mongo_wrapper import get_volunteer_data_as_csv, upsert_volunteers_data
import streamlit as st

def get_and_update_latest_data(session_selector, category_name, url, dataframe_path, temp_dir):
    downloader = GoogleDriveDownloader()

    downloader.download_google_sheet(url, f"{temp_dir}/it_file.csv")

    latest_data = pd.read_csv(f"{temp_dir}/it_file.csv", dtype={'Phone Number': str})
    current_data = get_volunteer_data_as_csv(session_selector, category_name)

    # Strip whitespace from all cells in latest_data
    latest_data = latest_data.map(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
    current_data = current_data.map(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
    
    # Clean column names
    latest_data.columns = latest_data.columns.str.strip()
    latest_data = latest_data.rename(columns=json.load(open("database/schemas/renaming_convention.json")))
    
    # Download resumes
    for name, resume in latest_data[["name", "CV"]].values:
        file_path = f"./database/{session_selector}/applicants_resume/{name.replace(' ', '_')}_resume_{category_name.lower()}.pdf"
        if not os.path.exists(file_path):
            downloader.download_pdf(resume, file_path)
        latest_data.loc[latest_data.name == name, "path_to_pdf"] = file_path

    # Compare and get differences
    # Use latest data columns since it won't have applicant_status column, session_name column and
    cols = [col for col in latest_data.columns]
    diff = pd.concat([current_data[cols], latest_data[cols]]).drop_duplicates(keep=False)
    if len(diff) > 0:
        st.write("Diff found")
        diff["applicant_status"] = "Under Review"
        st.write(diff)
        # Update database
        upsert_volunteers_data(diff, session_selector, category_name)
        
        # Combine current and new data
        updated_data = pd.concat([current_data, diff], ignore_index=True)
        st.write(updated_data)
        updated_data.to_csv(dataframe_path)
        
        return updated_data
    else:
        return current_data

def download_and_update_latest_data():
    session_catagory_data = st.session_state["current_session"]["categories"]
    session_selector = st.session_state["current_session"]["session_name"]

    with tempfile.TemporaryDirectory() as temp_dir:
        results = {}
        for category in session_catagory_data:
            category_name = category
            results[category_name] = get_and_update_latest_data(
                session_selector,
                category_name,
                session_catagory_data[category_name]["sheet_url"],
                session_catagory_data[category_name]["dataframe_path"],
                temp_dir
            )
        
    return results["it"], results["sel"], results["chess"]