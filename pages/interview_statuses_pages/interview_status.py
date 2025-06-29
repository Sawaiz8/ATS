import streamlit as st

def view_interview_status(status: str):
    # Get all categories from projects_data
    categories = list(st.session_state["projects_data"].keys())
    
    # Create tabs dynamically based on categories
    tabs = st.tabs([cat.upper() for cat in categories])
    
    # Create each tab with its data
    for tab, category in zip(tabs, categories):
        with tab:
            df = st.session_state["projects_data"][category]
            st.write(f"{status} {category.upper()} Applications: ")
            st.dataframe(df[df["applicant_status"] == status][["name", "email", "gender", "phone_number"]])
