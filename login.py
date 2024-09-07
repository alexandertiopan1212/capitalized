import streamlit as st

# Style related functionality
def apply_button_styles():
    """
    Apply custom button styles to the Streamlit buttons, including colors, hover effects, and link styling.
    """
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #000000;
            color: white;
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: none;
        }
        div.stButton > button:first-child:hover {
            background-color: #444444;
            color: white;
        }
        div.stButton > button:nth-child(3) {
            background: none;
            border: none;
            color: #007bff;
            text-decoration: underline;
            padding-left: 0;
            font-size: 0.8em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# UI related functionality
def display_title(title="Capitalized"):
    """
    Display the title of the login page. Default is 'Capitalized'.
    Parameters:
    - title: Customizable title for the page.
    """
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)


def display_login_form():
    """
    Display the login form with email and password fields.
    Returns the user's email, password, and the checkbox agreement status.
    """
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    agree = st.checkbox(
        "By clicking the Log in button, you agree to Capitalized's Terms of Service and Privacy Policy."
    )
    return email, password, agree


def display_forgot_password_link():
    """
    Display a 'Forgot Password?' link under the login form.
    """
    st.markdown(
        "<a href='#' style='text-decoration: none; color: #007bff;'>Forget Password?</a>",
        unsafe_allow_html=True,
    )


def handle_login(email, password, agree, navigate_to_dashboard):
    """
    Handle the login process when the user clicks the login button.
    Checks if the terms are agreed upon, and if valid, logs in the user and redirects to the dashboard.
    """
    if not agree:
        st.warning("You must agree to the terms and conditions to log in.")
    else:
        st.session_state.logged_in = True
        navigate_to_dashboard()


# Main logic for the login page
def login_page(navigate_to_demo, navigate_to_dashboard):
    """
    Main function to display the login page and handle login logic.
    Parameters:
    - navigate_to_demo: Function to navigate to the demo page.
    - navigate_to_dashboard: Function to navigate to the dashboard page.
    """

    # Set up initial session state for login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Apply custom styles
    apply_button_styles()

    # If user is not logged in, show the login page
    if not st.session_state.logged_in and st.session_state.page == "login":
        display_title()

        # Center the form
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            email, password, agree = display_login_form()

            if st.button("Login"):
                handle_login(email, password, agree, navigate_to_dashboard)

            display_forgot_password_link()

            if st.button("Request Demo", key="demo_button"):
                navigate_to_demo()

    # If the user is logged in, redirect to the respective pages
    elif st.session_state.logged_in:
        if st.session_state.page == "dashboard":
            navigate_to_dashboard()
        elif st.session_state.page == "demo":
            navigate_to_demo()


# Example usage of the refactored login_page function
if __name__ == "__main__":

    def navigate_to_demo():
        st.session_state.page = "demo"
        st.query_params.from_dict({"page": "demo"})
        st.write("Navigating to Demo...")

    def navigate_to_dashboard():
        st.session_state.page = "dashboard"
        st.query_params.from_dict({"page": "dashboard"})
        st.write("Navigating to Dashboard...")

    # Initialize session state for page navigation
    if "page" not in st.session_state:
        st.session_state.page = "login"

    login_page(navigate_to_demo, navigate_to_dashboard)
