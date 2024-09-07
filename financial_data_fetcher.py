import yfinance as yf


def get_financial_data(ticker):
    stock = yf.Ticker(ticker)

    # Extract necessary information from the ticker
    market_cap = stock.info.get("marketCap", None)
    balance_sheet = stock.balance_sheet

    # Safely get 'Total Liabilities', 'Book Value Equity', and 'Total Debt' using iloc
    total_liabilities = (
        balance_sheet.loc["Total Liabilities Net Minority Interest"].iloc[0]
        if "Total Liabilities Net Minority Interest" in balance_sheet.index
        else None
    )
    book_value_equity = (
        balance_sheet.loc["Stockholders Equity"].iloc[0]
        if "Stockholders Equity" in balance_sheet.index
        else None
    )
    total_debt = (
        balance_sheet.loc["Total Debt"].iloc[0]
        if "Total Debt" in balance_sheet.index
        else None
    )
    ltm_eps = stock.info.get("trailingEps", None)
    price_share = stock.info.get("currentPrice", None)
    volatility = stock.info.get("beta", None)

    # Extract LTM Revenue and EBITDA using iloc
    financials = stock.financials
    ltm_revenue = (
        financials.loc["Total Revenue"].iloc[0]
        if "Total Revenue" in financials.index
        else None
    )
    ltm_ebitda = (
        financials.loc["EBITDA"].iloc[0] if "EBITDA" in financials.index else None
    )

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
        "Price/ Share": price_share,
    }
