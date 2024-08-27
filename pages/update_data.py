import streamlit as st
import pandas as pd
from time import sleep

def update_data(project_name=None, chess=None, it=None, sel=None, chess_email=None, it_email=None, sel_email=None, chess_subject=None, it_subject=None, sel_subject=None):
    if it is not None:
        it = pd.read_csv(it)
        it.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv", index=False)
        st.success("Updated IT file")
    if chess is not None:
        chess = pd.read_csv(chess)
        chess.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv",index=False)
        st.success("Updated CHESS file")

    if sel is not None:
        sel = pd.read_csv(sel)
        sel.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv", index=False)
        st.write("Updated SEL file")

    email_prompts = pd.read_csv("./database/email_prompts.csv")
    update_condition = email_prompts.session_name == project_name
    email_prompts.loc[update_condition, ["it_prompt"]] = it_email
    email_prompts.loc[update_condition, ["sel_prompt"]] = chess_email
    email_prompts.loc[update_condition, ["chess_prompt"]] = sel_email

    email_prompts.loc[update_condition, ["it_header"]] = it_subject
    email_prompts.loc[update_condition, ["sel_header"]] = sel_subject
    email_prompts.loc[update_condition, ["chess_header"]] = chess_subject


    email_prompts.to_csv("./database/email_prompts.csv",index=False)

def update_page():

    email_prompts = pd.read_csv("./database/email_prompts.csv")

    st.title("Update Session Data")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"], key="update_selector")
    if selected_project is not None:
        st.subheader("Chess")
        chess_files = st.file_uploader("Upload Chess CSV files", type="csv")
        st.subheader("IT")
        it_files = st.file_uploader("Upload IT CSV files", type="csv")
        st.subheader("SEL")
        sel_files = st.file_uploader("Upload SEL CSV files", type="csv")


        it_email_container  = st.expander("IT Email Prompt")
        it_email_subject = it_email_container.text_input(label="Subject", value=email_prompts[email_prompts.session_name == selected_project]["it_header"].values[0], key="it_email_subject")
        it_email_prompt = it_email_container.text_area(label="Enter prompt:",value=email_prompts[email_prompts.session_name == selected_project]["it_prompt"].values[0], key="it_email_prompt")

        sel_email_container = st.expander("SEL Email Prompt")
        sel_email_subject = sel_email_container.text_input(label="Subject", value=email_prompts[email_prompts.session_name == selected_project]["sel_header"].values[0], key="sel_email_subject")
        sel_email_prompt = sel_email_container.text_area(label="Prompt",value=email_prompts[email_prompts.session_name == selected_project]["sel_prompt"].values[0], placeholder="SEL email prompt", key="sel_email_prompt")

        chess_email_container = st.expander("Chess Email Prompt")
        chess_email_subject = chess_email_container.text_input(label="Subject", value=email_prompts[email_prompts.session_name == selected_project]["chess_header"].values[0], key="chess_email_subject")
        chess_email_prompt = chess_email_container.text_area(label="Prompt",value=email_prompts[email_prompts.session_name == selected_project]["chess_prompt"].values[0] ,placeholder="CHESS email prompt", key="chess_email_prompt")

        with st.popover("Update"):
            st.error("Are you sure?")
            update_button = st.button("Confirm")
            if update_button:
                update_data(selected_project, chess_files, it_files, sel_files, chess_email_prompt, it_email_prompt, sel_email_prompt, chess_email_subject, it_email_subject, sel_email_subject)
                st.success("Successfully Updated Data")
                sleep(1.0)
                st.rerun()
