import pandas as pd
import numpy as np
import scipy.stats as stats
import math

def generate_break_table(df):
    # Group by 'Seniority' and sum
    df_grouped = df.groupby("Seniority").sum().reset_index()

    # Create an empty break_table with columns based on 'Security'
    break_table = pd.DataFrame(columns=df_grouped["Security"].to_list())

    # Populate break_table with calculated values
    for i in range(len(df_grouped)):
        break_table.loc[i, df_grouped["Security"][i]] = int(df_grouped["Shares Outstanding"][i] * df_grouped["Issue Price (USD)"][i])

    k = len(df_grouped)
    h = 0
    for i in range(k, k * 2 + 1, 1):
        h += 1
        for j in range(k-1, k-h, -1):
            if (k-h) > -1:
                break_table.loc[i, df_grouped["Security"][j]] = int(df_grouped["Shares Outstanding"][j] * 
                                                                    (df_grouped["Issue Price (USD)"][k-h+1] - df_grouped["Issue Price (USD)"][k-h]) * -1)

    # Fill NaN with 0
    break_table = break_table.fillna(0)

    # Remove rows with all zeros
    break_table = break_table[(break_table.T != 0).any()]

    # Reset index
    break_table = break_table.reset_index(drop=True)

    # Add a 'Total' column
    break_table['Total'] = break_table.sum(axis=1)

    # Add a total row
    totals = break_table.sum()
    break_table.loc[len(break_table)] = totals

    # Calculate 'Aggregate Value' and add 'Break Point From' and 'Break Point To' columns
    break_table['Aggregate Value'] = break_table['Total'].cumsum()
    break_table["Break Point From"] = break_table["Aggregate Value"].shift(1).fillna(0)
    break_table["Break Point To"] = break_table["Aggregate Value"]

    # Move 'Break Point From' and 'Break Point To' to the left
    columns_to_move = ['Break Point From', 'Break Point To']
    all_columns = break_table.columns.tolist()
    new_order = columns_to_move + [col for col in all_columns if col not in columns_to_move]
    break_table = break_table[new_order]

    # Drop 'Aggregate Value' column
    break_table = break_table.drop(["Aggregate Value"], axis=1)

    # Set the last 'Break Point To' to 'up to'
    break_table.loc[break_table.index[-1], 'Break Point To'] = "and up"

    return break_table


def generate_break_table_percent(df, break_table):
    # Group the DataFrame by 'Seniority' and sum the columns
    df_grouped = df.groupby("Seniority").sum().reset_index()
    
    # Create a copy of the break table
    break_table_percent = break_table.copy()

    # Calculate the percentage values for each item in df_grouped['Security']
    for i in range(len(break_table_percent)):
        for item in df_grouped["Security"]:
            break_table_percent[item][i] = 100 * (break_table_percent[item][i] / break_table_percent["Total"][i])

    # Recalculate the 'Total' column in percentage terms
    break_table_percent["Total"] = break_table_percent[df_grouped["Security"].to_list()].sum(axis=1)

    # Round the percentages to 1 decimal place
    break_table_percent[df_grouped["Security"].to_list()] = np.round(break_table_percent[df_grouped["Security"].to_list()], 1)

    return break_table_percent


def generate_break_table_bs(break_table_percent, equity_value, risk_free_rate, volatility, time_to_liquidity, dividend_yield):
    # Initialize break_table_bs with the "Strike" column
    break_table_bs = break_table_percent[["Break Point From"]].copy()
    break_table_bs.columns = ["Strike"]

    # Initialize the necessary columns with zeros
    break_table_bs["d1"] = 0
    break_table_bs["d2"] = 0
    break_table_bs["N(d1)"] = 0
    break_table_bs["N(d2)"] = 0
    break_table_bs["Call Price"] = 0
    break_table_bs["Incremental Value"] = 0
    break_table_bs["Weighted Ndi"] = 0

    # Calculate d1
    break_table_bs["d1"] = np.where(
        break_table_bs["Strike"] > 0,
        (np.log(equity_value / break_table_bs["Strike"]) + (risk_free_rate + (np.power(volatility, 2) / 2)) * time_to_liquidity) / (volatility * np.sqrt(time_to_liquidity)),
        0
    )

    # Calculate d2
    break_table_bs["d2"] = np.where(
        break_table_bs["Strike"] > 0,
        break_table_bs["d1"] - volatility * np.sqrt(time_to_liquidity),
        0
    )

    # Calculate N(d1)
    break_table_bs["N(d1)"] = np.where(
        break_table_bs["Strike"] > 0,
        stats.norm.cdf(break_table_bs["d1"]),
        1
    )

    # Calculate N(d2)
    break_table_bs["N(d2)"] = np.where(
        break_table_bs["Strike"] > 0,
        stats.norm.cdf(break_table_bs["d2"]),
        0
    )

    # Calculate the Call Price
    break_table_bs["Call Price"] = equity_value * math.exp(-dividend_yield * time_to_liquidity) * break_table_bs["N(d1)"] - \
                                   (break_table_bs["Strike"] * math.exp(-risk_free_rate * time_to_liquidity) * break_table_bs["N(d2)"])

    # Calculate the Incremental Value
    break_table_bs["Incremental Value"] = break_table_bs["Call Price"] - break_table_bs["Call Price"].shift(-1)
    break_table_bs["Incremental Value"].fillna(break_table_bs["Call Price"], inplace=True)

    # Calculate the Weighted Ndi
    break_table_bs["Weighted Ndi"] = break_table_bs["N(d1)"] - break_table_bs["N(d1)"].shift(-1)
    break_table_bs["Weighted Ndi"].fillna(break_table_bs["N(d1)"], inplace=True)

    return break_table_bs

