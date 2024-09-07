import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.express as px
from sidebar import render_page_based_on_sidebar

# Modular function to handle user inputs
def get_bond_inputs():
    """
    Display input fields for bond valuation parameters and return the inputs.
    """
    # Par Value and Purchase Price
    col1, col2 = st.columns(2)
    with col1:
        par_value = st.number_input(
            "Par Value (IDR)", value=1000000000.00, step=1000000.0
        )
    with col2:
        purchase_price = st.number_input(
            "Purchase Price (IDR)", value=700000000.00, step=1000000.0
        )

    # Coupon Rate and Frequency
    col3, col4 = st.columns(2)
    with col3:
        coupon_rate = st.number_input("Coupon Rate (%)", value=15.0, step=0.1) / 100
    with col4:
        coupon_frequency_options = {
            "Annual": 1,
            "Semi-Annual": 2,
            "Quarterly": 4,
            "Monthly": 12,
        }
        coupon_freq_label = st.selectbox(
            "Coupon Frequency", options=list(coupon_frequency_options.keys()), index=2
        )
        coupon_frequency = coupon_frequency_options[coupon_freq_label]

    # Tenor and Maturity Date
    col5, col6 = st.columns(2)
    with col5:
        tenor_years = st.number_input("Tenor (years)", value=5)
    with col6:
        maturity_date = st.date_input("Maturity Date", value=datetime(2028, 12, 31))

    # Government Bond Yield and Spread
    col7, col8 = st.columns(2)
    with col7:
        gov_bond_yield = (
            st.number_input("5-Year Government Bond Yield (%)", value=6.3, step=0.1)
            / 100
        )
    with col8:
        spread = st.number_input("Spread (%)", value=3.0, step=0.1) / 100

    # Market Yield, Investment Date, and Issuance Date
    col9, col10, col11 = st.columns(3)
    with col9:
        market_yield = st.number_input("Market Yield (%)", value=9.3, step=0.1) / 100
    with col10:
        investment_date = st.date_input("Investment Date", value=datetime(2024, 1, 5))
    with col11:
        issuance_date = st.date_input("Issuance Date", value=datetime(2024, 1, 1))

    return {
        "par_value": par_value,
        "purchase_price": purchase_price,
        "coupon_rate": coupon_rate,
        "coupon_frequency": coupon_frequency,
        "tenor_years": tenor_years,
        "maturity_date": maturity_date,
        "gov_bond_yield": gov_bond_yield,
        "spread": spread,
        "market_yield": market_yield,
        "investment_date": investment_date,
        "issuance_date": issuance_date,
    }


# Modular function to calculate bond value
def calculate_bond_value(inputs):
    """
    Calculate the bond valuation based on the input parameters.
    """
    par_value = inputs["par_value"]
    coupon_rate = inputs["coupon_rate"]
    coupon_frequency = inputs["coupon_frequency"]
    market_yield = inputs["market_yield"]
    issuance_date = inputs["issuance_date"]
    maturity_date = inputs["maturity_date"]

    # Generate coupon dates
    coupon_dates = pd.date_range(
        start=issuance_date,
        end=maturity_date,
        freq=pd.DateOffset(months=12 // coupon_frequency),
    )
    cash_flow_schedule = pd.DataFrame({"Date": coupon_dates})
    cash_flow_schedule["Period"] = np.arange(1, len(coupon_dates) + 1)

    # Calculate coupon payment
    coupon_payment = (par_value * coupon_rate) / coupon_frequency
    cash_flow_schedule["Coupon Payment"] = coupon_payment

    # Add principal repayment at maturity
    cash_flow_schedule.loc[
        cash_flow_schedule.index[-1], "Principal Payment"
    ] = par_value
    cash_flow_schedule["Principal Payment"] = cash_flow_schedule[
        "Principal Payment"
    ].fillna(0)

    # Calculate total cash flows
    cash_flow_schedule["Total Cash Flow"] = (
        cash_flow_schedule["Coupon Payment"] + cash_flow_schedule["Principal Payment"]
    )

    # Calculate present value of each cash flow
    discount_factors = [
        (1 + market_yield / coupon_frequency) ** -period
        for period in cash_flow_schedule["Period"]
    ]
    cash_flow_schedule["Present Value of Cash Flows"] = (
        cash_flow_schedule["Total Cash Flow"] * discount_factors
    )

    # Calculate bond price
    bond_price = cash_flow_schedule["Present Value of Cash Flows"].sum()

    return cash_flow_schedule, bond_price


# Modular function to display results
def display_results(cash_flow_schedule, bond_price):
    """
    Display the bond valuation results in a table and chart.
    """
    # Create a table of the bond values
    bond_values = pd.DataFrame(
        {
            "Coupon Payment": cash_flow_schedule["Coupon Payment"].values,
            "Principal Payment": cash_flow_schedule["Principal Payment"].values,
            "Total Cash Flow": cash_flow_schedule["Total Cash Flow"].values,
            "Present Value of Cash Flows": cash_flow_schedule[
                "Present Value of Cash Flows"
            ].values,
        }
    ).T  # Transpose for better display

    bond_values.columns = [
        date.strftime("%Y-%m-%d") for date in cash_flow_schedule["Date"]
    ]  # Set columns as dates
    st.write("### Cash Flow Schedule (Date Column-Based)")
    st.dataframe(bond_values.style.format("{:,.2f}"))

    # Display bond price
    st.write(f"### The calculated bond price is: **IDR {bond_price:,.2f}**")

    # Visualize Cash Flow Schedule
    st.subheader("Cash Flow and Present Value Over Time")
    fig = px.bar(
        cash_flow_schedule,
        x="Date",
        y=[
            "Coupon Payment",
            "Principal Payment",
            "Total Cash Flow",
            "Present Value of Cash Flows",
        ],
        title="Cash Flow and Present Value of Cash Flows Over Time",
        barmode="group",
    )
    st.plotly_chart(fig)


# Main debt page function
def debt_page():
    render_page_based_on_sidebar()
    st.title("Debt - Bond Valuation")
    st.subheader("Bond Valuation")

    # Get user inputs
    bond_inputs = get_bond_inputs()

    # Calculate bond value when the button is clicked
    if st.button("Calculate Bond Value"):
        cash_flow_schedule, bond_price = calculate_bond_value(bond_inputs)
        display_results(cash_flow_schedule, bond_price)


# Main entry point for the Streamlit application
if __name__ == "__main__":
    debt_page()
