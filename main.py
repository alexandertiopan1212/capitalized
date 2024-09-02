import streamlit as st
from login import login_page
from request_demo import demo_page
from dashboard import dashboard_page
from valuation import valuation_page


# Initialize session state to manage page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Functions to switch pages
def navigate_to_demo():
    st.session_state.page = 'demo'

def navigate_to_login():
    st.session_state.page = 'login'

def navigate_to_dashboard():
    st.session_state.page = 'dashboard'

def navigate_to_valuation():
    st.session_state.page = 'valuation'

# Render the correct page based on session state
if st.session_state.page == 'login':
    login_page(navigate_to_demo, navigate_to_dashboard)
elif st.session_state.page == 'demo':
    demo_page(navigate_to_login)
elif st.session_state.page == 'dashboard':
    dashboard_page(navigate_to_login, navigate_to_valuation)
elif st.session_state.page == 'valuation':
    valuation_page()
