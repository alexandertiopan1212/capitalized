import pandas as pd
from financial_data_fetcher import get_financial_data
from multiples_calculator import calculate_multiples


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

    # Convert the list of dictionaries into a DataFrame and replace NaN values with averages
    df = pd.DataFrame(data_list)
    num_cols = [
        "Price to Book Value (Equity)",
        "Price to Earning Ratio (Equity)",
        "Equity Value to Revenue (Equity)",
        "Equity Value to EBITDA (Equity)",
        "Enterprise Value to Revenue (Enterprise)",
        "Enterprise Value to EBITDA (Enterprise)",
    ]
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

    return df
