import yfinance as yf
import numpy as np
import streamlit as st


def calculate_volatility(ticker_list, period="1y"):
    try:
        data = yf.download(ticker_list, period=period)["Adj Close"]
        daily_returns = data.pct_change().dropna()
        volatilities = daily_returns.std() * np.sqrt(252)
        return volatilities
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None
