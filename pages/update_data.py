import streamlit as st
import pandas as pd

def update_data(project_name, chess, it, sel, chess_email, it_email, sel_email, chess_subject, it_subject, sel_subject):
    it = pd.read_csv(it)
    chess = pd.read_csv(chess)
    sel = pd.read_csv(sel)

    email_prompts = pd.read_csv("./database/email_prompts.csv")
    update_condition = email_prompts.session_name == project_name
    email_prompts.loc[update_condition, ["it_prompt"]] = it_email
    email_prompts.loc[update_condition, ["sel_prompt"]] = chess_email
    email_prompts.loc[update_condition, ["chess_prompt"]] = sel_email

    email_prompts.loc[update_condition, ["it_header"]] = it_subject
    email_prompts.loc[update_condition, ["sel_header"]] = sel_subject
    email_prompts.loc[update_condition, ["chess_header"]] = chess_subject


    email_prompts.to_csv("./database/email_prompts.csv",index=False)
    it.to_csv(f"./database/{project_name}/applicants_form_data/it_applicant_data.csv", index=False)
    chess.to_csv(f"./database/{project_name}/applicants_form_data/chess_applicant_data.csv",index=False)
    sel.to_csv(f"./database/{project_name}/applicants_form_data/sel_applicant_data.csv", index=False)

def update_page():

    email_prompts = pd.read_csv("./database/email_prompts.csv")

    default_prompt = """Subject: Congratulations on Your Selection as a Volunteer with Daadras Foundation!

    Dear [Applicant's Name],

    Congratulations! We are pleased to inform you that you have been selected for a volunteer position with Daadras Foundation. Your enthusiasm and commitment to making a difference have truly impressed us, and we are excited to welcome you to our team.

    To finalize your position and discuss the next steps, please contact us at your earliest convenience. We look forward to connecting with you and providing further details about your role and responsibilities.

    Once again, congratulations, and thank you for your willingness to contribute to our mission. We are confident that your involvement will make a meaningful impact.

    Best regards,
    """

    default_subject = "Your Application was Approved!"


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
        it_email_subject = it_email_container.text_input(label="Subject", value=default_subject, key="it_email_subject")
        it_email_prompt = it_email_container.text_area(label="Enter prompt:",value=default_prompt, key="it_email_prompt")

        sel_email_container = st.expander("SEL Email Prompt")
        sel_email_subject = sel_email_container.text_input(label="Subject", value=default_subject, key="sel_email_subject")
        sel_email_prompt = sel_email_container.text_area(label="Prompt",value=default_prompt, placeholder="SEL email prompt", key="sel_email_prompt")

        chess_email_container = st.expander("Chess Email Prompt")
        chess_email_subject = chess_email_container.text_input(label="Subject", value=default_subject, key="chess_email_subject")
        chess_email_prompt = chess_email_container.text_area(label="Prompt",value=default_prompt,placeholder="CHESS email prompt", key="chess_email_prompt")

        update_button = st.button("Update")
        if update_button:
            if chess_files and it_files and sel_files:
                update_data(selected_project, chess_files, it_files, sel_files, chess_email_prompt, it_email_prompt, sel_email_prompt, chess_email_subject, it_email_subject, sel_email_subject)
            else:
                st.error("Upload all required files!")
