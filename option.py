import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from american_option import binomial_tree_pricing
from european_option import black_scholes_dynamic_table
from monte_carlo import monte_carlo_simulation
from sidebar import render_page_based_on_sidebar


def option_page():
    st.title("Option Valuation")
    option_type = st.selectbox(
        "Select Option Type", ["American", "European", "Monte Carlo"]
    )

    render_page_based_on_sidebar()

    if option_type == "European":
        data = {
            "Strike (X)": [450, 450, 450, 450, 1500],
            "Spot Price (S)": [400, 400, 400, 400, 2100],
            "Risk free": [5.8, 5.9, 6.0, 6.1, 5.83],
            "Volatility": [53.9, 53.9, 53.9, 53.9, 34.64],
            "Dividend yield": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Number of shares": [20124910, 20124910, 20124910, 20124910, 20124910],
            "Grant Date": [
                "5/15/2023",
                "5/15/2023",
                "5/15/2023",
                "5/15/2023",
                "5/15/2023",
            ],
            "Vesting Date": [
                "5/19/2023",
                "5/17/2024",
                "5/16/2025",
                "5/16/2026",
                "5/15/2025",
            ],
        }
        df_bs = pd.DataFrame(data)
        if "df_bs" not in st.session_state:
            st.session_state.df_bs = df_bs
        st.subheader("Interactive Black-Scholes Input")
        df_bs = st.data_editor(df_bs, num_rows="dynamic", use_container_width=True)
        st.session_state.df_bs = df_bs

        if st.button("Calculate"):
            black_scholes_dynamic_table(st.session_state.df_bs)

    elif option_type == "American":
        S = st.number_input(
            "Asset Value at Valuation Date (S)", value=2100.0, min_value=0.0
        )
        K = st.number_input("Strike Price (K)", value=1500.0, min_value=0.0)
        T = st.number_input("Maturity in Years (T)", value=2.0, min_value=0.1)
        r = st.number_input(
            "Risk-free Rate (r)", value=0.0583, min_value=0.0, format="%.4f"
        )
        sigma = st.number_input(
            "Yearly Volatility (sigma)", value=0.3464, min_value=0.0, format="%.4f"
        )
        steps = T * 12
        if st.button("Calculate and Plot"):
            binomial_tree_pricing(S, K, T, r, sigma, int(steps))

    else:
        mc_option_type = st.selectbox("Select Type", ["option", "portfolio"])

        if mc_option_type == "option":
            S = st.number_input("Initial stock price (S)", value=2100)
            K = st.number_input("Strike price (K)", value=1500)
            T = st.number_input("Time to maturity (years, T)", value=2.0)
            r = st.number_input("Risk-free interest rate (r)", value=0.0583)
            sigma = st.number_input("Volatility (sigma)", value=0.3464)

            if st.button("Calculate"):
                option_price, std_error = monte_carlo_simulation(
                    "option", S=S, K=K, T=T, r=r, sigma=sigma
                )
                st.write(f"Estimated Call Option Price: ${option_price:.2f}")
                st.write(f"Standard Error: ±{std_error:.2f}")

        elif mc_option_type == "portfolio":
            data_s = {
                "Stock List": [
                    "BBCA.JK",
                    "TLKM.JK",
                    "ASII.JK",
                    "UNVR.JK",
                    "BMRI.JK",
                    "ICBP.JK",
                ]
            }
            df_s = pd.DataFrame(data_s)
            stocks = st.data_editor(df_s, num_rows="dynamic", use_container_width=True)

            if len(stocks) > 6:
                st.error("You can only enter up to 6 stocks.")
            else:
                start_date = st.date_input(
                    "Start date", value=(datetime.today() - timedelta(days=300)).date()
                )
                end_date = st.date_input("End date", value=datetime.today().date())

                if st.button("Calculate"):
                    monte_carlo_simulation(
                        "portfolio",
                        stocks=stocks["Stock List"].to_list(),
                        start_date=start_date,
                        end_date=end_date,
                    )


if __name__ == "__main__":
    option_page()
