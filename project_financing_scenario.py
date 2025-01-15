import pandas as pd
from scipy.optimize import differential_evolution
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from project_financing_scenario_function import financial_modelling
from sidebar import render_page_based_on_sidebar

# Function to dynamically create number inputs with options for fixed value or range inside an expander
def dynamic_input_with_option(label, min_default, max_default, step_default):
    with st.sidebar.expander(f"{label} Settings"):
        use_fixed_value = st.checkbox(f"Use fixed value for {label}", key=f"fixed_{label}")

        if use_fixed_value:
            value = st.number_input(f"Set {label} Value", value=min_default)
            return value, value, None, True  # Return value as both min and max for fixed, step=None, fixed=True
        else:
            min_value = st.number_input(f"Set {label} Min", value=min_default)
            max_value = st.number_input(f"Set {label} Max", value=max_default)
            step_value = st.number_input(f"Set {label} Step", value=step_default)
            if min_value >= max_value:
                st.error(f"Min value must be less than Max value for {label}")
            return min_value, max_value, step_value, False  # Return min, max, and step values, fixed=False

# Sidebar for sensitivity analysis with all inputs and targets displayed
def render_sensitivity_sidebar():
    st.sidebar.title("Scenario Settings")

    param_ranges = {}
    bounds = []  # Store the bounds separately
    fixed_values = {}  # Store fixed values for direct use

    # Display settings for each input
    st.sidebar.subheader("Input Settings")

    total_capex = dynamic_input_with_option("Total CAPEX", 80000, 120000, 1000)
    if total_capex[3]:  # If it's a fixed value
        fixed_values["Total CAPEX"] = total_capex[0]
    else:
        param_ranges["Total CAPEX"] = total_capex
        bounds.append((total_capex[0], total_capex[1]))

    initial_revenue = dynamic_input_with_option("Initial Revenue", 8000, 15000, 500)
    if initial_revenue[3]:
        fixed_values["Initial Revenue"] = initial_revenue[0]
    else:
        param_ranges["Initial Revenue"] = initial_revenue
        bounds.append((initial_revenue[0], initial_revenue[1]))

    operational_cost = dynamic_input_with_option("Operational Cost", 4000, 7000, 200)
    if operational_cost[3]:
        fixed_values["Operational Cost"] = operational_cost[0]
    else:
        param_ranges["Operational Cost"] = operational_cost
        bounds.append((operational_cost[0], operational_cost[1]))

    revenue_growth_rate = dynamic_input_with_option("Revenue Growth Rate", 2.0, 8.0, 0.1)
    if revenue_growth_rate[3]:
        fixed_values["Revenue Growth Rate"] = revenue_growth_rate[0]
    else:
        param_ranges["Revenue Growth Rate"] = revenue_growth_rate
        bounds.append((revenue_growth_rate[0], revenue_growth_rate[1]))

    op_cost_growth_rate = dynamic_input_with_option("Op. Cost Growth Rate", 1.0, 5.0, 0.1)
    if op_cost_growth_rate[3]:
        fixed_values["Op. Cost Growth Rate"] = op_cost_growth_rate[0]
    else:
        param_ranges["Op. Cost Growth Rate"] = op_cost_growth_rate
        bounds.append((op_cost_growth_rate[0], op_cost_growth_rate[1]))

    equity_percentage = dynamic_input_with_option("Equity Percentage", 20, 40, 1)
    if equity_percentage[3]:
        fixed_values["Equity Percentage"] = equity_percentage[0]
    else:
        param_ranges["Equity Percentage"] = equity_percentage
        bounds.append((equity_percentage[0], equity_percentage[1]))

    interest_rate = dynamic_input_with_option("Interest Rate", 3.0, 7.0, 0.1)
    if interest_rate[3]:
        fixed_values["Interest Rate"] = interest_rate[0]
    else:
        param_ranges["Interest Rate"] = interest_rate
        bounds.append((interest_rate[0], interest_rate[1]))

    bank_provision_percentage = dynamic_input_with_option("Bank Provision Percentage", 0.5, 2.0, 0.1)
    if bank_provision_percentage[3]:
        fixed_values["Bank Provision Percentage"] = bank_provision_percentage[0]
    else:
        param_ranges["Bank Provision Percentage"] = bank_provision_percentage
        bounds.append((bank_provision_percentage[0], bank_provision_percentage[1]))

    # Display settings for each output target
    st.sidebar.subheader("Output Settings")

    target_ranges = {}
    
    target_ranges["IRR Project"] = dynamic_input_with_option("Target IRR Project (%)", 20.0, 30.0, 0.1)
    target_ranges["NPV Project"] = dynamic_input_with_option("Target NPV Project", 50000, 200000, 1000)
    target_ranges["Payback Period Project"] = dynamic_input_with_option("Target Payback Period Project (years)", 3, 10, 1)
    target_ranges["IRR Equity"] = dynamic_input_with_option("Target IRR Equity (%)", 15.0, 25.0, 0.1)
    target_ranges["NPV Equity"] = dynamic_input_with_option("Target NPV Equity", 30000, 120000, 1000)

    return param_ranges, bounds, target_ranges, fixed_values

