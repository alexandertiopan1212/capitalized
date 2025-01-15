import streamlit as st
from sidebar import render_page_based_on_sidebar

import pandas as pd
from scipy.optimize import newton
import plotly.express as px


def generate_loan_amortization_df(
    loan_amount,
    interest_rate,
    tenor_years,
    repayment_mechanism,
    total_construction_months,
    start_date=None,
):
    """
    Generates a loan amortization schedule based on monthly calculations with repayments starting after construction finishes.
    """

    # Determine repayment frequency (number of payments per year)
    monthly_periods_per_year = 12
    total_monthly_periods = tenor_years * monthly_periods_per_year
    monthly_rate = (interest_rate / 100) / monthly_periods_per_year

    # Calculate the number of construction periods before repayments start
    construction_periods = int(total_construction_months)

    # Create a monthly date range starting from the start date to the end of the loan tenor
    total_timeline_monthly = construction_periods + total_monthly_periods
    monthly_date_range = pd.date_range(
        start=start_date, periods=total_timeline_monthly, freq="M"
    )

    # Initialize columns for loan amortization
    beginning_balances = []
    principal_payments = []
    interest_payments = []
    ending_balances = []

    # Set initial values
    balance = loan_amount

    # During the construction phase (no repayments)
    for _ in range(construction_periods):
        beginning_balances.append(balance)
        interest_payments.append(0)
        principal_payments.append(0)
        ending_balances.append(balance)

    # After construction, repayments start
    if interest_rate == 0:
        # Handle zero interest case
        if (
            repayment_mechanism == "Equal Installments"
            or repayment_mechanism == "Equal Principal"
        ):
            principal_payment = (
                loan_amount / total_monthly_periods
            )  # Equal principal payments

            for period in range(total_monthly_periods):
                interest_payment = 0  # No interest
                ending_balance = balance - principal_payment

                # Append values
                beginning_balances.append(balance)
                interest_payments.append(interest_payment)
                principal_payments.append(principal_payment)
                ending_balances.append(ending_balance)

                # Update balance
                balance = ending_balance
    else:
        # Case with non-zero interest rate (Equal Installments)
        if repayment_mechanism == "Equal Installments":
            payment = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** total_monthly_periods)
                / ((1 + monthly_rate) ** total_monthly_periods - 1)
            )

            for period in range(total_monthly_periods):
                interest_payment = balance * monthly_rate
                principal_payment = payment - interest_payment
                ending_balance = balance - principal_payment

                # Append values
                beginning_balances.append(balance)
                interest_payments.append(interest_payment)
                principal_payments.append(principal_payment)
                ending_balances.append(ending_balance)

                # Update balance
                balance = ending_balance

        elif repayment_mechanism == "Equal Principal":
            # Equal principal payments
            principal_payment = loan_amount / total_monthly_periods

            for period in range(total_monthly_periods):
                interest_payment = balance * monthly_rate
                ending_balance = balance - principal_payment

                # Append values
                beginning_balances.append(balance)
                interest_payments.append(interest_payment)
                principal_payments.append(principal_payment)
                ending_balances.append(ending_balance)

                # Update balance
                balance = ending_balance

    # Create the monthly amortization DataFrame
    loan_amortization_df = pd.DataFrame(
        {
            "Date": monthly_date_range,
            "Beginning Balance": beginning_balances,
            "Principal Payment": principal_payments,
            "Interest Payment": interest_payments,
            "Ending Balance": ending_balances,
        }
    )

    # loan_amortization_df = loan_amortization_df.set_index("Date")

    return loan_amortization_df


# Function to calculate growth multiplier based on frequency
def get_growth_multiplier(growth_rate, frequency):
    return {
        "Monthly": (1 + growth_rate / 100) ** (1 / 12),
        "Quarterly": (1 + growth_rate / 100) ** (1 / 4),
        "Semi-Annually": (1 + growth_rate / 100) ** (1 / 2),
        "Annually": 1 + growth_rate / 100,
    }[frequency]


