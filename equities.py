import streamlit as st
import pandas as pd
import numpy as np
import math
import yfinance as yf
from sidebar import render_page_based_on_sidebar
from equities_income_approach import equities_income_approach
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


# Function to fetch financial data for a single ticker
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Extract necessary information from the ticker
    market_cap = stock.info.get('marketCap', None)
    balance_sheet = stock.balance_sheet

    # Safely get 'Total Liabilities', 'Book Value Equity', and 'Total Debt' using iloc
    total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else None
    book_value_equity = balance_sheet.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in balance_sheet.index else None
    total_debt = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index else None
    ltm_eps = stock.info.get('trailingEps', None)
    price_share = stock.info.get('currentPrice', None)
    volatility = stock.info.get('beta', None)
    
    # Extract LTM Revenue and EBITDA using iloc
    financials = stock.financials
    ltm_revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
    ltm_ebitda = financials.loc['EBITDA'].iloc[0] if 'EBITDA' in financials.index else None

    # Return the extracted data as a dictionary
    return {
        "Ticker": ticker,
        "Volatility": volatility,
        "LTM Revenue": ltm_revenue,
        "LTM EBITDA": ltm_ebitda,
        "Market Cap": market_cap,
        "Total Liabilities": total_liabilities,
        "Book Value Equity": book_value_equity,
        "LTM EPS": ltm_eps,
        "Price/ Share": price_share
    }

# Function to calculate multiples based on the data
def calculate_multiples(data):
    # Handle missing values by providing default None or NaN for each ratio
    price_to_book = data['Market Cap'] / data['Book Value Equity'] if data['Book Value Equity'] else np.nan
    price_to_earning = data['Price/ Share'] / data['LTM EPS'] if data['LTM EPS'] else np.nan
    equity_value_to_revenue = data['Market Cap'] / data['LTM Revenue'] if data['LTM Revenue'] else np.nan
    equity_value_to_ebitda = data['Market Cap'] / data['LTM EBITDA'] if data['LTM EBITDA'] else np.nan
    enterprise_value_to_revenue = (data['Market Cap'] + data['Total Liabilities']) / data['LTM Revenue'] if data['LTM Revenue'] and data['Total Liabilities'] else np.nan
    enterprise_value_to_ebitda = (data['Market Cap'] + data['Total Liabilities']) / data['LTM EBITDA'] if data['LTM EBITDA'] and data['Total Liabilities'] else np.nan

    # Return the calculated multiples
    return {
        "Price to Book Value (Equity)": price_to_book,
        "Price to Earning Ratio (Equity)": price_to_earning,
        "Equity Value to Revenue (Equity)": equity_value_to_revenue,
        "Equity Value to EBITDA (Equity)": equity_value_to_ebitda,
        "Enterprise Value to Revenue (Enterprise)": enterprise_value_to_revenue,
        "Enterprise Value to EBITDA (Enterprise)": enterprise_value_to_ebitda
    }

# Function to fetch and process data for a list of tickers
def get_ticker_data(ticker_list):
    data_list = []
    
    for ticker in ticker_list:
        # Fetch financial data
        financial_data = get_financial_data(ticker)
        
        # Calculate multiples
        multiples = calculate_multiples(financial_data)
        
        # Combine financial data and multiples into one dictionary
        combined_data = {**financial_data, **multiples}
        data_list.append(combined_data)
    
    # Convert the list of dictionaries into a DataFrame adn Replace NaN values with average
    df = pd.DataFrame(data_list)
    num_cols = ["Price to Book Value (Equity)", "Price to Earning Ratio (Equity)", "Equity Value to Revenue (Equity)", "Equity Value to EBITDA (Equity)", "Enterprise Value to Revenue (Enterprise)", "Enterprise Value to EBITDA (Enterprise)"]
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

    return df

# Function to format numbers for display (thousands separator)
def format_value(x):
    if isinstance(x, (int, float)):
        return f"{x:,.2f}" if x < 1000 else f"{x:,.0f}"
    return x