# Function to run optimization and return valid combinations
def run_optimization(param_ranges, bounds, target_ranges, fixed_values):
    valid_combinations = []
    n_iterations = 5000

    # Fixed values are directly applied to the inputs
    def objective(inputs):
        # Unpack the inputs for corresponding parameters
        param_dict = dict(zip(param_ranges.keys(), inputs))
        # Add fixed values to parameters directly
        param_dict.update(fixed_values)

        try:
            npv_project, irr_project, pbp_project, npv_equity, irr_equity = financial_modelling(
                num_years=10,
                start_date="2024-01-01",
                initial_revenue=param_dict.get("Initial Revenue", 10000),
                initial_growth_rate=param_dict.get("Revenue Growth Rate", 5.0),
                total_capex=param_dict.get("Total CAPEX", 100000),
                discount_rate=8.0,
                initial_op_cost=param_dict.get("Operational Cost", 5000),
                initial_op_cost_growth_rate=param_dict.get("Op. Cost Growth Rate", 3.0),
                sell_fixed_assets=0,
                useful_life_years=5,
                equity_percentage=param_dict.get("Equity Percentage", 30),
                interest_rate=param_dict.get("Interest Rate", 5.0),
                bank_provision_percentage=param_dict.get("Bank Provision Percentage", 1.0),
                tenor_years=5,
                grace_period_years=2,
                tax_rate=22.0,
                repayment_mechanism="Equal Installments",
                construction_duration_years=2
            )

            # Check for valid outputs based on the selected targets
            valid = True
            penalties = 0

            # Normalized penalties for selected targets
            if "IRR Project" in target_ranges:
                target_range = target_ranges["IRR Project"]
                if not (target_range[0] <= irr_project <= target_range[1]):
                    penalties += abs((irr_project - target_range[1]) / (target_range[1] - target_range[0]))
                    valid = False

            if "NPV Project" in target_ranges:
                target_range = target_ranges["NPV Project"]
                if not (target_range[0] <= npv_project <= target_range[1]):
                    penalties += abs((npv_project - target_range[1]) / (target_range[1] - target_range[0]))
                    valid = False

            if "Payback Period Project" in target_ranges:
                target_range = target_ranges["Payback Period Project"]
                if not (target_range[0] <= pbp_project <= target_range[1]):
                    penalties += abs((pbp_project - target_range[1]) / (target_range[1] - target_range[0]))
                    valid = False

            if "IRR Equity" in target_ranges:
                target_range = target_ranges["IRR Equity"]
                if not (target_range[0] <= irr_equity <= target_range[1]):
                    penalties += abs((irr_equity - target_range[1]) / (target_range[1] - target_range[0]))
                    valid = False

            if "NPV Equity" in target_ranges:
                target_range = target_ranges["NPV Equity"]
                if not (target_range[0] <= npv_equity <= target_range[1]):
                    penalties += abs((npv_equity - target_range[1]) / (target_range[1] - target_range[0]))
                    valid = False

            # If all selected targets are valid, append to valid_combinations
            if valid:
                valid_combinations.append([*inputs, irr_project, npv_project, pbp_project, irr_equity, npv_equity])

            return penalties  # Minimize penalties if the targets are not within range

        except:
            return float('inf')  # Return a large number if calculation fails

    # Run the differential evolution optimizer with correct bounds
    differential_evolution(objective, bounds, strategy='best1bin', maxiter=n_iterations)

    return valid_combinations

