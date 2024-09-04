import streamlit as st

def demo_page(navigate_to_login):
    """
    Displays the demo request page. Users can fill in their details to request a demo.
    Provides a link to return to the login page.

    Parameters:
    - navigate_to_login: Function to navigate back to the login page.
    """

    # Display the main heading for the demo page
    st.markdown("<h1 style='text-align: left;'>Capitalized</h1>", unsafe_allow_html=True)

    # Create two columns to structure the page layout
    left_column, right_column = st.columns(2)

    # Left column content: Details about Capitalized and its services
    with left_column:
        st.markdown("<h2 style='text-align: left;'>Get demo by Capitalized</h2>", unsafe_allow_html=True)
        st.markdown("### Private and Public Companies")
        st.write("Whether you’re just starting out or running a well-established business, see how Capitalized makes managing equity a breeze.")
        
        st.markdown("### Investors and Fund Managers")
        st.write("Chat with an expert to see how Capitalized helps VCs and fund managers streamline their operations.")
        
        st.markdown("### Compensation Decision-Makers")
        st.write("Find out how Capitalized helps you attract and keep top talent with the world’s largest collection of real-time pay data.")
        
        st.markdown("### Trusted by over 40,000 Companies & Investors")
        
        # Display logos of trusted companies
        st.image([
            "https://upload.wikimedia.org/wikipedia/commons/0/0d/TBS_logo.svg",
            "https://upload.wikimedia.org/wikipedia/en/1/1a/Bank_of_America_logo.svg",
            "https://upload.wikimedia.org/wikipedia/en/thumb/8/80/KPMG_logo.svg/512px-KPMG_logo.svg.png",
            "https://upload.wikimedia.org/wikipedia/commons/0/02/Pwc-logo.svg",
            "https://upload.wikimedia.org/wikipedia/commons/7/7b/EY_logo_2019.svg",
            "https://upload.wikimedia.org/wikipedia/commons/2/23/Ecogreen_Oleochemicals_logo.png"
        ], width=100)

    # Right column content: Form for requesting a demo
    with right_column:
        st.markdown("<h2 style='text-align: left;'>Fill The Form & Get New Experience of Valuating Your Company</h2>", unsafe_allow_html=True)
        
        # Form fields for demo request
        country = st.selectbox("Where is your company headquartered?", ["Select Country", "Indonesia", "United States", "India", "Germany", "Other"])
        
        # Two-column layout for first and last name
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *")
        with col2:
            last_name = st.text_input("Last Name *")
        
        # Additional form fields
        org_name = st.text_input("Organization Name *")
        email = st.text_input("Work Email *")
        phone = st.text_input("Phone Number *")
        
        usage = st.selectbox("I will use this platform for *", ["Select Purpose", "Private Companies", "Investors", "Research and Study"])
        
        # Terms and conditions disclaimer
        st.markdown("By submitting your information, you agree to the processing of your personal data by Capitalized as described in Capitalized's [Privacy Policy](#).", unsafe_allow_html=True)

        # Custom button style with width set to one-third
        st.markdown(
            """
            <style>
            div.stButton > button {
                width: 33.33%;  /* Set the button width to one-third of the available space */
                background-color: #000000;
                color: white;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Handle the form submission for demo request
        if st.button("Request Demo"):
            st.success("Your demo request has been submitted successfully!")

        # Provide a button to navigate back to the login page
        if st.button("Back to Login"):
            # Set the session state back to login and update the query parameters
            st.session_state.page = 'login'
            st.query_params.from_dict({'page': 'login'})  # Update query parameters for login page
            navigate_to_login()  # Navigate back to the login page

# Main application logic
if __name__ == "__main__":
    demo_page()