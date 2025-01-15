import streamlit as st


# Define custom CSS styles for the sidebar buttons
def sidebar_button_style():
    st.markdown("""
        <style>
        /* Set sidebar button styles */
        .stButton button {
            display: block;
            padding: 10px;
            margin: 0px; /* No margin between buttons */
            width: 100%;
            text-align: left;
            background-color: transparent;
            color: black;
            font-size: 10px; /* Adjust the font size to match the sidebar menu */
            font-family: 'Source Sans Pro', sans-serif; /* Match font family */
            border: 1px solid #ddd; /* Border for buttons */
            border-radius: 5px; /* Optional: round the edges */
        }
        .stButton button:hover {
            background-color: #f0f0f0;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)

def render_page_based_on_sidebar():
    # Sidebar title
    st.sidebar.title("Capitalized")

    # Add CSS to style the buttons
    sidebar_button_style()

    # Expanders with styled buttons
    with st.sidebar.expander("Dashboard"):
        if st.button("Dashboard", key="dashboard"):
            st.session_state.page = "dashboard"

    with st.sidebar.expander("Valuation"):
        if st.button("Equities Valuation", key="equities"):
            st.session_state.page = "equities"
        if st.button("Debt Valuation", key="debt"):
            st.session_state.page = "debt"
        if st.button("Option Valuation", key="option"):
            st.session_state.page = "option"

    with st.sidebar.expander("Financial Modelling"):
        if st.button("Project Financing", key="project_financing"):
            st.session_state.page = "project_financing"
        if st.button("Scenario Analysis", key="scenario_analysis"):
            st.session_state.page = "scenario_analysis"

    with st.sidebar.expander("Portfolio"):
        if st.button("Portfolio", key="portfolio"):
            st.session_state.page = "portfolio"

    with st.sidebar.expander("Decision Flow"):
        if st.button("Decision Flow", key="decision_flow"):
            st.session_state.page = "decision_flow"

    with st.sidebar.expander("Help & Settings"):
        if st.button("Administrator", key="administrator"):
            st.session_state.page = "administrator"
        if st.button("Guidelines", key="guidelines"):
            st.session_state.page = "guidelines"
        if st.button("Settings", key="settings"):
            st.session_state.page = "settings"

    # Render the content based on the selected page
    if 'page' in st.session_state:
        st.session_state.page == "login"

# Main application logic
if __name__ == "__main__":
    render_page_based_on_sidebar()
