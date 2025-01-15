import pandas as pd
import numpy as np
from datetime import datetime
from scipy.optimize import newton
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")


def generate_capex_drawdown(
    start_date,
    total_construction_months,
    total_capex,
    equity_percentage,
    bank_provision_percentage,
    interest_rate,
):
    percentages = np.full(total_construction_months, 1 / total_construction_months)
    equity_capex, loan_capex = equity_percentage * total_capex / 100, total_capex * (
        1 - equity_percentage / 100
    )

    loan_drawdown_per_period = percentages * loan_capex
    equity_drawdown_per_period = percentages * equity_capex
    bank_provision_fee = bank_provision_percentage / 100 * loan_drawdown_per_period
    loan_with_bank_provision = loan_drawdown_per_period + bank_provision_fee

    cumulative_loan_drawdown = np.cumsum(loan_with_bank_provision)
    idc_list = cumulative_loan_drawdown * interest_rate / 1200
    loan_with_provision_idc = loan_with_bank_provision + idc_list

    new_capex_drawdown = equity_drawdown_per_period + loan_with_provision_idc
    drawdown_dates = pd.date_range(
        start=start_date, periods=total_construction_months, freq="M"
    )

    capex_drawdown_monthly_df = pd.DataFrame(
        {
            "Monthly Drawdowns Equity": equity_drawdown_per_period,
            "Monthly Drawdowns Loan": loan_drawdown_per_period,
            "Bank Provision Fee": bank_provision_fee,
            "Loan with Bank Provision": loan_with_bank_provision,
            "IDC": idc_list,
            "Loan with Bank Provision and IDC": loan_with_provision_idc,
            "New Capex Adjusted": new_capex_drawdown,
        },
        index=drawdown_dates,
    )

    return capex_drawdown_monthly_df

def generate_loan_amortization_df(
    loan_amount, interest_rate, tenor_years, repayment_mechanism,
    total_construction_months, start_date=None
):
    monthly_periods_per_year = 12
    total_monthly_periods = tenor_years * monthly_periods_per_year
    monthly_rate = (interest_rate / 100) / monthly_periods_per_year

    construction_periods = int(total_construction_months)
    total_timeline_monthly = construction_periods + total_monthly_periods
    monthly_date_range = pd.date_range(start=start_date, periods=total_timeline_monthly, freq="M")

    # Initialize arrays
    beginning_balances = np.full(total_timeline_monthly, loan_amount, dtype=float)
    principal_payments = np.zeros(total_timeline_monthly, dtype=float)
    interest_payments = np.zeros(total_timeline_monthly, dtype=float)
    ending_balances = np.full(total_timeline_monthly, loan_amount, dtype=float)

    balance = loan_amount

    # No repayments during the construction phase
    if interest_rate == 0:
        principal_payment = loan_amount / total_monthly_periods
        interest_payment = 0
        for period in range(construction_periods, total_timeline_monthly):
            beginning_balances[period] = balance
            principal_payments[period] = principal_payment
            interest_payments[period] = interest_payment
            balance -= principal_payment
            ending_balances[period] = balance
    else:
        if repayment_mechanism == "Equal Installments":
            payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_monthly_periods) / \
                      ((1 + monthly_rate) ** total_monthly_periods - 1)
            for period in range(construction_periods, total_timeline_monthly):
                interest_payment = balance * monthly_rate
                principal_payment = payment - interest_payment
                beginning_balances[period] = balance
                principal_payments[period] = principal_payment
                interest_payments[period] = interest_payment
                balance -= principal_payment
                ending_balances[period] = balance
        elif repayment_mechanism == "Equal Principal":
            principal_payment = loan_amount / total_monthly_periods
            for period in range(construction_periods, total_timeline_monthly):
                interest_payment = balance * monthly_rate
                beginning_balances[period] = balance
                principal_payments[period] = principal_payment
                interest_payments[period] = interest_payment
                balance -= principal_payment
                ending_balances[period] = balance

    # Create the DataFrame
    loan_amortization_df = pd.DataFrame(
        {
            "Beginning Balance": beginning_balances,
            "Principal Payment": principal_payments,
            "Interest Payment": interest_payments,
            "Ending Balance": ending_balances,
        },
        index=monthly_date_range
    )

    return loan_amortization_df

