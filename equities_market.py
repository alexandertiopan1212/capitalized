import streamlit as st
import pandas as pd
import numpy as np
from equities_income import equities_income
from ticker_data_processor import get_ticker_data
from bond_data_fetcher import get_bond_data
from volatility_calculator import calculate_volatility
from equities_market_function import (
    generate_break_table,
    generate_break_table_percent,
    generate_break_table_bs,
    generate_option_allocation_table,
    calculate_break_table_ds,
    calculate_estimated_volatility,
    calculate_estimated_DLOM,
    calculate_fair_value,
    format_value,
)

# Modular function to handle risk-free rate input
def handle_risk_free_rate_input():
    st.subheader("Step 1: Choose Risk-Free Rate Input Method")
    risk_free_rate_input_method = st.radio(
        "Would you like to manually input the risk-free rate or scrape the 10-year bond yield?",
        ("Manual Input", "Scrape from Web"),
    )

    if risk_free_rate_input_method == "Manual Input":
        st.session_state.risk_free_rate = st.number_input(
            "Enter risk-free rate (e.g., 0.05 for 5%)",
            value=0.0503,
            min_value=0.0,
            max_value=1.0,
            step=0.001,
        )
        st.success(
            f"Manual risk-free rate set to: {st.session_state.risk_free_rate:.2%}"
        )
    elif risk_free_rate_input_method == "Scrape from Web":
        if st.button("Get 10-Year Bond Yield"):
            with st.spinner("Processing... Please wait."):
                risk_free_rate = get_bond_data()
                if risk_free_rate is not None:
                    st.session_state.risk_free_rate = risk_free_rate
                    st.success(
                        f"Scraped 10-Year Bond Yield as Risk-Free Rate: {risk_free_rate:.2%}"
                    )


# Modular function to handle volatility input
def handle_volatility_input():
    st.subheader("Step 2: Choose Volatility Input Method")
    volatility_input_method = st.radio(
        "Would you like to manually input the volatility or calculate it from stock tickers?",
        ("Manual Input", "Calculate from Stock List"),
    )

    if volatility_input_method == "Manual Input":
        st.session_state.volatility = st.number_input(
            "Enter volatility (e.g., 0.6 for 60%)",
            value=0.6,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
        )
        st.success(f"Manual volatility set to: {st.session_state.volatility:.2f}")
    else:
        handle_ticker_input()


# Function to handle stock ticker input for volatility calculation
def handle_ticker_input():
    st.subheader("Step 2: Comparables Companies Setup")
    default_indonesian_stocks = ["BBCA.JK", "TLKM.JK", "ASII.JK", "BMRI.JK", "UNVR.JK"]

    if "stock_df" not in st.session_state:
        st.session_state.stock_df = pd.DataFrame(
            {"Stock Ticker": default_indonesian_stocks}
        )

    st.write("Modify stock tickers by adding or removing rows below:")
    st.session_state.stock_df = st.data_editor(
        st.session_state.stock_df, num_rows="dynamic"
    )

    ticker_list = st.session_state.stock_df["Stock Ticker"].tolist()

    if st.button("Calculate Volatility & Market Multiplier"):
        data_ticker = get_ticker_data(ticker_list)
        if data_ticker is not None:
            st.session_state.data_ticker_df = data_ticker
            st.session_state.multiplier_calculated = True

    if st.session_state.get("multiplier_calculated"):
        display_calculated_volatility()


# Function to display the calculated volatility and multiplier results
def display_calculated_volatility():
    st.subheader("Comparables Company and Market Multiples Results")
    st.dataframe(st.session_state.data_ticker_df, use_container_width=True)

    avg_method = st.radio(
        "Choose how to calculate the volatility & market multiplier:",
        ["Mean", "Median"],
    )

    columns_to_analyze = [
        "Volatility",
        "Price to Book Value (Equity)",
        "Price to Earning Ratio (Equity)",
        "Equity Value to Revenue (Equity)",
        "Equity Value to EBITDA (Equity)",
        "Enterprise Value to Revenue (Enterprise)",
        "Enterprise Value to EBITDA (Enterprise)",
    ]

    mean_values = st.session_state.data_ticker_df[columns_to_analyze].mean()
    median_values = st.session_state.data_ticker_df[columns_to_analyze].median()

    st.session_state.statistics_df = pd.DataFrame(
        {"Mean": mean_values, "Median": median_values}
    )

    multiplier = st.selectbox(
        "Select a multiplier to calculate equity value:", options=columns_to_analyze[1:]
    )
    input_and_calculate_equity_value(multiplier, avg_method)


