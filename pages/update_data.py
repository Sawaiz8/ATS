import pandas as pd
import streamlit as st
from google_connector.google_sheet_download import GoogleDriveDownloader
from time import sleep


def update_data(project_name=None, chess=None, it=None, sel=None, chess_email=None, it_email=None, sel_email=None, chess_subject=None, it_subject=None, sel_subject=None):
    downloader = GoogleDriveDownloader()
    sessions = pd.read_csv("./database/sessions.csv")
    if it is not None:
        downloaded_file = downloader.download_google_sheet(it, "temp_file.csv")
        conditional = (sessions.session_name == project_name) & (sessions.category == "IT")
        sessions.loc[conditional, "sheet_url"] = it
        it_df = pd.read_csv("temp_file.csv")
        it_df.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv", index=False)
        st.success("Updated IT file")
    if chess is not None:
        downloaded_file = downloader.download_google_sheet(chess, "temp_file.csv")
        conditional = (sessions.session_name == project_name) & (sessions.category == "CHESS")
        sessions.loc[conditional, "sheet_url"] = chess
        chess_df = pd.read_csv("temp_file.csv")
        chess_df.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv",index=False)
        st.success("Updated CHESS file")
    if sel is not None:
        downloaded_file = downloader.download_google_sheet(sel, "temp_file.csv")
        conditional = (sessions.session_name == project_name) & (sessions.category == "SEL")
        sessions.loc[conditional, "sheet_url"] = sel
        sel_df = pd.read_csv("temp_file.csv")
        sel_df.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv", index=False)
        st.write("Updated SEL file")



    email_prompts = pd.read_csv("./database/email_prompts.csv")
    update_condition = email_prompts.session_name == project_name
    email_prompts.loc[update_condition, ["it_prompt"]] = it_email
    email_prompts.loc[update_condition, ["sel_prompt"]] = chess_email
    email_prompts.loc[update_condition, ["chess_prompt"]] = sel_email

    email_prompts.loc[update_condition, ["it_header"]] = it_subject
    email_prompts.loc[update_condition, ["sel_header"]] = sel_subject
    email_prompts.loc[update_condition, ["chess_header"]] = chess_subject

    sessions.to_csv("./database/sessions.csv", index=False)
    email_prompts.to_csv("./database/email_prompts.csv",index=False)

def update_page():
    email_prompts = pd.read_csv("./database/email_prompts.csv")

    st.title("Update Session Data")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"], key="update_selector")
    if selected_project is not None:
        st.subheader("Chess")
        chess_files = st.text_input("Link to CHESS Sheet")
        st.subheader("IT")
        it_files = st.text_input("Link to IT Sheet")
        st.subheader("SEL")
        sel_files = st.text_input("Link to SEL Sheet")

        it_email_container  = st.expander("IT Email Prompt")
        it_email_subject = it_email_container.text_input(label="Subject", value=email_prompts[email_prompts.session_name == selected_project]["it_header"].values[0], key="it_email_subject")
        it_email_prompt = it_email_container.text_area(label="Enter prompt:",value=email_prompts[email_prompts.session_name == selected_project]["it_prompt"].values[0], key="it_email_prompt")

        sel_email_container = st.expander("SEL Email Prompt")
        sel_email_subject = sel_email_container.text_input(label="Subject", value=email_prompts[email_prompts.session_name == selected_project]["sel_header"].values[0], key="sel_email_subject")
        sel_email_prompt = sel_email_container.text_area(label="Prompt",value=email_prompts[email_prompts.session_name == selected_project]["sel_prompt"].values[0], placeholder="SEL email prompt", key="sel_email_prompt")

        chess_email_container = st.expander("Chess Email Prompt")
        chess_email_subject = chess_email_container.text_input(label="Subject", value=email_prompts[email_prompts.session_name == selected_project]["chess_header"].values[0], key="chess_email_subject")
        chess_email_prompt = chess_email_container.text_area(label="Prompt",value=email_prompts[email_prompts.session_name == selected_project]["chess_prompt"].values[0] ,placeholder="CHESS email prompt", key="chess_email_prompt")

        with st.popover("Update"):
            st.error("Are you sure?")
            update_button = st.button("Confirm")
            if update_button:
                update_data(selected_project, chess_files, it_files, sel_files, chess_email_prompt, it_email_prompt, sel_email_prompt, chess_email_subject, it_email_subject, sel_email_subject)
                st.success("Successfully Updated Data")
                sleep(1.0)
                st.rerun()
