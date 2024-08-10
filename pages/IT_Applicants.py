import numpy as np
import pandas as pd
import streamlit as st

def it_applicants():
    from streamlit_pdf_reader import pdf_reader
    # Read IT data from CSV file
    csv_files = pd.DataFrame(st.session_state["current_session"])
    it_data = st.session_state["it_data"]
    it_data["path_to_pdf"] = f"./database/{st.session_state["current_session"]}/applicants_resume/sample.pdf"

    applicant_dropdown = st.selectbox(
    "Search Individual **IT** Applicants",
    it_data["name"],
    index=None,
    )
    if applicant_dropdown is not None:
        current_applicant = it_data[it_data.name == applicant_dropdown]
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

        col_4, col_5, col_6 = st.columns(3)
        container_1 = col_4.container(border=True, height=150)
        container_2 = col_5.container(border=True, height=150)
        container_3 = col_6.container(border=True, height=150)
        container_1.caption("Computer Skills")
        container_1.markdown(current_applicant["cs_skills"].values[0])
        container_2.caption("Experience using Canva, Adobe...")
        container_2.markdown(current_applicant["adobe_canva"].values[0])
        container_3.caption("Any other computer skills benefitting kids aged 10-16?")
        container_3.markdown(current_applicant["other_skills"].values[0])
        pdf_source=current_applicant["path_to_pdf"].values[0]
        if pdf_source:
            pdf_reader("./database/session_1/applicants_resume/sample.pdf")