def generate_financial_df(
    start_date, total_years, total_construction_months, initial_revenue, initial_op_cost,
    revenue_growth_rate, op_cost_growth_rate, capex, useful_life_years
):
    total_months = total_years * 12
    total_construction_months = int(total_construction_months)
    dates = pd.date_range(start=start_date, periods=total_months, freq="M")

    # Revenue and Operational Cost Growth Multipliers
    revenue_growth_multiplier = (1 + revenue_growth_rate / 100) ** (1 / 12)
    op_cost_growth_multiplier = (1 + op_cost_growth_rate / 100) ** (1 / 12)

    # Initializing lists for revenue and costs
    revenue, operational_cost = [0] * total_construction_months, [0] * total_construction_months

    current_revenue = initial_revenue
    current_op_cost = initial_op_cost

    for _ in range(total_construction_months, total_months):
        revenue.append(current_revenue)
        operational_cost.append(current_op_cost)
        current_revenue *= revenue_growth_multiplier
        current_op_cost *= op_cost_growth_multiplier

    # Depreciation Calculation
    depreciation_per_period = capex / (useful_life_years * 12)
    depreciation = [0] * total_construction_months + [depreciation_per_period] * (total_months - total_construction_months)

    # Creating Financial DataFrame
    financial_df = pd.DataFrame(
        {"Revenue": revenue, "Operational Cost": operational_cost, "Depreciation": depreciation},
        index=dates
    )

    return financial_df

def create_profit_loss_table(financial_df, loan_df):
    # Ensure alignment between financial and loan dataframes
    loan_df = loan_df.reindex(financial_df.index).fillna(0)

    # Extract necessary columns
    revenue = financial_df["Revenue"]
    operational_cost = financial_df["Operational Cost"]
    depreciation = financial_df["Depreciation"]
    financing_cost = loan_df["Interest Payment"]

    # Calculate metrics
    ebitda = revenue - operational_cost
    operating_profit = ebitda - depreciation
    profit_before_tax = operating_profit - financing_cost

    # Create profit loss DataFrame
    profit_loss_df = pd.DataFrame({
        "Revenue": revenue,
        "Operational Cost": operational_cost,
        "EBITDA": ebitda,
        "Depreciation": depreciation,
        "Operating Profit": operating_profit,
        "Financing Cost": financing_cost,
        "Profit Before Tax": profit_before_tax
    })

    return profit_loss_df

def calculate_annual_tax(profit_loss_df, tax_rate):
    
    profit_loss_df = profit_loss_df.T
    
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
    )

    return taxation_df


def create_cashflow_tables_compliant(
    financial_df, taxation_df, loan_df, capex_drawdown_monthly_df, sell_fixed_assets, construction_duration
):

    dates = pd.to_datetime(financial_df.index)

    # Ensure alignment and fill missing columns with zeros
    loan_df = loan_df.reindex(financial_df.index, fill_value=0)
    capex_drawdown_monthly_df = capex_drawdown_monthly_df.reindex(financial_df.index, fill_value=0)

    # Operational Cash Flow
    revenue = financial_df["Revenue"]
    operational_cost = financial_df["Operational Cost"]
    depreciation = financial_df["Depreciation"]
    tax = taxation_df["Income Tax (PPh)"]
    financing_cost = loan_df["Interest Payment"]

    operational_cash_flow = revenue - operational_cost - tax

    # Investment Cash Flow
    total_fixed_asset = capex_drawdown_monthly_df["New Capex Adjusted"]
    buy_fixed_asset = -total_fixed_asset
    sell_fixed_asset_series = pd.Series([sell_fixed_assets] * len(dates), index=dates)
    investment_cash_flow = buy_fixed_asset + sell_fixed_asset_series

    # Financing Cash Flow
    loan_withdrawal = capex_drawdown_monthly_df["Loan with Bank Provision and IDC"]
    loan_repayment = loan_df["Principal Payment"]
    financing_cost_repayment = loan_df["Interest Payment"]
    capital_addition = capex_drawdown_monthly_df["Monthly Drawdowns Equity"]

    financing_cash_flow = loan_withdrawal + capital_addition - loan_repayment - financing_cost_repayment

    # Cash Flow Summary
    cash_change = operational_cash_flow + investment_cash_flow + financing_cash_flow
    end_balance_cash = cash_change.cumsum()

    # DataFrames
    operational_cashflow_df = pd.DataFrame({
        "Revenue": revenue,
        "Operational Cost": operational_cost,
        "Tax": tax,
        "Operational Cash Flow": operational_cash_flow,
    })

    investment_cashflow_df = pd.DataFrame({
        "Buy Fixed Asset": buy_fixed_asset,
        "Sell Fixed Asset": sell_fixed_asset_series,
        "Investment Cash Flow": investment_cash_flow,
    })

    financing_cashflow_df = pd.DataFrame({
        "Loan Withdrawal": loan_withdrawal,
        "Loan Repayment": loan_repayment,
        "Financing Cost Repayment": financing_cost_repayment,
        "Equity Injection": capital_addition,
        "Financing Cash Flow": financing_cash_flow,
    })

    cashflow_summary_df = pd.DataFrame({
        "Cash Change": cash_change,
        "End Balance Cash": end_balance_cash
    })

    return operational_cashflow_df, investment_cashflow_df, financing_cashflow_df, cashflow_summary_df


