from google_connector.google_sheet_download import GoogleDriveDownloader
import streamlit as st
import pandas as pd
from os import makedirs
from shutil import rmtree
from time import sleep
import glob
import os
def save_project(project_name, it_file, chess_file, sel_file):
    downloader = GoogleDriveDownloader()
    try:
        it_sheet = downloader.download_google_sheet(it_file, "temp_files/it_file.csv")
        chess_sheet = downloader.download_google_sheet(chess_file, "temp_files/chess_file.csv")
        sel_sheet = downloader.download_google_sheet(sel_file, "temp_files/sel_file.csv")


    except:
        st.error("Error downloading files")
        return
    sessions = pd.read_csv("./database/sessions.csv")
    if project_name in sessions["session_name"]:
        st.error("Project with same name already exists!")
        return
    makedirs(f"./database/{project_name}", exist_ok=True)
    makedirs(f"./database/{project_name}/applicants_form_data", exist_ok=True)
    makedirs(f"./database/{project_name}/applicants_resume", exist_ok=True)

    it = pd.read_csv("temp_files/it_file.csv")
    chess = pd.read_csv("temp_files/chess_file.csv")
    sel = pd.read_csv("temp_files/sel_file.csv")
    it.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
    chess = chess.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
    sel = sel.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces from string values
    
    it.rename(columns={
        'Timestamp': 'timestamp',
        'Email Address': 'email',
        'Name': 'name',
        'Age': 'age',
        'Gender': 'gender',
        'Phone Number': 'phone_number',
        'Transport': 'transport',
        'Have you worked for any NGO before?': 'ngo_work',
        'City': 'city',
        'In which area do you currently reside in your city?': 'city_address',
        'Your Current Occupation': 'occupation',
        'Institute where you currently study or studied': 'institute',
        'CV': 'CV',
        'Your Instagram Account:': 'insta_id',
        'Your LinkedIn Profile:': 'linkedin_id',
        'Do you have a Discord ID?': 'has_discord'
    }, inplace=True)

    sel.rename(columns={
        'Timestamp': 'timestamp',
        'Email Address': 'email',
        'Name': 'name',
        'Age': 'age',
        'Gender': 'gender',
        'Phone Number': 'phone_number',
        'Transport': 'transport',
        'Have you worked for any NGO before?': 'ngo_work',
        'City': 'city',
        'In which area do you currently reside in your city?': 'city_address',
        'Your Current Occupation': 'occupation',
        'Institute where you currently study or studied': 'institute',
        'CV': 'CV',
        'Your Instagram Account:': 'insta_id',
        'Your LinkedIn Profile:': 'linkedin_id',
        'Do you have a Discord ID?': 'has_discord'
    }, inplace=True)

    chess.rename(columns={
        'Timestamp': 'timestamp',
        'Email Address': 'email',
        'Name': 'name',
        'Age': 'age',
        'Gender': 'gender',
        'Phone Number': 'phone_number',
        'Transport': 'transport',
        'Have you worked for any NGO before?': 'ngo_work',
        'City': 'city',
        'In which area do you currently reside in your city?': 'city_address',
        'Your Current Occupation': 'occupation',
        'Institute where you currently study or studied': 'institute',
        'CV': 'CV',
        'Your Instagram Account:': 'insta_id',
        'Your LinkedIn Profile:': 'linkedin_id',
        'Do you have a Discord ID?': 'has_discord'
    }, inplace=True)

    for name, resume in it[["name", "CV"]].values:
        downloader.download_pdf(resume, f"./database/{project_name}/applicants_resume/{name.replace(' ', '_')}_resume_it.pdf")
        it.loc[it.name == name, "path_to_pdf"] = f"/database/{project_name}/applicants_resume/{name}_resume_it.pdf"
    for name, resume in sel[["name", "CV"]].values:
        downloader.download_pdf(resume, f"./database/{project_name}/applicants_resume/{name.replace(' ', '_')}_resume_sel.pdf")
        sel.loc[sel.name == name, "path_to_pdf"] = f"/database/{project_name}/applicants_resume/{name.replace(' ', '_')}_resume_sel.pdf"

    for name, resume in chess[["name", "CV"]].values:
        downloader.download_pdf(resume, f"./database/{project_name}/applicants_resume/{name.replace(' ', '_')}_resume_chess.pdf")
        chess.loc[chess.name == name, "path_to_pdf"] = f"/database/{project_name}/applicants_resume/{name.replace(' ', '_')}_resume_chess.pdf"

    it.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv", index=False)
    chess.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv", index=False)
    sel.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv", index=False)

    sessions.loc[len(sessions.index)] = [project_name, "IT", project_name, f"{project_name}/applicants_form_data/it_applicant_data.csv", it_file]
    sessions.loc[len(sessions.index)] = [project_name, "SEL", project_name, f"{project_name}/applicants_form_data/sel_applicant_data.csv", sel_file]
    sessions.loc[len(sessions.index)] = [project_name, "CHESS", project_name, f"{project_name}/applicants_form_data/chess_applicant_data.csv", chess_file]

    # Create a folder called cache if it doesn't exist in the database folder
    os.makedirs("./database/cache", exist_ok=True)

    it_status = it[["name", "age", "phone_number"]].copy()
    it_status["applicant_status"] = "Under Review"
    it_status.to_csv(f"./database/cache/it_{project_name}_applicant_status.csv", index=False)

    sel_status = sel[["name", "age", "phone_number"]].copy()
    sel_status["applicant_status"] = "Under Review"
    sel_status.to_csv(f"./database/cache/sel_{project_name}_applicant_status.csv", index=False)

    chess_status = chess[["name", "age", "phone_number"]].copy()
    chess_status["applicant_status"] = "Under Review"
    chess_status.to_csv(f"./database/cache/chess_{project_name}_applicant_status.csv", index=False)

    sessions.to_csv("./database/sessions.csv", index=False)
    os.remove("temp_files/it_file.csv")
    os.remove("temp_files/sel_file.csv")
    os.remove("temp_files/chess_file.csv")
    st.toast(f"{project_name} created successfully!")


