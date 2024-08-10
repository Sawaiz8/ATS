import os
from dotenv import load_dotenv
import streamlit as st
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

from pages.hr import hr_page

load_dotenv()

st.set_page_config(
    layout="wide",
)

sessions = pd.read_csv("./database/sessions.csv")

def intro_page():
    st.title("Welcome to Daadras ATS")

    st.markdown("Choose a session to analyze and manage applications.")


def home_page():
    st.write(st.session_state)
    # Read form data of relevant session
    csv_files = pd.DataFrame(st.session_state["current_session"])
    it_data = pd.read_csv(f"./database/{csv_files[csv_files.category == "IT"].sheet_link.values[0]}")
    sel_data = pd.read_csv(f"./database/{csv_files[csv_files.category == "CHESS"].sheet_link.values[0]}")
    chess_data = pd.read_csv(f"./database/{csv_files[csv_files.category == "SEL"].sheet_link.values[0]}")

    st.session_state["it_data"] = it_data
    st.session_state["sel_data"] = sel_data
    st.session_state["chess_data"] = chess_data

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
        it_with_ngo_experience = app_data[app_data['ngo_work'] == 'yes']
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

if "current_page" not in st.session_state.keys():
    st.session_state["current_page"] = "Intro"

if st.session_state["current_page"] == "Intro":
    intro_page()
session_selector = st.sidebar.selectbox(
    "Select Session",
    sessions.session_name.unique(),
    index=None,
    key='selection',
)
accept_button = st.sidebar.button("Accept", type="primary")

st.session_state["sessions"] = sessions
st.session_state["project_sessions"] = sessions.session_name.unique()

if accept_button:
    st.session_state["current_page"] = "Applicant"
if session_selector is not None and st.session_state["current_page"] == "Applicant":
    st.session_state["current_session"] = sessions[sessions.session_name == session_selector]
    st.sidebar.divider()
    st.sidebar.caption("Home")
    col1, col2, col3 = st.sidebar.columns(3)
    it_button = col1.button(label="IT", use_container_width=True)
    sel_button = col2.button(label="SEL", use_container_width=True)
    chess_button = col3.button(label="CHESS", use_container_width=True)
    indiv_toggle = st.sidebar.toggle("Individual Applicants")

    if it_button:
        st.session_state["current_applicant"] = "IT"
    elif sel_button:
        st.session_state["current_applicant"] = "SEL"
    elif chess_button:
        st.session_state["current_applicant"] = "CHESS"
    elif not indiv_toggle:
        home_page()
    if indiv_toggle:
        if st.session_state["current_applicant"] == "IT":
            current_data = st.session_state["it_data"]
            it_applicants()
        elif st.session_state["current_applicant"] == "SEL":
            current_data = st.session_state["sel_data"]
            sel_applicants()
        elif st.session_state["current_applicant"] == "CHESS":
            current_data = st.session_state["chess_data"]
            chess_applicants()
        if st.sidebar.button(label="Accepted Applicants") or st.session_state["current_applicant"] == "Accepted":
            st.session_state["current_applicant"] = "Accepted"
            st.dataframe(current_data[current_data.applicant_status == "Accepted"]);
        if st.sidebar.button(label="Rejected Applicants") or st.session_state["current_applicant"] == "Rejected":
            st.session_state["current_applicant"] = "Rejected"
            st.dataframe(current_data[current_data.applicant_status == "Rejected"]);


    else:
        if it_button:
            st.session_state["current_applicant"] = "IT"
            it_home()
        elif sel_button:
            st.session_state["current_applicant"] = "SEL"
            sel_home()
        elif chess_button:
            st.session_state["current_applicant"] = "CHESS"
            chess_home()


st.sidebar.divider()
st.sidebar.caption("HR")
if st.sidebar.button(label="Project Management") or st.session_state["current_page"] == "HR":
    st.session_state["current_page"] = "HR"
    hr_page()

def retrieve_csv():
    pass
update_csvs = st.sidebar.button("Update Data", disabled=True, on_click=retrieve_csv)
