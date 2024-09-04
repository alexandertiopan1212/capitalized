import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from scipy.stats import norm
from datetime import datetime, timedelta
from sidebar import render_page_based_on_sidebar
import yfinance as yf

def monte_carlo_simulation(simulation_type, **kwargs):
    """
    Monte Carlo simulation for financial analysis (option pricing or portfolio simulation).
    """

    def mcVaR(returns, alpha=5):
        """Calculate VaR at the given confidence level."""
        return np.percentile(returns, alpha)

    def mcCVaR(returns, alpha=5):
        """Calculate CVaR (Expected Shortfall) at the given confidence level."""
        belowVaR = returns <= mcVaR(returns, alpha)
        return returns[belowVaR].mean()

    def get_data(stocks, start, end):
        """Fetch stock data using yfinance, and return mean returns and covariance matrix."""
        stockData = yf.download(stocks, start=start, end=end)['Adj Close']
        returns = stockData.pct_change()
        meanReturns = returns.mean()
        covMatrix = returns.cov()

        # Add a small value to the diagonal to make the covariance matrix positive definite
        covMatrix += np.eye(covMatrix.shape[0]) * 1e-10

        return meanReturns, covMatrix

    if simulation_type == 'option':
        # Unpack arguments for option pricing
        S = kwargs['S']
        K = kwargs['K']
        T = kwargs['T']
        r = kwargs['r']
        sigma = kwargs['sigma']
        n = kwargs.get('n', int(T * 12))  # Monthly steps by default
        M = kwargs.get('M', 10000)

        # Time step size in years (based on months)
        dt = T / n

        # Precompute constants for Monte Carlo
        nudt = (r - 0.5 * sigma ** 2) * dt
        volsdt = sigma * np.sqrt(dt)

        # Simulate M paths for the underlying asset price
        lnS = np.log(S)
        Z = np.random.normal(size=(n, M))  # Generate M random normal variables for n time steps
        delta_lnSt = nudt + volsdt * Z     # Log returns for each time step
        lnSt = lnS + np.cumsum(delta_lnSt, axis=0)  # Simulated paths for log prices
        ST = np.exp(lnSt[-1])  # Final stock price at maturity

        # Calculate the payoff for each simulation (European call option)
        payoff = np.maximum(0, ST - K)

        # Discount the average payoff to present value
        option_price = np.exp(-r * T) * np.mean(payoff)

        # Calculate the standard error
        std_error = np.std(payoff) / np.sqrt(M)

        # Plot the distribution of the final payoff using Plotly
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=payoff, nbinsx=50, histnorm='probability', name='Payoff Distribution'))

        fig.update_layout(
            title="Probability Distribution of Option Payoff",
            xaxis_title="Payoff",
            yaxis_title="Probability",
            bargap=0.1,
            showlegend=True
        )
        st.plotly_chart(fig)

        return option_price, std_error

    elif simulation_type == 'portfolio':
        # Unpack arguments for portfolio simulation
        stocks = kwargs['stocks']
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        mc_sims = kwargs.get('mc_sims', 100)
        T = kwargs.get('T', 100)
        initial_portfolio = kwargs.get('initial_portfolio', 10000)

        # Fetch stock data and calculate mean returns and covariance matrix
        meanReturns, covMatrix = get_data(stocks, start_date, end_date)

        # Initialize weights randomly
        weights = np.random.random(len(meanReturns))
        weights /= np.sum(weights)

        # Create matrices to hold simulation results
        meanM = np.full(shape=(T, len(weights)), fill_value=meanReturns)
        meanM = meanM.T
        portfolio_sims = np.full(shape=(T, mc_sims), fill_value=0.0)

        # Run Monte Carlo simulation
        for m in range(mc_sims):
            Z = np.random.normal(size=(T, len(weights)))  # Uncorrelated random variables
            L = np.linalg.cholesky(covMatrix)  # Cholesky decomposition
            daily_returns = meanM + np.inner(L, Z)  # Correlated daily returns
            portfolio_sims[:, m] = np.cumprod(np.inner(weights, daily_returns.T) + 1) * initial_portfolio

        # Create plot using Plotly
        fig = go.Figure()

        # Add traces for each simulation
        for i in range(portfolio_sims.shape[1]):
            fig.add_trace(go.Scatter(x=np.arange(0, portfolio_sims.shape[0]), 
                                     y=portfolio_sims[:, i], 
                                     mode='lines', 
                                     line=dict(width=1),
                                     showlegend=False))

        # Include stock names in the title
        stock_names = ', '.join(stocks)

        # Update layout
        fig.update_layout(
            title=f"Monte Carlo Simulation of a Stock Portfolio ({stock_names})",
            xaxis_title="Days",
            yaxis_title="Portfolio Value ($)",
            showlegend=False
        )

        st.plotly_chart(fig)

        # Calculate VaR and CVaR
        portResults = pd.Series(portfolio_sims[-1, :])

        VaR = initial_portfolio - mcVaR(portResults, alpha=5)
        CVaR = initial_portfolio - mcCVaR(portResults, alpha=5)

        st.write(f'VaR_5: ${round(VaR, 2)}')
        st.write(f'CVaR_5: ${round(CVaR, 2)}')

        return None

