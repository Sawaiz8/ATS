import pandas as pd
import streamlit as st


def view_rejected():
    it = st.session_state["it_data"]
    sel = st.session_state["sel_data"]
    chess = st.session_state["chess_data"]

    tab1, tab2, tab3 = st.tabs(["IT", "CHESS", "SEL"])
    it["email_status"] = "Unsent"
    chess["email_status"] = "Unsent"
    sel["email_status"] = "Unsent"
    with tab1:
        st.write("Rejected IT Applications: ")
        st.dataframe(it[it.applicant_status == "Rejected"][["name", "email", "gender", "phone_number", "email_status"]])
        email_button = st.button(label="Send Emails ✉️", key="it_email")

    with tab2:
        st.write("Rejected SEL Applications: ")
        st.dataframe(chess[chess.applicant_status == "Rejected"][["name", "email", "gender", "phone_number", "email_status"]])
        email_button = st.button(label="Send Emails ✉️", key="sel_email")

    with tab3:
        st.write("Rejected CHESS Applications: ")
        st.dataframe(sel[sel.applicant_status == "Rejected"][["name", "email", "gender", "phone_number", "email_status"]])
        email_button = st.button(label="Send Emails ✉️", key="chess_email")


    if email_button:
        st.toast("Email Sent!")