# Function to handle input fields and calculate equity value
def input_and_calculate_equity_value(multiplier, avg_method):
    if multiplier == "Price to Book Value (Equity)":
        st.session_state.book_value_equity = st.number_input(
            "Enter Book Value of Equity:", value=0.0
        )
    elif multiplier == "Price to Earning Ratio (Equity)":
        st.session_state.ltm_eps = st.number_input("Enter LTM EPS:", value=0.0)
    elif multiplier == "Equity Value to Revenue (Equity)":
        st.session_state.ltm_revenue = st.number_input("Enter LTM Revenue:", value=0.0)
    elif multiplier == "Equity Value to EBITDA (Equity)":
        st.session_state.ltm_ebitda = st.number_input("Enter LTM EBITDA:", value=0.0)
    elif multiplier == "Enterprise Value to Revenue (Enterprise)":
        st.session_state.ltm_revenue = st.number_input("Enter LTM Revenue:", value=0.0)
        st.session_state.total_liabilities = st.number_input(
            "Enter Total Liabilities:", value=0.0
        )
    elif multiplier == "Enterprise Value to EBITDA (Enterprise)":
        st.session_state.ltm_ebitda = st.number_input("Enter LTM EBITDA:", value=0.0)
        st.session_state.total_liabilities = st.number_input(
            "Enter Total Liabilities:", value=0.0
        )

    if st.button("Calculate Equity Value"):
        equity_value = calculate_equity_value(multiplier, avg_method)
        st.success(f"Calculated Equity Value: {equity_value:.4f}")


# Function to calculate equity value based on the selected multiplier and method
def calculate_equity_value(multiplier, avg_method):
    if multiplier == "Price to Book Value (Equity)":
        return (
            st.session_state.statistics_df[avg_method][multiplier]
            * st.session_state.book_value_equity
        )
    elif multiplier == "Price to Earning Ratio (Equity)":
        return (
            st.session_state.statistics_df[avg_method][multiplier]
            * st.session_state.ltm_eps
        )
    elif multiplier == "Equity Value to Revenue (Equity)":
        return (
            st.session_state.statistics_df[avg_method][multiplier]
            * st.session_state.ltm_revenue
        )
    elif multiplier == "Equity Value to EBITDA (Equity)":
        return (
            st.session_state.statistics_df[avg_method][multiplier]
            * st.session_state.ltm_ebitda
        )
    elif multiplier == "Enterprise Value to Revenue (Enterprise)":
        return st.session_state.statistics_df[avg_method][multiplier] * (
            st.session_state.ltm_revenue - st.session_state.total_liabilities
        )
    elif multiplier == "Enterprise Value to EBITDA (Enterprise)":
        return st.session_state.statistics_df[avg_method][multiplier] * (
            st.session_state.ltm_ebitda - st.session_state.total_liabilities
        )


# Main equity valuation process
def equities_market():
    st.title("Equity Valuation - Market Approach")

    # Step 1: Handle risk-free rate input
    handle_risk_free_rate_input()

    # Step 2: Handle volatility input
    handle_volatility_input()

    # Step 3: Main equity valuation process
    st.subheader("Step 3: Equity Valuation")

    # Initialize input parameters and capitalization table
    initialize_valuation_inputs()

    if st.button("Proceed with Valuation"):
        proceed_with_valuation()