# Function to generate financial data after construction with growth for revenue and operational cost
def generate_financial_data_after_construction(
    start_date,
    total_years,
    total_construction_months,
    initial_revenue,
    initial_op_cost,
    revenue_growth_rate,
    op_cost_growth_rate,
):
    total_months = total_years * 12
    total_construction_months = int(total_construction_months)
    dates = pd.date_range(start=start_date, periods=total_months, freq="M")

    revenue = []
    operational_cost = []

    revenue_growth_multiplier = get_growth_multiplier(revenue_growth_rate, "Monthly")
    op_cost_growth_multiplier = get_growth_multiplier(op_cost_growth_rate, "Monthly")

    # Fill in zeros during the construction period
    for _ in range(total_construction_months):
        revenue.append(0)
        operational_cost.append(0)

    # Calculate revenue and operational costs after construction
    current_revenue = initial_revenue
    current_op_cost = initial_op_cost
    for _ in range(total_construction_months, total_months):
        revenue.append(current_revenue)
        operational_cost.append(current_op_cost)
        current_revenue *= revenue_growth_multiplier
        current_op_cost *= op_cost_growth_multiplier

    # Create DataFrame
    financial_df = pd.DataFrame(
        {"Revenue": revenue, "Operational Cost": operational_cost}, index=dates
    )

    return financial_df


# Function to adjust display of financial data based on frequency
def resample_financial_data(financial_df, frequency):
    frequency_mapping = {
        "Monthly": "M",
        "Quarterly": "Q",
        "Semi-Annually": "6M",
        "Annually": "A",
    }

    resampled_df = financial_df.resample(frequency_mapping[frequency]).sum()
    return resampled_df


# Function to calculate depreciation
def calculate_depreciation(capex, useful_life_years, start_date, construction_duration):
    construction_duration = int(construction_duration)

    # Create the date range from start_date, covering the useful life + construction period
    periods = useful_life_years * 12 + construction_duration
    dates = pd.date_range(start=start_date, periods=periods, freq="M")
    depreciation_per_period = capex / (useful_life_years * 12)

    # Initialize depreciation values
    depreciation_values = []

    # Fill depreciation with zeros during the construction period
    for i in range(construction_duration):
        depreciation_values.append(0)

    # Fill the rest of the periods with depreciation value
    for i in range(construction_duration, len(dates)):
        depreciation_values.append(depreciation_per_period)

    # Create a depreciation DataFrame that matches the financial_df date structure
    depreciation_df = pd.DataFrame({"Date": dates, "Depreciation": depreciation_values})

    # Align the depreciation dataframe to the financial_df by merging on the 'Date' column
    depreciation_df.set_index("Date", inplace=True)

    return depreciation_df


# Function to create profit loss table with EBITDA and without Gross Profit
def create_profit_loss_table(financial_df, loan_df):

    for col in financial_df.columns:
        if col not in loan_df.columns:
            loan_df[col] = pd.NA  # Add missing columns with NaN values

    loan_df = loan_df.fillna(0)

    revenue = financial_df.loc["Revenue"]
    operational_cost = financial_df.loc["Operational Cost"]
    depreciation = financial_df.loc["Depreciation"]

    financing_cost = loan_df.loc["Interest Payment"]

    # EBITDA = Revenue - Operational Costs (no depreciation, interest, or taxes included)
    ebitda = revenue - operational_cost

    # Operating Profit = EBITDA - Depreciation
    operating_profit = ebitda - depreciation

    # Profit Before Tax = Operating Profit - Financing Cost (Interest Payment)
    profit_before_tax = operating_profit - financing_cost

    # Create DataFrame for the Profit and Loss table without Gross Profit
    profit_loss_df = pd.DataFrame(
        {
            "Revenue": revenue,
            "Operational Cost": operational_cost,
            "EBITDA": ebitda,  # Including EBITDA
            "Depreciation": depreciation,
            "Operating Profit": operating_profit,
            "Financing Cost": financing_cost,
            "Profit Before Tax": profit_before_tax,
        }
    ).T

    return profit_loss_df