def create_balance_sheet(
    financial_df,
    taxation_df,
    cashflow_summary_df,
    financing_cashflow_df,
    capex_drawdown_monthly_df
):

    # Ensure alignment between DataFrames, filling missing columns with zeros
    capex_drawdown_monthly_df = capex_drawdown_monthly_df.reindex(financial_df.index, fill_value=0)

    # Cash balance and fixed assets calculation
    end_balance_cash = cashflow_summary_df["End Balance Cash"]
    capex = capex_drawdown_monthly_df["New Capex Adjusted"]
    depreciation = financial_df["Depreciation"]
    fixed_assets = capex.cumsum() - depreciation.cumsum()

    # Total assets (cash + fixed assets)
    assets_df = pd.DataFrame({"Cash": end_balance_cash, "Fixed Assets": fixed_assets}).T

    # Loan balance (cumulative withdrawals - repayments)
    loan_withdrawal = financing_cashflow_df["Loan Withdrawal"]
    loan_repayment = financing_cashflow_df["Loan Repayment"]
    loan_balance = loan_withdrawal.cumsum() - loan_repayment.cumsum()

    # Liabilities (loan balance)
    liabilities_df = pd.DataFrame({"Loan Balance": loan_balance}).T

    # Equity (cumulative equity injections + retained earnings)
    equity_injection = financing_cashflow_df["Equity Injection"].cumsum()
    retained_earnings = taxation_df["Net Income After Tax"].cumsum()
    equity_df = pd.DataFrame({
        "Equity Injection": equity_injection,
        "Retained Earnings": retained_earnings
    }).T

    # Checking balance (Assets - Liabilities - Equity)
    total_assets = assets_df.sum()
    total_liabilities = liabilities_df.sum()
    total_equity = equity_df.sum()
    checking_balance = total_assets - (total_liabilities + total_equity)

    checking_df = pd.DataFrame({
        "Total Assets": total_assets,
        "Total Liabilities": total_liabilities,
        "Total Equity": total_equity,
        "Check (Should be 0)": checking_balance
    }).T

    return assets_df.T, liabilities_df.T, equity_df.T, checking_df.T


def calculate_project_cashflow(financial_df, taxation_df, capex_drawdown_monthly_df):

    # Ensure alignment between financial_df and capex_drawdown_monthly_df
    capex_drawdown_monthly_df = capex_drawdown_monthly_df.reindex(financial_df.index, fill_value=0)

    # Calculate relevant financial metrics
    revenue = financial_df["Revenue"]
    tax = taxation_df["Income Tax (PPh)"]
    operational_cost = financial_df["Operational Cost"]
    total_capex = capex_drawdown_monthly_df["New Capex Adjusted"]
    
    ebitda = revenue - operational_cost
    project_cashflow = ebitda - total_capex - tax

    # Return the results as a DataFrame
    return pd.DataFrame({
        "EBITDA": ebitda,
        "Tax": tax,
        "CAPEX": total_capex,
        "Project Cashflow": project_cashflow
    })

def calculate_equity_cashflow(financial_df, taxation_df, loan_df, capex_drawdown_monthly_df):
    
    # Align loan_df and capex_drawdown_monthly_df with financial_df and fill missing columns with 0
    loan_df = loan_df.reindex(financial_df.index, fill_value=0)
    capex_drawdown_monthly_df = capex_drawdown_monthly_df.reindex(financial_df.index, fill_value=0)

    # Calculate financial metrics
    revenue = financial_df["Revenue"]
    operational_cost = financial_df["Operational Cost"]
    financing_cost = loan_df["Interest Payment"]
    tax = taxation_df["Income Tax (PPh)"]
    principal_payment = loan_df["Principal Payment"]
    depreciation = financial_df["Depreciation"] * 0  # Depreciation is zero
    net_income = revenue - operational_cost - financing_cost - tax

    total_capex = capex_drawdown_monthly_df["New Capex Adjusted"]
    equity_cashflow = net_income + depreciation - principal_payment - total_capex

    # Return the resulting DataFrame
    return pd.DataFrame({
        "Revenue": revenue,
        "Operational Cost": operational_cost,
        "Financing Cost": financing_cost,
        "Tax": tax,
        "Net Income": net_income,
        "CAPEX": total_capex,
        "Principal Payment": principal_payment,
        "Equity Cashflow": equity_cashflow
    })


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