# Function to calculate the option price using the Binomial Tree method (American option pricing)
def binomial_tree_pricing(S, K, T, r, sigma, steps, q=0):
    # Calculate time step
    dt = T / steps

    # Calculate up and down move factors based on volatility
    u = np.exp(sigma * np.sqrt(dt))  # Up move factor
    d = 1 / u  # Down move factor

    # Calculate the risk-neutral probabilities of up and down movements
    p_up = (np.exp((r * dt) - (q * dt)) - d) / (u - d)  # Probability of up move
    p_down = 1 - p_up  # Probability of down move

    # Initialize matrices for asset prices, expected discounted value (EDV), intrinsic value (IV), and final value (FV)
    asset_prices = np.zeros((steps + 1, steps + 1))
    edv_values = np.zeros((steps + 1, steps + 1))
    iv_values = np.zeros((steps + 1, steps + 1))
    fv_values = np.zeros((steps + 1, steps + 1))

    # Step 1: Calculate asset prices for each node in the binomial tree
    for i in range(steps + 1):
        for j in range(i + 1):
            asset_prices[j, i] = S * (u ** (i - j)) * (d ** j)

    # Step 2: Initialize EDV option values at maturity using intrinsic values
    for j in range(steps + 1):
        edv_values[j, steps] = max(0, asset_prices[j, steps] - K)

    # Step 3: Backward induction to calculate EDV option values at earlier nodes
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            edv_values[j, i] = (p_up * edv_values[j, i + 1] + p_down * edv_values[j + 1, i + 1]) / np.exp(r * dt)

    # Step 4: Calculate the intrinsic value (IV) for each node
    for i in range(steps + 1):
        for j in range(i + 1):
            iv_values[j, i] = max(asset_prices[j, i] - K, 0)

    # Step 5: Calculate the final value (FV) at each node as the max of EDV and IV
    for i in range(steps + 1):
        for j in range(i + 1):
            fv_values[j, i] = max(edv_values[j, i], iv_values[j, i])

    # Final option price is the value at the root of the binomial tree
    final_option_price = fv_values[0, 0]

    # Helper function to plot the binomial tree using Plotly
    def plot_tree(tree_df, title):
        edge_x = []
        edge_y = []
        node_x = []
        node_y = []
        node_text = []

        # Midpoint for y-axis symmetry in the tree diagram
        midpoint = steps / 2

        # Generate the tree structure with coordinates for each node
        for i in range(steps + 1):
            for j in range(i + 1):
                x_pos = i
                y_pos = j - (i / 2) + midpoint  # Center the tree along the y-axis
                value = tree_df[j, i]
                node_x.append(x_pos)
                node_y.append(y_pos)
                node_text.append(f"{value:.2f}")

                # Connect parent nodes to their children
                if i < steps:
                    # Connect to the upper child
                    edge_x.extend([x_pos, x_pos + 1, None])
                    edge_y.extend([y_pos, y_pos - 0.5, None])
                    # Connect to the lower child
                    edge_x.extend([x_pos, x_pos + 1, None])
                    edge_y.extend([y_pos, y_pos + 0.5, None])

        # Create edge and node traces for the tree graph
        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=2, color='blue'), hoverinfo='none', mode='lines')
        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text, textposition="top center",
                                hoverinfo='text', marker=dict(size=10, color='red', line_width=2))

        # Set layout for the plot
        layout = go.Layout(title=title, showlegend=False, height=800, xaxis=dict(showgrid=False, zeroline=False),
                           yaxis=dict(showgrid=False, zeroline=False), template="plotly_white")

        # Return the figure object
        return go.Figure(data=[edge_trace, node_trace], layout=layout)

    # Generate and display tree graphs for asset prices, EDV, IV, and FV
    asset_fig = plot_tree(asset_prices, "Asset Price Tree")
    edv_fig = plot_tree(edv_values, "EDV Option Tree")
    iv_fig = plot_tree(iv_values, "IV Option Tree")
    fv_fig = plot_tree(fv_values, "FV Option Tree")

    # Display the plots in the Streamlit app
    st.plotly_chart(asset_fig)
    st.plotly_chart(edv_fig)
    st.plotly_chart(iv_fig)
    st.plotly_chart(fv_fig)

    # Display the final calculated option price
    st.write(f"**Final Option Price**: ${final_option_price:.2f}")