# Function to calculate annual tax with carried-forward losses based on December results
def calculate_annual_tax(profit_loss_df, tax_rate):

    profit_before_tax = profit_loss_df.loc["Profit Before Tax"]

    dates = profit_before_tax.index

    # Initialize the columns for tax amount, net income after tax, and carried-forward losses
    tax_amount = pd.Series(0, index=dates)
    net_income_after_tax = pd.Series(0, index=dates)
    carried_forward_loss_column = pd.Series(0, index=dates)
    taxable_income_after_compensation = pd.Series(0, index=dates)
    compensation_used = pd.Series(0, index=dates)
    previous_years_losses = pd.Series(
        0, index=dates
    )  # Track the losses from previous years

    # Variable to track carried forward losses (list of tuples: (loss, year))
    carry_forward_losses = []

    # Get the unique years from the dates
    years = pd.to_datetime(dates).year.unique()

    for year in years:
        # Filter the dates to focus only on the last period of the year (December)
        year_dates = [date for date in dates if pd.to_datetime(date).year == year]
        last_period_of_year = [
            date for date in year_dates if pd.to_datetime(date).month == 12
        ]

        if last_period_of_year:
            year_end_date = last_period_of_year[0]
            year_profit = profit_before_tax[
                year_dates
            ].sum()  # Calculate the total profit for the year

            # Remove any losses that are older than 5 years from the carry forward list
            carry_forward_losses = [
                (loss, loss_year)
                for loss, loss_year in carry_forward_losses
                if year - loss_year <= 5
            ]

            # Calculate the total amount of losses available to compensate
            total_loss_to_compensate = sum(
                loss for loss, loss_year in carry_forward_losses
            )
            previous_years_losses[year_end_date] = total_loss_to_compensate

            if year_profit < 0:
                # If the company incurs a loss, add it to the carry forward losses
                carry_forward_losses.append((abs(year_profit), year))
                carried_forward_loss_column[year_end_date] = (
                    abs(year_profit) + total_loss_to_compensate
                )
                taxable_income_after_compensation[year_end_date] = 0
                compensation_used[year_end_date] = 0
                tax_amount[year_end_date] = 0
                # Net income after tax is simply the fiscal profit/loss minus the tax amount
                net_income_after_tax[year_end_date] = year_profit
            else:
                # If the company makes a profit, use carry forward losses to offset the profit
                loss_used_for_compensation = min(total_loss_to_compensate, year_profit)
                taxable_income = year_profit - loss_used_for_compensation
                tax_payable = taxable_income * (
                    tax_rate / 100
                )  # Taxable income after compensation, taxed at the given rate

                # Update DataFrame columns
                compensation_used[year_end_date] = loss_used_for_compensation
                taxable_income_after_compensation[year_end_date] = taxable_income
                tax_amount[year_end_date] = tax_payable
                carried_forward_loss_column[year_end_date] = (
                    total_loss_to_compensate - loss_used_for_compensation
                )
                # Net income after tax is the fiscal profit/loss minus the tax amount
                net_income_after_tax[year_end_date] = year_profit - tax_payable

                # Update the carry forward loss list based on the compensation used
                remaining_loss_to_use = loss_used_for_compensation
                updated_carry_forward_losses = []
                for loss, loss_year in carry_forward_losses:
                    if remaining_loss_to_use > 0:
                        used_amount = min(remaining_loss_to_use, loss)
                        remaining_loss = loss - used_amount
                        remaining_loss_to_use -= used_amount
                        if remaining_loss > 0:
                            updated_carry_forward_losses.append(
                                (remaining_loss, loss_year)
                            )
                    else:
                        updated_carry_forward_losses.append((loss, loss_year))
                carry_forward_losses = updated_carry_forward_losses
        else:
            # If it is not December, keep the tax and net income values as 0 for the other periods
            carried_forward_loss_column[year_dates] = carried_forward_loss_column[
                year_dates
            ].shift()
            tax_amount[year_dates] = 0
            net_income_after_tax[year_dates] = 0

    net_income_after_tax = profit_before_tax - tax_amount

    # Create the final taxation table DataFrame
    taxation_df = pd.DataFrame(
        {
            "Fiscal Profit/Loss": profit_before_tax,
            "Losses Carried Forward from Previous Years": previous_years_losses,
            "Taxable Income After Compensation": taxable_income_after_compensation,
            "Losses Used for Compensation": compensation_used,
            "Remaining Losses Carried Forward": carried_forward_loss_column,
            "Income Tax (PPh)": tax_amount,
            "Net Income After Tax": net_income_after_tax,  # Net income after tax is the fiscal profit/loss minus the income tax
        }
    ).T

    return taxation_df


