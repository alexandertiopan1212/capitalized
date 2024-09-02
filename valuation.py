import streamlit as st
import pandas as pd
import numpy as np
import math
import scipy.stats as stats

# Import functions from valuation_gen_break_table.py
from valuation_gen_break_table import (
    generate_break_table,
    generate_break_table_percent,
    generate_break_table_bs,
    generate_option_allocation_table,
    calculate_break_table_ds,
    calculate_estimated_volatility,
    calculate_estimated_DLOM,
    calculate_fair_value
)

# Set the page configuration
st.set_page_config(layout="wide")

def valuation_page():
    st.title("Valuation")

    # Sidebar for navigation
    st.sidebar.title("Capitalized")
        
    sidebar_dashboard = st.sidebar.selectbox("Dashboard", 
                                    ["Select Dashboard", "Dashboard"])
    
    sidebar_valuation = st.sidebar.selectbox("Valuation", 
                                    ["Select Valuation", "Equities", "Debt", "Option"])
    
    sidebar_portfolio = st.sidebar.selectbox("Portfolio", 
                                    ["Select Portfolio", "Portfolio"])
    
    sidebar_others = st.sidebar.selectbox("Help & Settings", 
                                    ["Select Help & Settings", "Administrator", "Guidelines", "Settings"])

    # Initialize the data
    data = {
        "Security": ["B2", "Series B", "Series A", "Series Seed", "ESOP", "Ordinaries"],
        "Entry date": ["", "", "", "", "", ""],
        "Shares Outstanding": [26023, 70202, 42970, 11760, 15442, 82684],
        "Percentage": ["10.4%", "28.2%", "17.3%", "4.7%", "6.2%", "33.2%"],
        "Seniority": [1, 2, 3, 4, 5, 5],
        "Issue Price (USD)": [336.24, 321.83, 152.43, 42.52, 0.00, 0.00],
        "Liquidation Preference": ["1.0x", "1.0x", "1.0x", "1.0x", "", ""],
        "Participating": ["No", "No", "No", "No", "", ""],
        "Dividend": ["0%", "0%", "0%", "0%", "", ""],
    }

    df = pd.DataFrame(data)

    # Initialize session state for inputs if not already initialized
    if 'df' not in st.session_state:
        st.session_state.df = df
    
    if 'equity_value' not in st.session_state:
        st.session_state.equity_value = 73659791.0  # Cast to float for consistency
        
    if 'volatility' not in st.session_state:
        st.session_state.volatility = 0.6

    if 'time_to_liquidity' not in st.session_state:
        st.session_state.time_to_liquidity = 2.0  # Cast to float for consistency

    if 'risk_free_rate' not in st.session_state:
        st.session_state.risk_free_rate = 0.0503

    if 'dividend_yield' not in st.session_state:
        st.session_state.dividend_yield = 0.0  # Cast to float for consistency

    st.subheader("Input Parameters")

    # Use st.columns to align the inputs horizontally
    cols = st.columns(5)
    st.session_state.equity_value = cols[0].number_input("Equity Value", value=float(st.session_state.equity_value))
    st.session_state.volatility = cols[1].number_input("Volatility", value=float(st.session_state.volatility), min_value=0.0, max_value=1.0, step=0.01)
    st.session_state.time_to_liquidity = cols[2].number_input("Time to Liquidity (years)", value=float(st.session_state.time_to_liquidity))
    st.session_state.risk_free_rate = cols[3].number_input("Risk-Free Rate", value=float(st.session_state.risk_free_rate), min_value=0.0, max_value=1.0, step=0.001)
    st.session_state.dividend_yield = cols[4].number_input("Dividend Yield", value=float(st.session_state.dividend_yield), min_value=0.0, max_value=1.0, step=0.001)

    st.subheader("Interactive Capitalization Table Input")

    # Editable table with full-width
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

    # Proceed button to display the final table and generate other tables
    if st.button("Proceed"):
        with st.spinner("Processing... Please wait."):
            st.subheader("Final Edited Capitalization Table")
            st.dataframe(st.session_state.df, use_container_width=True)

            # Generate Break Table
            break_table = generate_break_table(st.session_state.df)
            st.session_state.break_table = break_table
            st.subheader("Generated Break Table")
            st.dataframe(st.session_state.break_table, use_container_width=True)

            # Generate Break Table Percentages
            break_table_percent = generate_break_table_percent(st.session_state.df, break_table)
            st.session_state.break_table_percent = break_table_percent
            st.subheader("Generated Break Table Percentages")
            st.dataframe(st.session_state.break_table_percent, use_container_width=True)

            # Generate Break Table Black-Scholes
            break_table_bs = generate_break_table_bs(
                st.session_state.break_table_percent, 
                st.session_state.equity_value, 
                st.session_state.risk_free_rate, 
                st.session_state.volatility, 
                st.session_state.time_to_liquidity, 
                st.session_state.dividend_yield
            )
            st.session_state.break_table_bs = break_table_bs
            st.subheader("Generated Break Table Black-Scholes")
            st.dataframe(st.session_state.break_table_bs, use_container_width=True)

            # Generate Option Allocation Table
            break_table_oa = generate_option_allocation_table(
                st.session_state.break_table, 
                st.session_state.break_table_bs, 
                st.session_state.break_table_percent, 
                st.session_state.df
            )
            st.session_state.break_table_oa = break_table_oa
            st.subheader("Generated Option Allocation Table")
            st.dataframe(st.session_state.break_table_oa, use_container_width=True)

            # Calculate Delta Spread Table
            break_table_ds = calculate_break_table_ds(
                st.session_state.break_table_bs, 
                st.session_state.break_table_percent, 
                st.session_state.df
            )
            st.session_state.break_table_ds = break_table_ds
            st.subheader("Calculated Delta Spread Table")
            st.dataframe(st.session_state.break_table_ds, use_container_width=True)

            # Calculate Estimated Volatility
            estimated_volatility = calculate_estimated_volatility(
                st.session_state.df, 
                st.session_state.break_table_ds, 
                st.session_state.break_table_oa, 
                st.session_state.equity_value, 
                st.session_state.volatility
            )
            st.session_state.estimated_volatility = estimated_volatility
            st.subheader("Estimated Volatility for Each Class")
            st.dataframe(st.session_state.estimated_volatility, use_container_width=True)

            # Calculate Estimated DLOM
            estimated_DLOM = calculate_estimated_DLOM(
                st.session_state.df, 
                st.session_state.break_table_oa, 
                st.session_state.estimated_volatility, 
                st.session_state.time_to_liquidity, 
                st.session_state.dividend_yield, 
                st.session_state.risk_free_rate
            )
            st.session_state.estimated_DLOM = estimated_DLOM
            st.subheader("Estimated DLOM for Each Class")
            st.dataframe(st.session_state.estimated_DLOM, use_container_width=True)

            # Calculate Fair Value
            fair_value = calculate_fair_value(
                st.session_state.df, 
                st.session_state.break_table_oa
            )
            st.session_state.fair_value = fair_value
            st.subheader("Calculated Fair Value")
            st.dataframe(st.session_state.fair_value, use_container_width=True)

# To display the valuation page
if __name__ == "__main__":
    valuation_page()