def generate_option_allocation_table(break_table, break_table_bs, break_table_percent, df):
    # Initialize break_table_oa with "Break Point From", "Break Point To", and "Option Value"
    break_table_oa = break_table[["Break Point From", "Break Point To"]].copy()
    break_table_oa["Option Value"] = break_table_bs["Incremental Value"]

    # Group the input DataFrame by "Seniority" and sum the columns
    df_grouped = df.groupby("Seniority").sum().reset_index()

    # Add columns for each security in the grouped DataFrame to break_table_oa and initialize with 0
    security_list = df_grouped["Security"].to_list()
    break_table_oa[security_list] = 0

    # Populate the first set of values for each security in break_table_oa
    for i in range(len(df_grouped)):
        break_table_oa.loc[i, df_grouped["Security"][i]] = break_table_oa["Option Value"][i]

    # Additional calculations to populate the rest of the option allocation
    k = len(df_grouped)
    h = 0
    for i in range(k - 1, len(break_table_oa)):
        h += 1
        for j in range(k - 1, k - 1 - h, -1):
            if (k - h) > -1:
                break_table_oa.loc[i, df_grouped["Security"][j]] = break_table_oa["Option Value"][i] * break_table_percent.loc[i, df_grouped["Security"][j]] / 100

    # Calculate the total for each row
    break_table_oa["Total"] = break_table_oa[security_list].sum(axis=1)

    return break_table_oa

def calculate_break_table_ds(break_table_bs, break_table_percent, df):
    # Initialize break_table_ds with the "N(d1)" column from break_table_bs
    break_table_ds = break_table_bs[["N(d1)"]].copy()

    # Calculate the "Incremental N(d1)" by taking the difference between "N(d1)" and its shifted version
    break_table_ds["Incremental N(d1)"] = break_table_ds["N(d1)"] - break_table_ds["N(d1)"].shift(-1)
    break_table_ds["Incremental N(d1)"].fillna(break_table_ds["N(d1)"], inplace=True)

    # Group the input DataFrame by "Seniority" and sum the columns
    df_grouped = df.groupby("Seniority").sum().reset_index()

    # Select the relevant columns from break_table_percent based on the grouped security names
    selected_columns = df_grouped["Security"].to_list()
    break_table_percent_selected = break_table_percent[selected_columns]

    # Align the `Incremental N(d1)` column for multiplication and normalize it
    break_table_ds_selected = (break_table_ds[["Incremental N(d1)"] * len(selected_columns)]) / 100

    # Perform element-wise multiplication
    break_table_ds[selected_columns] = break_table_percent_selected.mul(break_table_ds_selected.values, axis=0)

    # Calculate the total across all selected columns
    break_table_ds["Total"] = break_table_ds[selected_columns].sum(axis=1)

    return break_table_ds

def calculate_estimated_volatility(df, break_table_ds, break_table_oa, equity_value, volatility):
    # Group the input DataFrame by "Seniority" and sum the columns
    df_grouped = df.groupby("Seniority").sum().reset_index()

    # Initialize the estimated_volatility DataFrame with the required indices and columns
    security_list = df_grouped["Security"].to_list()
    estimated_volatility = pd.DataFrame(index=["Weighted N(d1)", "S/Ki", "Aggregate Volatility", "Volatility for Each Class"],
                                        columns=security_list)

    # Calculate "Weighted N(d1)" as the sum of break_table_ds across the selected securities
    estimated_volatility.loc["Weighted N(d1)"] = break_table_ds[security_list].sum(axis=0)

    # Calculate "S/Ki" as equity_value divided by the sum of break_table_oa across the selected securities
    estimated_volatility.loc["S/Ki"] = equity_value / break_table_oa[security_list].sum(axis=0)

    # Set "Aggregate Volatility" to the provided volatility value
    estimated_volatility.loc["Aggregate Volatility"] = volatility

    # Calculate "Volatility for Each Class"
    estimated_volatility.loc["Volatility for Each Class"] = (estimated_volatility.loc["Weighted N(d1)"] *
                                                             estimated_volatility.loc["S/Ki"] *
                                                             estimated_volatility.loc["Aggregate Volatility"])

    return estimated_volatility

