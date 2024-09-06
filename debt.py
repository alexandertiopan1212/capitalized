import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.express as px
from sidebar import render_page_based_on_sidebar

# Define the debt page
def debt_page():
    render_page_based_on_sidebar()

    st.title("Debt")
    st.write("This is the Debt page.")
    
    st.subheader("Bond Valuation")

    # Arrange Par Value and Purchase Price horizontally
    col1, col2 = st.columns(2)
    with col1:
        par_value = st.number_input("Par Value (IDR)", value=1000000000.00, step=1000000.0)
    with col2:
        purchase_price = st.number_input("Purchase Price (IDR)", value=700000000.00, step=1000000.0)
    
    # Arrange Coupon Rate and Coupon Frequency horizontally
    col3, col4 = st.columns(2)
    with col3:
        coupon_rate = st.number_input("Coupon Rate (%)", value=15.0, step=0.1) / 100
    with col4:
        coupon_frequency_options = {'Annual': 1, 'Semi-Annual': 2, 'Quarterly': 4, 'Monthly': 12}
        coupon_freq_label = st.selectbox("Coupon Frequency", options=list(coupon_frequency_options.keys()), index=2)
        coupon_frequency = coupon_frequency_options[coupon_freq_label]

    # Arrange Tenor and Maturity Date horizontally
    col5, col6 = st.columns(2)
    with col5:
        tenor_years = st.number_input("Tenor (years)", value=5)
    with col6:
        maturity_date = st.date_input("Maturity Date", value=datetime(2028, 12, 31))

    # Arrange Government Bond Yield and Spread horizontally
    col7, col8 = st.columns(2)
    with col7:
        gov_bond_yield = st.number_input("5-Year Government Bond Yield (%)", value=6.3, step=0.1) / 100
    with col8:
        spread = st.number_input("Spread (%)", value=3.0, step=0.1) / 100

    # Arrange Market Yield, Investment Date, and Issuance Date horizontally
    col9, col10, col11 = st.columns(3)
    with col9:
        market_yield = st.number_input("Market Yield (%)", value=9.3, step=0.1) / 100
    with col10:
        investment_date = st.date_input("Investment Date", value=datetime(2024, 1, 5))
    with col11:
        issuance_date = st.date_input("Issuance Date", value=datetime(2024, 1, 1))

    # Calculate bond valuation when the user clicks the button
    if st.button("Calculate Bond Value"):
        # Generate the schedule of coupon dates and cash flows
        coupon_dates = pd.date_range(start=issuance_date, end=maturity_date, freq=pd.DateOffset(months=12 // coupon_frequency))
        cash_flow_schedule = pd.DataFrame({'Date': coupon_dates})
        cash_flow_schedule['Period'] = np.arange(1, len(coupon_dates) + 1)

        # Compute Coupon Payment
        coupon_payment = (par_value * coupon_rate) / coupon_frequency
        cash_flow_schedule['Coupon Payment'] = coupon_payment

        # Add principal repayment at maturity
        cash_flow_schedule.loc[cash_flow_schedule.index[-1], 'Principal Payment'] = par_value
        cash_flow_schedule['Principal Payment'] = cash_flow_schedule['Principal Payment'].fillna(0)

        # Compute the total cash flow for each period
        cash_flow_schedule['Total Cash Flow'] = cash_flow_schedule['Coupon Payment'] + cash_flow_schedule['Principal Payment']

        # Calculate present value of each cash flow
        discount_factors = [(1 + market_yield / coupon_frequency) ** -period for period in cash_flow_schedule['Period']]
        cash_flow_schedule['Present Value of Cash Flows'] = cash_flow_schedule['Total Cash Flow'] * discount_factors

        # Display only Date as columns and relevant values under them
        bond_values = pd.DataFrame({
            'Coupon Payment': cash_flow_schedule['Coupon Payment'].values,
            'Principal Payment': cash_flow_schedule['Principal Payment'].values,
            'Total Cash Flow': cash_flow_schedule['Total Cash Flow'].values,
            'Present Value of Cash Flows': cash_flow_schedule['Present Value of Cash Flows'].values
        }).T  # Transpose to make rows as "Coupon Payment", "Principal Payment", etc.

        bond_values.columns = [date.strftime("%Y-%m-%d") for date in cash_flow_schedule['Date']]  # Set columns as dates

        # Display the bond values table with only date columns
        st.write("### Cash Flow Schedule (Date Column-Based)")
        st.dataframe(bond_values.style.format("{:,.2f}"))

        # Calculate bond price
        bond_price = cash_flow_schedule['Present Value of Cash Flows'].sum()
        st.write(f"### The calculated bond price is: **IDR {bond_price:,.2f}**")

        # Visualization of Cash Flow Schedule using Plotly Bar Graph
        st.subheader("Cash Flow and Present Value Over Time")
        fig = px.bar(cash_flow_schedule, x='Date', y=['Coupon Payment', 'Principal Payment', 'Total Cash Flow', 'Present Value of Cash Flows'],
                      title="Cash Flow and Present Value of Cash Flows Over Time", barmode='group')
        
        # Display the bar chart
        st.plotly_chart(fig)

# Main entry point for the Streamlit application
if __name__ == "__main__":
    debt_page()
