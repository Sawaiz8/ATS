import pandas as pd
import streamlit as st


def view_scheduled():
    it = st.session_state["it_data"]
    sel = st.session_state["sel_data"]
    chess = st.session_state["chess_data"]

    tab1, tab2, tab3 = st.tabs(["IT", "SEL", "CHESS"])
    with tab1:
        st.write("Interviews Scheduled for IT Applications: ")
        st.dataframe(it[it.applicant_status == "Interview_Scheduled"][["name", "email", "gender", "phone_number"]])

    with tab2:
        st.write("Interviews Scheduled for SEL Applications: ")
        st.dataframe(chess[chess.applicant_status == "Interview_Scheduled"][["name", "email", "gender", "phone_number"]])

    with tab3:
        st.write("Interviews Scheduled for CHESS Applications: ")
        st.dataframe(sel[sel.applicant_status == "Interview_Scheduled"][["name", "email", "gender", "phone_number"]])
