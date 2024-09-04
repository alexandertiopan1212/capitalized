import streamlit as st

def apply_custom_styles():
    """
    Apply custom styles to buttons and links for the login page.
    Styles include button colors, hover effects, and link styling.
    """
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #000000;
            color: white;
            width: 100%;  /* Full width for login buttons */
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
        unsafe_allow_html=True
    )

def display_title():
    """
    Display the main title of the application.
    The title is centered and can be customized as needed.
    """
    st.markdown("<h1 style='text-align: center;'>Capitalized</h1>", unsafe_allow_html=True)

def display_login_form():
    """
    Display the login form consisting of:
    - Email input
    - Password input (masked)
    - Checkbox for agreeing to terms of service
    Returns:
    - email: The email input from the user.
    - password: The password input from the user.
    - agree: Boolean indicating if the terms checkbox was selected.
    """
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    agree = st.checkbox("By clicking the Log in button, you agree to Capitalized's Terms of Service and Privacy Policy.")
    return email, password, agree

def login_page(navigate_to_demo, navigate_to_dashboard):
    """
    Main function to display the login page and handle login logic.
    When successfully logged in, the user is redirected to the dashboard.
    
    Parameters:
    - navigate_to_demo: Function to call when the "Request Demo" button is clicked.
    - navigate_to_dashboard: Function to call when login is successful.
    """

    # Initialize session state for login if not already set
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Default to not logged in

    # Show the login page if the user is not logged in and on the login page
    if not st.session_state.logged_in and st.session_state.page == 'login':

        # Apply custom styles for the login page
        apply_custom_styles()

        # Display the title of the application
        display_title()

        # Center the login form using columns, with the form taking up 1/5 of the page width
        col1, col2, col3 = st.columns([2, 1, 2])  # col2 is the center column

        with col2:
            # Display the login form and retrieve user inputs
            email, password, agree = display_login_form()

            # Handle the login button click event
            if st.button("Login"):
                if not agree:
                    st.warning("You must agree to the terms and conditions to log in.")
                else:
                    # Set the session state to logged in
                    st.session_state.logged_in = True
                    st.session_state.page = 'dashboard'  # Navigate to the dashboard
                    st.query_params.from_dict({'page': 'dashboard'})  # Update query params

            # Display a "Forget Password" link
            st.markdown("<a href='#' style='text-decoration: none; color: #007bff;'>Forget Password?</a>", unsafe_allow_html=True)

            # Handle the "Request Demo" button click event
            if st.button("Request Demo", key="demo_button"):
                st.session_state.logged_in = True
                st.session_state.page = 'demo'  # Navigate to the demo page
                st.query_params.from_dict({'page': 'demo'})  # Update query params

    else:
        # If logged in, redirect the user to the appropriate page
        if st.session_state.page == 'dashboard':
            navigate_to_dashboard()
        elif st.session_state.page == 'demo':
            navigate_to_demo()

# Main application logic
if __name__ == "__main__":
    login_page()