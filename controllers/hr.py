
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

def save_project(session_name, it_file, chess_file, sel_file):
    downloader = GoogleDriveDownloader()

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            downloader.download_google_sheet(it_file, f"{temp_dir}/it_file.csv")
            downloader.download_google_sheet(chess_file, f"{temp_dir}/chess_file.csv")
            downloader.download_google_sheet(sel_file, f"{temp_dir}/sel_file.csv")
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
        it = pd.read_csv(f"{temp_dir}/it_file.csv", dtype={'Phone Number': str})
        chess = pd.read_csv(f"{temp_dir}/chess_file.csv", dtype={'Phone Number': str})
        sel = pd.read_csv(f"{temp_dir}/sel_file.csv", dtype={'Phone Number': str})

        it = it.map(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
        chess = chess.map(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
        sel = sel.map(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
        
        # Strip whitespace from column names for all dataframes
        it.columns = it.columns.str.strip()
        chess.columns = chess.columns.str.strip()
        sel.columns = sel.columns.str.strip()

        it.rename(columns=json.load(open("database/schemas/renaming_convention.json")), inplace=True)
        sel.rename(columns=json.load(open("database/schemas/renaming_convention.json")), inplace=True)
        chess.rename(columns=json.load(open("database/schemas/renaming_convention.json")), inplace=True)
        
        def download_resumes_and_update_paths(df, session_name, category):
            for name, resume in df[["name", "CV"]].values:
                file_path = f"./database/{session_name}/applicants_resume/{name.replace(' ', '_')}_resume_{category}.pdf"
                downloader.download_pdf(resume, file_path)
                df.loc[df.name == name, "path_to_pdf"] = file_path

        download_resumes_and_update_paths(it, session_name, "it")
        download_resumes_and_update_paths(sel, session_name, "sel") 
        download_resumes_and_update_paths(chess, session_name, "chess")

        it["applicant_status"] = "Under_Review"
        chess["applicant_status"] = "Under_Review"
        sel["applicant_status"] = "Under_Review"

        upsert_volunteers_data(df=it, session_name=session_name, category="it")
        upsert_volunteers_data(df=chess, session_name=session_name, category="chess") 
        upsert_volunteers_data(df=sel, session_name=session_name, category="sel")

        it.to_csv(f"./database/{session_name}/applicants_form_data/it_applicant_data.csv", index=False)
        chess.to_csv(f"./database/{session_name}/applicants_form_data/chess_applicant_data.csv", index=False)
        sel.to_csv(f"./database/{session_name}/applicants_form_data/sel_applicant_data.csv", index=False)

        session_data_mongo = json.load(open("database/schemas/session_data_schema.json"))
        session_data_mongo["session_name"] = session_name
        
        sheet_urls = [it_file, chess_file, sel_file]
        categories = ["it", "chess", "sel"]
        for url, category in zip(sheet_urls, categories):
            session_data_mongo["categories"][category]["sheet_url"] = url
            session_data_mongo["categories"][category]["dataframe_path"] = f"./database/{session_name}/applicants_form_data/{category}_applicant_data.csv"

        asyncio.run(mongo_store.upsert_session_data(session_data_mongo))
        st.toast(f"{session_name} created successfully!")

    
    

   

    


    
    

   

    
    
   

   
