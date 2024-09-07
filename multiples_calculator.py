import numpy as np


def calculate_multiples(data):
    # Handle missing values by providing default None or NaN for each ratio
    price_to_book = (
        data["Market Cap"] / data["Book Value Equity"]
        if data["Book Value Equity"]
        else np.nan
    )
    price_to_earning = (
        data["Price/ Share"] / data["LTM EPS"] if data["LTM EPS"] else np.nan
    )
    equity_value_to_revenue = (
        data["Market Cap"] / data["LTM Revenue"] if data["LTM Revenue"] else np.nan
    )
    equity_value_to_ebitda = (
        data["Market Cap"] / data["LTM EBITDA"] if data["LTM EBITDA"] else np.nan
    )
    enterprise_value_to_revenue = (
        (data["Market Cap"] + data["Total Liabilities"]) / data["LTM Revenue"]
        if data["LTM Revenue"] and data["Total Liabilities"]
        else np.nan
    )
    enterprise_value_to_ebitda = (
        (data["Market Cap"] + data["Total Liabilities"]) / data["LTM EBITDA"]
        if data["LTM EBITDA"] and data["Total Liabilities"]
        else np.nan
    )

    # Return the calculated multiples
    return {
        "Price to Book Value (Equity)": price_to_book,
        "Price to Earning Ratio (Equity)": price_to_earning,
        "Equity Value to Revenue (Equity)": equity_value_to_revenue,
        "Equity Value to EBITDA (Equity)": equity_value_to_ebitda,
        "Enterprise Value to Revenue (Enterprise)": enterprise_value_to_revenue,
        "Enterprise Value to EBITDA (Enterprise)": enterprise_value_to_ebitda,
    }
