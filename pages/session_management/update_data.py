import pandas as pd
import streamlit as st
from time import sleep
from controllers.update_session_Data import update_data
from controllers.home import get_session_data 

def update_page():
    st.title("Update Session Data")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"], key="update_selector")
    
    if selected_project is not None:
        # Get categories from current session data
        category_urls = {}
         
        session_information_data = get_session_data(selected_project)
        # Create input fields for each category
        for category in session_information_data["categories"].keys():
            st.subheader(category.upper())
            category_urls[category] = st.text_input(f"Link to {category.upper()} Sheet")

        with st.popover("Update"):
            st.error("Are you sure?")
            update_button = st.button("Confirm")
            if update_button:
                update_data(selected_project, category_urls)
                st.success("Successfully Updated Data")
                sleep(1.0)
                st.rerun()
