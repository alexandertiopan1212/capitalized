import streamlit as st


def render_page_based_on_sidebar():
    # st.set_page_config(layout="wide")  # Enable full-width layout for this page
    # Sidebar for navigation
    st.sidebar.title("Capitalized")

    # Sidebar options
    sidebar_dashboard = st.sidebar.selectbox(
        "Dashboard", ["Select Dashboard", "Dashboard"]
    )
    sidebar_valuation = st.sidebar.selectbox(
        "Valuation", ["Select Valuation", "Equities", "Debt", "Option"]
    )
    sidebar_portfolio = st.sidebar.selectbox(
        "Portfolio", ["Select Portfolio", "Portfolio"]
    )
    sidebar_others = st.sidebar.selectbox(
        "Help & Settings",
        ["Select Help & Settings", "Administrator", "Guidelines", "Settings"],
    )

    # Conditional display based on the sidebar selections
    if (
        sidebar_dashboard == "Dashboard"
        and sidebar_valuation == "Select Valuation"
        and sidebar_portfolio == "Select Portfolio"
        and sidebar_others == "Select Help & Settings"
    ):
        st.session_state.page = "dashboard"
        st.query_params.from_dict({"page": "dashboard"})  # Update query params

    elif (
        sidebar_valuation == "Equities"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_portfolio == "Select Portfolio"
        and sidebar_others == "Select Help & Settings"
    ):
        st.session_state.page = "equities"
        st.query_params.from_dict({"page": "equities"})  # Update query params

    elif (
        sidebar_valuation == "Option"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_portfolio == "Select Portfolio"
        and sidebar_others == "Select Help & Settings"
    ):
        st.session_state.page = "option"
        st.query_params.from_dict({"page": "option"})  # Update query params

    elif (
        sidebar_valuation == "Debt"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_portfolio == "Select Portfolio"
        and sidebar_others == "Select Help & Settings"
    ):
        st.session_state.page = "debt"
        st.query_params.from_dict({"page": "debt"})  # Update query params

    elif (
        sidebar_portfolio == "Portfolio"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_valuation == "Select Valuation"
        and sidebar_others == "Select Help & Settings"
    ):
        st.session_state.page = "portfolio"
        st.query_params.from_dict({"page": "portfolio"})  # Update query params

    elif (
        sidebar_others == "Administrator"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_valuation == "Select Valuation"
        and sidebar_portfolio == "Select Portfolio"
    ):
        st.session_state.page = "administrator"
        st.query_params.from_dict({"page": "administrator"})  # Update query params

    elif (
        sidebar_others == "Guidelines"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_valuation == "Select Valuation"
        and sidebar_portfolio == "Select Portfolio"
    ):
        st.session_state.page = "guidelines"
        st.query_params.from_dict({"page": "guidelines"})  # Update query params

    elif (
        sidebar_others == "Settings"
        and sidebar_dashboard == "Select Dashboard"
        and sidebar_valuation == "Select Valuation"
        and sidebar_portfolio == "Select Portfolio"
    ):
        st.session_state.page = "settings"
        st.query_params.from_dict({"page": "settings"})  # Update query params

    else:
        st.write(
            "Please make a selection in one of the sidebar options to view the corresponding page."
        )


# Main application logic
if __name__ == "__main__":
    render_page_based_on_sidebar()