def calculate_estimated_DLOM(df, break_table_oa, estimated_volatility, time_to_liquidity, dividend_yield, risk_free_rate):
    # Define the index for the estimated_DLOM DataFrame
    index = [
        "Strike price / breakpoint",
        "Spot price",
        "Time to maturity",
        "Dividends",
        "RFR",
        "Implied volatility",
        "D1",
        "D2",
        "Put value",
        "DLOM (B/A)"
    ]
    
    # Group the input DataFrame by "Seniority" and sum the columns
    df_grouped = df.groupby("Seniority").sum().reset_index()
    
    # Initialize the estimated_DLOM DataFrame with the required indices and columns
    estimated_DLOM = pd.DataFrame(index=index, columns=df_grouped["Security"].to_list())
    
    # Populate the estimated_DLOM DataFrame
    estimated_DLOM.loc["Strike price / breakpoint"] = break_table_oa[df_grouped["Security"].to_list()].sum(axis=0)
    estimated_DLOM.loc["Spot price"] = estimated_DLOM.loc["Strike price / breakpoint"]
    estimated_DLOM.loc["Time to maturity"] = time_to_liquidity
    estimated_DLOM.loc["Dividends"] = dividend_yield
    estimated_DLOM.loc["RFR"] = risk_free_rate
    estimated_DLOM.loc["Implied volatility"] = estimated_volatility.loc["Volatility for Each Class"]
    
    # Function to calculate D1, D2, and Put value
    def calculate_d1_d2_put(estimated_DLOM):
        for col in estimated_DLOM.columns:
            spot_price = estimated_DLOM.loc["Spot price", col]
            strike_price = estimated_DLOM.loc["Strike price / breakpoint", col]
            rfr = estimated_DLOM.loc["RFR", col]
            implied_volatility = estimated_DLOM.loc["Implied volatility", col]
            time_to_maturity = estimated_DLOM.loc["Time to maturity", col]
            
            # Calculate D1
            estimated_DLOM.loc["D1", col] = (np.log(spot_price / strike_price) + 
                                             (rfr + (implied_volatility**2 / 2)) * time_to_maturity) / \
                                             (implied_volatility * np.sqrt(time_to_maturity))
            
            # Calculate D2
            estimated_DLOM.loc["D2", col] = estimated_DLOM.loc["D1", col] - (implied_volatility * np.sqrt(time_to_maturity))
            
            # Calculate Put value
            N_d1 = stats.norm.cdf(-estimated_DLOM.loc["D1", col])  # Equivalent to 1 - NORM.S.DIST(D1)
            N_d2 = stats.norm.cdf(-estimated_DLOM.loc["D2", col])  # Equivalent to 1 - NORM.S.DIST(D2)
            
            estimated_DLOM.loc["Put value", col] = (strike_price * np.exp(-rfr * time_to_maturity) * N_d2) - (spot_price * N_d1)
        
        return estimated_DLOM
    
    # Apply the function to calculate D1, D2, and Put value
    estimated_DLOM = calculate_d1_d2_put(estimated_DLOM)
    
    # Calculate DLOM (B/A)
    estimated_DLOM.loc["DLOM (B/A)"] = estimated_DLOM.loc["Put value"] / estimated_DLOM.loc["Spot price"]
    
    return estimated_DLOM

def calculate_fair_value(df, break_table_oa):
    # Group the input DataFrame by "Seniority" and sum the columns
    df_grouped = df.groupby("Seniority").sum().reset_index()

    # Initialize the fair_value DataFrame with the required indices and columns
    fair_value = pd.DataFrame(index=[
        "Fair value of share class",
        "Number of shares",
        "Fair value per share",
        "Issue price per share",
        "% change"
    ], columns=df_grouped["Security"].to_list())

    # Populate the fair_value DataFrame
    fair_value.loc["Fair value of share class"] = break_table_oa[df_grouped["Security"].to_list()].sum(axis=0)
    fair_value.loc["Number of shares"] = df_grouped["Shares Outstanding"].to_list()
    fair_value.loc["Fair value per share"] = fair_value.loc["Fair value of share class"] / fair_value.loc["Number of shares"]
    fair_value.loc["Issue price per share"] = df_grouped["Issue Price (USD)"].to_list()

    # Calculate % change only when the issue price per share is not zero
    fair_value.loc["% change"] = fair_value.apply(
        lambda row: (row["Fair value per share"] / row["Issue price per share"] - 1) if row["Issue price per share"] != 0 else 0,
        axis=0
    )

    return fair_value