# Function to initialize input fields for equity valuation
def initialize_valuation_inputs():
    st.session_state.df = pd.DataFrame(
        {
            "Security": [
                "B2",
                "Series B",
                "Series A",
                "Series Seed",
                "ESOP",
                "Ordinaries",
            ],
            "Entry date": ["", "", "", "", "", ""],
            "Shares Outstanding": [26023, 70202, 42970, 11760, 15442, 82684],
            "Percentage": ["10.4%", "28.2%", "17.3%", "4.7%", "6.2%", "33.2%"],
            "Seniority": [1, 2, 3, 4, np.nan, np.nan],
            "Issue Price (USD)": [336.24, 321.83, 152.43, 42.52, 0, 0],
            "Liquidation Preference": [1, 1, 1, 1, np.nan, np.nan],
            "Participating": ["No", "No", "No", "No", "", ""],
            "Dividend": ["0%", "0%", "0%", "0%", "", ""],
        }
    )

    st.session_state.equity_value = 73659791.0
    st.session_state.time_to_liquidity = 2.0
    st.session_state.risk_free_rate = 0.0503
    st.session_state.dividend_yield = 0.0

    st.subheader("Input Parameters")
    cols = st.columns(2)
    st.session_state.time_to_liquidity = cols[0].number_input(
        "Time to Liquidity (years)", value=2.0
    )
    st.session_state.dividend_yield = cols[1].number_input(
        "Dividend Yield", value=0.0, min_value=0.0, max_value=1.0, step=0.001
    )

    st.subheader("Interactive Capitalization Table Input")
    st.session_state.df = st.data_editor(
        st.session_state.df, num_rows="dynamic", use_container_width=True
    )


# Function to proceed with the full valuation process
def proceed_with_valuation():
    with st.spinner("Processing... Please wait."):
        st.subheader("Final Edited Capitalization Table")
        st.dataframe(
            st.session_state.df.applymap(format_value), use_container_width=True
        )

        # Generate tables and calculate final values
        generate_and_display_all_tables()


# Function to generate and display all tables related to equity valuation
def generate_and_display_all_tables():
    break_table = generate_break_table(st.session_state.df)
    st.session_state.break_table = break_table
    st.subheader("Generated Break Table")
    st.dataframe(
        st.session_state.break_table.applymap(format_value), use_container_width=True
    )

    break_table_percent = generate_break_table_percent(st.session_state.df, break_table)
    st.session_state.break_table_percent = break_table_percent
    st.subheader("Generated Break Table Percentages")
    st.dataframe(st.session_state.break_table_percent, use_container_width=True)

    break_table_bs = generate_break_table_bs(
        st.session_state.break_table_percent,
        st.session_state.equity_value,
        st.session_state.risk_free_rate,
        st.session_state.volatility,
        st.session_state.time_to_liquidity,
        st.session_state.dividend_yield,
    )
    st.session_state.break_table_bs = break_table_bs
    st.subheader("Generated Break Table (Black-Scholes)")
    st.dataframe(
        st.session_state.break_table_bs.applymap(format_value), use_container_width=True
    )

    break_table_oa = generate_option_allocation_table(
        st.session_state.break_table,
        st.session_state.break_table_bs,
        st.session_state.break_table_percent,
        st.session_state.df,
    )
    st.session_state.break_table_oa = break_table_oa
    st.subheader("Generated Option Allocation Table")
    st.dataframe(
        st.session_state.break_table_oa.applymap(format_value), use_container_width=True
    )

    break_table_ds = calculate_break_table_ds(
        st.session_state.break_table_bs,
        st.session_state.break_table_percent,
        st.session_state.df,
    )
    st.session_state.break_table_ds = break_table_ds
    st.subheader("Calculated Delta Spread Table")
    st.dataframe(st.session_state.break_table_ds, use_container_width=True)

    estimated_volatility = calculate_estimated_volatility(
        st.session_state.df,
        st.session_state.break_table_ds,
        st.session_state.break_table_oa,
        st.session_state.equity_value,
        st.session_state.volatility,
    )
    st.session_state.estimated_volatility = estimated_volatility
    st.subheader("Estimated Volatility for Each Class")
    st.dataframe(st.session_state.estimated_volatility, use_container_width=True)

    estimated_DLOM = calculate_estimated_DLOM(
        st.session_state.df,
        st.session_state.break_table_oa,
        st.session_state.estimated_volatility,
        st.session_state.time_to_liquidity,
        st.session_state.dividend_yield,
        st.session_state.risk_free_rate,
    )
    st.session_state.estimated_DLOM = estimated_DLOM
    st.subheader("Estimated DLOM for Each Class")
    st.dataframe(
        st.session_state.estimated_DLOM.applymap(format_value), use_container_width=True
    )

    fair_value = calculate_fair_value(
        st.session_state.df, st.session_state.break_table_oa
    )
    st.session_state.fair_value = fair_value
    st.subheader("Calculated Fair Value")
    st.dataframe(
        st.session_state.fair_value.applymap(format_value), use_container_width=True
    )


if __name__ == "__main__":
    equities_market()
