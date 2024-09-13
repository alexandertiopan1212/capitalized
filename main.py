import streamlit as st
from login import login_page
from request_demo import demo_page
from dashboard import dashboard_page
from equities import equities_page
from option import option_page
from debt import debt_page
from project_financing import project_financing_page
from portfolio import portfolio_page
from administrator import administrator_page
from guidelines import guidelines_page
from settings import settings_page

# Modular navigation logic
def set_page_config():
    """
    Configure the page layout and set default page if not in session state.
    """
    st.set_page_config(layout="wide")
    if "page" not in st.session_state:
        query_params = st.query_params.to_dict()  # Access query params as a dictionary
        st.session_state.page = query_params.get(
            "page", "login"
        )  # Default to 'login' if not set


# Navigation functions
def navigate(page_name):
    """
    Update session state and query parameters to navigate to the specified page.
    """
    st.session_state.page = page_name
    st.query_params.from_dict({"page": page_name})  # Update the query parameters


# Function to route to appropriate page
def route_page():
    """
    Render the appropriate page based on session state.
    """
    if st.session_state.page == "login":
        login_page(lambda: navigate("demo"), lambda: navigate("dashboard"))

    elif st.session_state.page == "dashboard":
        dashboard_page()

    elif st.session_state.page == "demo":
        demo_page(lambda: navigate("login"))

    elif st.session_state.page == "equities":
        equities_page()

    elif st.session_state.page == "option":
        option_page()

    elif st.session_state.page == "debt":
        debt_page()

    elif st.session_state.page == "project_financing":
        project_financing_page()

    elif st.session_state.page == "portfolio":
        portfolio_page()

    elif st.session_state.page == "administrator":
        administrator_page()

    elif st.session_state.page == "guidelines":
        guidelines_page()

    elif st.session_state.page == "settings":
        settings_page()


# Main function
def main():
    set_page_config()
    route_page()


# Entry point
if __name__ == "__main__":
    main()
