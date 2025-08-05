import pandas as pd
import os
from google_connector.google_sheet_download import GoogleDriveDownloader
import json
import tempfile
from utilities.mongo_db.streamlit_mongo_wrapper import get_volunteer_data_as_csv, upsert_volunteers_data
import streamlit as st

def get_and_update_latest_data(session_selector, category_name, url, dataframe_path, temp_dir):
    downloader = GoogleDriveDownloader()

    downloader.download_google_sheet(url, f"{temp_dir}/{category_name}_file.csv")

    latest_data = pd.read_csv(f"{temp_dir}/{category_name}_file.csv", dtype={'Phone Number': str})
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

    # Compare and get differences using email as primary key
    email_col = 'email'  # or whatever your email column is named

    if current_data.empty:
        latest_data.to_csv(dataframe_path)
        new_records = latest_data
    else:
        new_records = latest_data[~latest_data[email_col].isin(current_data[email_col])]

    if len(new_records) > 0:
        # st.write("New records found")
        new_records["applicant_status"] = "Under Review"
        # st.write(new_records)
        
        # Update database
        upsert_volunteers_data(new_records, session_selector, category_name)
        
        # Combine current and new data
        updated_data = pd.concat([current_data, new_records], ignore_index=True)
        updated_data.to_csv(dataframe_path)        
        return updated_data
    else:
        current_data.to_csv(dataframe_path)
        return current_data

@st.cache_data(ttl=60*5)
def download_and_update_latest_data():
    session_catagory_data = st.session_state["current_session"]["categories"]
    session_selector = st.session_state["current_session"]["session_name"]

    os.makedirs(f"./database/{session_selector}", exist_ok=True)
    os.makedirs(f"./database/{session_selector}/applicants_form_data", exist_ok=True)
    os.makedirs(f"./database/{session_selector}/applicants_resume", exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        projects_data = {}
        for category in session_catagory_data:
            category_name = category
            projects_data[category_name] = get_and_update_latest_data(
                session_selector,
                category_name,
                session_catagory_data[category_name]["sheet_url"],
                session_catagory_data[category_name]["dataframe_path"],
                temp_dir
            )
        
    return projects_data


@st.cache_data(ttl=300)
def get_existing_data(session_name):
    """
    Loads the projects_data for a given session_name from existing CSV files.

    Args:
        session_name (str): The name of the session/project.

    Returns:
        dict: A dictionary where keys are category names and values are pandas DataFrames.
    """

    projects_data = {}
    session_path = f"./database/{session_name}/applicants_form_data"
    if not os.path.exists(session_path):
        return projects_data

    for file in os.listdir(session_path):
        if file.endswith(".csv"):
            category_name = file.replace(".csv", "")
            file_path = os.path.join(session_path, file)
            df = pd.read_csv(file_path)
            projects_data[category_name] = df
    return projects_data
