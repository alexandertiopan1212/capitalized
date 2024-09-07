import numpy as np
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
import streamlit as st


def monte_carlo_simulation(simulation_type, **kwargs):
    def mcVaR(returns, alpha=5):
        return np.percentile(returns, alpha)

    def mcCVaR(returns, alpha=5):
        belowVaR = returns <= mcVaR(returns, alpha)
        return returns[belowVaR].mean()

    def get_data(stocks, start, end):
        stockData = yf.download(stocks, start=start, end=end)["Adj Close"]
        returns = stockData.pct_change()
        meanReturns = returns.mean()
        covMatrix = returns.cov()
        covMatrix += np.eye(covMatrix.shape[0]) * 1e-10
        return meanReturns, covMatrix

    if simulation_type == "option":
        S = kwargs["S"]
        K = kwargs["K"]
        T = kwargs["T"]
        r = kwargs["r"]
        sigma = kwargs["sigma"]
        n = kwargs.get("n", int(T * 12))
        M = kwargs.get("M", 10000)

        dt = T / n
        nudt = (r - 0.5 * sigma**2) * dt
        volsdt = sigma * np.sqrt(dt)
        lnS = np.log(S)
        Z = np.random.normal(size=(n, M))
        delta_lnSt = nudt + volsdt * Z
        lnSt = lnS + np.cumsum(delta_lnSt, axis=0)
        ST = np.exp(lnSt[-1])
        payoff = np.maximum(0, ST - K)
        option_price = np.exp(-r * T) * np.mean(payoff)
        std_error = np.std(payoff) / np.sqrt(M)

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=payoff, nbinsx=50, histnorm="probability", name="Payoff Distribution"
            )
        )
        fig.update_layout(
            title="Probability Distribution of Option Payoff",
            xaxis_title="Payoff",
            yaxis_title="Probability",
            bargap=0.1,
            showlegend=True,
        )
        st.plotly_chart(fig)

        return option_price, std_error

    elif simulation_type == "portfolio":
        stocks = kwargs["stocks"]
        start_date = kwargs["start_date"]
        end_date = kwargs["end_date"]
        mc_sims = kwargs.get("mc_sims", 100)
        T = kwargs.get("T", 100)
        initial_portfolio = kwargs.get("initial_portfolio", 10000)

        meanReturns, covMatrix = get_data(stocks, start_date, end_date)
        weights = np.random.random(len(meanReturns))
        weights /= np.sum(weights)
        meanM = np.full(shape=(T, len(weights)), fill_value=meanReturns)
        meanM = meanM.T
        portfolio_sims = np.full(shape=(T, mc_sims), fill_value=0.0)

        for m in range(mc_sims):
            Z = np.random.normal(size=(T, len(weights)))
            L = np.linalg.cholesky(covMatrix)
            daily_returns = meanM + np.inner(L, Z)
            portfolio_sims[:, m] = (
                np.cumprod(np.inner(weights, daily_returns.T) + 1) * initial_portfolio
            )

        fig = go.Figure()
        for i in range(portfolio_sims.shape[1]):
            fig.add_trace(
                go.Scatter(
                    x=np.arange(0, portfolio_sims.shape[0]),
                    y=portfolio_sims[:, i],
                    mode="lines",
                    line=dict(width=1),
                    showlegend=False,
                )
            )
        fig.update_layout(
            title=f"Monte Carlo Simulation of a Stock Portfolio ({', '.join(stocks)})",
            xaxis_title="Days",
            yaxis_title="Portfolio Value ($)",
            showlegend=False,
        )
        st.plotly_chart(fig)

        portResults = pd.Series(portfolio_sims[-1, :])
        VaR = initial_portfolio - mcVaR(portResults, alpha=5)
        CVaR = initial_portfolio - mcCVaR(portResults, alpha=5)

        st.write(f"VaR_5: ${round(VaR, 2)}")
        st.write(f"CVaR_5: ${round(CVaR, 2)}")

        return None
