import streamlit as st
import pandas as pd
import numpy as np
import math
import yfinance as yf
from sidebar import render_page_based_on_sidebar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    if isinstance(x, (int, float)):
        return f"{x:,.2f}" if x < 1000 else f"{x:,.0f}"
    return x

# Function to scrape 10-year bond yield and other bond details as the risk-free rate
def get_bond_data():
    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument('--headless')  # Run headless mode
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options)

    # Navigate to the bond yield page
    url = 'https://www.cnbcindonesia.com/market-data/bonds/ID10YT=RR'
    driver.get(url)

    try:
        # Wait for the 10Y Yield section to appear
        yield_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"YIELD")]/following-sibling::span'))
        )

        # Extract the yield and other details
        yield_value = driver.find_element(By.XPATH, '//span[contains(text(),"YIELD")]/following-sibling::span').text.strip()
        price = driver.find_element(By.XPATH, '//span[contains(text(),"PRICE")]/following-sibling::span').text.strip()
        price_change = driver.find_element(By.XPATH, '//span[contains(@class, "bg-red-100")]').text.strip()

        # Extract additional bond details
        last_updated_time = driver.find_element(By.XPATH, '//span[contains(@class,"text-gray")]').text.strip()
        yield_prev_close = driver.find_element(By.XPATH, '//span[contains(text(),"Yield Prev. Close")]/following-sibling::span').text.strip()
        yield_open = driver.find_element(By.XPATH, '//span[contains(text(),"Yield Open")]/following-sibling::span').text.strip()
        yield_day_range = driver.find_element(By.XPATH, '//span[contains(text(),"Yield Day Range")]/following-sibling::span').text.strip()
        price_prev_close = driver.find_element(By.XPATH, '//span[contains(text(),"Price Prev. Close")]/following-sibling::span').text.strip()
        price_open = driver.find_element(By.XPATH, '//span[contains(text(),"Price Open")]/following-sibling::span').text.strip()
        price_day_range = driver.find_element(By.XPATH, '//span[contains(text(),"Price Day Range")]/following-sibling::span').text.strip()

        # Store the extracted data into a dictionary
        bond_data = {
            '10Y Yield': [yield_value],
            'Price': [price],
            'Price Change': [price_change],
            'Last Updated': [last_updated_time],
            'Yield Prev Close': [yield_prev_close],
            'Yield Open': [yield_open],
            'Yield Day Range': [yield_day_range],
            'Price Prev Close': [price_prev_close],
            'Price Open': [price_open],
            'Price Day Range': [price_day_range]
        }

        # Convert bond data to a DataFrame
        bond_df = pd.DataFrame(bond_data)

        # Close WebDriver
        driver.quit()

        # Store the bond_df and return the yield as a decimal
        st.session_state.bond_df = bond_df
        return float(yield_value.replace("%", "")) / 100  # Convert to a decimal (e.g., 6.67% -> 0.0667)

    except Exception as e:
        driver.quit()
        st.error(f"An error occurred during scraping: {e}")
        return None

