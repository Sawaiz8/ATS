import numpy as np
import pandas as pd
import streamlit as st
from streamlit_pdf_reader import pdf_reader

def chess_applicants():
    # Read Chess data from CSV file
    chess_data = st.session_state["chess_data"]
    chess_data["path_to_pdf"] = f"./database/{st.session_state["current_session"]}/applicants_resume/sample.pdf"


    applicant_dropdown = st.selectbox(
        "Search Individual **CHESS** Applicants",
        chess_data["name"],
        index=None,
    )
    if applicant_dropdown is not None:
        current_applicant = chess_data[chess_data.name == applicant_dropdown]
        col_1, col_2, col_3= st.columns(3)
        col_1.metric("Name", applicant_dropdown)
        col_1.metric("NGO Experience", current_applicant["ngo_work"].values[0])
        col_2.metric("Age", current_applicant["age"].values[0])
        col_3.metric("Gender", current_applicant["gender"].values[0])
        current_occupation = current_applicant["occupation"].values[0]
        match current_occupation:
            case "Both":
                col_2.metric("Occupation", "Student, Employed")
            case _:
                col_2.metric("Occupation", current_occupation)


        col_3.metric("City", current_applicant["city"].values[0])

        st.metric("Institution", current_applicant["institute"].values[0])
        st.metric("Transport", current_applicant["transport"].values[0])

        with st.expander("Contact Details"):
            col_a, col_b = st.columns(2)
            col_a.metric("Personal", f"0{current_applicant['phone_number'].values[0]}")
            col_a.metric("Instagram",  f"{current_applicant['insta_id'].values[0]}")
            col_b.metric("Emergency", f"0{current_applicant['emergency_contact'].values[0]}")
            col_b.metric("LinkedIn",  f"{current_applicant['linkedin_id'].values[0]}")
            st.markdown(f"***email***: {current_applicant['email'].values[0]}")
            st.markdown(f"***Has Discord?***: {current_applicant['has_discord'].values[0]}")

        pdf_source = current_applicant["path_to_pdf"].values[0]


        if pdf_source:
            pdf_reader(pdf_source)
