import pandas as pd
import plotly.express as px
from datetime import timedelta, datetime
import streamlit as st
from decision_flow_finmod_function import *
import calendar




# Utility Functions
def find_node_in_database(node_id):
    """Check if the node ID already exists in the database."""
    for data in st.session_state["input_database"]:
        if data["node_id"] == node_id:
            return data
    return None


def get_days_in_month(date_obj):
    """Return the number of days in the month of the given date."""
    return calendar.monthrange(date_obj.year, date_obj.month)[1]


def resample_data_input(df, frequency, is_constant):
    """Resample the input data based on frequency and is_constant."""
    if is_constant == "Yes":
        if frequency == "Monthly":
            return df
        elif frequency == "Quarterly":
            return df.iloc[::3]
        elif frequency == "Semi-Annual":
            return df.iloc[::6]
        elif frequency == "Annually":
            return df.iloc[::12]
    else:
        if frequency == "Monthly":
            return df
        elif frequency == "Quarterly":
            return df.resample("Q").sum()
        elif frequency == "Semi-Annual":
            return df.resample("6M").sum()
        elif frequency == "Annually":
            return df.resample("A").sum()


def create_monthly_dataframe(
    starting_date, initial_value, growth_rate, duration_monthly, value_column_name
):
    """Generate a monthly dataframe based on inputs with exact monthly intervals."""
    monthly_growth_rate = (1 + growth_rate / 100) ** (1 / 12) - 1
    data = []

    # Iterate over the number of months and generate data for each month
    for month in range(duration_monthly):
        # Use DateOffset to ensure proper monthly intervals
        current_date = starting_date + pd.DateOffset(months=month)
        value = initial_value * (1 + monthly_growth_rate) ** month
        data.append({"Date": current_date, value_column_name: round(value, 2)})

    df = pd.DataFrame(data)
    df.set_index("Date", inplace=True)  # Set 'Date' as the index
    return df