# Function to calculate stock volatility
def calculate_volatility(ticker_list, period="1y"):
    try:
        data = yf.download(ticker_list, period=period)["Adj Close"]
        daily_returns = data.pct_change().dropna()
        volatilities = daily_returns.std() * np.sqrt(252)  # Annualizing the volatility
        return volatilities
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def equities_page():
    st.title("Equity Valuation with Bond Yield Data and Volatility Setup")

    render_page_based_on_sidebar()

    # Step 1: Choose Risk-Free Rate Input Method
    st.subheader("Step 1: Choose Risk-Free Rate Input Method")
    risk_free_rate_input_method = st.radio(
        "Would you like to manually input the risk-free rate or scrape the 10-year bond yield?",
        ("Manual Input", "Scrape from Web")
    )

    if risk_free_rate_input_method == "Manual Input":
        # Manually input the risk-free rate
        st.session_state.risk_free_rate = st.number_input(
            "Enter risk-free rate (e.g., 0.05 for 5%)", value=0.0503, min_value=0.0, max_value=1.0, step=0.001
        )
        st.success(f"Manual risk-free rate set to: {st.session_state.risk_free_rate:.2%}")

    elif risk_free_rate_input_method == "Scrape from Web":
        # Scrape the bond data
        if st.button("Get 10-Year Bond Yield"):
            with st.spinner("Processing... Please wait."):
                risk_free_rate = get_bond_data()
                if risk_free_rate is not None:
                    st.session_state.risk_free_rate = risk_free_rate
                    st.success(f"Scraped 10-Year Bond Yield as Risk-Free Rate: {risk_free_rate:.2%}")
    
    # Display bond scraping result if available
    if "bond_df" in st.session_state:
        st.subheader("Scraped Bond Data")
        st.dataframe(st.session_state.bond_df)

    # Step 2: Choose Volatility Input Method
    st.subheader("Step 2: Choose Volatility Input Method")
    volatility_input_method = st.radio(
        "Would you like to manually input the volatility or calculate it from stock tickers?",
        ("Manual Input", "Calculate from Stock List")
    )

    if volatility_input_method == "Manual Input":
        # Manually input volatility
        st.session_state.volatility = st.number_input(
            "Enter volatility (e.g., 0.6 for 60%)", value=0.6, min_value=0.0, max_value=1.0, step=0.01
        )
        st.success(f"Manual volatility set to: {st.session_state.volatility:.2f}")

    elif volatility_input_method == "Calculate from Stock List":
        # Step 2: Setup for stock volatility
        st.subheader("Step 2: Stock Volatility Setup")

        # Default list of Indonesian stocks
        default_indonesian_stocks = ["BBCA.JK", "TLKM.JK", "ASII.JK", "BMRI.JK", "UNVR.JK"]

        # Initialize session state for the DataFrame if it doesn't exist
        if "stock_df" not in st.session_state:
            st.session_state.stock_df = pd.DataFrame({"Stock Ticker": default_indonesian_stocks})

        # Show editable DataFrame using st.data_editor
        st.write("Modify stock tickers by adding or removing rows below:")
        st.session_state.stock_df = st.data_editor(st.session_state.stock_df, num_rows="dynamic")

        # Convert the edited DataFrame into a list of tickers
        ticker_list = st.session_state.stock_df["Stock Ticker"].tolist()

        # Period selection
        period = st.selectbox("Select period", options=["1y", "2y", "5y"], index=0)

        # Button to calculate volatility
        if st.button("Calculate Volatility"):
            volatilities = calculate_volatility(ticker_list, period=period)
            if volatilities is not None:
                # Store the stock tickers and their volatilities in a new DataFrame
                stock_volatility_df = pd.DataFrame({
                    "Stock Ticker": ticker_list,
                    "Volatility": volatilities.values
                })
                st.session_state.stock_volatility_df = stock_volatility_df  # Store in session state
                st.session_state.volatility_calculated = True  # Mark as calculated

        # Display the calculated volatility results if they exist
        if st.session_state.get("volatility_calculated"):
            st.subheader("Calculated Volatilities for Selected Stocks")

            # Display stock volatility results using st.data_editor
            st.session_state.stock_volatility_df = st.data_editor(st.session_state.stock_volatility_df)

            # Provide an option to choose how to calculate the average volatility
            avg_method = st.radio("Choose how to calculate the average volatility:", ["Mean", "Median"])

            # Calculate average based on the user's selection
            if avg_method == "Mean":
                st.session_state.volatility = st.session_state.stock_volatility_df["Volatility"].mean()
            else:
                st.session_state.volatility = st.session_state.stock_volatility_df["Volatility"].median()

            # Show the calculated average volatility
            st.success(f"Average volatility ({avg_method}): {st.session_state.volatility:.4f}")

    # Step 3: Main equity valuation process
    st.subheader("Step 3: Equity Valuation")

    # Initialize data for the table
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
    if 'time_to_liquidity' not in st.session_state:
        st.session_state.time_to_liquidity = 2.0  # Default time to liquidity in years
    if 'risk_free_rate' not in st.session_state:
        st.session_state.risk_free_rate = 0.0503  # Default risk-free rate
    if 'dividend_yield' not in st.session_state:
        st.session_state.dividend_yield = 0.0  # Default dividend yield

    # Input parameters
    st.subheader("Input Parameters")
    cols = st.columns(3)
    st.session_state.equity_value = cols[0].number_input("Equity Value", value=float(st.session_state.equity_value))
    st.session_state.time_to_liquidity = cols[1].number_input("Time to Liquidity (years)", value=float(st.session_state.time_to_liquidity))
    # st.session_state.risk_free_rate = cols[2].number_input("Risk-Free Rate", value=float(st.session_state.risk_free_rate), min_value=0.0, max_value=1.0, step=0.001)
    st.session_state.dividend_yield = cols[2].number_input("Dividend Yield", value=float(st.session_state.dividend_yield), min_value=0.0, max_value=1.0, step=0.001)

    # Capitalization table
    st.subheader("Interactive Capitalization Table Input")
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)


    # Proceed with calculations
    if st.button("Proceed with Valuation"):
        with st.spinner("Processing... Please wait."):
            # Display final capitalization table
            st.subheader("Final Edited Capitalization Table")
            st.dataframe(st.session_state.df.applymap(format_value), use_container_width=True)

            # Generate break table
            break_table = generate_break_table(st.session_state.df)
            st.session_state.break_table = break_table
            st.subheader("Generated Break Table")
            st.dataframe(st.session_state.break_table.applymap(format_value), use_container_width=True)

            # Break table percentages
            break_table_percent = generate_break_table_percent(st.session_state.df, break_table)
            st.session_state.break_table_percent = break_table_percent
            st.subheader("Generated Break Table Percentages")
            st.dataframe(st.session_state.break_table_percent, use_container_width=True)

            # Break table using Black-Scholes model
            break_table_bs = generate_break_table_bs(
                st.session_state.break_table_percent,
                st.session_state.equity_value,
                st.session_state.risk_free_rate,
                st.session_state.volatility,  # Use either manual or stock-based volatility
                st.session_state.time_to_liquidity,
                st.session_state.dividend_yield
            )
            st.session_state.break_table_bs = break_table_bs
            st.subheader("Generated Break Table (Black-Scholes)")
            st.dataframe(st.session_state.break_table_bs.applymap(format_value), use_container_width=True)

            # Option allocation table
            break_table_oa = generate_option_allocation_table(
                st.session_state.break_table,
                st.session_state.break_table_bs,
                st.session_state.break_table_percent,
                st.session_state.df
            )
            st.session_state.break_table_oa = break_table_oa
            st.subheader("Generated Option Allocation Table")
            st.dataframe(st.session_state.break_table_oa.applymap(format_value), use_container_width=True)

            # Delta spread table
            break_table_ds = calculate_break_table_ds(
                st.session_state.break_table_bs,
                st.session_state.break_table_percent,
                st.session_state.df
            )
            st.session_state.break_table_ds = break_table_ds
            st.subheader("Calculated Delta Spread Table")
            st.dataframe(st.session_state.break_table_ds, use_container_width=True)

            # Estimated volatility for each class
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

            # Estimated DLOM for each class
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

            # Fair value for each class
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
