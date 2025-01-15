import streamlit as st
from sidebar import render_page_based_on_sidebar

import pandas as pd
import numpy as np
from datetime import datetime
from scipy.optimize import newton

# Import necessary functions from project_financing_function.py
from project_financing_function import (
    generate_loan_amortization_df,
    generate_financial_data_after_construction,
    resample_financial_data,
    calculate_depreciation,
    create_profit_loss_table,
    calculate_annual_tax,
    create_cashflow_tables_compliant,
    create_balance_sheet,
    calculate_project_cashflow,
    calculate_equity_cashflow,
    calculate_npv,
    calculate_irr,
    calculate_payback_period,
    plot_bar_chart,
)


def create_financial_and_loan_simulation():
    st.title("Project Financing")
    # Sidebar section
    st.sidebar.subheader("Input and Assumptions")

    # Timing Inputs Section in the sidebar
    with st.sidebar.expander("Timing Inputs", expanded=True):
        num_years = st.number_input(
            "Number of Years",
            min_value=1,
            max_value=50,
            value=10,
            help="The total duration of the project in years.",
        )
        start_date = st.date_input(
            "Start Date",
            value=datetime.today(),
            help="Select the start date for the project.",
        )
        construction_duration_years = st.number_input(
            "Construction Duration (Years)",
            min_value=0.0,
            value=2.0,
            help="Duration of the construction phase in years.",
        )
        timing_frequency = st.selectbox(
            "Timing Frequency",
            options=["Monthly", "Quarterly", "Semi-Annually", "Annually"],
            help="Choose how frequently financial data will be calculated.",
        )

    # Financial Inputs Section in the sidebar
    with st.sidebar.expander("Financial Inputs", expanded=False):
        initial_revenue = st.number_input(
            "Initial Revenue",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            help="The starting revenue amount for the project.",
        )
        initial_growth_rate = st.number_input(
            "Annual Growth Rate for Revenue (%)",
            min_value=-100.0,
            value=5.0,
            step=0.1,
            help="Expected annual revenue growth rate in percentage.",
        )
        total_capex = st.number_input(
            "CAPEX (Capital Expenditure)",
            min_value=0.0,
            value=50000.0,
            step=1000.0,
            help="Total capital expenditure for the project.",
        )
        discount_rate = st.number_input(
            "Discount Rate (%)",
            min_value=0.0,
            value=8.0,
            step=0.1,
            help="Discount rate used for NPV calculation.",
        )
        initial_op_cost = st.number_input(
            "Initial Operational Cost",
            min_value=0.0,
            value=5000.0,
            step=500.0,
            help="Initial operational cost at the start of the project.",
        )
        initial_op_cost_growth_rate = st.number_input(
            "Annual Growth Rate for Operational Cost (%)",
            min_value=-100.0,
            value=3.0,
            step=0.1,
            help="Expected annual growth rate of operational costs.",
        )
        sell_fixed_assets = st.number_input(
            "Sell Fixed Assets",
            min_value=0.0,
            value=0.0,
            help="Amount expected from selling fixed assets during the project.",
        )
        useful_life_years = st.number_input(
            "Useful Life of Assets (in years)",
            min_value=1,
            value=5,
            help="Expected useful life of assets in years.",
        )

    # Loan & Tax Inputs Section in the sidebar
    with st.sidebar.expander("Loan & Tax Inputs", expanded=False):
        equity_percentage = st.number_input(
            "Equity Injection Percentage (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=0.1,
            help="Percentage of equity injected into the project.",
        )
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            value=5.0,
            step=0.1,
            help="Annual interest rate for the loan.",
        )
        bank_provision_percentage = st.number_input(
            "Bank Provision Percentage (%)",
            min_value=0.0,
            max_value=100.0,
            value=1.0,
            step=0.1,
            help="Provision fee as a percentage of the loan amount.",
        )
        tenor_years = st.number_input(
            "Loan Tenor (in years)",
            min_value=1,
            value=5,
            help="Loan repayment duration in years.",
        )
        grace_period_years = st.number_input(
            "Grace Period (in years)",
            min_value=0,
            value=2,
            help="Duration of the grace period before loan repayment starts.",
        )
        tax_rate = st.number_input(
            "Tax Rate (%)",
            min_value=0.0,
            value=22.0,
            step=0.1,
            help="Tax rate applied on profits.",
        )
        repayment_mechanism = st.selectbox(
            "Repayment Mechanism",
            options=["Equal Installments", "Equal Principal"],
            help="Choose the loan repayment method.",
        )

    # Define frequency to months mapping
    frequency_to_months = {
        "Monthly": 1,
        "Quarterly": 3,
        "Semi-Annually": 6,
        "Annually": 12,
    }

    # Add the second frequency input for the drawdown schedule
    total_construction_months = int(construction_duration_years) * 12

    equity_capex = equity_percentage * total_capex / 100
    loan_capex = total_capex - equity_capex

    # Create an expander for the Drawdown Schedule Inputs
    with st.expander("Drawdown Schedule Inputs", expanded=True):
        drawdown_frequency = st.selectbox(
            "Select Drawdown Schedule Frequency",
            options=["Monthly", "Quarterly", "Semi-Annually", "Annually"],
            # value="Monthly",
            help="Choose the frequency at which the CAPEX drawdown will occur.",
        )

        # Get the number of periods based on the drawdown frequency
        drawdown_frequency_months = frequency_to_months[drawdown_frequency]
        num_periods = total_construction_months // drawdown_frequency_months

        # Create an empty dataframe for the user to input percentages based on the selected frequency
        drawdown_data = pd.DataFrame(
            {f"Period {i+1}": [0.0] for i in range(num_periods)}
        )
        drawdown_data.index = ["CAPEX Drawdown %"]

        # Use st.data_editor to allow users to edit the drawdown percentages
        edited_data = st.data_editor(drawdown_data, use_container_width=True)

        # Sum all the percentages entered by the user
        total_percentage = edited_data.sum(axis=1)[0]

        # Validate that total percentage is 100%
        if total_percentage != 100.0:
            st.error(
                f"The total percentage must be 100%. Current total is {total_percentage:.1f}%"
            )
        else:
            st.success("Total drawdown percentages are valid and equal 100%.")

    if total_percentage == 100.0:
        st.subheader("Simulation Results")
        st.session_state.run_simulation = True

        with st.expander("CAPEX Adjustment"):
            # Convert percentages to decimals
            percentages = edited_data.iloc[0, :num_periods].values / 100.0

            # Calculate the amount for each period
            loan_drawdown_per_period = percentages * loan_capex
            equity_drawdown_per_period = percentages * equity_capex

            # Distribute the drawdowns across the months for each period
            monthly_drawdowns_loan = np.repeat(
                loan_drawdown_per_period / drawdown_frequency_months,
                drawdown_frequency_months,
            )
            monthly_drawdowns_equity = np.repeat(
                equity_drawdown_per_period / drawdown_frequency_months,
                drawdown_frequency_months,
            )

            # Calculate bank provision fee
            bank_provision_fee = (
                bank_provision_percentage / 100
            ) * monthly_drawdowns_loan

            # Loan with bank provision included
            loan_with_bank_provision = monthly_drawdowns_loan + bank_provision_fee

            # Calculate cumulative loan drawdown at each month using cumsum
            cumulative_loan_drawdown = np.cumsum(loan_with_bank_provision)

            # Vectorized IDC calculation
            idc_list = (
                cumulative_loan_drawdown * interest_rate / 100
            ) / 12  # Monthly IDC based on annual interest rate

            # Loan with provision and IDC included
            loan_with_provision_idc = loan_with_bank_provision + idc_list

            # New Capex adjusted with IDC and bank provision
            new_capex_drawdown = monthly_drawdowns_equity + loan_with_provision_idc

            # Generate the index of dates from the start_date for each month of construction
            drawdown_dates = pd.date_range(
                start=start_date, periods=total_construction_months, freq="M"
            )

            # Create a dataframe with the monthly drawdowns
            capex_drawdown_monthly_df = pd.DataFrame(
                {
                    "Monthly Drawdowns Equity": monthly_drawdowns_equity,
                    "Monthly Drawdowns Loan": monthly_drawdowns_loan,
                    "Bank Provision Fee": bank_provision_fee,
                    "Loan with Bank Provision": loan_with_bank_provision,
                    "IDC": idc_list,
                    "Loan with Bank Provision and IDC": loan_with_provision_idc,
                    "New Capex Adjusted": new_capex_drawdown,
                },
                index=drawdown_dates,
            )

            capex_drowdown_new = resample_financial_data(
                capex_drawdown_monthly_df, frequency=timing_frequency
            )

            st.dataframe(capex_drowdown_new.T, use_container_width=True)

            plot_bar_chart(
                capex_drowdown_new,  # Your dataframe
                [
                    "Monthly Drawdowns Equity",
                    "Loan with Bank Provision and IDC",
                ],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Loan Amortization Schedule"):
            # Generate loan amortization schedule with monthly calculation, prorated display
            loan_amount_adjusted = capex_drawdown_monthly_df[
                "Loan with Bank Provision and IDC"
            ].sum()

            loan_df_disp = generate_loan_amortization_df(
                loan_amount=loan_amount_adjusted,
                interest_rate=interest_rate,
                tenor_years=tenor_years,
                repayment_mechanism=repayment_mechanism,
                total_construction_months=total_construction_months,
                start_date=start_date,
            )

            loan_df_disp["Total Payment"] = (
                loan_df_disp["Interest Payment"] + loan_df_disp["Principal Payment"]
            )

            loan_df = loan_df_disp.copy()
            loan_df = loan_df.set_index("Date")

            # Resample the DataFrame based on the display frequency
            frequency_to_periods = {
                "Monthly": "M",
                "Quarterly": "Q",
                "Semi-Annually": "6M",
                "Annually": "A",
            }

            # Resample the monthly amortization for display purposes
            loan_df_new = loan_df_disp.resample(
                frequency_to_periods[timing_frequency], on="Date"
            ).agg(
                {
                    "Beginning Balance": "first",
                    "Principal Payment": "sum",
                    "Interest Payment": "sum",
                    "Ending Balance": "last",
                    "Total Payment": "sum",
                }
            )

            st.dataframe(loan_df_new.T, use_container_width=True)

            loan_df_plot = loan_df_new.copy()
            loan_df_plot["Principal Payment"] = loan_df_plot["Principal Payment"] * -1
            loan_df_plot["Interest Payment"] = loan_df_plot["Interest Payment"] * -1

            plot_bar_chart(
                loan_df_plot,  # Your dataframe
                [
                    "Ending Balance",
                    "Principal Payment",
                    "Interest Payment",
                ],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander(
            "Financial Data (Revenue and Operational Cost) After Construction"
        ):
            # Generate financial data (Revenue and Operational Cost) after construction
            financial_df = generate_financial_data_after_construction(
                start_date=start_date,
                total_years=num_years,
                total_construction_months=total_construction_months,
                initial_revenue=initial_revenue,
                initial_op_cost=initial_op_cost,
                revenue_growth_rate=initial_growth_rate,
                op_cost_growth_rate=initial_op_cost_growth_rate,
            )

            # Calculate depreciation
            total_capex_adjusted = capex_drawdown_monthly_df["New Capex Adjusted"].sum()
            depreciation_df = calculate_depreciation(
                capex=total_capex_adjusted,
                useful_life_years=num_years - construction_duration_years,
                start_date=start_date,
                construction_duration=total_construction_months,
            )

            financial_df["Depreciation"] = depreciation_df

            # Resample the financial data
            financial_df_new = resample_financial_data(
                financial_df, frequency=timing_frequency
            )

            # Display the financial data in a dataframe
            st.dataframe(financial_df_new.T, use_container_width=True)

            financial_df_plot = financial_df_new.copy()
            financial_df_plot["Operational Cost"] = (
                financial_df_plot["Operational Cost"] * -1
            )

            plot_bar_chart(
                financial_df_plot,  # Your dataframe
                ["Revenue", "Operational Cost"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Profit and Loss Table"):
            # Generate the profit and loss table
            profit_loss_df = create_profit_loss_table(financial_df.T, loan_df.T)

            # Resample the financial data
            profit_loss_df_new = resample_financial_data(
                profit_loss_df.T, frequency=timing_frequency
            )

            # Display the profit and loss table
            st.dataframe(profit_loss_df_new.T, use_container_width=True)

            profit_loss_plot = profit_loss_df_new.copy()
            profit_loss_plot["Operational Cost"] = (
                -1 * profit_loss_plot["Operational Cost"]
            )
            profit_loss_plot["Depreciation"] = -1 * profit_loss_plot["Depreciation"]
            profit_loss_plot["Financing Cost"] = -1 * profit_loss_plot["Financing Cost"]

            plot_bar_chart(
                profit_loss_plot,  # Your dataframe
                [
                    "Revenue",
                    "Operational Cost",
                    "Depreciation",
                    "Financing Cost",
                ],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Tax Calculation"):
            # Calculate annual tax
            taxation_df = calculate_annual_tax(
                profit_loss_df=profit_loss_df, tax_rate=tax_rate
            )

            # Resample the financial data
            taxation_df_new = resample_financial_data(taxation_df.T, timing_frequency)

            # Display the tax information
            st.dataframe(taxation_df_new.T, use_container_width=True)

            taxation_df_plot = taxation_df_new.copy()
            taxation_df_plot["Income Tax (PPh)"] = (
                taxation_df_plot["Income Tax (PPh)"] * -1
            )

            plot_bar_chart(
                taxation_df_plot,  # Your dataframe
                [
                    "Fiscal Profit/Loss",
                    "Income Tax (PPh)",
                    "Net Income After Tax",
                ],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        (
            operational_cashflow_df,
            investment_cashflow_df,
            financing_cashflow_df,
            cashflow_summary_df,
        ) = create_cashflow_tables_compliant(
            financial_df=financial_df.T,
            taxation_df=taxation_df,
            loan_df=loan_df.T,
            capex_drawdown_monthly_df=capex_drawdown_monthly_df.T,
            sell_fixed_assets=0,
            construction_duration=total_construction_months,
            timing_frequency=timing_frequency,
        )

        with st.expander("Operational Cashflow"):
            st.dataframe(operational_cashflow_df, use_container_width=True)

            operational_cashflow_df_plot = operational_cashflow_df.T.copy()

            plot_bar_chart(
                operational_cashflow_df_plot,  # Your dataframe
                ["Operational Cash Flow"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Investment Cashflow"):
            st.dataframe(investment_cashflow_df, use_container_width=True)

            investment_cashflow_df_plot = investment_cashflow_df.T.copy()

            plot_bar_chart(
                investment_cashflow_df_plot,  # Your dataframe
                ["Investment Cash Flow"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Financing Cashflow"):
            st.dataframe(financing_cashflow_df, use_container_width=True)

            financing_cashflow_df_plot = financing_cashflow_df.T.copy()

            plot_bar_chart(
                financing_cashflow_df_plot,  # Your dataframe
                ["Financing Cash Flow"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Cashflow Summary"):
            st.dataframe(cashflow_summary_df, use_container_width=True)

            cashflow_summary_df_plot = cashflow_summary_df.T.copy()

            plot_bar_chart(
                cashflow_summary_df_plot,  # Your dataframe
                ["End Balance Cash"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        assets_df, liabilities_df, equity_df, checking_df = create_balance_sheet(
            financial_df=financial_df.T,
            taxation_df=taxation_df,
            cashflow_summary_df=cashflow_summary_df,
            financing_cashflow_df=financing_cashflow_df,
            capex_drawdown_monthly_df=capex_drawdown_monthly_df.T,
            timing_frequency=timing_frequency,
        )

        with st.expander("Assets"):
            st.dataframe(assets_df, use_container_width=True)

        with st.expander("Liabilities"):
            st.dataframe(liabilities_df, use_container_width=True)

        with st.expander("Equity"):
            st.dataframe(equity_df, use_container_width=True)

        with st.expander("Checking Balance"):
            st.dataframe(checking_df, use_container_width=True)

            checking_df_plot = checking_df.T.copy()
            # checking_df_plot["Total Liabilities"] = checking_df_plot["Total Liabilities"] * -1
            # checking_df_plot["Total Equity"] = checking_df_plot["Total Equity"] * -1

            plot_bar_chart(
                checking_df_plot,  # Your dataframe
                [
                    "Total Assets",
                    "Total Liabilities",
                    "Total Equity",
                ],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Project Cashflow and Key Metrics"):
            # Project Cashflow Data
            # Calculate project cashflow and resample
            project_cashflow = calculate_project_cashflow(
                financial_df=financial_df.T,
                taxation_df=taxation_df,
                capex_drawdown_monthly_df=capex_drawdown_monthly_df.T,
            )

            project_cashflow_new = resample_financial_data(
                project_cashflow.T, timing_frequency
            )

            # Display the project cashflow in a styled dataframe
            st.dataframe(project_cashflow_new.T, use_container_width=True)

            # Calculate and display NPV, IRR, and Payback Period
            # Calculate NPV
            npv_project = calculate_npv(
                discount_rate=discount_rate,
                cash_flows=project_cashflow_new["Project Cashflow"].values,
                timing_frequency=timing_frequency,
            )
            st.write(f"**Project NPV:** :blue[{npv_project:,.2f}]")

            # Calculate IRR
            irr_project = calculate_irr(
                cash_flows=project_cashflow_new["Project Cashflow"].values,
                frequency=timing_frequency,
            )
            if irr_project is not None:
                st.write(f"**Project IRR:** :green[{irr_project:.2f}%]")
            else:
                st.write(f"**Unable to Calculate IRR Project**")

            # Calculate Payback Period
            pbp_project = calculate_payback_period(
                cash_flows=project_cashflow_new["Project Cashflow"].values,
                frequency=timing_frequency,
            )
            if pbp_project is not None:
                st.write(
                    f"**Project Payback Period:** :orange[{pbp_project:.2f} Years]"
                )
            else:
                st.write(f"**Project Not Payback**")

            plot_bar_chart(
                project_cashflow_new,  # Your dataframe
                ["Project Cashflow"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )

        with st.expander("Equity Cashflow and Key Metrics"):
            # Calculate equity cashflow
            equity_cashflow = calculate_equity_cashflow(
                financial_df=financial_df.T,
                taxation_df=taxation_df.T,
                loan_df=loan_df.T,
                capex_drawdown_monthly_df=capex_drawdown_monthly_df.T,
            )

            # Resample financial data for equity cashflow
            equity_cashflow_new = resample_financial_data(
                equity_cashflow.T, frequency=timing_frequency
            )

            # Display the equity cashflow dataframe
            st.dataframe(equity_cashflow_new.T)

            # Calculate and display NPV for equity cashflow
            npv_equity = calculate_npv(
                discount_rate=discount_rate,
                cash_flows=equity_cashflow_new["Equity Cashflow"].values,
                timing_frequency=timing_frequency,
            )
            st.write(f"**Equity NPV:** :blue[{npv_equity:,.2f}]")

            # Calculate and display IRR for equity cashflow
            irr_equity = calculate_irr(
                cash_flows=equity_cashflow_new["Equity Cashflow"].values,
                frequency=timing_frequency,
            )

            if irr_equity is not None:
                st.write(f"**Equity IRR:** {irr_equity:.2f}%")
            else:
                st.write(f"**Unable to Calculate IRR Equity**")

            plot_bar_chart(
                equity_cashflow_new,  # Your dataframe
                ["Equity Cashflow"],  # Variables to plot
                x_axis_label="Time",  # Custom x-axis label
                y_axis_label="Amount",  # Custom y-axis label
            )


def project_financing_page():
    render_page_based_on_sidebar()
    create_financial_and_loan_simulation()


# Run the application
if __name__ == "__main__":
    project_financing_page()
