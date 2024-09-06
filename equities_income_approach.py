import streamlit as st
import pandas as pd

def equities_income_approach():
    def set_column_names_from_rows(df: pd.DataFrame, year_row: str, forecast_row: str, fill_value="") -> pd.DataFrame:
        """
        Sets new column names for the DataFrame by combining values from two specified rows ('Year' and 'Actual/Forecast').
        Handles NaN values and ensures unique column names.
        
        Parameters:
        df (pd.DataFrame): The DataFrame containing the 'Year' and 'Actual/Forecast' rows.
        year_row (str): The row name or index corresponding to 'Year'.
        forecast_row (str): The row name or index corresponding to 'Actual/Forecast'.
        fill_value (str): Value to replace NaN values in the rows (default is an empty string).
        
        Returns:
        pd.DataFrame: The DataFrame with updated column names.
        """
        # Replace NaN values in both rows with the provided fill_value
        df.loc[year_row].fillna(fill_value, inplace=True)
        df.loc[forecast_row].fillna(fill_value, inplace=True)
        
        # Combine the 'Year' and 'Actual/Forecast' rows to form new column names
        new_column_names = df.loc[year_row].astype(str) + " " + df.loc[forecast_row].astype(str)
        
        # Ensure all new column names are unique
        new_column_names = make_unique(new_column_names)
        
        # Set the new column names in the DataFrame
        df.columns = new_column_names
        
        return df

    def make_unique(column_names: pd.Series) -> pd.Series:
        """
        Ensures that column names are unique by appending a numerical suffix to duplicates.
        
        Parameters:
        column_names (pd.Series): Series of column names to be made unique.
        
        Returns:
        pd.Series: Series of unique column names.
        """
        seen = {}
        for i, name in enumerate(column_names):
            count = seen.get(name, 0)
            if count > 0:
                # If the name has been seen before, append a suffix to make it unique
                new_name = f"{name}.{count}"
                column_names[i] = new_name
            seen[name] = count + 1
        return column_names

    def calculate_financials(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates additional financial metrics such as Gross Profit, Operating Income, Net Income, and related margins.
        Drops unnecessary rows and rearranges the financial data in a logical order.
        
        Parameters:
        df (pd.DataFrame): Transposed DataFrame containing essential financial data like Revenue, COGS, etc.
        
        Returns:
        pd.DataFrame: DataFrame with calculated financial metrics and reordered rows.
        """
        df = df.copy()
        
        # Ensure numeric types for calculations
        df = df.apply(pd.to_numeric, errors='coerce', axis=1)
        
        # Calculate Gross Profit (Revenue + COGS)
        if 'Revenue' in df.index and 'COGS' in df.index:
            df.loc['Gross Profit'] = df.loc['Revenue'] + df.loc['COGS']
        
        # Calculate Gross Margin (Gross Profit / Revenue)
        if 'Gross Profit' in df.index and 'Revenue' in df.index:
            df.loc['Gross Margin'] = df.loc['Gross Profit'] / df.loc['Revenue']
        
        # Calculate Operating Income (Gross Profit + Operating Expense)
        if 'Gross Profit' in df.index and 'Operating Expense' in df.index:
            df.loc['Operating Income'] = df.loc['Gross Profit'] + df.loc['Operating Expense']
        
        # Calculate Operating Margin (Operating Income / Revenue)
        if 'Operating Income' in df.index and 'Revenue' in df.index:
            df.loc['Operating Margin'] = df.loc['Operating Income'] / df.loc['Revenue']
        
        # Calculate Income Before Taxes (Operating Income + Other Income/(Expense))
        if 'Operating Income' in df.index and 'Other Income/(Expense)' in df.index:
            df.loc['Income Before Taxes'] = df.loc['Operating Income'] + df.loc['Other Income/(Expense)']
        
        # Calculate Income Taxes (-22% * Income Before Taxes)
        if 'Income Before Taxes' in df.index:
            df.loc['Income Taxes'] = -0.22 * df.loc['Income Before Taxes']
        
        # Calculate Net Income (Income Before Taxes + Income Taxes)
        if 'Income Before Taxes' in df.index and 'Income Taxes' in df.index:
            df.loc['Net Income'] = df.loc['Income Before Taxes'] + df.loc['Income Taxes']
        
        # Calculate Net Margin (Net Income / Revenue)
        if 'Net Income' in df.index and 'Revenue' in df.index:
            df.loc['Net Margin'] = df.loc['Net Income'] / df.loc['Revenue']
        
        # Calculate EBITDA (Operating Income + Depreciation)
        if 'Operating Income' in df.index and 'Depreciation' in df.index:
            df.loc['EBITDA'] = df.loc['Operating Income'] + df.loc['Depreciation']
        
        # Calculate EBITDA Margin (EBITDA / Revenue)
        if 'EBITDA' in df.index and 'Revenue' in df.index:
            df.loc['EBITDA Margin'] = df.loc['EBITDA'] / df.loc['Revenue']
        
        # Remove unnecessary rows if present
        df = df.drop(['Year', 'Actual/Forecast'], errors='ignore')
        
        # Define the order of rows for the financial statement
        rows_order = [
            'Revenue', 'COGS', 'Gross Profit', 'Gross Margin', 'Operating Expense',
            'Operating Income', 'Operating Margin', 'Other Income/(Expense)', 
            'Income Before Taxes', 'Income Taxes', 'Net Income', 'Net Margin', 
            'Depreciation', 'EBITDA', 'EBITDA Margin'
        ]
        
        # Reorder the rows in the DataFrame
        df = df.reindex(rows_order + [i for i in df.index if i not in rows_order])
        
        return df
    
    # Initialize session state DataFrame if not already set
    if 'df_income_statement_input' not in st.session_state:
        # Sample financial data input
        data_income_statement = {
            'Year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028],
            'Actual/Forecast': ['Actual', 'Actual', 'Actual', 'Actual', 'Forecast', 'Forecast', 'Forecast', 'Forecast', 'Forecast'],
            'Revenue': [27583, 30995, 19495, 18905, 22077, 25782, 30108, 35161, 41061],
            'COGS': [-17113, -21942, -16095, -13207, -15744, -18386, -21471, -25074, -29281],
            'Operating Expense': [-2621, -2299, -2032, -1893, -2699, -2780, -2863, -2949, -3038],
            'Other Income/(Expense)': [0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Depreciation': [738, 656, 522, 422, 341, 275, 222, 179, 145]
        }
        # Create the DataFrame and transpose it
        df_income_statement_input = pd.DataFrame(data_income_statement).T
        st.session_state.df_income_statement_input = df_income_statement_input

    # UI components
    st.title("Equity Valuation - Income Approach")
    st.subheader("Project Income Statement Input")

    # Button to add a new column
    if st.button("Add New Column"):
        new_column_name = f"New Column {len(st.session_state.df_income_statement_input.columns) + 1}"
        st.session_state.df_income_statement_input[new_column_name] = [None] * len(st.session_state.df_income_statement_input)

    # Button to delete the last column
    if st.button("Delete Last Column") and len(st.session_state.df_income_statement_input.columns) > 0:
        st.session_state.df_income_statement_input.drop(st.session_state.df_income_statement_input.columns[-1], axis=1, inplace=True)

    # Display the data editor for the DataFrame
    st.session_state.df_income_statement_input = st.data_editor(
        set_column_names_from_rows(st.session_state.df_income_statement_input, "Year", "Actual/Forecast"), 
        num_rows="dynamic", use_container_width=True
    )

    # Display current assets balance sheet inputs only if income statement has been generated
    st.subheader("Projected Balance Sheet - Current Assets Input")

    # Initialize current assets balance sheet if not already in session state
    if 'df_current_assets_input' not in st.session_state:
        data_current_assets = {
            'Cash & Equivalent Cash': [4426, 2595, 4876, 1647, 5511, 8573, 12223, 16563, 21706],
            'Trade Receivables': [3051, 4292, 1894, 3708, 2994, 3496, 4083, 4768, 5568],
            'Non-trade Receivables': [471, 478, 38, 1, 1, 1, 1, 1, 1],
            'Inventories': [2894, 3649, 2079, 1802, 2366, 2763, 3226, 3768, 4400],
            'Supplies': [56, 107, 128, 149, 149, 149, 149, 149, 149]
        }
        df_current_assets_input = pd.DataFrame(data_current_assets).T
        df_current_assets_input.columns = st.session_state.df_income_statement_input.columns
        st.session_state.df_current_assets_input = df_current_assets_input

    # Editable data editor for the balance sheet
    st.session_state.df_current_assets_input = st.data_editor(st.session_state.df_current_assets_input, num_rows="dynamic", use_container_width=True)

    # Display non current assets balance sheet inputs only if income statement has been generated
    st.subheader("Projected Balance Sheet - Non Current Assets Input")

    # Initialize non current assets balance sheet if not already in session state
    if 'df_non_current_assets_input' not in st.session_state:
        data_non_current_assets = {
            'Fixed Asset': [4421, 3585, 2718, 2085, 1745, 1469, 1247, 1068, 923],
            'Pre-operating Cost': [0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        df_non_current_assets_input = pd.DataFrame(data_non_current_assets).T
        df_non_current_assets_input.columns = st.session_state.df_income_statement_input.columns
        st.session_state.df_non_current_assets_input = df_non_current_assets_input

    # Editable data editor for the balance sheet
    st.session_state.df_non_current_assets_input = st.data_editor(st.session_state.df_non_current_assets_input, num_rows="dynamic", use_container_width=True)

    # Display projected liabilities balance sheet inputs
    st.subheader("Projected Balance Sheet - Liabilities Input")

    # Initialize liabilities balance sheet input if not already in session state
    if 'df_liabilities_input' not in st.session_state:
        data_liabilities = {
            'Trade Payables': [1963, 1409, 1452, 1319, 1453, 1696, 1981, 2313, 2702],
            "Customer's Deposit": [455, 212, 93, 126, 126, 126, 126, 126, 126],
            'Tax Payables': [26, 23, 65, 93, 93, 93, 93, 93, 93],
            'Lease Liabilities': [168, 35, 0, 0, 0, 0, 0, 0, 0],
            'Bank Loan': [576, 0, 0, 0, 0, 0, 0, 0, 0],
            'Shareholder Loan': [0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        df_liabilities_input = pd.DataFrame(data_liabilities).T
        df_liabilities_input.columns = st.session_state.df_income_statement_input.columns  # Ensure columns match the income statement
        st.session_state.df_liabilities_input = df_liabilities_input

    # Editable data editor for the liabilities balance sheet
    st.session_state.df_liabilities_input = st.data_editor(st.session_state.df_liabilities_input, num_rows="dynamic", use_container_width=True)

    # Display projected equity balance sheet inputs only if the income statement has been generated
    st.subheader("Projected Balance Sheet - Equity Input")

    # Initialize equity balance sheet input if not already in session state
    if 'df_equity_input' not in st.session_state:
        data_equity = {
            'Paid-up Capital': [2200, 2200, 2200, 2200, 2200, 2200, 2200, 2200, 2200],
            'Retained Earnings': [9864, 12125, 8317, 8177, 5654, 8489, 12090, 16594, 22161],
            'Income Current Year': [801, 43, -47, 228, 2835, 3601, 4504, 5567, 6818],
            'Cash Dividend': [-733, -1339, -348, -2751, 0, 0, 0, 0, 0]  # Assuming the rest are 0 since not provided
        }
        df_equity_input = pd.DataFrame(data_equity).T
        df_equity_input.columns = st.session_state.df_income_statement_input.columns  # Ensure columns match the income statement
        st.session_state.df_equity_input = df_equity_input

    # Editable data editor for the equity balance sheet
    st.session_state.df_equity_input = st.data_editor(st.session_state.df_equity_input, num_rows="dynamic", use_container_width=True)

    # Filter only 'Forecast' columns based on the 'Actual/Forecast' row
    st.session_state.forecast_columns = st.session_state.df_income_statement_input.loc['Actual/Forecast'] == 'Forecast'
    st.session_state.forecast_columns = st.session_state.df_income_statement_input.columns[st.session_state.forecast_columns]
        
    # Append "Terminal" to the forecast columns
    st.session_state.forecast_columns_with_terminal = st.session_state.forecast_columns.append(pd.Index(['Terminal']))

    if 'df_discount_factor' not in st.session_state:
        data_discount_factor = {
            'Discount Factor': [0.880206897, 0.829867021, 0.782406131, 0.737659574, 0.695472116, 0.695472116]
        }
        df_discount_factor = pd.DataFrame(data_discount_factor).T 
        df_discount_factor.columns = st.session_state.forecast_columns_with_terminal
        st.session_state.df_discount_factor = df_discount_factor
    
    st.session_state.df_discount_factor = st.data_editor(st.session_state.df_discount_factor, num_rows="dynamic", use_container_width=True)

    st.session_state.long_term_growth = st.number_input("Enter Long Term Growth (in decimal)", value=0.03, step=0.01)
    st.session_state.wacc = st.number_input("Enter WACC (in decimal)", value=0.125, step=0.01)

    # Generate the projected income statement
    if st.button("Generate Forecasting Table"):
        # Ensure df_ia is updated correctly
        st.session_state.df_income_statement_result = st.session_state.df_income_statement_input.copy()
        st.session_state.df_income_statement_result = calculate_financials(st.session_state.df_income_statement_result)
        
        # Display the projected income statement
        st.subheader("Projected Income Statement")
        st.dataframe(st.session_state.df_income_statement_result, use_container_width=True, height=560)

        # Calculate Current 
        st.session_state.df_current_assets_result = st.session_state.df_current_assets_input.copy()
        st.session_state.df_current_assets_result.loc["Current Assets"] = st.session_state.df_current_assets_result.sum(axis=0)

        # Display the non current assets
        st.subheader("Projected Balance Sheet - Current Assets")
        st.dataframe(st.session_state.df_current_assets_result, use_container_width=True)

        # Calculate Non Current 
        st.session_state.df_non_current_assets_result = st.session_state.df_non_current_assets_input.copy()
        st.session_state.df_non_current_assets_result.loc["Non Current Assets"] = st.session_state.df_non_current_assets_result.sum(axis=0)

        # Display the non current assets
        st.subheader("Projected Balance Sheet - Non Current Assets")
        st.dataframe(st.session_state.df_non_current_assets_result, use_container_width=True)

        # Display total assets
        if 'df_total_assets' not in st.session_state:
            # Create a new DataFrame with the same columns as current and non-current assets
            st.session_state.df_total_assets = pd.DataFrame(columns=st.session_state.df_current_assets_result.columns)

        # Calculate Total Assets
        st.session_state.df_total_assets.loc["Total Assets"] = st.session_state.df_current_assets_result.loc["Current Assets"] + st.session_state.df_non_current_assets_result.loc["Non Current Assets"]

        # Display Total Assets DataFrame
        st.subheader("Project Balance Sheet - Total Assets")
        st.dataframe(st.session_state.df_total_assets, use_container_width=True)

        # Calculate Projected Liabilities
        st.session_state.df_liabilities_result = st.session_state.df_liabilities_input.copy()
        st.session_state.df_liabilities_result.loc["Total Liabilities"] = st.session_state.df_liabilities_result.sum(axis=0)

        # Display the projected liabilities
        st.subheader("Projected Balance Sheet - Liabilities")
        st.dataframe(st.session_state.df_liabilities_result, use_container_width=True)

        # Calculate Projected Equity
        st.session_state.df_equity_result = st.session_state.df_equity_input.copy()
        st.session_state.df_equity_result.loc["Total Equity"] = st.session_state.df_equity_result.sum(axis=0)

        # Display the projected equity
        st.subheader("Projected Balance Sheet - Equity")
        st.dataframe(st.session_state.df_equity_result, use_container_width=True)

        # Display total liabilities & equities
        if 'df_total_liabilities_equities' not in st.session_state:
            # Create a new DataFrame with the same columns as the liabilities and equity inputs
            st.session_state.df_total_liabilities_equities = pd.DataFrame(columns=st.session_state.df_liabilities_result.columns)

        # Calculate Total Liabilities & Equities
        st.session_state.df_total_liabilities_equities.loc["Total Liabilities & Equities"] = (
            st.session_state.df_liabilities_result.loc["Total Liabilities"] + 
            st.session_state.df_equity_result.loc["Total Equity"]
        )

        # Display the total liabilities & equities
        st.subheader("Total Liabilities & Equities")
        st.dataframe(st.session_state.df_total_liabilities_equities, use_container_width=True)


        # Ensure that both current assets and liabilities exist in session state
        if 'df_current_assets_result' in st.session_state and 'df_liabilities_result' in st.session_state:
            # Create a new DataFrame for Working Capital results
            df_working_capital_result = pd.DataFrame(columns=st.session_state.df_current_assets_result.columns)

            # Display Trade Receivables, Non-trade Receivables, Inventories, Supplies
            df_working_capital_result.loc["Trade Receivables"] = st.session_state.df_current_assets_result.loc["Trade Receivables"]
            df_working_capital_result.loc["Non-trade Receivables"] = st.session_state.df_current_assets_result.loc["Non-trade Receivables"]
            df_working_capital_result.loc["Inventories"] = st.session_state.df_current_assets_result.loc["Inventories"]
            df_working_capital_result.loc["Supplies"] = st.session_state.df_current_assets_result.loc["Supplies"]

            # Display Trade Payables, Customer's Deposit, Tax Payables from liabilities
            df_working_capital_result.loc["Trade Payables"] = st.session_state.df_liabilities_result.loc["Trade Payables"]
            df_working_capital_result.loc["Customer's Deposit"] = st.session_state.df_liabilities_result.loc["Customer's Deposit"]
            df_working_capital_result.loc["Tax Payables"] = st.session_state.df_liabilities_result.loc["Tax Payables"]

            # Calculate Working Capital: Current Assets - (Trade Payables + Customer's Deposit + Tax Payables)
            df_working_capital_result.loc["Working Capital"] = (
                st.session_state.df_current_assets_result.loc["Trade Receivables"] +
                st.session_state.df_current_assets_result.loc["Non-trade Receivables"] +
                st.session_state.df_current_assets_result.loc["Inventories"] +
                st.session_state.df_current_assets_result.loc["Supplies"] -
                st.session_state.df_liabilities_result.loc["Trade Payables"] -
                st.session_state.df_liabilities_result.loc["Customer's Deposit"] -
                st.session_state.df_liabilities_result.loc["Tax Payables"]
            )

            # Calculate Change in Working Capital (differences between periods)
            df_working_capital_result.loc["Change in Working Capital"] = df_working_capital_result.loc["Working Capital"].diff()

            # Display the working capital and change in working capital
            st.subheader("Projected Working Capital and Change in Working Capital")
            st.dataframe(df_working_capital_result, use_container_width=True)
        else:
            st.write("Please generate both Current Assets and Liabilities first.")

        # Filter only 'Forecast' columns based on the 'Actual/Forecast' row
        forecast_columns = st.session_state.df_income_statement_input.loc['Actual/Forecast'] == 'Forecast'
        forecast_columns = st.session_state.df_income_statement_input.columns[forecast_columns]
        
        # Append "Terminal" to the forecast columns
        forecast_columns_with_terminal = forecast_columns.append(pd.Index(['Terminal']))

        # Calculate Free Cash Flow (Net Income + Depreciation - Change in Working Capital)
        df_free_cash_flow_result = pd.DataFrame(columns=forecast_columns_with_terminal)
        df_free_cash_flow_result.loc["Net Income"] = st.session_state.df_income_statement_result.loc["Net Income"]
        df_free_cash_flow_result.loc["Depreciation"] = st.session_state.df_income_statement_result.loc["Depreciation"]
        df_free_cash_flow_result.loc["Change in Working Capital"] = df_working_capital_result.loc["Change in Working Capital"]

        # FCF = Net Income + Depreciation - Change in Working Capital
        df_free_cash_flow_result.loc["Free Cash Flow"] = (
            df_free_cash_flow_result.loc["Net Income"] +
            df_free_cash_flow_result.loc["Depreciation"] -
            df_free_cash_flow_result.loc["Change in Working Capital"]
        )

        # Calculate Terminal Value based on user inputs for Long Term Growth and WACC
        last_forecast_fcf = df_free_cash_flow_result.loc["Free Cash Flow"].iloc[-2]
        if st.session_state.wacc > st.session_state.long_term_growth:  # Ensure WACC is greater than long-term growth
            terminal_value_fcf = last_forecast_fcf * (1 + st.session_state.long_term_growth) / (st.session_state.wacc - st.session_state.long_term_growth)
        else:
            terminal_value_fcf = 0  # Default to 0 if WACC is less than or equal to Long Term Growth

        df_free_cash_flow_result.loc["Free Cash Flow", "Terminal"] = terminal_value_fcf

        # Get discount factors from session state
        df_discount_factor = st.session_state.df_discount_factor

        # Multiply Free Cash Flow by discount factor to get Present Value of FCF
        df_present_value_fcf = df_free_cash_flow_result.loc["Free Cash Flow"] * df_discount_factor.loc["Discount Factor"]
        df_free_cash_flow_result.loc["Present Value of Free Cash Flow"] = df_present_value_fcf
        total_enterprise_value = df_free_cash_flow_result.loc["Present Value of Free Cash Flow"].sum(axis=0)


        # Display the Free Cash Flow table
        st.subheader("Projected Free Cash Flow (FCF)")
        st.dataframe(df_free_cash_flow_result, use_container_width=True)
        st.write(f"### Total Enterprise Value is: **{total_enterprise_value:,.2f}**")