# Function to create four cash flow tables without starting cash
def create_cashflow_tables_compliant(
    financial_df,
    taxation_df,
    loan_df,
    capex_drawdown_monthly_df,
    sell_fixed_assets,
    construction_duration,
    timing_frequency,
):
    """
    Create cash flow tables (operational, investment, financing) with cumulative sums depending on the selected timing frequency.

    Args:
        financial_df (pd.DataFrame): Financial data including CAPEX, Revenue, Operational Cost, etc.
        taxation_df (pd.DataFrame): Tax-related data including Income Tax.
        loan_df (pd.DataFrame): Loan data including Loan Withdrawals, Repayments, Interest Payments.
        sell_fixed_assets (float): Value of fixed assets sold.
        equity_injection (float): Equity injected into the business.
        construction_duration (int): Duration of the construction phase in months.
        timing_frequency (str): The user-selected frequency (Monthly, Quarterly, Semi-Annually, Annually).

    Returns:
        tuple: DataFrames for operational, investment, financing, and cash flow summary.
    """

    # Map the timing_frequency to Pandas resample codes
    frequency_mapping = {
        "Monthly": "M",
        "Quarterly": "Q",
        "Semi-Annually": "6M",
        "Annually": "A",
    }

    # Default to "M" (Monthly) if the timing_frequency is not recognized
    frequency = frequency_mapping.get(timing_frequency, "M")

    # Resample and cumsum helper function
    def resample_cumsum(df, frequency):
        return df.resample(frequency).sum().cumsum()

    # Convert dates to DateTimeIndex if needed
    dates = pd.to_datetime(financial_df.columns)

    construction_periods = int(construction_duration)

    for col in financial_df.columns:
        if col not in loan_df.columns:
            loan_df[col] = pd.NA  # Add missing columns with NaN values

    for col in financial_df.columns:
        if col not in capex_drawdown_monthly_df.columns:
            capex_drawdown_monthly_df[
                col
            ] = pd.NA  # Add missing columns with NaN values

    loan_df = loan_df.fillna(0)
    capex_drawdown_monthly_df = capex_drawdown_monthly_df.fillna(0)

    # Operational Cash Flow
    revenue = financial_df.loc["Revenue"].resample(frequency).sum()
    operational_cost = financial_df.loc["Operational Cost"].resample(frequency).sum()
    depreciation = financial_df.loc["Depreciation"].resample(frequency).sum()
    tax = taxation_df.loc["Income Tax (PPh)"].resample(frequency).sum()
    financing_cost = loan_df.loc["Interest Payment"].resample(frequency).sum()
    total_fixed_asset = (
        capex_drawdown_monthly_df.loc["New Capex Adjusted"].resample(frequency).sum()
    )

    # Calculate Operational Cash Flow (without IDC)
    operational_cash_flow = (
        revenue - operational_cost - depreciation * 0 - financing_cost * 0 - tax
    )

    # Investment Cash Flow: CAPEX spending during construction
    buy_fixed_asset = -total_fixed_asset
    sell_fixed_asset_series = (
        pd.Series([sell_fixed_assets] * len(dates), index=dates)
        .resample(frequency)
        .sum()
    )
    investment_cash_flow = buy_fixed_asset + sell_fixed_asset_series

    # Financing Cash Flow
    loan_withdrawal = (
        capex_drawdown_monthly_df.loc["Loan with Bank Provision and IDC"]
        .resample(frequency)
        .sum()
    )
    loan_repayment = loan_df.loc["Principal Payment"].resample(frequency).sum()
    financing_cost_repayment = loan_df.loc["Interest Payment"].resample(frequency).sum()

    # Equity Injection: Spread equity injection over construction duration
    capital_addition = (
        capex_drawdown_monthly_df.loc["Monthly Drawdowns Equity"]
        .resample(frequency)
        .sum()
    )

    # Financing Cash Flow
    financing_cash_flow = (
        loan_withdrawal + capital_addition - loan_repayment - financing_cost_repayment
    )

    # Cash Flow Summary: Summing all cash flows and calculating cumulative cash balance
    cash_change = operational_cash_flow + investment_cash_flow + financing_cash_flow
    end_balance_cash = cash_change.cumsum()

    # Create DataFrames for each cash flow table
    operational_cashflow_df = pd.DataFrame(
        {
            "Revenue": revenue,
            "Operational Cost": operational_cost,
            "Tax": tax,
            "Operational Cash Flow": operational_cash_flow,
        }
    ).T

    investment_cashflow_df = pd.DataFrame(
        {
            "Buy Fixed Asset": buy_fixed_asset,
            "Sell Fixed Asset": sell_fixed_asset_series,
            "Investment Cash Flow": investment_cash_flow,
        }
    ).T

    financing_cashflow_df = pd.DataFrame(
        {
            "Loan Withdrawal": loan_withdrawal,
            "Loan Repayment": loan_repayment,
            "Financing Cost Repayment": financing_cost_repayment,
            "Equity Injection": capital_addition,
            "Financing Cash Flow": financing_cash_flow,
        }
    ).T

    cashflow_summary_df = pd.DataFrame(
        {"Cash Change": cash_change, "End Balance Cash": end_balance_cash}
    ).T

    return (
        operational_cashflow_df,
        investment_cashflow_df,
        financing_cashflow_df,
        cashflow_summary_df,
    )


