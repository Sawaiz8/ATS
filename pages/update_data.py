import pandas as pd
import streamlit as st
from google_connector.google_sheet_download import GoogleDriveDownloader
from time import sleep


def update_data(project_name, chess, it, sel):
    downloader = GoogleDriveDownloader()
    sessions = pd.read_csv("./database/sessions.csv")
    if len(it) != 0:
        downloaded_file = downloader.download_google_sheet(it, "temp_file.csv")
        conditional = (sessions.session_name == project_name) & (sessions.category == "IT")
        sessions.loc[conditional, "sheet_url"] = it
        it_df = pd.read_csv("temp_file.csv")
        it_df.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv", index=False)
        st.success("Updated IT file")
    if len(chess) != 0:
        downloaded_file = downloader.download_google_sheet(chess, "temp_file.csv")
        conditional = (sessions.session_name == project_name) & (sessions.category == "CHESS")
        sessions.loc[conditional, "sheet_url"] = chess
        chess_df = pd.read_csv("temp_file.csv")
        chess_df.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv",index=False)
        st.success("Updated CHESS file")
    if len(sel) != 0:
        downloaded_file = downloader.download_google_sheet(sel, "temp_file.csv")
        conditional = (sessions.session_name == project_name) & (sessions.category == "SEL")
        sessions.loc[conditional, "sheet_url"] = sel
        sel_df = pd.read_csv("temp_file.csv")
        sel_df.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv", index=False)
        st.success("Updated SEL file")


    sessions.to_csv("./database/sessions.csv", index=False)

def update_page():
    st.title("Update Session Data")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"], key="update_selector")
    if selected_project is not None:
        st.subheader("Chess")
        chess_link = st.text_input("Link to CHESS Sheet")
        st.subheader("IT")
        it_link = st.text_input("Link to IT Sheet")
        st.subheader("SEL")
        sel_link = st.text_input("Link to SEL Sheet")
        with st.popover("Update"):
            st.error("Are you sure?")
            update_button = st.button("Confirm")
            if update_button:
                update_data(selected_project, chess_link, it_link, sel_link)
                st.success("Successfully Updated Data")
                sleep(1.0)
                st.rerun()
