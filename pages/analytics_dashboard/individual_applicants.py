import numpy as np
import pandas as pd
import streamlit as st
from streamlit_extras.row import row
from streamlit_pdf_reader import pdf_reader
from main.database import mongo_store
import asyncio
renamed_columns = [
    'timestamp',           # from 'Timestamp'
    'email',              # from 'Email Address'
    'name',               # from 'Name'
    'age',                # from 'Age'
    'gender',             # from 'Gender'
    'phone_number',       # from 'Phone Number'
    'transport',          # from 'Transport'
    'ngo_work',           # from 'Have you worked for any NGO before?'
    'city',               # from 'City'
    'city_address',       # from 'In which area do you currently reside in your city?'
    'occupation',         # from 'Your Current Occupation'
    'institute',          # from 'Institute where you currently study or studied'
    'cv',                 # from 'CV'
    'insta_id',          # from 'Your Instagram Account:'
    'linkedin_id',        # from 'Your LinkedIn Profile:'
    'has_discord'         # from 'Do you have a Discord ID?'
]

def applicants_page(category):
    current_session_data = st.session_state["current_session"]
    df_applicant = st.session_state["projects_data"][category]
    applicant_dropdown = st.selectbox(
        f"Search Individual **{category.upper()}** Applicants",
        df_applicant["name"],
        index=None,
    )
    
    if applicant_dropdown is not None:
        current_applicant = df_applicant[df_applicant.name == applicant_dropdown]
        st.metric("Application Status", current_applicant["applicant_status"].values[0])

        st.markdown("---")  # Separator line before contact details
        st.subheader("Personal Details")  # Heading for contact details
        col_1, col_2, col_3= st.columns(3)
        col_1.metric("Age", current_applicant["age"].values[0])
        col_2.metric("Gender", current_applicant["gender"].values[0])
        col_3.metric("NGO Experience", current_applicant["ngo_work"].values[0])
        col_1.metric("Transport", current_applicant["transport"].values[0])
        current_occupation = current_applicant["occupation"].values[0]
        match current_occupation:
            case "Both":
                col_2.metric("Occupation", "Student, Employed")
            case _:
                col_2.metric("Occupation", current_occupation)
        col_3.metric("City", current_applicant["city"].values[0])
        st.metric("Institution", current_applicant["institute"].values[0])
        
        st.markdown("---")  # Separator line before contact details
        st.subheader("Contact Details")  # Heading for contact details
        col_a, col_b = st.columns(2)
        col_a.metric("Personal", f"0{current_applicant['phone_number'].values[0]}")
        col_a.metric("Instagram",  f"{current_applicant['insta_id'].values[0]}")
        col_b.metric("LinkedIn",  f"{current_applicant['linkedin_id'].values[0]}")
        st.markdown(f"***email***: {current_applicant['email'].values[0]}")
        st.markdown(f"***Has Discord?***: {current_applicant['has_discord'].values[0]}")

        st.markdown("---")  # Separator line before contact details
        st.subheader("Question and Answers")  # Heading for contact details
        # Get columns not in renamed_columns list
        extra_columns = [col for col in df_applicant.columns if col not in renamed_columns + ['applicant_status', 'path_to_pdf']]
        
        # Show each extra column sequentially in its own row
        for col in extra_columns:
            if col != "CV":
                container = st.container(border=True)
                container.caption(col)
                container.markdown(current_applicant[col].values[0])

        pdf_source = current_applicant["path_to_pdf"].values[0]

        if pdf_source:
            try:
                # Handle file paths with spaces
                pdf_reader(pdf_source)
            except ValueError as e:
                st.error(f"Could not load PDF: {pdf_source}")
        action_row = row([0.27, 0.4, 0.15, 0.2], vertical_align="center", gap="small")
        approve_interview_button = action_row.button(label="Approve Interview")
        schedule_interview_button = action_row.button(label="Interview Scheduled (For HR only)")
        reject_button = action_row.button(label="Reject")
        accept_button = action_row.button(label="Accept")

        name = str(current_applicant.name.values[0])
        email = str(current_applicant.email.values[0])
        if accept_button:
            df_applicant.loc[df_applicant['name'] == name, ["applicant_status"]] = 'Accepted'
            st.toast('Applicant Accepted', icon="❗")
            st.session_state[f"{category}_data"] = df_applicant
            df_applicant.to_csv(current_session_data["categories"][category]['dataframe_path'], index=False)
            asyncio.run(mongo_store.update_volunteer_status(name, email, 'Accepted'))
            st.write(df_applicant)
            st.rerun()
        elif reject_button:
            df_applicant.loc[df_applicant['name'] == name, ["applicant_status"]] = 'Rejected'
            st.toast('Applicant Rejected', icon="❗")
            st.session_state[f"{category}_data"] = df_applicant
            df_applicant.to_csv(current_session_data["categories"][category]['dataframe_path'], index=False)
            asyncio.run(mongo_store.update_volunteer_status(name, email, 'Rejected'))
            st.write(df_applicant)
            st.rerun()
        elif schedule_interview_button:
            df_applicant.loc[df_applicant['name'] == name, ["applicant_status"]] = 'Interview_Scheduled'
            st.session_state[f"{category}_data"] = df_applicant
            df_applicant.to_csv(current_session_data["categories"][category]['dataframe_path'], index=False)
            asyncio.run(mongo_store.update_volunteer_status(name, email, 'Interview_Scheduled'))
            st.write(df_applicant)
            st.rerun()
        elif approve_interview_button:
            df_applicant.loc[df_applicant['name'] == name, ["applicant_status"]] = 'Interview_Approved'
            st.session_state[f"{category}_data"] = df_applicant
            df_applicant.to_csv(current_session_data["categories"][category]['dataframe_path'], index=False)
            asyncio.run(mongo_store.update_volunteer_status(name, email, 'Interview_Approved'))
            st.write(df_applicant)
            st.rerun()
