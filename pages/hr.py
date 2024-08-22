import streamlit as st
import pandas as pd
from os import mkdir
from shutil import rmtree
import glob

def save_project(project_name, it_file, chess_file, sel_file):
    mkdir(f"./database/{project_name}")
    mkdir(f"./database/{project_name}/applicants_form_data")
    mkdir(f"./database/{project_name}/applicants_resume")

    it = pd.read_csv(it_file)
    chess = pd.read_csv(chess_file)
    sel = pd.read_csv(sel_file)

    it.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv")
    chess.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv")
    sel.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv")
    sessions = pd.read_csv("./database/sessions.csv", index_col=0)

    st.write(sessions)
    sessions.loc[len(sessions.index)] = [project_name, "IT", project_name, f"{project_name}/applicants_form_data/it_applicant_data.csv"]
    sessions.loc[len(sessions.index)] = [project_name, "SEL", project_name, f"{project_name}/applicants_form_data/sel_applicant_data.csv"]
    sessions.loc[len(sessions.index)] = [project_name, "CHESS", project_name, f"{project_name}/applicants_form_data/chess_applicant_data.csv"]


    sessions.to_csv("./database/sessions.csv")
    st.toast(f"{project_name} created successfully!")


def hr_page():
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

    st.write("### Upload CSV Files")

    st.subheader("Chess")
    chess_files = st.file_uploader("Upload Chess CSV files", type="csv")

    st.subheader("IT")
    it_files = st.file_uploader("Upload IT CSV files", type="csv")

    st.subheader("SEL")
    sel_files = st.file_uploader("Upload SEL CSV files", type="csv")

    if st.button("Save Project"):
        if new_project_name:
            save_project(new_project_name, it_files, chess_files, sel_files)
        else:
            st.error("Please provide a project name.")


    st.header("Delete Project")
    delete_selector = st.selectbox("Choose a project", st.session_state["project_sessions"], key="delete")
    with st.popover("Delete"):
        st.error("Are you sure?")
        delete_button = st.button("Confirm")
    if delete_selector and delete_button:
        sessions = pd.read_csv("./database/sessions.csv", index_col=0)
        selected_session_directory = sessions[sessions.session_name == delete_selector].session_number.values[0]
        try:
            rmtree(f"./database/{selected_session_directory}")
            sessions = sessions[sessions.session_name != delete_selector]
            sessions.to_csv("./database/sessions.csv")
            st.success("Project Deleted Successfully!")
        except OSError as e:
            st.error("Error deleting project!")
            st.write(e)
