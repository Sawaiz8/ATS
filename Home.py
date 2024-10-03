import os
from dotenv import load_dotenv
from google_connector.google_sheet_download import GoogleDriveDownloader
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.row import row
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from pages.IT_Home import it_home
from pages.Chess_Home import chess_home
from pages.SEL_Home import sel_home

from pages.IT_Applicants import it_applicants
from pages.SEL_Applicants import sel_applicants
from pages.Chess_Applicants import chess_applicants

from pages.accepted import view_accepted
from pages.rejected import view_rejected
from pages.interview_scheduled import view_scheduled
from pages.interview_approved import view_approved

from pages.hr import hr_page
from pages.update_data import update_page

import yaml
from yaml.loader import SafeLoader

load_dotenv()

credentials = {
    'usernames': {
        'admin': {
            'email': st.secrets['credentials']['usernames']['admin']['email'],
            'name': st.secrets['credentials']['usernames']['admin']['name'],
            'password': st.secrets['credentials']['usernames']['admin']['password']
        }
    }
}
authenticator = stauth.Authenticate(
    credentials,
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)

def auth_page():
    name, st.session_state["authentication_status"], username = authenticator.login('main')
    if st.session_state["authentication_status"]:
        st.rerun()
    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')

def intro_page():
    st.title("Welcome to Daadras ATS")
    st.markdown("Choose a session to analyze and manage applications.")


