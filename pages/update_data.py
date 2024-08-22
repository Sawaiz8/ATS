import streamlit as st
import pandas as pd

def update_data(project_name, chess, it, sel):
    it = pd.read_csv(it)
    chess = pd.read_csv(chess)
    sel = pd.read_csv(sel)

    it.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv")
    chess.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv")
    sel.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv")

def update_page():
    st.title("Update Session Data")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"], key="update_selector")
    if selected_project is not None:
        st.subheader("Chess")
        chess_files = st.file_uploader("Upload Chess CSV files", type="csv")

        st.subheader("IT")
        it_files = st.file_uploader("Upload IT CSV files", type="csv")

        st.subheader("SEL")
        sel_files = st.file_uploader("Upload SEL CSV files", type="csv")
        update_button = st.button("Update")
        if chess_files and it_files and sel_files and update_button:
            update_data(selected_project, chess_files, it_files, sel_files)
        else:
            st.error("Upload all required files!")
