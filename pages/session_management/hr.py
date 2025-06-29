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
    new_session_name = st.text_input("Project Name")

    st.write("### Add Categories")
    
    # Dynamic category inputs
    categories_dict = {}
    
    # Container for dynamic category inputs
    categories_container = st.container()
    
    # Add category button
    if st.button("Add Category"):
        if "num_categories" not in st.session_state:
            st.session_state.num_categories = 1
        else:
            st.session_state.num_categories += 1
            
    # Remove category button    
    if st.button("Remove Category") and st.session_state.get("num_categories", 0) > 0:
        st.session_state.num_categories -= 1
            
    # Display dynamic category inputs
    with categories_container:
        for i in range(st.session_state.get("num_categories", 1)):
            col1, col2 = st.columns(2)
            with col1:
                category_name = st.text_input(f"Category Name {i+1} (e.g. Chess, IT, SEL)", key=f"cat_name_{i}")
            with col2:
                sheet_link = st.text_input(f"Sheet Link {i+1}", key=f"sheet_link_{i}")
                
            if category_name and sheet_link:
                # Convert name to lowercase and replace spaces with underscore
                formatted_name = category_name.lower().replace(" ", "_")
                categories_dict[formatted_name] = sheet_link

    if st.button("Save Project"):
        if new_session_name and categories_dict:
            # Show loading spinner
            with st.spinner("Saving project..."):
                save_project(new_session_name, categories_dict)
            st.success("Project created successfully")
            sleep(1.0)
            st.cache_data.clear()
            st.rerun()
        else:   
            st.error("Please provide a project name and at least one category.")

    st.header("Delete Project")
    delete_selector = st.selectbox("Choose a project", st.session_state["project_sessions"], key="delete")
    with st.popover("Delete"):
        st.error("Are you sure?")
        delete_button = st.button("Confirm")
    if delete_selector and delete_button:
        try:
            asyncio.run(mongo_store.delete_session_data(delete_selector))
            path = f"./database/{delete_selector}"
            if os.path.exists(path):
                rmtree(path)
            st.success("Project Deleted Successfully!")
            sleep(1.0)
            st.cache_data.clear()
            st.rerun()
        except OSError as e:
            st.error("Error deleting project!")
            st.write(e)