def setup_node_input(nodes_data, idx):
    """Configure inputs and visuals for each node."""
    node_id, col_name = nodes_data["id"][idx], nodes_data["id"][idx].split("_")[0]
    node_data = find_node_in_database(node_id)

    # Default values for durations based on frequency
    freq_defaults = {
        "duration_monthly": 12,  # Default: 12 months
        "duration_quarterly": 4,  # Default: 4 quarters
        "duration_semiannual": 2,  # Default: 2 semi-annual periods
        "duration_annual": 1,  # Default: 1 year
    }

    # Use .get() to avoid KeyErrors and provide default values
    node_data_defaults = {
        "start_date": node_data.get("start_date", datetime.today())
        if node_data
        else datetime.today(),
        "initial_value": node_data.get("initial_value", 0.0) if node_data else 0.0,
        "growth_rate": node_data.get("growth_rate", 0.0) if node_data else 0.0,
        "duration_freq": node_data.get("duration_freq", "Monthly")
        if node_data
        else "Monthly",
        "duration_monthly": node_data.get(
            "duration_monthly", freq_defaults["duration_monthly"]
        )
        if node_data
        else freq_defaults["duration_monthly"],
        "duration_quarterly": node_data.get(
            "duration_quarterly", freq_defaults["duration_quarterly"]
        )
        if node_data
        else freq_defaults["duration_quarterly"],
        "duration_semiannual": node_data.get(
            "duration_semiannual", freq_defaults["duration_semiannual"]
        )
        if node_data
        else freq_defaults["duration_semiannual"],
        "duration_annual": node_data.get(
            "duration_annual", freq_defaults["duration_annual"]
        )
        if node_data
        else freq_defaults["duration_annual"],
        "constant": node_data.get("constant", "No") if node_data else "No",
        "button_label": "Update" if node_data else "Save",
    }

    with st.expander(f"Node: {node_id} - Input and Visualization", expanded=True):
        col1, col2 = st.columns(2)
        start_date = col1.date_input(
            "Starting Date",
            value=node_data_defaults["start_date"],
            key=f"start_date_{idx}",
        )
        initial_value = col1.number_input(
            "Initial Value",
            value=round(node_data_defaults["initial_value"], 2),
            key=f"initial_value_{idx}",
        )
        duration_freq = col2.selectbox(
            "Duration Frequency",
            ["Monthly", "Quarterly", "Semi-Annual", "Annually"],
            index=["Monthly", "Quarterly", "Semi-Annual", "Annually"].index(
                node_data_defaults["duration_freq"]
            ),
            key=f"duration_freq_{idx}",
        )
        growth_rate = col2.number_input(
            "Annual Growth Rate (%)",
            value=round(node_data_defaults["growth_rate"], 2),
            key=f"growth_rate_{idx}",
        )

        # Add the corresponding input field for the selected frequency
        if duration_freq == "Monthly":
            duration_value = st.number_input(
                "Duration (Months)",
                value=node_data_defaults["duration_monthly"],
                key=f"duration_monthly_{idx}",
            )
            duration_monthly = (
                duration_value  # Explicitly set duration_monthly to input value
            )
            duration_quarterly = duration_value / 3
            duration_semiannual = duration_value / 6
            duration_annual = duration_value / 12
        elif duration_freq == "Quarterly":
            duration_value = st.number_input(
                "Duration (Quarters)",
                value=node_data_defaults["duration_quarterly"],
                key=f"duration_quarterly_{idx}",
            )
            duration_quarterly = duration_value
            duration_monthly = duration_value * 3
            duration_semiannual = duration_value / 2
            duration_annual = duration_value / 4
        elif duration_freq == "Semi-Annual":
            duration_value = st.number_input(
                "Duration (Semi-Annual Periods)",
                value=node_data_defaults["duration_semiannual"],
                key=f"duration_semiannual_{idx}",
            )
            duration_semiannual = duration_value
            duration_monthly = duration_value * 6
            duration_quarterly = duration_value * 2
            duration_annual = duration_value / 2
        else:  # Annually
            duration_value = st.number_input(
                "Duration (Years)",
                value=node_data_defaults["duration_annual"],
                key=f"duration_annual_{idx}",
            )
            duration_annual = duration_value
            duration_monthly = duration_value * 12
            duration_quarterly = duration_value * 4
            duration_semiannual = duration_value * 2

        # Generate the DataFrame based on the selected frequency and duration
        monthly_df = create_monthly_dataframe(
            start_date, initial_value, growth_rate, duration_monthly, col_name
        )
        constant = st.selectbox(
            "Constant",
            ["Yes", "No"],
            index=["Yes", "No"].index(node_data_defaults["constant"]),
            key=f"constant_{idx}",
        )

        if st.button(node_data_defaults["button_label"], key=f"save_button_{idx}"):
            # Store the respective duration value based on the frequency
            new_node_data = {
                "node_id": node_id,
                "start_date": start_date,
                "initial_value": round(initial_value, 2),  # Round to 2 decimal places
                "growth_rate": round(growth_rate, 2),  # Round to 2 decimal places
                "duration_freq": duration_freq,
                "duration_monthly": duration_monthly,  # Now set based on the input duration for Monthly
                "duration_quarterly": duration_value
                if duration_freq == "Quarterly"
                else duration_quarterly,
                "duration_semiannual": duration_value
                if duration_freq == "Semi-Annual"
                else duration_semiannual,
                "duration_annual": duration_value
                if duration_freq == "Annually"
                else duration_annual,
                "constant": constant,
                "dataframe": monthly_df.round(
                    2
                ),  # Round entire DataFrame to 2 decimal places
            }
            if node_data:
                st.session_state["input_database"][
                    st.session_state["input_database"].index(node_data)
                ] = new_node_data
                st.success(f"Updated data for node {node_id}.")
            else:
                st.session_state["input_database"].append(new_node_data)
                st.success(f"Saved data for node {node_id}.")

        st.write("Generated Monthly Data:")
        st.dataframe(
            monthly_df.T.round(2), use_container_width=True
        )  # Round to 2 decimal places when displaying

        st.write(f"{col_name} Bar Chart")
        display_freq = st.selectbox(
            "Select Display Frequency",
            ["Monthly", "Quarterly", "Semi-Annual", "Annually"],
            key=f"display_freq_{idx}",
        )
        filtered_df = resample_data_input(monthly_df, display_freq, constant)
        st.plotly_chart(
            px.bar(
                filtered_df.reset_index(),
                x="Date",
                y=col_name,
                title=f"{col_name} over Time ({display_freq})",
            ).update_traces(marker_line_width=2, texttemplate="%{y:.2f}")
        )  # Ensure plot is formatted to 2 decimal places


# Calculation Functions
def find_node_dataframe(node_id):
    """Locate the node's dataframe from session state."""
    return next(
        (
            data["dataframe"]
            for data in st.session_state["input_database"]
            if data["node_id"] == node_id
        ),
        None,
    )