# Function to display results with subplots in a single row
def display_results_per_scenario():
    # Get the necessary data from session state
    valid_combinations_df = st.session_state['valid_combinations_df']
    param_ranges = st.session_state['param_ranges']
    target_ranges = st.session_state['target_ranges']
    fixed_values = st.session_state['fixed_values']

    # Multiselect for choosing which inputs and outputs to visualize
    selected_inputs = st.multiselect(
        "Select Inputs to Display", 
        options=list(fixed_values.keys()) + list(param_ranges.keys()),  # Include both fixed and variable inputs
        default=st.session_state.get('display_selected_inputs', list(fixed_values.keys()) + list(param_ranges.keys())),  # Load from session state or default
        key='display_selected_inputs'
    )
    
    selected_outputs = st.multiselect(
        "Select Outputs to Display", 
        options=list(target_ranges.keys()), 
        default=st.session_state.get('display_selected_outputs', list(target_ranges.keys())),  # Load from session state or default
        key='display_selected_outputs'
    )

    # Combine selected inputs and outputs to create subplots in a single row
    all_selected = selected_inputs + selected_outputs

    if len(all_selected) == 0:
        st.warning("Please select at least one input or output to display.")
        return

    # Create subplots (all in one row based on the selected inputs and outputs)
    fig = make_subplots(rows=1, cols=len(all_selected), shared_yaxes=False, column_widths=[1/len(all_selected)] * len(all_selected))

    # Add selected input box plots
    for i, param in enumerate(selected_inputs, start=1):
        fig.add_trace(go.Box(
            y=valid_combinations_df[param],
            name=param,
            boxmean=True,
            marker=dict(size=8)  # Adjust marker size
        ), row=1, col=i)
    
    # Add selected output box plots
    for i, target in enumerate(selected_outputs, start=len(selected_inputs) + 1):
        fig.add_trace(go.Box(
            y=valid_combinations_df[target],
            name=target,
            boxmean=True,
            marker=dict(size=8)  # Adjust marker size
        ), row=1, col=i)

    # Update layout for wider boxes and bigger figure
    fig.update_layout(
        title="Selected Input and Output Parameter Distributions (Wider Box Plots)",
        showlegend=False,
        height=500,  # Adjust height based on number of subplots
        width=200 * len(all_selected),  # Increase width based on the number of plots
        boxmode='group'  # Group all box plots together
    )
    st.plotly_chart(fig)


# Main function to manage optimization and visualization using session state
def scenario_analysis_page():
    render_page_based_on_sidebar()  # Include this to render page from sidebar
    
    # Get the ranges for parameters and targets
    param_ranges, bounds, target_ranges, fixed_values = render_sensitivity_sidebar()

    # Sidebar inputs and outputs session state
    if 'sidebar_selected_inputs' not in st.session_state:
        st.session_state['sidebar_selected_inputs'] = list(fixed_values.keys()) + list(param_ranges.keys())

    if 'sidebar_selected_outputs' not in st.session_state:
        st.session_state['sidebar_selected_outputs'] = list(target_ranges.keys())

    # Run optimization or load existing results
    if st.sidebar.button("Run Optimization"):
        with st.spinner("Running optimization..."):  # Add the spinner during optimization
            valid_combinations = run_optimization(param_ranges, bounds, target_ranges, fixed_values)

            # Store optimization results and parameters in session state
            st.session_state['valid_combinations'] = valid_combinations
            st.session_state['param_ranges'] = param_ranges
            st.session_state['target_ranges'] = target_ranges
            st.session_state['fixed_values'] = fixed_values

            # Update selected inputs and outputs after running optimization
            st.session_state['sidebar_selected_inputs'] = list(fixed_values.keys()) + list(param_ranges.keys())
            st.session_state['sidebar_selected_outputs'] = list(target_ranges.keys())

            # Also update the display selections for visualization
            st.session_state['display_selected_inputs'] = st.session_state['sidebar_selected_inputs']
            st.session_state['display_selected_outputs'] = st.session_state['sidebar_selected_outputs']

            # Create the DataFrame from the results
            columns = list(param_ranges.keys()) + ["IRR Project", "NPV Project", "Payback Period Project", "IRR Equity", "NPV Equity"]
            valid_combinations_df = pd.DataFrame(valid_combinations, columns=columns)

            # Add fixed values to the DataFrame for all rows
            for fixed_param, fixed_value in fixed_values.items():
                valid_combinations_df[fixed_param] = fixed_value

            # Store the DataFrame in session state
            st.session_state['valid_combinations_df'] = valid_combinations_df

            st.success("Optimization completed.")
    
    # Display results if available
    if 'valid_combinations_df' in st.session_state:
        display_results_per_scenario()
    else:
        st.write("No valid combinations found. Please run the optimization.")



# Run the application
if __name__ == "__main__":
    sensitivity_analysis_page()
