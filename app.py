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
import os
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
        st.session_state["current_page"] = "access_project"
    
    st.session_state["project_sessions"] = session_names

    if session_selector is not None and st.session_state["current_page"] == "access_project":
        st.session_state["current_session_name"] = session_selector  
        st.session_state["current_session_data"] = {
            "session_information": get_session_data(session_selector),
            "category_data": download_and_update_latest_data()
        }
        
        st.sidebar.divider()

        home_button = st.sidebar.button(label="Home", use_container_width=True)
        if home_button:
            st.session_state["on_page"] = "Home"
            home_page()
        
        # Create columns dynamically based on number of categories
        num_categories = len(st.session_state["current_session_data"]["category_data"])
        cols = st.sidebar.columns(num_categories, gap="small")

        # Dictionary to store expanders and buttons
        expanders = {}
        buttons = {}

        # Create expanders and buttons for each category
        for i, (category, data) in enumerate(st.session_state["current_session_data"]["category_data"].items()):
            category_upper = category.upper()
            expanders[category] = cols[i].popover(category_upper, use_container_width=True)
            
            with expanders[category]:
                # Create home and applicant buttons for this category
                buttons[f"{category}_home"] = st.button(
                    label="Home", 
                    use_container_width=True,
                    key=f"{category}_button"
                )
                buttons[f"{category}_applicant"] = st.button(
                    label="Individual Applicants",
                    use_container_width=True, 
                    key=f"{category}_applicant"
                )

        st.sidebar.caption("Interviews")
        int_sch, int_app = st.sidebar.columns(2)
        interview_scheduled = int_sch.button("Scheduled", use_container_width=True)
        interview_approved = int_app.button("Approved", use_container_width=True)
        st.sidebar.caption("Applicants") 
        acc, rej = st.sidebar.columns(2)
        accepted = acc.button("Accepted", use_container_width=True)
        rejected = rej.button("Rejected", use_container_width=True)

        ##################################################### Named Categories #####################################################
        # Handle button clicks
        for category, data in st.session_state["current_session_data"]["category_data"].items():
            if buttons[f"{category}_home"]:
                st.session_state["on_page"] = f"{category.upper()}_home"
                break
            elif buttons[f"{category}_applicant"]:
                st.session_state["on_page"] = category.upper()
                break
        else:
            if accepted:
                st.session_state["on_page"] = "Accepted"
            elif rejected:
                st.session_state["on_page"] = "Rejected"
            elif interview_scheduled:
                st.session_state["on_page"] = "Scheduled"
            elif interview_approved:
                st.session_state["on_page"] = "Approved"




    st.sidebar.divider()
    st.sidebar.caption("HR")
    if st.sidebar.button(label="Session Management"):
        st.session_state["on_page"] = "HR"
    if st.sidebar.button(label="Update Data"):
        st.session_state["on_page"] = "Updater"

    ##################################################### Named Categories #####################################################
    # Handle page navigation dynamically
    if st.session_state["on_page"] is not None:
        if st.session_state["on_page"].endswith("_home"):
            # Handle analytics home pages
            analytics_home(category=st.session_state["on_page"][:-5].lower())
        elif "current_session_data" in st.session_state and st.session_state["on_page"] in [cat.upper() for cat in st.session_state["current_session_data"]["category_data"].keys()]:
            # Handle individual applicant pages
            applicants_page(category=st.session_state["on_page"][:-5].lower())
        else:
            # Handle other pages
            match st.session_state["on_page"]:
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

else:
    auth_page()