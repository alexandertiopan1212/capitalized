import streamlit as st

def login_page(navigate_to_demo, navigate_to_dashboard):
    # st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Capitalized</h1>", unsafe_allow_html=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    agree = st.checkbox("By clicking the Log in button, you agree to Capitalized's Terms of Service and Privacy Policy.")
    
    if st.button("Login"):
        if not agree:
            st.warning("You must agree to the terms and conditions to log in.")
        else:
            st.success("Logged in successfully!")
            navigate_to_dashboard()
    
    st.markdown("<a href='#' style='text-decoration: none; color: #007bff;'>Forget Password?</a>", unsafe_allow_html=True)
    
    # Request Demo clickable text link
    if st.button("Request Demo", key="demo_button"):
        navigate_to_demo()

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
        unsafe_allow_html=True
    )
