import streamlit as st
from login import login_page
from request_demo import demo_page
from dashboard import dashboard_page
from equities import equities_page
from option import option_page
from debt import debt_page
from portfolio import portfolio_page
from administrator import administrator_page
from guidelines import guidelines_page
from settings import settings_page

def main():

    # Set full-width layout for the entire app
    st.set_page_config(layout="wide")

    # Initialize session state for page navigation if it doesn't already exist
    if 'page' not in st.session_state:
        query_params = st.query_params  # Access query params from URL
        if 'page' in query_params:
            st.session_state.page = query_params['page']
        else:
            st.session_state.page = 'login'  # Default to the login page

    # Navigation functions to switch between pages
    def navigate_to_demo():
        """
        Switch the current page to the demo page.
        """
        st.session_state.page = 'demo'
        st.query_params.from_dict({'page': 'demo'})  # Update query params

    def navigate_to_dashboard():
        """
        Switch the current page to the dashboard page.
        """
        st.session_state.page = 'dashboard'
        st.query_params.from_dict({'page': 'dashboard'})  # Update query params

    def navigate_to_login():
        """
        Switch the current page back to the login page.
        """
        st.session_state.page = 'login'
        st.query_params.from_dict({'page': 'login'})  # Update query params

    def navigate_to_equities():
        """
        Switch the current page the equities page.
        """
        st.session_state.page = 'equities'
        st.query_params.from_dict({'page': 'equities'})  # Update query params

    def navigate_to_debt():
        """
        Switch the current page the debt page.
        """
        st.session_state.page = 'debt'
        st.query_params.from_dict({'page': 'debt'})  # Update query params

    # Page routing logic based on session state
    if st.session_state.page == 'login':
        login_page(navigate_to_demo, navigate_to_dashboard)

    elif st.session_state.page == 'dashboard':
        dashboard_page()

    elif st.session_state.page == 'demo':
        demo_page(navigate_to_login)

    elif st.session_state.page == 'equities':
        equities_page()

    elif st.session_state.page == 'option':
        option_page()

    elif st.session_state.page == 'debt':
        debt_page()

# Main application logic
if __name__ == "__main__":
    main()