def hr_page():

    default_prompt = """
    Dear [Applicant's Name],

    Congratulations! We are pleased to inform you that you have been selected for a volunteer position with Daadras Foundation. Your enthusiasm and commitment to making a difference have truly impressed us, and we are excited to welcome you to our team.

    To finalize your position and discuss the next steps, please contact us at your earliest convenience. We look forward to connecting with you and providing further details about your role and responsibilities.

    Once again, congratulations, and thank you for your willingness to contribute to our mission. We are confident that your involvement will make a meaningful impact.

    Best regards,"""


    st.title("Project Management")

    # Select existing project
    st.header("Select a Project")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"])

    if selected_project:
        st.write(f"### {selected_project}")
        current_sessions = st.session_state["sessions"]
        search = f"./database/{current_sessions[current_sessions.session_name == selected_project].session_number.values[0]}/applicants_form_data/*"
        st.write("This project has the following files:")
        for file in glob.glob(search):
            st.write(f"- {file}")
    # Create new project
    st.header("Create a New Project")
    new_project_name = st.text_input("Project Name")

    st.write("### Link CSV Files")

    st.subheader("Chess")
    chess_files = st.text_input("Link to CHESS Sheet")

    st.subheader("IT")
    it_files = st.text_input("Link to IT Sheet")

    st.subheader("SEL")
    sel_files = st.text_input("Link to SEL Sheet")
    if st.button("Save Project"):
        if new_project_name:
            save_project(new_project_name, it_files, chess_files, sel_files)
            st.success("Project created successfully")
            sleep(1.0)
            st.rerun()
        else:
            st.error("Please provide a project name.")


    st.header("Delete Project")
    delete_selector = st.selectbox("Choose a project", st.session_state["project_sessions"], key="delete")
    with st.popover("Delete"):
        st.error("Are you sure?")
        delete_button = st.button("Confirm")
    if delete_selector and delete_button:
        sessions = pd.read_csv("./database/sessions.csv")
        selected_session_directory = sessions[sessions.session_name == delete_selector].session_number.values[0]
        try:
            rmtree(f"./database/{selected_session_directory}")
            sessions = sessions[sessions.session_name != delete_selector]
            # Remove IT cache files
            it_cache_files = glob.glob(f"./database/cache/it_{delete_selector}_*")
            for file in it_cache_files:
                os.remove(file)

            # Remove Chess cache files
            chess_cache_files = glob.glob(f"./database/cache/chess_{delete_selector}_*")
            for file in chess_cache_files:
                os.remove(file)

            # Remove SEL cache files
            sel_cache_files = glob.glob(f"./database/cache/sel_{delete_selector}_*")
            for file in sel_cache_files:
                os.remove(file)
                
            sessions.to_csv("./database/sessions.csv", index=False)
            st.success("Project Deleted Successfully!")
            sleep(1.0)
            st.rerun()
        except OSError as e:
            st.error("Error deleting project!")
            st.write(e)