def create_balance_sheet(
    financial_df,
    taxation_df,
    cashflow_summary_df,
    financing_cashflow_df,
    capex_drawdown_monthly_df,
    timing_frequency,
):
    """
    Create a balance sheet with cumsum behavior based on the selected timing frequency.

    Args:
        financial_df (pd.DataFrame): DataFrame containing financial data (e.g., CAPEX, depreciation).
        taxation_df (pd.DataFrame): DataFrame containing tax-related data (e.g., retained earnings).
        cashflow_summary_df (pd.DataFrame): DataFrame containing the cash flow summary.
        financing_cashflow_df (pd.DataFrame): DataFrame containing financing cash flow (e.g., loans, repayments).
        timing_frequency (str): The user-selected timing frequency ("Monthly", "Quarterly", "Semi-Annually", "Annually").

    Returns:
        tuple: DataFrames for assets, liabilities, equity, and checking balance.
    """

    for col in financial_df.columns:
        if col not in capex_drawdown_monthly_df.columns:
            capex_drawdown_monthly_df[
                col
            ] = pd.NA  # Add missing columns with NaN values

    capex_drawdown_monthly_df = capex_drawdown_monthly_df.fillna(0)

    # Map the timing_frequency to Pandas resample codes
    frequency_mapping = {
        "Monthly": "M",
        "Quarterly": "Q",
        "Semi-Annually": "6M",
        "Annually": "A",
    }

    # Default to "M" (Monthly) if the timing_frequency is not recognized
    frequency = frequency_mapping.get(timing_frequency, "M")

    # Resample the data based on the frequency and calculate the cumulative sum (cumsum)
    def resample_cumsum(df, frequency):
        return df.resample(frequency).sum().cumsum()

    # Convert the index or columns (dates) to datetime if necessary
    dates = pd.to_datetime(financial_df.columns)

    # Resample CAPEX and Depreciation based on frequency
    capex = (
        capex_drawdown_monthly_df.loc["New Capex Adjusted"].resample(frequency).sum()
    )

    depreciation = financial_df.loc["Depreciation"].resample(frequency).sum()

    # Assets Table
    end_balance_cash = (
        cashflow_summary_df.loc["End Balance Cash"].resample(frequency).sum()
    )

    # Fixed assets = CAPEX - cumulative depreciation, calculated based on the chosen frequency
    fixed_assets = resample_cumsum(capex, frequency) - resample_cumsum(
        depreciation, frequency
    )

    # Total assets = Cash + Fixed Assets
    assets_df = pd.DataFrame({"Cash": end_balance_cash, "Fixed Assets": fixed_assets}).T

    # Liabilities Table
    loan_withdrawal = (
        financing_cashflow_df.loc["Loan Withdrawal"].resample(frequency).sum()
    )
    loan_repayment = (
        financing_cashflow_df.loc["Loan Repayment"].resample(frequency).sum()
    )

    # Loan balance: calculate the cumulative loan withdrawal and subtract cumulative repayments
    loan_balance = resample_cumsum(loan_withdrawal, frequency) - resample_cumsum(
        loan_repayment, frequency
    )

    # Interest payable (optional in your case, set to zero)
    interest_payable = (
        financing_cashflow_df.loc["Financing Cost Repayment"].resample(frequency).sum()
        * 0
    )

    # Total liabilities = Loan Balance + Interest Payable
    liabilities_df = pd.DataFrame({"Loan Balance": loan_balance}).T

    # Equity Table
    equity_injection = (
        financing_cashflow_df.loc["Equity Injection"].resample(frequency).sum()
    )  # Use from financing_cashflow_df
    retained_earnings = (
        taxation_df.loc["Net Income After Tax"].resample(frequency).sum().cumsum()
    )  # Retained earnings = cumulative net income after tax

    equity_df = pd.DataFrame(
        {
            "Equity Injection": resample_cumsum(
                equity_injection, frequency
            ),  # Cumulative equity injection
            "Retained Earnings": retained_earnings,
        }
    ).T

    # Calculate totals for the balance sheet
    total_assets = assets_df.sum()
    total_liabilities = liabilities_df.sum()
    total_equity = equity_df.sum()

    # Checking Table: Assets - Liabilities - Equity should be 0
    checking_balance = total_assets - (total_liabilities + total_equity)

    checking_df = pd.DataFrame(
        {
            "Total Assets": total_assets,
            "Total Equity": total_equity,
            "Total Liabilities": total_liabilities,
            "Total Liabilities + Equity": total_liabilities + total_equity,
            "Check (Should be 0)": checking_balance,
        }
    ).T

    return assets_df, liabilities_df, equity_df, checking_df


