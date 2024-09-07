import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st

# Function to initialize Selenium WebDriver
def initialize():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # Run headless mode
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options)
    return driver


def get_bond_data():
    # Initialize WebDriver
    driver = initialize()

    # Navigate to the bond yield page
    url = "https://www.cnbcindonesia.com/market-data/bonds/ID10YT=RR"
    driver.get(url)

    try:
        # Wait for the 10Y Yield section to appear
        yield_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(text(),"YIELD")]/following-sibling::span')
            )
        )

        # Extract the yield and price data
        yield_value = driver.find_element(
            By.XPATH, '//span[contains(text(),"YIELD")]/following-sibling::span'
        ).text.strip()
        price = driver.find_element(
            By.XPATH, '//span[contains(text(),"PRICE")]/following-sibling::span'
        ).text.strip()
        price_change = driver.find_element(
            By.XPATH, '//span[contains(@class, "bg-red-100")]'
        ).text.strip()

        # Extract the last updated time
        last_updated_time = driver.find_element(
            By.XPATH, '//span[contains(@class,"text-gray")]'
        ).text.strip()

        # Other bond details
        yield_prev_close = driver.find_element(
            By.XPATH,
            '//span[contains(text(),"Yield Prev. Close")]/following-sibling::span',
        ).text.strip()
        yield_open = driver.find_element(
            By.XPATH, '//span[contains(text(),"Yield Open")]/following-sibling::span'
        ).text.strip()
        yield_day_range = driver.find_element(
            By.XPATH,
            '//span[contains(text(),"Yield Day Range")]/following-sibling::span',
        ).text.strip()

        price_prev_close = driver.find_element(
            By.XPATH,
            '//span[contains(text(),"Price Prev. Close")]/following-sibling::span',
        ).text.strip()
        price_open = driver.find_element(
            By.XPATH, '//span[contains(text(),"Price Open")]/following-sibling::span'
        ).text.strip()
        price_day_range = driver.find_element(
            By.XPATH,
            '//span[contains(text(),"Price Day Range")]/following-sibling::span',
        ).text.strip()

        # Store the extracted data into a dictionary
        bond_data = {
            "10Y Yield": [yield_value],
            "Price": [price],
            "Price Change": [price_change],
            "Last Updated": [last_updated_time],
            "Yield Prev Close": [yield_prev_close],
            "Yield Open": [yield_open],
            "Yield Day Range": [yield_day_range],
            "Price Prev Close": [price_prev_close],
            "Price Open": [price_open],
            "Price Day Range": [price_day_range],
        }

        # Convert bond data into a DataFrame
        bond_df = pd.DataFrame(bond_data)

        # Close the WebDriver
        driver.quit()

        # Store the bond data in session state and return the yield as a decimal
        st.session_state.bond_df = bond_df
        return (
            float(yield_value.replace("%", "")) / 100
        )  # Convert yield to decimal (e.g., 6.67% -> 0.0667)

    except Exception as e:
        driver.quit()
        st.error(f"An error occurred during scraping: {e}")
        return None