def home_page():
    app_data = [st.session_state["it_data"], st.session_state["chess_data"], st.session_state["sel_data"]]
    app_data = pd.concat(app_data)
    tab1, tab2, tab3 = st.tabs(["🔎 Overview", "📈 Charts", "📍 Map"])
    with tab1:
        # Basic Queries for IT Metrics
        average_age = round(app_data['age'].mean(), 1)
        males = len(app_data[app_data.gender == "Male"])
        females = len(app_data[app_data.gender == "Female"])
        total_applicants = len(app_data)
        university_students = len(app_data[app_data.occupation == "Student"])
        not_working = len(app_data[app_data.occupation == "not working"])
        doing_jobs = len(app_data[app_data.occupation == "Employed"])
        ngo_work = len(app_data[app_data.ngo_work == "yes"])


        st.header("Overview of All Applications")

        # Display IT metrics using st.metric
        age_metric, male_metric, female_metric, total_metric = st.columns(4)
        age_metric.metric(label="Average Age", value=f"{average_age} yrs")
        male_metric.metric(label="Males", value=f"{males} 🧍‍♂️")
        female_metric.metric(label="Females", value=f"{females} 🧍‍♀️")
        total_metric.metric(label="Total Applicants", value=total_applicants)
        university_metric, unemployed_metric, job_metric, ngo_metric = st.columns(4)
        job_metric.metric(label="Have Jobs", value = doing_jobs)
        university_metric.metric(label="University Students", value=university_students)
        unemployed_metric.metric(label="Not Working", value=not_working)
        ngo_metric.metric(label="Have worked in NGO's", value=ngo_work)

    with tab2:
        graph_1, graph_2 = st.columns(spec=2, gap="large")
        # Graph Applicants by institute using st.bar_chart
        applicants_by_institute = app_data["institute"].value_counts().reset_index()
        applicants_by_institute.columns = ['institute', 'count']
        graph_1.plotly_chart(
            px.bar(
                applicants_by_institute,
                x="institute",
                y="count",
                title="Number of Applicants by Institute",
                labels = {
                    "institute": "Institute/Organization Name",
                    "count": "Number of People"
                }
            ).update_layout(
                yaxis=dict(
                    tickmode='linear',
                    tick0= 0,
                    dtick = 1
                )
            )
        )
        transport_counts = app_data["transport"].value_counts().reset_index()
        transport_counts.columns = ['transport', 'count']
        graph_2.plotly_chart(
            px.bar(
                transport_counts,
                x='transport',
                y='count',
                title="How are the applicants going to come?",
                labels = {
                    "transport": "Transport",
                    "count": "Number of People",
                },
            ).update_layout(
                yaxis=dict(
                    tickmode='linear',
                    tick0= 0,
                    dtick = 1
                )
            )
        )

        # Graph Applicants with NGO experience using st.bar_chart
        # Filter the data for those who have NGO experience
        it_with_ngo_experience = app_data[app_data['ngo_work'] == 'Yes']
        # Group by Institute/Organization Name and count the number of people with NGO experience
        institute_counts = it_with_ngo_experience['institute'].value_counts().reset_index()
        institute_counts.columns = ['institute', 'count']
        st.plotly_chart(
            px.bar(institute_counts,
                x="institute",
                y="count",
                title="Number of People with NGO Experience by Institute",
                labels = {
                    "institute": "Institute/Organization Name",
                    "count": "Number of People"
                },
                range_y = [1, 5],
            ).update_layout(
                yaxis=dict(
                    tickmode='linear',
                    tick0= 0,
                    dtick = 1
                )
            )
        )

    with tab3:
        tab3.subheader("Where are the applicants coming from?")
        def get_coordinates(address):
            random_coords = (np.random.randn(2, 1) / [10, 10]) + [31.5204, 74.3587]
            return random_coords[0]

        map_df = app_data.filter(items=["name", "transport", "city_address"])
        map_df["lat"] = map_df["city_address"].apply(lambda x: get_coordinates(x)[0])
        map_df["lon"] = map_df["city_address"].apply(lambda x: get_coordinates(x)[1])

        # Read mapbox access token from env
        MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

        map_fig = go.Figure(go.Scattermapbox(
            lon = map_df["lon"], lat = map_df["lat"],
            text = map_df["name"] + ": " + map_df["transport"],
            textposition = "top right",
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=12,
                color='rgb(113, 77, 191)',
                opacity=0.8,
            ),
            hoverinfo='text'
            ))

        map_fig.update_layout(
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            center=dict(
                lat=31.5204,
                lon=74.3587
            ),
            zoom = 10,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        st.plotly_chart(map_fig)

if "first_run" not in st.session_state.keys():
    st.session_state["first_run"] = True
if st.session_state["authentication_status"]:
    logout_button = st.sidebar.button("Logout")
    if logout_button:
        st.session_state["on_page"] = None
        st.session_state["authentication_status"] = None
        st.rerun()
    if "on_page" not in st.session_state.keys():
        st.session_state["on_page"] = None
        intro_page()

    header_1, header_2 = st.sidebar.columns(2)
    header_1.write("**دادرس**")
    header_2.caption("Daadras ATS")
    sessions = pd.read_csv("./database/sessions.csv")

    if "current_page" not in st.session_state.keys():
        st.session_state["current_page"] = "Intro"

    session_selector = st.sidebar.selectbox(
        "Select Session",
        sessions.session_name.unique(),
        index=None,
        key='selection',
    )
    accept_button = st.sidebar.button("Access", type="primary")
    if accept_button:
        st.session_state["current_page"] = "Applicant"
    st.session_state["sessions"] = sessions
    st.session_state["project_sessions"] = sessions.session_name.unique()

    if session_selector is not None and st.session_state["current_page"] == "Applicant":
        st.session_state["current_session"] = sessions[sessions.session_name == session_selector].reset_index()
        downloader = GoogleDriveDownloader()
        # Read data of relevant session
        csv_files = pd.DataFrame(st.session_state["current_session"])


        if st.session_state["first_run"]:
            download_it_file = downloader.download_google_sheet(f"{csv_files[csv_files.category == 'IT']['sheet_url'].values[0]}", f"./database/{csv_files[csv_files.category == 'IT'].sheet_link.values[0]}")
            download_sel_file = downloader.download_google_sheet(f"{csv_files[csv_files.category == 'CHESS']['sheet_url'].values[0]}", f"./database/{csv_files[csv_files.category == 'CHESS'].sheet_link.values[0]}")
            download_chess_file = downloader.download_google_sheet(f"{csv_files[csv_files.category == 'SEL']['sheet_url'].values[0]}", f"./database/{csv_files[csv_files.category == 'SEL'].sheet_link.values[0]}")

            it_data = pd.read_csv(f"./database/{csv_files[csv_files.category == 'IT'].sheet_link.values[0]}")
            sel_data = pd.read_csv(f"./database/{csv_files[csv_files.category == 'CHESS'].sheet_link.values[0]}")
            chess_data = pd.read_csv(f"./database/{csv_files[csv_files.category == 'SEL'].sheet_link.values[0]}")


            it_data["applicant_status"] = "Under Review"
            sel_data["applicant_status"] = "Under Review"
            chess_data["applicant_status"] = "Under Review"
            it_data.rename(columns={
                'Timestamp': 'timestamp',
                'Email Address': 'email',
                'Name': 'name',
                'Age': 'age',
                'Gender': 'gender',
                'Phone Number': 'phone_number',
                'Transport': 'transport',
                'Have you worked for any NGO before?': 'ngo_work',
                'City': 'city',
                'In which area do you currently reside in your city?': 'city_address',
                'Your Current Occupation': 'occupation',
                'Institute where you currently study or studied': 'institute',
                'CV': 'cv',
                'What computers skills do you have?': 'cs_skills',
                'Do you have any experience using Canva, or any tool from the Adobe media kit like Photoshop, Lightroom e.t.c': 'adobe_canva',
                'Do you have any other computer skills that you believe is beneficial to teach kids between the age of 10 to 16?': 'other_skills',
                'Your Instagram Account:': 'insta_id',
                'Your LinkedIn Profile:': 'linkedin_id',
                'Do you have a Discord ID?': 'has_discord'
            }, inplace=True)

            sel_data.rename(columns={
                'Timestamp': 'timestamp',
                'Email Address': 'email',
                'Name': 'name',
                'Age': 'age',
                'Gender': 'gender',
                'Phone Number': 'phone_number',
                'Transport': 'transport',
                'Have you worked for any NGO before?': 'ngo_work',
                'City': 'city',
                'In which area do you currently reside in your city?': 'city_address',
                'Your Current Occupation': 'occupation',
                'Institute where you currently study or studied': 'institute',
                'CV': 'cv',
                'What computers skills do you have?': 'cs_skills',
                'Do you have any experience using Canva, or any tool from the Adobe media kit like Photoshop, Lightroom e.t.c': 'adobe_canva',
                'Do you have any other computer skills that you believe is beneficial to teach kids between the age of 10 to 16?': 'other_skills',
                'Your Instagram Account:': 'insta_id',
                'Your LinkedIn Profile:': 'linkedin_id',
                'Do you have a Discord ID?': 'has_discord'
            }, inplace=True)

            chess_data.rename(columns={
                'Timestamp': 'timestamp',
                'Email Address': 'email',
                'Name': 'name',
                'Age': 'age',
                'Gender': 'gender',
                'Phone Number': 'phone_number',
                'Transport': 'transport',
                'Have you worked for any NGO before?': 'ngo_work',
                'City': 'city',
                'In which area do you currently reside in your city?': 'city_address',
                'Your Current Occupation': 'occupation',
                'Institute where you currently study or studied': 'institute',
                'CV': 'cv',
                'What computers skills do you have?': 'cs_skills',
                'Do you have any experience using Canva, or any tool from the Adobe media kit like Photoshop, Lightroom e.t.c': 'adobe_canva',
                'Do you have any other computer skills that you believe is beneficial to teach kids between the age of 10 to 16?': 'other_skills',
                'Your Instagram Account:': 'insta_id',
                'Your LinkedIn Profile:': 'linkedin_id',
                'Do you have a Discord ID?': 'has_discord'
            }, inplace=True)

            for name, resume in it_data[["name", "cv"]].values:
                    downloader.download_pdf(resume, f"./database/{session_selector}/applicants_resume/{name}_resume_it.pdf")
                    it_data.loc[it_data.name == name, "path_to_pdf"] = f"./database/{session_selector}/applicants_resume/{name}_resume_it.pdf"
            for name, resume in sel_data[["name", "cv"]].values:
                    downloader.download_pdf(resume, f"./database/{session_selector}/applicants_resume/{name}_resume_sel.pdf")
                    sel_data.loc[sel_data.name == name, "path_to_pdf"] = f"./database/{session_selector}/applicants_resume/{name}_resume_it.pdf"

            for name, resume in chess_data[["name", "cv"]].values:
                    downloader.download_pdf(resume, f"./database/{session_selector}/applicants_resume/{name}_resume_chess.pdf")
                    chess_data.loc[chess_data.name == name, "path_to_pdf"] = f"./database/{session_selector}/applicants_resume/{name}_resume_it.pdf"


            it_data["city_address"] = ""
            sel_data["city_address"] = ""
            chess_data["city_address"] = ""

            it_data.to_csv(f"./database/{session_selector}/applicants_form_data/it_applicant_data.csv")
            chess_data.to_csv(f"./database/{session_selector}/applicants_form_data/chess_applicant_data.csv")
            sel_data.to_csv(f"./database/{session_selector}/applicants_form_data/sel_applicant_data.csv")

            st.session_state["it_data"], st.session_state["sel_data"], st.session_state["chess_data"] = it_data, sel_data, chess_data
            st.session_state["first_run"] = False
        st.sidebar.divider()

        home_button = st.sidebar.button(label="Home", use_container_width=True)
        if home_button:
            st.session_state["on_page"] = "Home"
            home_page()

        col1, col2, col3 = st.sidebar.columns(3, gap="small")

        it_expander = col1.popover("IT", use_container_width=True)
        sel_expander = col2.popover("SEL", use_container_width=True)
        chess_expander = col3.popover("CHESS", use_container_width=True)
        with it_expander:
            it_button = st.button(label="Home", use_container_width=True, key="it_button")
            it_applicants_button = st.button(label="Individual Applicants", use_container_width=True, key="it_applicant")

        with sel_expander:
            sel_button = st.button(label="Home", use_container_width=True, key="sel_button")
            sel_applicants_button = st.button(label="Individual Applicants", use_container_width=True, key="sel_applicant")

        with chess_expander:
            chess_button = st.button(label="Home", use_container_width=True, key="chess_button")
            chess_applicants_button = st.button(label="Individual Applicants", use_container_width=True, key="chess_applicant")

        st.sidebar.caption("Interviews")
        int_sch, int_app = st.sidebar.columns(2)
        interview_scheduled = int_sch.button("Scheduled", use_container_width=True)
        interview_approved = int_app.button("Approved", use_container_width=True)
        st.sidebar.caption("Applicants")
        acc, rej = st.sidebar.columns(2)
        accepted = acc.button("Accepted", use_container_width=True)
        rejected = rej.button("Rejected", use_container_width=True)

        if it_button:
            st.session_state["on_page"] = "IT_home"
        elif sel_button:
            st.session_state["on_page"] = "SEL_home"
        elif chess_button:
            st.session_state["on_page"] = "CHESS_home"
        elif it_applicants_button:
            st.session_state["on_page"] = "IT"
        elif sel_applicants_button:
            st.session_state["on_page"] = "SEL"
        elif chess_applicants_button:
            st.session_state["on_page"] = "CHESS"
        elif accepted:
            st.session_state["on_page"] = "Accepted"
        elif rejected:
            st.session_state["on_page"] = "Rejected"
        elif interview_scheduled:
            st.session_state["on_page"] = "Scheduled"
        elif interview_approved:
            st.session_state["on_page"] = "Approved"
        else:
            pass

    st.sidebar.divider()
    st.sidebar.caption("HR")
    if st.sidebar.button(label="Project Management"):
        st.session_state["on_page"] = "HR"
    if st.sidebar.button(label="Update Data"):
        st.session_state["on_page"] = "Updater"

    match st.session_state["on_page"]:
        case "IT_home":
            it_home()
        case "SEL_home":
            sel_home()
        case "CHESS_home":
            chess_home()
        case "IT":
            it_applicants()
        case "SEL":
            sel_applicants()
        case "CHESS":
            chess_applicants()
        case "Accepted":
            view_accepted()
        case "Rejected":
            view_rejected()
        case "HR":
            hr_page()
        case "Updater":
            update_page()
        case "Scheduled":
            view_scheduled()
        case "Approved":
            view_approved()
        case _:
            pass

else:
    auth_page()
