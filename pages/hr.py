import streamlit as st
import pandas as pd
from os import mkdir
from shutil import copy
import glob

def save_project(project_name, it_file, chess_file, sel_file):
    mkdir(f"./database/{project_name}")

    it = pd.read_csv(it_file)
    chess = pd.read_csv(chess_file)
    sel = pd.read_csv(sel_file)

    it.to_csv(f"./database/{project_name}/it_applicant_data.csv")
    chess.to_csv(f"./database/{project_name}/chess_applicant_data.csv")
    sel.to_csv(f"./database/{project_name}/sel_applicant_data.csv")
    sessions = pd.read_csv("./database/sessions.csv")

    new_entries = {
        "session_name": [project_name, project_name, project_name],
        "category": ["IT", "SEL", "CHESS"],
        "sheet_link": ["./database/{project_name}/it_applicant_data.csv",
            "./database/{project_name}/sel_applicant_data.csv",
            "./database/{project_name}/chess_applicant_data.csv"],
    }
    sessions.append(new_entries)

    sessions.to_csv("./database/sessions.csv")


def hr_page():
    st.title("Project Management")

    # Select existing project
    st.header("Select a Project")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"])

    if selected_project:
        st.write(f"### {selected_project}")
        search = f"./database/{st.session_state["sessions"][st.session_state["sessions"].session_name == selected_project].sheet_link.values[0]}/applicants_form_data/*"
        st.write("This project has the following files:")
        for file in glob.glob(search):
            st.write(f"- {file}")

    # Create new project
    st.header("Create a New Project")
    new_project_name = st.text_input("Project Name")

    st.write("### Upload CSV Files")

    st.subheader("Chess")
    chess_files = st.file_uploader("Upload Chess CSV files", type="csv", accept_multiple_files=True, key="chess")

    st.subheader("IT")
    it_files = st.file_uploader("Upload IT CSV files", type="csv", accept_multiple_files=True, key="it")

    st.subheader("SEL")
    sel_files = st.file_uploader("Upload SEL CSV files", type="csv", accept_multiple_files=True, key="sel")

    st.write(chess_files)
    it_files
    sel_files

    if st.button("Save Project"):
        if new_project_name:
            save_project(new_project_name, it_files, chess_files, sel_files)
        else:
            st.error("Please provide a project name.")