# def aggregate_cash_flows_to_annual(cash_flows, frequency):
#     """
#     Aggregate cash flows to annual cash flows based on the frequency.

#     Args:
#         cash_flows (list): List of cash flows (input frequency).
#         frequency (str): Frequency of the cash flows ("Monthly", "Quarterly", "Semi-Annually", "Annually").

#     Returns:
#         list: Aggregated cash flows to annual periods.
#     """
#     # Add support for semi-annual frequency
#     freq_map = {"Monthly": 12, "Quarterly": 4, "Semi-Annually": 2, "Annually": 1}
#     periods_per_year = freq_map.get(frequency, 1)

#     if periods_per_year == 1:
#         # If the cash flows are already annual, no need to aggregate
#         return cash_flows

#     # Aggregate the cash flows by summing over the periods_per_year
#     aggregated_cash_flows = []
#     for i in range(0, len(cash_flows), periods_per_year):
#         annual_cash_flow = sum(cash_flows[i : i + periods_per_year])
#         aggregated_cash_flows.append(annual_cash_flow)

#     return aggregated_cash_flows


# def calculate_irr(cash_flows, frequency="Annually"):
#     """
#     Calculate the IRR (Internal Rate of Return) for a series of cash flows.

#     Args:
#         cash_flows (list): List of cash flows, where the first value is the initial investment (negative value),
#                            and subsequent values are future cash inflows.
#         frequency (str): The frequency of the cash flows ("Monthly", "Quarterly", "Annually").

#     Returns:
#         float: The IRR for the given cash flows (annualized).
#     """
#     # First, aggregate the cash flows to annual cash flows
#     annual_cash_flows = aggregate_cash_flows_to_annual(cash_flows, frequency)

#     # Define the NPV function with an adjustable rate
#     def npv_with_rate(rate):
#         return sum(cf / (1 + rate) ** t for t, cf in enumerate(annual_cash_flows))

#     # Use the Newton method from scipy to solve for IRR where NPV is 0
#     try:
#         # Initial guess for IRR is 10% (0.1)
#         irr = newton(npv_with_rate, 0.1)

#         # Since the cash flows are aggregated to annual already, we can directly return the IRR
#         return irr * 100  # Convert to percentage
#     except RuntimeError as e:
#         print("Error calculating IRR:", e)
#         return None
import numpy_financial as npf
import numpy as np

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
        annual_cash_flow = sum(cash_flows[i: i + periods_per_year])
        aggregated_cash_flows.append(annual_cash_flow)

    return aggregated_cash_flows


def calculate_irr(cash_flows, frequency="Annually"):
    """
    Calculate the IRR (Internal Rate of Return) for a series of cash flows using numpy_financial.

    Args:
        cash_flows (list): List of cash flows, where the first value is the initial investment (negative value),
                           and subsequent values are future cash inflows.
        frequency (str): The frequency of the cash flows ("Monthly", "Quarterly", "Annually").

    Returns:
        float or None: The IRR for the given cash flows (annualized), or None if it doesn't converge.
    """
    # First, aggregate the cash flows to annual cash flows
    annual_cash_flows = aggregate_cash_flows_to_annual(cash_flows, frequency)

    # Use numpy_financial's IRR function to calculate the internal rate of return
    try:
        irr = npf.irr(annual_cash_flows)
        
        # Check if the IRR result is valid (e.g., NaN or no convergence)
        if np.isnan(irr) or irr is None:
            return None  # Skip if not converging
        
        return irr * 100  # Convert to percentage
    except Exception as e:
        print(f"IRR calculation failed: {e}")
        return None  # Skip if IRR calculation failed


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

