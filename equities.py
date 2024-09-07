import streamlit as st
from sidebar import render_page_based_on_sidebar
from equities_income import equities_income
from equities_market import equities_market


def display_valuation_options():
    approach_option = st.selectbox(
        "Select Valuation Approach", options=["Market", "Income"], index=0
    )

    if approach_option == "Market":
        equities_market()

    elif approach_option == "Income":
        equities_income()


# Main function to render the equity valuation page
def equities_page():
    render_page_based_on_sidebar()
    display_valuation_options()


# Run the application
if __name__ == "__main__":
    equities_page()
