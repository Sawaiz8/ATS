import pandas as pd
import streamlit as st


def view_approved():
    it = st.session_state["it_data"]
    sel = st.session_state["sel_data"]
    chess = st.session_state["chess_data"]

    tab1, tab2, tab3 = st.tabs(["IT", "SEL", "CHESS"])
    with tab1:
        st.write("Interviews Approved for IT Applications: ")
        st.dataframe(it[it.applicant_status == "Interview_Approved"][["name", "email", "gender", "phone_number"]])

    with tab2:
        st.write("Interviews Approved for SEL Applications: ")
        st.dataframe(chess[chess.applicant_status == "Interview_Approved"][["name", "email", "gender", "phone_number"]])

    with tab3:
        st.write("Interviews Approved for CHESS Applications: ")
        st.dataframe(sel[sel.applicant_status == "Interview_Approved"][["name", "email", "gender", "phone_number"]])
