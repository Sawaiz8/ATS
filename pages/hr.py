import streamlit as st
import pandas as pd
from os import mkdir
from shutil import rmtree
import glob
def save_project(project_name, it_file, chess_file, sel_file, it_email, chess_email, sel_email, it_subject, chess_subject, sel_subject):

    sessions = pd.read_csv("./database/sessions.csv", index_col=0)
    if project_name in sessions["session_name"]:
        st.error("Project with same name already exists!")
        return
    email_prompts = pd.read_csv("./database/email_prompts.csv")
    email_prompts.loc[len(email_prompts)] = [project_name, it_subject,it_email, chess_subject ,chess_email, sel_subject,sel_email]
    email_prompts.to_csv("./database/email_prompts.csv", index=False)
    mkdir(f"./database/{project_name}")
    mkdir(f"./database/{project_name}/applicants_form_data")
    mkdir(f"./database/{project_name}/applicants_resume")

    it = pd.read_csv(it_file)
    chess = pd.read_csv(chess_file)
    sel = pd.read_csv(sel_file)

    it.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv")
    chess.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv")
    sel.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv")

    sessions.loc[len(sessions.index)] = [project_name, "IT", project_name, f"{project_name}/applicants_form_data/it_applicant_data.csv"]
    sessions.loc[len(sessions.index)] = [project_name, "SEL", project_name, f"{project_name}/applicants_form_data/sel_applicant_data.csv"]
    sessions.loc[len(sessions.index)] = [project_name, "CHESS", project_name, f"{project_name}/applicants_form_data/chess_applicant_data.csv"]


    sessions.to_csv("./database/sessions.csv")
    st.toast(f"{project_name} created successfully!")


def hr_page():

    default_prompt = """Subject: Congratulations on Your Selection as a Volunteer with Daadras Foundation!

    Dear [Applicant's Name],

    Congratulations! We are pleased to inform you that you have been selected for a volunteer position with Daadras Foundation. Your enthusiasm and commitment to making a difference have truly impressed us, and we are excited to welcome you to our team.

    To finalize your position and discuss the next steps, please contact us at your earliest convenience. We look forward to connecting with you and providing further details about your role and responsibilities.

    Once again, congratulations, and thank you for your willingness to contribute to our mission. We are confident that your involvement will make a meaningful impact.

    Best regards,"""

    default_subject = "Your Application was Approved!"
    st.title("Project Management")
    email_prompts = pd.read_csv("./database/email_prompts.csv")

    # Select existing project
    st.header("Select a Project")
    selected_project = st.selectbox("Choose a project", st.session_state["project_sessions"])

    if selected_project:
        st.write(f"### {selected_project}")
        current_sessions = st.session_state["sessions"]
        search = f"./database/{current_sessions[current_sessions.session_name == selected_project].session_number.values[0]}/applicants_form_data/*"
        st.write("This project has the following files:")
        for file in glob.glob(search):
            st.write(f"- {file}")

        st.subheader("Email Prompts")
        it_expander = st.expander("IT Prompt")
        it_expander.markdown(f"Subject: {email_prompts[email_prompts.session_name == selected_project]["it_header"].values[0]}")
        it_expander.write(email_prompts[email_prompts.session_name == selected_project]["it_prompt"].values[0])
        sel_expander = st.expander("SEL Prompt")
        sel_expander.markdown(f"Subject: {email_prompts[email_prompts.session_name == selected_project]["sel_header"].values[0]}")
        sel_expander.write(email_prompts[email_prompts.session_name == selected_project]["it_prompt"].values[0])
        chess_expander = st.expander("CHESS Prompt")
        chess_expander.markdown(f"Subject: {email_prompts[email_prompts.session_name == selected_project]["chess_header"].values[0]}")
        chess_expander.write(email_prompts[email_prompts.session_name == selected_project]["chess_prompt"].values[0])

    # Create new project
    st.header("Create a New Project")
    new_project_name = st.text_input("Project Name")

    st.write("### Upload CSV Files")

    st.subheader("Chess")
    chess_files = st.file_uploader("Upload Chess CSV files", type="csv")

    st.subheader("IT")
    it_files = st.file_uploader("Upload IT CSV files", type="csv")

    st.subheader("SEL")
    sel_files = st.file_uploader("Upload SEL CSV files", type="csv")

    it_email_container  = st.expander("IT Email Prompt")
    it_email_subject = it_email_container.text_input(label="Subject", value=default_subject, key="it_email_subject")
    it_email_prompt = it_email_container.text_area(label="Enter prompt:",value=default_prompt, key="it_email_prompt")

    sel_email_container = st.expander("SEL Email Prompt")
    sel_email_subject = sel_email_container.text_input(label="Subject", value=default_subject, key="sel_email_subject")
    sel_email_prompt = sel_email_container.text_area(label="Prompt",value=default_prompt, placeholder="SEL email prompt", key="sel_email_prompt")

    chess_email_container = st.expander("Chess Email Prompt")
    chess_email_subject = chess_email_container.text_input(label="Subject", value=default_subject, key="chess_email_subject")
    chess_email_prompt = chess_email_container.text_area(label="Prompt",value=default_prompt,placeholder="CHESS email prompt", key="chess_email_prompt")

    if st.button("Save Project"):
        if new_project_name:
            save_project(new_project_name, it_files, chess_files, sel_files, it_email_prompt, sel_email_prompt, chess_email_prompt, it_email_subject, sel_email_subject, chess_email_subject)
            st.rerun()
        else:
            st.error("Please provide a project name.")


    st.header("Delete Project")
    delete_selector = st.selectbox("Choose a project", st.session_state["project_sessions"], key="delete")
    with st.popover("Delete"):
        st.error("Are you sure?")
        delete_button = st.button("Confirm")
    if delete_selector and delete_button:
        sessions = pd.read_csv("./database/sessions.csv", index_col=0)
        email_prompts = pd.read_csv("./database/email_prompts.csv")
        selected_session_directory = sessions[sessions.session_name == delete_selector].session_number.values[0]
        try:
            rmtree(f"./database/{selected_session_directory}")
            sessions = sessions[sessions.session_name != delete_selector]
            email_prompts = email_prompts[email_prompts.session_name != delete_selector]
            email_prompts.to_csv("./database/email_prompts.csv", index=False)
            sessions.to_csv("./database/sessions.csv")
            st.success("Project Deleted Successfully!")
            st.rerun()
        except OSError as e:
            st.error("Error deleting project!")
            st.write(e)
