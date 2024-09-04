import streamlit as st
import pandas as pd
import numpy as np
import math
import scipy.stats as stats
from sidebar import render_page_based_on_sidebar

# Import custom functions from equity_market_approach_function.py
from equity_market_approach_func import (
    generate_break_table,
    generate_break_table_percent,
    generate_break_table_bs,
    generate_option_allocation_table,
    calculate_break_table_ds,
    calculate_estimated_volatility,
    calculate_estimated_DLOM,
    calculate_fair_value
)

def format_value(x):
    """
    Format numeric values based on their type and value.
    Apply different formatting for large and small numbers.
    Skip non-numeric values.
    """
    if isinstance(x, (int, float)):
        return f"{x:,.2f}" if x < 1000 else f"{x:,.0f}"
    return x  # Return the value as-is if it's not a number

# Set the page configuration for a wide layout
# st.set_page_config(layout="wide")

def equities_page():
    """
    Main function to display the Equity Valuation page.
    Handles input parameters, interactive tables, and calculations.
    """

    # Set the title of the page
    st.title("Equity Valuation")

    # Render the page based on the sidebar selection
    render_page_based_on_sidebar()

    # Conditional display based on the sidebar selections
    if st.session_state.page == 'equities':

        # Initialize the data for the table
        data = {
            'Security': ['B2', 'Series B', 'Series A', 'Series Seed', 'ESOP', 'Ordinaries'],
            'Entry date': ['', '', '', '', '', ''],
            'Shares Outstanding': [26023, 70202, 42970, 11760, 15442, 82684],
            'Percentage': ['10.4%', '28.2%', '17.3%', '4.7%', '6.2%', '33.2%'],
            'Seniority': [1, 2, 3, 4, np.nan, np.nan],
            'Issue Price (USD)': [336.24, 321.83, 152.43, 42.52, 0, 0],
            'Liquidation Preference': [1, 1, 1, 1, np.nan, np.nan],
            'Participating': ['No', 'No', 'No', 'No', '', ''],
            'Dividend': ['0%', '0%', '0%', '0%', '', '']
        }

        df = pd.DataFrame(data)

        # Initialize session state for input fields if not already initialized
        if 'df' not in st.session_state:
            st.session_state.df = df
        if 'equity_value' not in st.session_state:
            st.session_state.equity_value = 73659791.0  # Default equity value
        if 'volatility' not in st.session_state:
            st.session_state.volatility = 0.6  # Default volatility
        if 'time_to_liquidity' not in st.session_state:
            st.session_state.time_to_liquidity = 2.0  # Default time to liquidity in years
        if 'risk_free_rate' not in st.session_state:
            st.session_state.risk_free_rate = 0.0503  # Default risk-free rate
        if 'dividend_yield' not in st.session_state:
            st.session_state.dividend_yield = 0.0  # Default dividend yield

        # Display input parameters section
        st.subheader("Input Parameters")

        # Arrange input fields horizontally using st.columns
        cols = st.columns(5)
        st.session_state.equity_value = cols[0].number_input("Equity Value", value=float(st.session_state.equity_value))
        st.session_state.volatility = cols[1].number_input("Volatility", value=float(st.session_state.volatility), min_value=0.0, max_value=1.0, step=0.01)
        st.session_state.time_to_liquidity = cols[2].number_input("Time to Liquidity (years)", value=float(st.session_state.time_to_liquidity))
        st.session_state.risk_free_rate = cols[3].number_input("Risk-Free Rate", value=float(st.session_state.risk_free_rate), min_value=0.0, max_value=1.0, step=0.001)
        st.session_state.dividend_yield = cols[4].number_input("Dividend Yield", value=float(st.session_state.dividend_yield), min_value=0.0, max_value=1.0, step=0.001)

        # Display interactive capitalization table input section
        st.subheader("Interactive Capitalization Table Input")
        st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

        # Proceed button to generate the necessary tables and calculations
        if st.button("Proceed"):
            with st.spinner("Processing... Please wait."):
                # Display the final edited capitalization table
                st.subheader("Final Edited Capitalization Table")
                st.dataframe(st.session_state.df.applymap(format_value), use_container_width=True)

                # Generate and display the Break Table
                break_table = generate_break_table(st.session_state.df)
                st.session_state.break_table = break_table
                st.subheader("Generated Break Table")
                st.dataframe(st.session_state.break_table.applymap(format_value), use_container_width=True)

                # Generate and display the Break Table Percentages
                break_table_percent = generate_break_table_percent(st.session_state.df, break_table)
                st.session_state.break_table_percent = break_table_percent
                st.subheader("Generated Break Table Percentages")
                st.dataframe(st.session_state.break_table_percent, use_container_width=True)

                # Generate and display the Break Table using Black-Scholes model
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
                st.dataframe(st.session_state.break_table_bs.applymap(format_value), use_container_width=True)

                # Generate and display the Option Allocation Table
                break_table_oa = generate_option_allocation_table(
                    st.session_state.break_table, 
                    st.session_state.break_table_bs, 
                    st.session_state.break_table_percent, 
                    st.session_state.df
                )
                st.session_state.break_table_oa = break_table_oa
                st.subheader("Generated Option Allocation Table")
                st.dataframe(st.session_state.break_table_oa.applymap(format_value), use_container_width=True)

                # Calculate and display the Delta Spread Table
                break_table_ds = calculate_break_table_ds(
                    st.session_state.break_table_bs, 
                    st.session_state.break_table_percent, 
                    st.session_state.df
                )
                st.session_state.break_table_ds = break_table_ds
                st.subheader("Calculated Delta Spread Table")
                st.dataframe(st.session_state.break_table_ds, use_container_width=True)

                # Calculate and display the Estimated Volatility for each class
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

                # Calculate and display the Estimated DLOM for each class
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
                st.dataframe(st.session_state.estimated_DLOM.applymap(format_value), use_container_width=True)

                # Calculate and display the Fair Value for each class
                fair_value = calculate_fair_value(
                    st.session_state.df, 
                    st.session_state.break_table_oa
                )
                st.session_state.fair_value = fair_value
                st.subheader("Calculated Fair Value")
                st.dataframe(st.session_state.fair_value.applymap(format_value), use_container_width=True)

# Run the application
if __name__ == "__main__":
    equities_page()
