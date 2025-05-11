import streamlit as st

def view_interview_status(status: str):
    it = st.session_state["it_data"]
    sel = st.session_state["sel_data"]
    chess = st.session_state["chess_data"]

    tab1, tab2, tab3 = st.tabs(["IT", "SEL", "CHESS"])
    with tab1:
        st.write(f"{status} IT Applications: ")
        st.dataframe(it[it["applicant_status"] == status][["name", "email", "gender", "phone_number"]])

    with tab2:
        st.write(f"{status} SEL Applications: ")
        st.dataframe(sel[sel["applicant_status"] == status][["name", "email", "gender", "phone_number"]])

    with tab3:
        st.write(f"{status} CHESS Applications: ")
        st.dataframe(chess[chess["applicant_status"] == status][["name", "email", "gender", "phone_number"]])