def financial_modelling(
    # Timing Inputs
    num_years,  # Number of Years
    start_date,  # Start Date
    construction_duration_years,  # Construction Duration (Years)

    # Financial Inputs
    initial_revenue,  # Initial Revenue
    initial_growth_rate,  # Annual Growth Rate for Revenue (%)
    total_capex,  # CAPEX (Capital Expenditure)
    discount_rate,  # Discount Rate (%)
    initial_op_cost,  # Initial Operational Cost
    initial_op_cost_growth_rate,  # Annual Growth Rate for Operational Cost (%)
    sell_fixed_assets,  # Sell Fixed Assets
    useful_life_years,  # Useful Life of Assets (in years)

    # Loan & Tax Inputs
    equity_percentage,  # Equity Injection Percentage (%)
    interest_rate,  # Interest Rate (%)
    bank_provision_percentage,  # Bank Provision Percentage (%)
    tenor_years,  # Loan Tenor (in years)
    grace_period_years,  # Grace Period (in years)
    tax_rate,  # Tax Rate (%)
    repayment_mechanism  # Repayment Mechanism
):
    # Construction Period
    total_construction_months = int(construction_duration_years * 12)
    
    # Capex
    capex_drawdown_monthly_df = generate_capex_drawdown(
        start_date=start_date, 
        total_construction_months=total_construction_months, 
        total_capex=total_capex, 
        equity_percentage=equity_percentage, 
        bank_provision_percentage=bank_provision_percentage, 
        interest_rate=interest_rate
    )
    
    # Loan
    loan_amount_adjusted = capex_drawdown_monthly_df["Loan with Bank Provision and IDC"].sum()
    loan_df = generate_loan_amortization_df(
        loan_amount=loan_amount_adjusted,
        interest_rate=interest_rate,
        tenor_years=tenor_years,
        repayment_mechanism=repayment_mechanism,
        total_construction_months=total_construction_months,
        start_date=start_date,
    )
    
    # Financial 
    total_capex_adjusted = capex_drawdown_monthly_df["New Capex Adjusted"].sum()
    financial_df = financial_df = generate_financial_df(
        start_date, 
        total_years=num_years, 
        total_construction_months=total_construction_months,
        initial_revenue=initial_revenue, 
        initial_op_cost=initial_op_cost, 
        revenue_growth_rate=initial_growth_rate,
        op_cost_growth_rate=initial_op_cost_growth_rate, 
        capex=total_capex_adjusted, 
        useful_life_years = num_years - construction_duration_years,
    )
    
    # Profit Loss
    profit_loss_df = create_profit_loss_table(
        financial_df, 
        loan_df
    )
    
    taxation_df = calculate_annual_tax(
        profit_loss_df=profit_loss_df, 
        tax_rate=tax_rate
    )
    
    (
    operational_cashflow_df,
    investment_cashflow_df,
    financing_cashflow_df,
    cashflow_summary_df,
    ) = create_cashflow_tables_compliant(
        financial_df=financial_df,
        taxation_df=taxation_df,
        loan_df=loan_df,
        capex_drawdown_monthly_df=capex_drawdown_monthly_df,
        sell_fixed_assets=0,
        construction_duration=total_construction_months,
    )
    
    assets_df, liabilities_df, equity_df, checking_df = create_balance_sheet(
        financial_df=financial_df,
        taxation_df=taxation_df,
        cashflow_summary_df=cashflow_summary_df,
        financing_cashflow_df=financing_cashflow_df,
        capex_drawdown_monthly_df=capex_drawdown_monthly_df,
    )
    
    project_cashflow = calculate_project_cashflow(
       financial_df=financial_df,
       taxation_df=taxation_df,
       capex_drawdown_monthly_df=capex_drawdown_monthly_df,
    )
    
    equity_cashflow = calculate_equity_cashflow(
       financial_df=financial_df,
       taxation_df=taxation_df,
       loan_df=loan_df,
       capex_drawdown_monthly_df=capex_drawdown_monthly_df,
    )
    
    npv_project = calculate_npv(
       discount_rate=discount_rate,
       cash_flows=project_cashflow["Project Cashflow"].values,
       timing_frequency="Monthly",
    )
    
    irr_project = calculate_irr(
        cash_flows=project_cashflow["Project Cashflow"].values,
        frequency="Monthly",
    )
        
    pbp_project = calculate_payback_period(
        cash_flows=project_cashflow["Project Cashflow"].values,
        frequency="Monthly",
    )
    
    npv_equity = calculate_npv(
        discount_rate=discount_rate,
        cash_flows=equity_cashflow["Equity Cashflow"].values,
        timing_frequency="Monthly",
    )
        
    irr_equity = calculate_irr(
        cash_flows=equity_cashflow["Equity Cashflow"].values,
        frequency="Monthly",
    )
    
    return npv_project, irr_project, pbp_project, npv_equity, irr_equity