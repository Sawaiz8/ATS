import numpy as np
import pandas as pd
import streamlit as st
from streamlit_extras.row import row
from streamlit_pdf_reader import pdf_reader

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

def chess_applicants():
    # Read Chess data from CSV file
    csv_files = pd.DataFrame(st.session_state["current_session"])
    chess_data = st.session_state["chess_data"]
    chess_status = st.session_state["chess_status"]

    applicant_dropdown = st.selectbox(
        "Search Individual **CHESS** Applicants",
        chess_data["name"],
        index=None,
    )
    if applicant_dropdown is not None:
        current_applicant = chess_data[chess_data.name == applicant_dropdown]
        st.metric("Application Status", current_applicant["applicant_status"].values[0])
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
            col_b.metric("LinkedIn",  f"{current_applicant['linkedin_id'].values[0]}")
            st.markdown(f"***email***: {current_applicant['email'].values[0]}")
            st.markdown(f"***Has Discord?***: {current_applicant['has_discord'].values[0]}")

                # Get columns not in renamed_columns list
        extra_columns = [col for col in chess_data.columns if col not in renamed_columns + ['applicant_status', 'path_to_pdf']]
        
        # Create rows of 3 columns each
        for i in range(0, len(extra_columns), 3):
            row_cols = st.columns(3)
            
            # Create containers for each column in the row
            for j in range(3):
                if i+j < len(extra_columns):
                    col = extra_columns[i+j]
                    container = row_cols[j].container(border=True, height=150)
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

        if accept_button:
            chess_data.loc[chess_data['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Accepted'
            st.toast('Applicant Accepted', icon="❗")
            st.session_state["chess_data"] = chess_data
            chess_data.to_csv(f"./database/{csv_files[csv_files.category == 'CHESS'].sheet_link.values[0]}", index=False)
            chess_status.loc[chess_status['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Accepted'
            st.session_state["chess_status"] = chess_status
            chess_status.to_csv(f"./database/cache/chess_{st.session_state['current_session_name']}_applicant_status.csv", index=False)
            st.rerun()

        elif reject_button:
            chess_data.loc[chess_data['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Rejected'
            st.toast('Applicant Rejected', icon="❗")
            st.session_state["chess_data"] = chess_data
            chess_data.to_csv(f"./database/{csv_files[csv_files.category == 'CHESS'].sheet_link.values[0]}", index=False)
            chess_status.loc[chess_status['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Rejected'
            st.session_state["chess_status"] = chess_status
            chess_status.to_csv(f"./database/cache/chess_{st.session_state['current_session_name']}_applicant_status.csv", index=False)
            st.rerun()
        elif schedule_interview_button:
            chess_data.loc[chess_data['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Interview_Scheduled'
            st.session_state["chess_data"] = chess_data
            chess_data.to_csv(f"./database/{csv_files[csv_files.category == 'CHESS'].sheet_link.values[0]}", index=False)
            chess_status.loc[chess_status['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Interview_Scheduled'
            st.session_state["chess_status"] = chess_status
            chess_status.to_csv(f"./database/cache/chess_{st.session_state['current_session_name']}_applicant_status.csv", index=False)
            st.rerun()
        elif approve_interview_button:
            chess_data.loc[chess_data['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Interview_Approved'
            st.session_state["chess_data"] = chess_data
            chess_data.to_csv(f"./database/{csv_files[csv_files.category == 'CHESS'].sheet_link.values[0]}", index=False)
            chess_status.loc[chess_status['name'] == current_applicant.name.values[0], ["applicant_status"]] = 'Interview_Approved'
            st.session_state["chess_status"] = chess_status
            chess_status.to_csv(f"./database/cache/chess_{st.session_state['current_session_name']}_applicant_status.csv", index=False)
            st.rerun()