# Function to scrape 10-year bond yield and other bond details (for risk-free rate)
def get_bond_data():
    # Initialize Selenium WebDriver for scraping bond data
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options)

    # Navigate to the bond yield page
    url = 'https://www.cnbcindonesia.com/market-data/bonds/ID10YT=RR'
    driver.get(url)

    try:
        # Wait for the bond yield section to load
        yield_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"YIELD")]/following-sibling::span'))
        )

        # Extract bond yield and other relevant details
        yield_value = driver.find_element(By.XPATH, '//span[contains(text(),"YIELD")]/following-sibling::span').text.strip()
        price = driver.find_element(By.XPATH, '//span[contains(text(),"PRICE")]/following-sibling::span').text.strip()
        price_change = driver.find_element(By.XPATH, '//span[contains(@class, "bg-red-100")]').text.strip()
        last_updated_time = driver.find_element(By.XPATH, '//span[contains(@class,"text-gray")]').text.strip()
        yield_prev_close = driver.find_element(By.XPATH, '//span[contains(text(),"Yield Prev. Close")]/following-sibling::span').text.strip()
        yield_open = driver.find_element(By.XPATH, '//span[contains(text(),"Yield Open")]/following-sibling::span').text.strip()
        yield_day_range = driver.find_element(By.XPATH, '//span[contains(text(),"Yield Day Range")]/following-sibling::span').text.strip()
        price_prev_close = driver.find_element(By.XPATH, '//span[contains(text(),"Price Prev Close")]/following-sibling::span').text.strip()
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

        # Convert bond data into a DataFrame
        bond_df = pd.DataFrame(bond_data)

        # Close the WebDriver
        driver.quit()

        # Store the bond data in session state and return the yield as a decimal
        st.session_state.bond_df = bond_df
        return float(yield_value.replace("%", "")) / 100  # Convert yield to a decimal (e.g., 6.67% -> 0.0667)

    except Exception as e:
        driver.quit()
        st.error(f"An error occurred during scraping: {e}")
        return None