def aggregate_cash_flows_to_annual(cash_flows, frequency):
    """
    Aggregate cash flows to annual cash flows based on the frequency.

    Args:
        cash_flows (list): List of cash flows (input frequency).
        frequency (str): Frequency of the cash flows ("Monthly", "Quarterly", "Semi-Annually", "Annually").

    Returns:
        list: Aggregated cash flows to annual periods.
    """
    # Add support for semi-annual frequency
    freq_map = {"Monthly": 12, "Quarterly": 4, "Semi-Annually": 2, "Annually": 1}
    periods_per_year = freq_map.get(frequency, 1)

    if periods_per_year == 1:
        # If the cash flows are already annual, no need to aggregate
        return cash_flows

    # Aggregate the cash flows by summing over the periods_per_year
    aggregated_cash_flows = []
    for i in range(0, len(cash_flows), periods_per_year):
        annual_cash_flow = sum(cash_flows[i : i + periods_per_year])
        aggregated_cash_flows.append(annual_cash_flow)

    return aggregated_cash_flows


def calculate_irr(cash_flows, frequency="Annually"):
    """
    Calculate the IRR (Internal Rate of Return) for a series of cash flows.

    Args:
        cash_flows (list): List of cash flows, where the first value is the initial investment (negative value),
                           and subsequent values are future cash inflows.
        frequency (str): The frequency of the cash flows ("Monthly", "Quarterly", "Annually").

    Returns:
        float: The IRR for the given cash flows (annualized).
    """
    # First, aggregate the cash flows to annual cash flows
    annual_cash_flows = aggregate_cash_flows_to_annual(cash_flows, frequency)

    # Define the NPV function with an adjustable rate
    def npv_with_rate(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(annual_cash_flows))

    # Use the Newton method from scipy to solve for IRR where NPV is 0
    try:
        # Initial guess for IRR is 10% (0.1)
        irr = newton(npv_with_rate, 0.1)

        # Since the cash flows are aggregated to annual already, we can directly return the IRR
        return irr * 100  # Convert to percentage
    except RuntimeError as e:
        print("Error calculating IRR:", e)
        return None


