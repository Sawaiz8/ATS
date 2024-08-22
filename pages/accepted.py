import pandas as pd
import streamlit as st


def view_accepted(it, chess, sel):
    tab1, tab2, tab3 = st.tabs(["IT", "SEL", "CHESS"])
    it["email_status"] = "Unsent"
    chess["email_status"] = "Unsent"
    sel["email_status"] = "Unsent"
    with tab1:
        st.write("Accepted IT Applications: ")
        st.dataframe(it[it.applicant_status == "Accepted"][["name", "email", "gender", "phone_number", "email_status"]])
        email_button = st.button(label="Send Emails ✉️", key="it_email")

    with tab2:
        st.write("Accepted SEL Applications: ")
        st.dataframe(chess[chess.applicant_status == "Accepted"][["name", "email", "gender", "phone_number", "email_status"]])
        email_button = st.button(label="Send Emails ✉️", key="sel_email")

    with tab3:
        st.write("Accepted CHESS Applications: ")
        st.dataframe(sel[sel.applicant_status == "Accepted"][["name", "email", "gender", "phone_number", "email_status"]])
        email_button = st.button(label="Send Emails ✉️", key="chess_email")


    if email_button:
        st.toast("Email Sent!")
