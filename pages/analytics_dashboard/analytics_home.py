import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()

def analytics_home(category):
    # Read Chess data from CSV file
    df_applicant = st.session_state[f"{category}_data"]

    tab1, tab2, tab3 = st.tabs(["🔎 Overview", "📈 Charts", "📍 Map"])
    with tab1:
        # Basic Queries for IT Metrics
        average_age = round(df_applicant['age'].mean(), 1)
        males = len(df_applicant[df_applicant.gender == "Male"])
        females = len(df_applicant[df_applicant.gender == "Female"])
        total_applicants = len(df_applicant)
        university_students = len(df_applicant[df_applicant.occupation == "Student"])
        not_working = len(df_applicant[df_applicant.occupation == "not working"])
        doing_jobs = len(df_applicant[df_applicant.occupation == "Employed"])
        ngo_work = len(df_applicant[df_applicant.ngo_work == "yes"])

        st.header(f"Overview of {category} Applications")

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
        applicants_by_institute = df_applicant["institute"].value_counts().reset_index()
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
        transport_counts = df_applicant["transport"].value_counts().reset_index()
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
        it_with_ngo_experience = df_applicant[df_applicant['ngo_work'] == 'Yes']
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
        tab3.subheader(f"Where are the {category} applicants coming from?")
        def get_coordinates(address):
            random_coords = (np.random.randn(2, 1) / [10, 10]) + [31.5204, 74.3587]
            return random_coords[0]

        map_df = df_applicant.filter(items=["name", "transport", "city_address"])
        map_df["lat"] = map_df["city_address"].apply(lambda x: get_coordinates(x)[0])
        map_df["lon"] = map_df["city_address"].apply(lambda x: get_coordinates(x)[1])

        # Read mapbox access token from file: mapbox_token
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