def calculate_payback_period(cash_flows, frequency="Annually"):
    """
    Calculate the Payback Period for a series of cash flows.
    Args:
    cash_flows (list): List of cash flows, where the first value is the initial investment (negative value),
                    and subsequent values are future cash inflows.
    frequency (str): The frequency of the cash flows ("Monthly", "Quarterly", "Annually").
    Returns:
    float: The payback period in the appropriate time units (years, months, quarters).
    """
    # Map the frequency to the appropriate number of periods per year
    freq_map = {"Monthly": 12, "Quarterly": 4, "Semi-Annually": 2, "Annually": 1}
    periods_per_year = freq_map.get(frequency, 1)
    # Calculate the cumulative cash flow
    cumulative_cash_flow = 0
    for t, cash_flow in enumerate(cash_flows):
        cumulative_cash_flow += cash_flow
        # Check when the cumulative cash flow becomes positive
        if cumulative_cash_flow >= 0:
            # Calculate the fraction of the period when payback occurs
            payback_period = t / periods_per_year  # Convert periods into years
            return payback_period
    # If the cumulative cash flow never becomes positive, return None
    return None


def calculate_project_cashflow(financial_df, taxation_df, capex_drawdown_monthly_df):

    for col in financial_df.columns:
        if col not in capex_drawdown_monthly_df.columns:
            capex_drawdown_monthly_df[
                col
            ] = pd.NA  # Add missing columns with NaN values

    capex_drawdown_monthly_df = capex_drawdown_monthly_df.fillna(0)

    revenue = financial_df.loc["Revenue"]
    tax = taxation_df.loc["Income Tax (PPh)"]
    operational_cost = financial_df.loc["Operational Cost"]
    total_capex = capex_drawdown_monthly_df.loc["New Capex Adjusted"]
    ebitda = revenue - operational_cost
    project_cashflow = ebitda - total_capex - tax
    return pd.DataFrame(
        {
            "EBITDA": ebitda,
            "Tax": tax,
            "CAPEX": total_capex,
            "Project Cashflow": project_cashflow,
        }
    ).T


