import streamlit as st
import pandas as pd
from shutil import rmtree
from time import sleep
import glob
import os
from controllers.hr import save_project
from main.database import mongo_store
import asyncio

def hr_page():

    st.title("Session Management")

    # Select existing project
    st.header("Select a Project")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"])

    if selected_project:
        st.write(f"### {selected_project}")
        search = f"./database/{selected_project}/applicants_form_data/*"
        st.write("This project has the following files:")
        for file in glob.glob(search):
            st.write(f"- {file}")
    
    # Create new project
    st.header("Create a New Project")
    new_project_name = st.text_input("Project Name")

    st.write("### Link CSV Files")

    st.subheader("Chess")
    chess_file = st.text_input("Link to CHESS Sheet")

    st.subheader("IT")
    it_file = st.text_input("Link to IT Sheet")

    st.subheader("SEL")
    sel_file = st.text_input("Link to SEL Sheet")
    if st.button("Save Project"):
        if new_project_name:
            save_project(new_project_name, it_file, chess_file, sel_file)
            st.success("Project created successfully")
            sleep(1.0)
            st.cache_data.clear()
            st.rerun()
        else:   
            st.error("Please provide a project name.")


    st.header("Delete Project")
    delete_selector = st.selectbox("Choose a project", st.session_state["project_sessions"], key="delete")
    with st.popover("Delete"):
        st.error("Are you sure?")
        delete_button = st.button("Confirm")
    if delete_selector and delete_button:
        try:
            asyncio.run(mongo_store.delete_session_data(delete_selector))
            rmtree(f"./database/{delete_selector}")
            st.success("Project Deleted Successfully!")
            sleep(1.0)
            st.cache_data.clear()
            st.rerun()
        except OSError as e:
            st.error("Error deleting project!")
            st.write(e)