# Function to calculate the option price using Black-Scholes model for a dynamic table (European option pricing)
def black_scholes_dynamic_table(df):
    # Black-Scholes formula for European options
    def black_scholes(S, X, T, r, sigma):
        d1 = (np.log(S / X) + (r + (sigma ** 2) / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        call_price = (S * N_d1) - (X * np.exp(-r * T) * N_d2)
        return d1, d2, N_d1, N_d2, call_price

    # Convert dates to calculate time to maturity in years
    df['Grant Date'] = pd.to_datetime(df['Grant Date'])
    df['Vesting Date'] = pd.to_datetime(df['Vesting Date'])
    df['Time to Maturity'] = (df['Vesting Date'] - df['Grant Date']).dt.days + 1  # Adjust to match Excel calculation
    df['Time to Maturity'] = df['Time to Maturity'] / 365  # Convert days to years

    # Add columns for Black-Scholes results (d1, d2, N(d1), N(d2), Mesop Value)
    df['d1'] = np.nan
    df['d2'] = np.nan
    df['N(d1)'] = np.nan
    df['N(d2)'] = np.nan
    df['Mesop Value/ share'] = np.nan
    df['Mesop Value'] = np.nan

    # Perform Black-Scholes calculation for each row
    for index, row in df.iterrows():
        S = row['Spot Price (S)']
        X = row['Strike (X)']
        r = row['Risk free'] / 100  # Convert percentage to decimal
        sigma = row['Volatility'] / 100  # Convert percentage to decimal
        T = row['Time to Maturity']

        # Calculate option prices and other values using Black-Scholes
        d1, d2, N_d1, N_d2, call_price = black_scholes(S, X, T, r, sigma)
        df.at[index, 'd1'] = d1
        df.at[index, 'd2'] = d2
        df.at[index, 'N(d1)'] = N_d1
        df.at[index, 'N(d2)'] = N_d2
        df.at[index, 'Mesop Value/ share'] = call_price
        df.at[index, 'Mesop Value'] = call_price * row['Number of shares']

    # Display the resulting dataframe in Streamlit
    st.dataframe(df)
    return df

# Streamlit page to run the option models
def option_page():
    """
    Streamlit page for calculating and plotting American and European option models.
    """

    # Render sidebar elements (customized for this project)
    render_page_based_on_sidebar()

    # Title for the option valuation app
    st.title("Option Valuation")

    # Dropdown menu to select between American and European option models
    option_type = st.selectbox("Select Option Type", ["American", "European", "Monte Carlo"])

    # Input for European option using dynamic table
    if option_type == "European":
        data = {
            'Strike (X)': [450, 450, 450, 450, 1500],
            'Spot Price (S)': [400, 400, 400, 400, 2100],
            'Risk free': [5.8, 5.9, 6.0, 6.1, 5.83],  # in percentages
            'Volatility': [53.9, 53.9, 53.9, 53.9, 34.64],  # in percentages
            'Dividend yield': [0.0, 0.0, 0.0, 0.0, 0.0],  # in percentages
            'Number of shares': [20124910, 20124910, 20124910, 20124910, 20124910],
            'Grant Date': ['5/15/2023', '5/15/2023', '5/15/2023', '5/15/2023', '5/15/2023'],
            'Vesting Date': ['5/19/2023', '5/17/2024', '5/16/2025', '5/16/2026', '5/15/2025']
        }

        df_bs = pd.DataFrame(data)

        # Store the dataframe in session state for dynamic editing
        if 'df_bs' not in st.session_state:
            st.session_state.df_bs = df_bs

        # Display interactive table for Black-Scholes input
        st.subheader("Interactive Black-Scholes Input")
        df_bs = st.data_editor(df_bs, num_rows="dynamic", use_container_width=True)
        st.session_state.df_bs = df_bs

        # Button to calculate Black-Scholes results
        if st.button("Calculate"):
            black_scholes_dynamic_table(st.session_state.df_bs)

    # Input for American option pricing
    elif option_type == "American":
        # Get inputs for the American option pricing (Binomial Tree)
        S = st.number_input("Asset Value at Valuation Date (S)", value=2100.0, min_value=0.0)
        K = st.number_input("Strike Price (K)", value=1500.0, min_value=0.0)
        T = st.number_input("Maturity in Years (T)", value=2.0, min_value=0.1)
        r = st.number_input("Risk-free Rate (r)", value=0.0583, min_value=0.0, format="%.4f")
        sigma = st.number_input("Yearly Volatility (sigma)", value=0.3464, min_value=0.0, format="%.4f")
        steps = T * 12  # Approximate monthly steps

        # Button to calculate and plot the binomial tree model
        if st.button("Calculate and Plot"):
            binomial_tree_pricing(S, K, T, r, sigma, int(steps))

    # Input for Monte Carlo option pricing
    else:
        mc_option_type = st.selectbox("Select Type", ["option", "portfolio"])

        if mc_option_type == "option":
            # Option pricing input fields
            S = st.number_input("Initial stock price (S)", value=2100)
            K = st.number_input("Strike price (K)", value=1500)
            T = st.number_input("Time to maturity (years, T)", value=2.0)
            r = st.number_input("Risk-free interest rate (r)", value=0.0583)
            sigma = st.number_input("Volatility (sigma)", value=0.3464)

            if st.button('Calculate'):
                option_price, std_error = monte_carlo_simulation(
                    'option', S=S, K=K, T=T, r=r, sigma=sigma)
                
                st.write(f"Estimated Call Option Price: ${option_price:.2f}")
                st.write(f"Standard Error: ±{std_error:.2f}")

        elif mc_option_type == "portfolio":
            # Portfolio input fields
            data_s = {
            'Stock List': ['BBCA.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK', 'BMRI.JK', 'ICBP.JK']
            }

            df_s = pd.DataFrame(data_s)

            stocks = st.data_editor(df_s, num_rows="dynamic", use_container_width=True)
            
            # stocks = st.text_input("Enter up to 6 stock symbols separated by commas", value=",".join(stocks.to_list())).split(",")
            
            if len(stocks) > 6:
                st.error("You can only enter up to 6 stocks.")
            else:
                start_date = st.date_input("Start date", value=(datetime.today() - timedelta(days=300)).date())
                end_date = st.date_input("End date", value=datetime.today().date())

                if st.button('Calculate'):
                    monte_carlo_simulation('portfolio', stocks=stocks['Stock List'].to_list(), start_date=start_date, end_date=end_date)



# Main entry point for the Streamlit application
if __name__ == "__main__":
    option_page()