def resample_data_output(df, frequency):
    """Resample output data based on selected frequency, ensuring DatetimeIndex."""
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    return (
        df.resample(
            {"Monthly": "M", "Quarterly": "Q", "Semiannually": "6M", "Annually": "A"}[
                frequency
            ]
        )
        .sum()
        .round(2)
    )


def resample_to_daily(df, is_constant, max_date):
    """Resample the dataframe to daily frequency based on the is_constant flag and distribute values based on remaining days or max date."""
    # Ensure the index is a DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    def distribute_values(series):
        # Resample to daily frequency and forward fill
        resampled = series.resample("D").ffill()  # Resample to daily and forward-fill
        if is_constant == "No":
            for month, group in resampled.groupby(pd.Grouper(freq="M")):
                month_start = group.index[0]  # Start of the resampled period
                month_end = group.index[-1]  # End of the resampled period
                total_days_in_month = len(group)  # Number of days in that month
                # Handle the max date month case
                if month == max_date.to_period("M"):
                    month_end = max_date
                    remaining_days = (month_end - month_start).days + 1
                else:
                    # For non-max date months, distribute over remaining days
                    remaining_days = total_days_in_month

                try:
                    # Get the monthly value for the current month
                    monthly_value = series.loc[series.index.month == month.month].iloc[
                        0
                    ]
                except (KeyError, IndexError):
                    continue  # Skip if the month is not found

                # Spread the monthly value across the remaining days
                resampled.loc[month_start:month_end] = monthly_value / remaining_days

        return resampled

    return df.apply(distribute_values)


def calculate_output_for_nodes(nodes_data, edges_data):
    """Compute outputs for selected nodes based on operations."""
    for idx in range(len(nodes_data)):
        if nodes_data["type"][idx] == "output":
            output_id = nodes_data["id"][idx]

            for edge in edges_data.itertuples():
                if edge.target == output_id:
                    connected_id = edge.source
                    node_data_filtered = nodes_data[nodes_data["id"] == connected_id]

                    # Check if the filtered DataFrame is not empty
                    if not node_data_filtered.empty:
                        operation = (
                            node_data_filtered["data"]
                            .values[0]
                            .get("content", "")
                            .lower()
                        )
                    else:
                        st.warning(f"No data found for node with ID {connected_id}")
                        continue

                    input_dfs = []
                    is_constant_list = []

                    for e in edges_data.itertuples():
                        if e.target == connected_id:
                            input_node_id = e.source
                            input_node_filtered = nodes_data[
                                nodes_data["id"] == input_node_id
                            ]

                            if not input_node_filtered.empty:
                                if input_node_filtered["type"].values[0] == "input":
                                    input_df = find_node_dataframe(input_node_id)
                                    if input_df is not None:
                                        if not isinstance(
                                            input_df.index, pd.DatetimeIndex
                                        ):
                                            input_df.index = pd.to_datetime(
                                                input_df.index
                                            )

                                        is_constant = find_node_in_database(
                                            input_node_id
                                        ).get("constant", "No")
                                        input_dfs.append(input_df)
                                        is_constant_list.append(is_constant)

                    if input_dfs:
                        max_date = max(df.index.max() for df in input_dfs)

                        resampled_dfs = [
                            resample_to_daily(input_df, is_constant_list[i], max_date)
                            for i, input_df in enumerate(input_dfs)
                        ]
                        min_date = min(df.index.min() for df in resampled_dfs)
                        date_range = pd.date_range(min_date, max_date)

                        result_df = resampled_dfs[0].reindex(date_range, fill_value=0)
                        for i, input_df in enumerate(resampled_dfs[1:], start=1):
                            reindexed_df = input_df.reindex(date_range, fill_value=0)
                            if operation == "multiply":
                                result_df = result_df.multiply(
                                    reindexed_df.values, fill_value=0
                                )
                            elif operation == "divide":
                                result_df = result_df.divide(
                                    reindexed_df.replace(0, float("nan")).values,
                                    fill_value=0,
                                )
                            elif operation == "add":
                                result_df = result_df.add(
                                    reindexed_df.values, fill_value=0
                                )
                            elif operation == "subtract":
                                result_df = result_df.subtract(
                                    reindexed_df.values, fill_value=0
                                )

                        result_df_monthly = result_df.resample("M").sum()
                        result_df_monthly.columns = [output_id]
                        st.session_state["output_database"][
                            output_id
                        ] = result_df_monthly.round(2)
                    else:
                        st.warning(
                            f"No valid input or output dataframes found for output node {output_id}"
                        )
