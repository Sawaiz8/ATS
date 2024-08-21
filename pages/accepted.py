import pandas as pd
import streamlit as st


def view_accepted(it, chess, sel):

    st.write("Accepted IT Applications: ")
    st.table(it[it.applicant_status == "Accepted"][["name", "email", "gender", "phone_number"]])
    st.write("Accepted SEL Applications: ")
    st.table(chess[chess.applicant_status == "Accepted"][["name", "email", "gender", "phone_number"]])
    st.write("Accepted CHESS Applications: ")
    st.table(sel[sel.applicant_status == "Accepted"][["name", "email", "gender", "phone_number"]])

    email_button = st.button(label="Send Emails ✉️")

    if email_button:
        st.toast("Email Sent!")