# Function to calculate stock volatility for a list of tickers
def calculate_volatility(ticker_list, period="1y"):
    try:
        # Download historical stock prices for the given period
        data = yf.download(ticker_list, period=period)["Adj Close"]
        daily_returns = data.pct_change().dropna()
        # Annualize the volatility (standard deviation of daily returns)
        volatilities = daily_returns.std() * np.sqrt(252)
        return volatilities
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Main function to render the equity valuation page
def equities_page():
    render_page_based_on_sidebar()

    approach_option = st.selectbox("Select Valuation Approach", options=["Market", "Income"], index=0)

    if approach_option == "Market":
        st.title("Equity Valuation - Market Approach")

        # Step 1: Risk-Free Rate Input Method
        st.subheader("Step 1: Choose Risk-Free Rate Input Method")
        risk_free_rate_input_method = st.radio(
            "Would you like to manually input the risk-free rate or scrape the 10-year bond yield?",
            ("Manual Input", "Scrape from Web")
        )

        # Handle manual input or web scraping for the risk-free rate
        if risk_free_rate_input_method == "Manual Input":
            st.session_state.risk_free_rate = st.number_input(
                "Enter risk-free rate (e.g., 0.05 for 5%)", value=0.0503, min_value=0.0, max_value=1.0, step=0.001
            )
            st.success(f"Manual risk-free rate set to: {st.session_state.risk_free_rate:.2%}")

        elif risk_free_rate_input_method == "Scrape from Web":
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

        # Step 2: Volatility Input Method
        st.subheader("Step 2: Choose Volatility Input Method")
        volatility_input_method = st.radio(
            "Would you like to manually input the volatility or calculate it from stock tickers?",
            ("Manual Input", "Calculate from Stock List")
        )

        # Handle manual input or calculation of volatility
        if volatility_input_method == "Manual Input":
            st.session_state.volatility = st.number_input(
                "Enter volatility (e.g., 0.6 for 60%)", value=0.6, min_value=0.0, max_value=1.0, step=0.01
            )
            st.success(f"Manual volatility set to: {st.session_state.volatility:.2f}")

        elif volatility_input_method == "Calculate from Stock List":
            # Allow users to input stock tickers and calculate volatility
            st.subheader("Step 2: Comparables Companies Setup")

            # Default list of Indonesian stocks
            default_indonesian_stocks = ["BBCA.JK", "TLKM.JK", "ASII.JK", "BMRI.JK", "UNVR.JK"]

            # Initialize session state for the DataFrame if it doesn't exist
            if "stock_df" not in st.session_state:
                st.session_state.stock_df = pd.DataFrame({"Stock Ticker": default_indonesian_stocks})

            # Editable DataFrame for stock tickers
            st.write("Modify stock tickers by adding or removing rows below:")
            st.session_state.stock_df = st.data_editor(st.session_state.stock_df, num_rows="dynamic")

            # Convert the edited DataFrame into a list of tickers
            ticker_list = st.session_state.stock_df["Stock Ticker"].tolist()

            # Button to calculate volatility and market multiplier
            if st.button("Calculate Volatility & Market Multiplier"):
                data_ticker = get_ticker_data(ticker_list)
                if data_ticker is not None:
                    st.session_state.data_ticker_df = data_ticker  # Store in session state
                    st.session_state.multiplier_calculated = True  # Mark as calculated

            # Display the calculated volatility results if they exist
            if st.session_state.get("multiplier_calculated"):
                st.subheader("Comparables Company and Market Multiples Results")

                # Display stock volatility results
                st.dataframe(st.session_state.data_ticker_df, use_container_width=True)

                # Choose method to calculate the average (mean or median)
                avg_method = st.radio("Choose how to calculate the volatility & market multiplier:", ["Mean", "Median"])

                # Columns to calculate mean and median for
                columns_to_analyze = [
                    'Volatility',
                    'Price to Book Value (Equity)',
                    'Price to Earning Ratio (Equity)',
                    'Equity Value to Revenue (Equity)',
                    'Equity Value to EBITDA (Equity)',
                    'Enterprise Value to Revenue (Enterprise)',
                    'Enterprise Value to EBITDA (Enterprise)'
                ]

                # Calculate mean and median of these columns
                mean_values = st.session_state.data_ticker_df[columns_to_analyze].mean()
                median_values = st.session_state.data_ticker_df[columns_to_analyze].median()

                # Combine mean and median into a single DataFrame
                if 'statistic_df' not in st.session_state:
                    st.session_state.statistics_df = pd.DataFrame({
                        'Mean': mean_values,
                        'Median': median_values
                    })

                # Select the multiplier to display
                multiplier = st.selectbox("Select a multiplier to calculate equity value:", options=[
                    'Price to Book Value (Equity)',
                    'Price to Earning Ratio (Equity)',
                    'Equity Value to Revenue (Equity)',
                    'Equity Value to EBITDA (Equity)',
                    'Enterprise Value to Revenue (Enterprise)',
                    'Enterprise Value to EBITDA (Enterprise)'
                ])

                # Input fields based on selected multiplier
                if multiplier == 'Price to Book Value (Equity)':
                    book_value_equity = st.number_input("Enter Book Value of Equity:")
                elif multiplier == 'Price to Earning Ratio (Equity)':
                    ltm_eps = st.number_input("Enter LTM EPS:")
                elif multiplier == 'Equity Value to Revenue (Equity)':
                    ltm_revenue = st.number_input("Enter LTM Revenue:")
                elif multiplier == 'Equity Value to EBITDA (Equity)':
                    ltm_ebitda = st.number_input("Enter LTM EBITDA:")
                elif multiplier == 'Enterprise Value to Revenue (Enterprise)':
                    ltm_revenue = st.number_input("Enter LTM Revenue:")
                    total_liabilities = st.number_input("Enter Total Liabilities:")
                elif multiplier == 'Enterprise Value to EBITDA (Enterprise)':
                    ltm_ebitda = st.number_input("Enter LTM EBITDA:")
                    total_liabilities = st.number_input("Enter Total Liabilities:")

                # Button to calculate equity value
                if st.button("Calculate Equity Value"):
                    if multiplier == 'Price to Book Value (Equity)':
                        equity_value = st.session_state.statistics_df[avg_method][multiplier] * book_value_equity
                    elif multiplier == 'Price to Earning Ratio (Equity)':
                        equity_value = st.session_state.statistics_df[avg_method][multiplier] * ltm_eps
                    elif multiplier == 'Equity Value to Revenue (Equity)':
                        equity_value = st.session_state.statistics_df[avg_method][multiplier] * ltm_revenue
                    elif multiplier == 'Equity Value to EBITDA (Equity)':
                        equity_value = st.session_state.statistics_df[avg_method][multiplier] * ltm_ebitda
                    elif multiplier == 'Enterprise Value to Revenue (Enterprise)':
                        equity_value = st.session_state.statistics_df[avg_method][multiplier] * (ltm_revenue - total_liabilities)
                    elif multiplier == 'Enterprise Value to EBITDA (Enterprise)':
                        equity_value = st.session_state.statistics_df[avg_method][multiplier] * (ltm_ebitda - total_liabilities)

                    # Display calculated average volatility and equity value
                    st.success(f"Calculated Equity Value: {equity_value:.4f}")
                
                # Calculate average based on the user's selection
                if avg_method == "Mean":
                    st.session_state.volatility = st.session_state.statistics_df["Mean"]["Volatility"]
                    st.session_state.multiplier_coef = st.session_state.statistics_df[avg_method][multiplier]
                else:
                    st.session_state.volatility = st.session_state.statistics_df["Median"]["Volatility"]
                    st.session_state.multiplier_coef = st.session_state.statistics_df[avg_method][multiplier]

                # Display calculated average volatility
                st.dataframe(st.session_state.statistics_df, use_container_width=True)
                st.success(f"Average volatility ({avg_method}): {st.session_state.volatility:.4f}")
                st.success(f"Multiplier ({avg_method}) {multiplier}: {st.session_state.statistics_df[avg_method][multiplier]:.4f}")

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

        # Input parameters section
        st.subheader("Input Parameters")
        cols = st.columns(2)
        st.session_state.time_to_liquidity = cols[0].number_input("Time to Liquidity (years)", value=float(st.session_state.time_to_liquidity))
        st.session_state.dividend_yield = cols[1].number_input("Dividend Yield", value=float(st.session_state.dividend_yield), min_value=0.0, max_value=1.0, step=0.001)

        # Capitalization table input section
        st.subheader("Interactive Capitalization Table Input")
        st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

        # Proceed with the valuation process
        if st.button("Proceed with Valuation"):
            with st.spinner("Processing... Please wait."):
                # Display final capitalization table
                st.subheader("Final Edited Capitalization Table")
                st.dataframe(st.session_state.df.applymap(format_value), use_container_width=True)

                # Generate and display break table
                break_table = generate_break_table(st.session_state.df)
                st.session_state.break_table = break_table
                st.subheader("Generated Break Table")
                st.dataframe(st.session_state.break_table.applymap(format_value), use_container_width=True)

                # Generate and display break table percentages
                break_table_percent = generate_break_table_percent(st.session_state.df, break_table)
                st.session_state.break_table_percent = break_table_percent
                st.subheader("Generated Break Table Percentages")
                st.dataframe(st.session_state.break_table_percent, use_container_width=True)

                # Generate and display break table using Black-Scholes model
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

                # Generate and display option allocation table
                break_table_oa = generate_option_allocation_table(
                    st.session_state.break_table,
                    st.session_state.break_table_bs,
                    st.session_state.break_table_percent,
                    st.session_state.df
                )
                st.session_state.break_table_oa = break_table_oa
                st.subheader("Generated Option Allocation Table")
                st.dataframe(st.session_state.break_table_oa.applymap(format_value), use_container_width=True)

                # Generate and display delta spread table
                break_table_ds = calculate_break_table_ds(
                    st.session_state.break_table_bs,
                    st.session_state.break_table_percent,
                    st.session_state.df
                )
                st.session_state.break_table_ds = break_table_ds
                st.subheader("Calculated Delta Spread Table")
                st.dataframe(st.session_state.break_table_ds, use_container_width=True)

                # Generate and display estimated volatility for each class
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

                # Generate and display estimated DLOM for each class
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

                # Generate and display fair value for each class
                fair_value = calculate_fair_value(
                    st.session_state.df,
                    st.session_state.break_table_oa
                )
                st.session_state.fair_value = fair_value
                st.subheader("Calculated Fair Value")
                st.dataframe(st.session_state.fair_value.applymap(format_value), use_container_width=True)

    if approach_option == "Income":
        equities_income_approach()
        


# Run the application
if __name__ == "__main__":
    equities_page()
