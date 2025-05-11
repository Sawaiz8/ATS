from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth

from pages.analytics_dashboard.analytics_home import analytics_home
from pages.analytics_dashboard.individual_applicants import applicants_page
from pages.interview_statuses_pages.interview_status import view_interview_status
from pages.session_management.hr import hr_page
from pages.session_management.update_data import update_page
from pages.home.Home import intro_page, home_page
from controllers.home import download_and_update_latest_data
from utilities.mongo_db.streamlit_mongo_wrapper import get_all_session_names, get_session_data

load_dotenv()

credentials = {
    'usernames': {
        'admin': {
            'email': st.secrets['credentials']['usernames']['admin']['email'],
            'name': st.secrets['credentials']['usernames']['admin']['name'],
            'password': st.secrets['credentials']['usernames']['admin']['password']
        }
    }
}
authenticator = stauth.Authenticate(
    credentials,
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)

def auth_page():
    name, st.session_state["authentication_status"], username = authenticator.login('main')
    if st.session_state["authentication_status"]:
        st.rerun()
    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')

if "first_run" not in st.session_state.keys():
    st.session_state["first_run"] = True
    
if st.session_state["authentication_status"]:
    logout_button = st.sidebar.button("Logout")
    if logout_button:
        st.session_state["on_page"] = None
        st.session_state["authentication_status"] = None
        st.rerun()
    
    if "on_page" not in st.session_state.keys():
        st.session_state["on_page"] = None
        intro_page()

    header_1, header_2 = st.sidebar.columns(2)
    header_1.write("**دادرس**")
    header_2.caption("Daadras ATS")

    # Get a list of all sessions from mongo_store
    session_names = get_all_session_names()

    if "current_page" not in st.session_state.keys():
        st.session_state["current_page"] = "Intro"

    # Update sessions list
    session_selector = st.sidebar.selectbox(
        "Select Session",
        session_names,
        index=None,
        key='selection',
    )
    access_button = st.sidebar.button("Access", type="primary")
    if access_button:
        st.session_state["current_page"] = "Applicant"
    st.session_state["sessions"] = session_names
    st.session_state["project_sessions"] = session_names

    if session_selector is not None and st.session_state["current_page"] == "Applicant":
        st.session_state["current_session"] = get_session_data(session_selector)
        st.session_state["current_session_name"] = session_selector    

        if st.session_state["first_run"]:
            it_data, sel_data, chess_data = download_and_update_latest_data()
            st.session_state["it_data"], st.session_state["sel_data"], st.session_state["chess_data"] = it_data, sel_data, chess_data
            st.session_state["first_run"] = False
        st.sidebar.divider()

        home_button = st.sidebar.button(label="Home", use_container_width=True)
        if home_button:
            st.session_state["on_page"] = "Home"
            home_page()

        col1, col2, col3 = st.sidebar.columns(3, gap="small")

        it_expander = col1.popover("IT", use_container_width=True)
        sel_expander = col2.popover("SEL", use_container_width=True)
        chess_expander = col3.popover("CHESS", use_container_width=True)
        
        with it_expander:
            it_button = st.button(label="Home", use_container_width=True, key="it_button")
            it_applicants_button = st.button(label="Individual Applicants", use_container_width=True, key="it_applicant")

        with sel_expander:
            sel_button = st.button(label="Home", use_container_width=True, key="sel_button")
            sel_applicants_button = st.button(label="Individual Applicants", use_container_width=True, key="sel_applicant")

        with chess_expander:
            chess_button = st.button(label="Home", use_container_width=True, key="chess_button")
            chess_applicants_button = st.button(label="Individual Applicants", use_container_width=True, key="chess_applicant")

        st.sidebar.caption("Interviews")
        int_sch, int_app = st.sidebar.columns(2)
        interview_scheduled = int_sch.button("Scheduled", use_container_width=True)
        interview_approved = int_app.button("Approved", use_container_width=True)
        st.sidebar.caption("Applicants")
        acc, rej = st.sidebar.columns(2)
        accepted = acc.button("Accepted", use_container_width=True)
        rejected = rej.button("Rejected", use_container_width=True)

        if it_button:
            st.session_state["on_page"] = "IT_home"
        elif sel_button:
            st.session_state["on_page"] = "SEL_home"
        elif chess_button:
            st.session_state["on_page"] = "CHESS_home"
        elif it_applicants_button:
            st.session_state["on_page"] = "IT"
        elif sel_applicants_button:
            st.session_state["on_page"] = "SEL"
        elif chess_applicants_button:
            st.session_state["on_page"] = "CHESS"
        elif accepted:
            st.session_state["on_page"] = "Accepted"
        elif rejected:
            st.session_state["on_page"] = "Rejected"
        elif interview_scheduled:
            st.session_state["on_page"] = "Scheduled"
        elif interview_approved:
            st.session_state["on_page"] = "Approved"
        else:
            pass

    st.sidebar.divider()
    st.sidebar.caption("HR")
    if st.sidebar.button(label="Session Management"):
        st.session_state["on_page"] = "HR"
    if st.sidebar.button(label="Update Data"):
        st.session_state["on_page"] = "Updater"

    match st.session_state["on_page"]:
        case "IT_home":
            analytics_home(category="it")
        case "SEL_home":
            analytics_home(category="sel")
        case "CHESS_home":
            analytics_home(category="chess")
        case "IT":
            applicants_page(category="it")
        case "SEL":
            applicants_page(category="sel")
        case "CHESS":
            applicants_page(category="chess")
        case "Accepted":
            view_interview_status(status="Accepted")
        case "Rejected":
            view_interview_status(status="Rejected")
        case "Scheduled":
            view_interview_status(status="Interview_Scheduled")
        case "Approved":
            view_interview_status(status="Interview_Approved")
        case "HR":
            hr_page()
        case "Updater":
            update_page()
        case _:
            pass

else:
    auth_page()