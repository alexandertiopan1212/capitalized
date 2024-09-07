import numpy as np
import pandas as pd
from scipy.stats import norm
import streamlit as st


def black_scholes_dynamic_table(df):
    def black_scholes(S, X, T, r, sigma):
        d1 = (np.log(S / X) + (r + (sigma**2) / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        call_price = (S * N_d1) - (X * np.exp(-r * T) * N_d2)
        return d1, d2, N_d1, N_d2, call_price

    df["Grant Date"] = pd.to_datetime(df["Grant Date"])
    df["Vesting Date"] = pd.to_datetime(df["Vesting Date"])
    df["Time to Maturity"] = (df["Vesting Date"] - df["Grant Date"]).dt.days + 1
    df["Time to Maturity"] = df["Time to Maturity"] / 365

    df["d1"] = np.nan
    df["d2"] = np.nan
    df["N(d1)"] = np.nan
    df["N(d2)"] = np.nan
    df["Mesop Value/ share"] = np.nan
    df["Mesop Value"] = np.nan

    for index, row in df.iterrows():
        S = row["Spot Price (S)"]
        X = row["Strike (X)"]
        r = row["Risk free"] / 100
        sigma = row["Volatility"] / 100
        T = row["Time to Maturity"]

        d1, d2, N_d1, N_d2, call_price = black_scholes(S, X, T, r, sigma)
        df.at[index, "d1"] = d1
        df.at[index, "d2"] = d2
        df.at[index, "N(d1)"] = N_d1
        df.at[index, "N(d2)"] = N_d2
        df.at[index, "Mesop Value/ share"] = call_price
        df.at[index, "Mesop Value"] = call_price * row["Number of shares"]

    st.dataframe(df)
    return df