def calculate_equity_cashflow(
    financial_df, taxation_df, loan_df, capex_drawdown_monthly_df
):

    for col in financial_df.columns:
        if col not in loan_df.columns:
            loan_df[col] = pd.NA  # Add missing columns with NaN values

    for col in financial_df.columns:
        if col not in capex_drawdown_monthly_df.columns:
            capex_drawdown_monthly_df[
                col
            ] = pd.NA  # Add missing columns with NaN values

    capex_drawdown_monthly_df = capex_drawdown_monthly_df.fillna(0)

    loan_df = loan_df.fillna(0)
    revenue = financial_df.loc["Revenue"]
    operational_cost = financial_df.loc["Operational Cost"]
    financing_cost = loan_df.loc["Interest Payment"]
    tax = taxation_df.T.loc["Income Tax (PPh)"]
    principal_payment = loan_df.loc["Principal Payment"]
    depreciation = financial_df.loc["Depreciation"] * 0
    net_income = revenue - operational_cost - financing_cost - tax

    total_capex = capex_drawdown_monthly_df.loc["New Capex Adjusted"]
    equity_cashflow = net_income + depreciation - principal_payment - total_capex
    return pd.DataFrame(
        {
            "Revenue": revenue,
            "Operational Cost": operational_cost,
            "Financing Cost": financing_cost,
            "Tax": tax,
            "Net Income": net_income,
            "CAPEX": total_capex,
            "Principal Payment": principal_payment,
            "Equity Cashflow": equity_cashflow,
        }
    ).T


def calculate_npv(discount_rate, cash_flows, timing_frequency="Annually"):
    """
    Calculate the Net Present Value (NPV) of a series of cash flows adjusted for timing frequency.
    Parameters:
    discount_rate (float): The annual discount rate expressed as a percentage (e.g., 10 for 10%).
    cash_flows (list): A list of cash flows, where the first value is the initial investment (usually negative),
                    and subsequent values are returns in future periods.
    timing_frequency (str): The timing frequency for cash flows (options: 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually').
    Returns:
    float: The NPV of the cash flows.
    """
    # Adjust the discount rate according to the timing frequency
    frequency_mapping = {
        "Annually": 1,
        "Semi-Annually": 2,
        "Quarterly": 4,
        "Monthly": 12,
    }
    periods_per_year = frequency_mapping.get(
        timing_frequency, 1
    )  # Default to Annually if invalid timing_frequency is provided
    adjusted_discount_rate = (1 + discount_rate / 100) ** (
        1 / periods_per_year
    ) - 1  # Convert annual rate to period rate
    npv = 0
    for t in range(len(cash_flows)):
        npv += cash_flows[t] / (1 + adjusted_discount_rate) ** t
        # print(
        # f"Cash flow at time {t}: {cash_flows[t]}, Discounted: {cash_flows[t] / (1 + adjusted_discount_rate) ** t}"
        # )
    return npv


def plot_bar_chart(dataframe, variables, x_axis_label="Time", y_axis_label="Amount"):
    """
    Function to plot a bar chart with Plotly, with no decimals in values and the legend below the graph.

    Args:
        dataframe (pd.DataFrame): The input dataframe containing the data to plot.
        variables (list): The list of column names from the dataframe to display as y-axis.
        x_axis_label (str): Label for the x-axis (default: 'Time').
        y_axis_label (str): Label for the y-axis (default: 'Amount').

    Returns:
        None
    """
    # Plot bar chart using Plotly with values as integers (no decimals)
    fig = px.bar(
        dataframe[variables],  # Use the input variables
        x=dataframe.index,  # X-axis is the index of the dataframe
        y=variables,  # Y-axis uses the specified columns
        text_auto=True,  # Automatically show values
        labels={"index": x_axis_label, "value": y_axis_label},  # Custom labels
    )

    # Manually set the text and ensure no decimals
    fig.update_traces(
        texttemplate="%{y:.0f}",  # No decimals in the text
        textposition="auto",  # Position the text inside the bars
    )

    # Configure the layout
    fig.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.3,  # Position the legend below the chart
            xanchor="center",
            x=0.5,  # Center the legend horizontally
        ),
        legend_title_text=None,  # Remove the legend title
    )

    # Display the chart
    st.plotly_chart(fig)
