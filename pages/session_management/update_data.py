import pandas as pd
import streamlit as st
from time import sleep
from controllers.update_session_Data import update_data

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

        
