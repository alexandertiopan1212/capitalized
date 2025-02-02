import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from sidebar import render_page_based_on_sidebar


def generate_dummy_candlestick_data(num_days=30, base_price=4100):
    """
    Generate dummy candlestick data for a given number of days and base price.

    Parameters:
    - num_days (int): Number of days for the candlestick data.
    - base_price (float): Base price to generate random open, high, low, and close prices.

    Returns:
    - pd.DataFrame: DataFrame containing the generated candlestick data.
    """
    np.random.seed(int(time.time()))  # Seed for randomness
    dates = pd.date_range(start="2024-01-01", periods=num_days)
    open_prices = np.random.normal(base_price, 50, num_days)
    close_prices = open_prices + np.random.normal(0, 30, num_days)
    high_prices = np.maximum(open_prices, close_prices) + np.random.normal(
        0, 20, num_days
    )
    low_prices = np.minimum(open_prices, close_prices) - np.random.normal(
        0, 20, num_days
    )

    return pd.DataFrame(
        {
            "Date": dates,
            "Open": open_prices,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
        }
    )


def dashboard_page():
    """
    Display the dashboard page with market index, watchlist, and bond yield data.
    Provides candlestick charts for each selected item and allows the user to refresh data.
    """

    # Check if the page is 'dashboard' and render the sidebar content
    if st.session_state.page == "dashboard":
        render_page_based_on_sidebar()

        st.button("Refresh Data")  # Button to manually refresh data (if needed)

        st.markdown(
            "<h1 style='text-align: left;'>Market Index & Watchlist</h1>",
            unsafe_allow_html=True,
        )

        # Market Index Section with Dummy Data
        st.markdown("### Market Index")
        market_data = {
            "Index": ["S&P 500", "NASDAQ", "DOW JONES", "RUSSELL 2000"],
            "Value": np.round(
                np.random.normal([4200.70, 12650.20, 34500.65, 2233.45], 20), 2
            ),
            "Net Change": np.round(
                np.random.normal([50.70, 120.90, 210.80, 45.20], 5), 2
            ),
            "% Change": np.round(np.random.normal([1.22, 1.50, 0.61, 2.07], 0.1), 2),
        }
        st.table(pd.DataFrame(market_data))  # Display market data in a table

        # Dropdown to select which index candlestick chart to display
        index_selected = st.selectbox(
            "Select Market Index Candlestick", options=market_data["Index"]
        )

        if index_selected:
            base_price = market_data["Value"][
                market_data["Index"].index(index_selected)
            ]
            st.markdown(f"### {index_selected} Candlestick Chart")
            candlestick_data = generate_dummy_candlestick_data(base_price=base_price)

            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=candlestick_data["Date"],
                        open=candlestick_data["Open"],
                        high=candlestick_data["High"],
                        low=candlestick_data["Low"],
                        close=candlestick_data["Close"],
                    )
                ]
            )
            fig.update_layout(
                title=f"{index_selected} Candlestick Chart",
                xaxis_title="Date",
                yaxis_title="Price",
                width=1200,  # Set the chart width
                height=400,  # Set the chart height
            )
            st.plotly_chart(fig, use_container_width=True)

        # Watchlist Section with Dummy Data
        st.markdown("### Watchlist")
        watchlist_data = {
            "Stock": ["AAPL", "GOOGL", "AMZN", "TSLA", "MSFT"],
            "Value": np.round(
                np.random.normal([150.00, 2700.00, 3300.00, 750.00, 310.00], 10), 2
            ),
            "Net Change": np.round(
                np.random.normal([2.00, 30.00, 45.00, 15.00, 5.00], 2), 2
            ),
            "% Change": np.round(
                np.random.normal([1.35, 1.12, 1.38, 2.04, 1.64], 0.1), 2
            ),
        }
        st.table(pd.DataFrame(watchlist_data))  # Display watchlist data in a table

        # Dropdown to select which stock candlestick chart to display
        stock_selected = st.selectbox(
            "Select Watchlist Stock Candlestick", options=watchlist_data["Stock"]
        )

        if stock_selected:
            base_price = watchlist_data["Value"][
                watchlist_data["Stock"].index(stock_selected)
            ]
            st.markdown(f"### {stock_selected} Candlestick Chart")
            candlestick_data = generate_dummy_candlestick_data(base_price=base_price)

            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=candlestick_data["Date"],
                        open=candlestick_data["Open"],
                        high=candlestick_data["High"],
                        low=candlestick_data["Low"],
                        close=candlestick_data["Close"],
                    )
                ]
            )
            fig.update_layout(
                title=f"{stock_selected} Candlestick Chart",
                xaxis_title="Date",
                yaxis_title="Price",
                width=1200,  # Set the chart width
                height=400,  # Set the chart height
            )
            st.plotly_chart(fig, use_container_width=True)

        # Government Bond Yields Section with Dummy Data
        st.markdown("### Government Bond Yields")
        bond_yields_data = {
            "Country": [
                "United States",
                "United States",
                "United States",
                "United States",
                "United States",
            ],
            "Yield": np.round(
                np.random.normal([3.88, 3.88, 3.88, 3.88, 3.88], 0.05), 2
            ),
            "1 Day": np.random.randint(-5, 5, 5),
            "1 Month": np.random.randint(-30, 30, 5),
            "1 Year": np.random.randint(-50, 50, 5),
        }
        st.table(pd.DataFrame(bond_yields_data))  # Display bond yield data in a table

        # Dropdown to select which bond yield candlestick chart to display
        bond_selected = st.selectbox(
            "Select Government Bond Yield Candlestick",
            options=bond_yields_data["Country"],
        )

        if bond_selected:
            base_yield = bond_yields_data["Yield"][
                bond_yields_data["Country"].index(bond_selected)
            ]
            st.markdown(f"### {bond_selected} Government Bond Yields Candlestick Chart")
            bond_candlestick_data = generate_dummy_candlestick_data(
                base_price=base_yield
            )

            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=bond_candlestick_data["Date"],
                        open=bond_candlestick_data["Open"],
                        high=bond_candlestick_data["High"],
                        low=bond_candlestick_data["Low"],
                        close=bond_candlestick_data["Close"],
                    )
                ]
            )
            fig.update_layout(
                title=f"{bond_selected} Government Bond Yields Candlestick Chart",
                xaxis_title="Date",
                yaxis_title="Yield",
                width=1200,  # Set the chart width
                height=400,  # Set the chart height
            )
            st.plotly_chart(fig, use_container_width=True)

        # Footer Section
        st.markdown(
            "<footer style='text-align: center; font-size: small;'>© 2024 Capitalized. All rights reserved.</footer>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <style>
            footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #f1f1f1;
                color: #555;
                padding: 10px;
                text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


# Main application logic
if __name__ == "__main__":
    dashboard_page()
