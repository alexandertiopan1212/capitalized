# Streamlit Modules
import streamlit as st
from streamlit_flow import streamlit_flow

# Utilities
import random
import pandas as pd

# Set pandas display format for float numbers
pd.options.display.float_format = "{:.2f}".format

# Custom Functions
from sidebar import render_page_based_on_sidebar
from df_function import *




def decision_flow_page():
    # Sidebar
    # render_page_based_on_sidebar()
        
    initialize_session_state() # Initialize Session State
    new_node = None  # Initialize new_node

    # Sidebar Configurations
    with st.sidebar:
        # Insert Item
        with st.expander("Insert Item", expanded=True):
            # Tabs Configurations
            input_tab, output_tab, rule_tab = st.tabs(["Input", "Output", "Rule"])                        
            # Input Tab
            with input_tab:                
                st.subheader("General Setup", divider=True)
                input_name = st.text_input(
                    "Input Name", 
                    key="input-name"
                    )
                input_description = st.text_input(
                    "Descriptions", 
                    key="input-descriptions"
                    )

                # Type setup
                st.subheader("Type Setup", divider=True)
                input_type = st.radio(
                    "Type", 
                    [
                        "Constant", 
                        "Variable", 
                        "Upload"
                        ], 
                    key="input-type",
                )

                # Constant input
                if input_type == "Constant":

                    # Parameter
                    st.subheader("Parameter", divider=True)

                    value_constant = st.number_input("Value", key="value-constant")

                    unit_constant = st.selectbox(
                        "Unit", ["USD", "IDR", "Others"], key="unit-constant"
                    )

                    if unit_constant == "Others":
                        unit_others = st.text_input("Others", key="others-constant")

                    # Action button
                    add_constant = st.button(
                        "Add", key="add-constant", use_container_width=True
                    )

                    if add_constant:
                        if not input_name or not input_description:
                            st.warning(
                                "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                            )
                        else:
                            db_list = [
                                "constant_inputs",
                                "variable_inputs",
                                "upload_inputs",
                                "outputs",
                                # "rules",
                            ]

                            # Check if the input name is already used by another node in any of the databases
                            node_exist = any(
                                (input_name == node["input_name"])
                                for db in db_list  # Iterate over the list of databases
                                for node in st.session_state.get(
                                    db, []
                                )  # Access each database in session_state
                            )

                            if node_exist:
                                st.warning(
                                    "The input name you entered is already in use. Please choose a different name."
                                )
                            else:
                                if unit_constant == "Others" and not unit_others:
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    add_input_cons(
                                        input_name=input_name,
                                        descriptions=input_description,
                                        type=input_type,
                                        value=value_constant,
                                        unit=unit_constant,
                                        unit_others=unit_others
                                        if unit_constant == "Others"
                                        else None,
                                    )

                # Variable Input
                if input_type == "Variable":

                    # Trend setup
                    st.subheader("Parameter", divider=True)

                    as_multiplier_variable = st.toggle(
                        "As Multiplier", key="as-multiplier-variable"
                    )

                    unit_variable = st.selectbox(
                        "Unit", ["USD", "IDR", "Others"], key="unit-variable"
                    )

                    if unit_variable == "Others":
                        unit_others_variable = st.text_input("Others", key="unit-others-variable")

                    start_date_variable = st.date_input(
                        "Starting Date", key="start-date-variable"
                    )

                    trend_frequency_variable = st.selectbox(
                        "Trend Frequency",
                        ["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"],
                        key="trend-frequency-variable",
                    )

                    number_of_conditions = st.number_input(
                        "Number of Conditions",
                        min_value=1,
                        max_value=10,
                        step=1,  # Limits for the number of conditions
                        key="number-of-conditions",
                    )

                    st.subheader("Conditions")

                    # Dynamically create tabs based on the number of conditions
                    if number_of_conditions > 0:
                        tab_names = [f"{i+1}" for i in range(int(number_of_conditions))]
                        tabs = st.tabs(tab_names)
                        conditions = []
                        # First condition inputs
                        with tabs[0]:
                            st.write(f"Base Condition")
                            initial_trend_percent = st.number_input(
                                f"% Trend ({trend_frequency_variable})",
                                key="initial-trend-percent",
                                min_value=0.0,
                                max_value=100.0,
                                step=0.1,
                            )

                            initial_trend_duration = st.number_input(
                                f"Duration ({trend_frequency_variable})",
                                key="initial-trend-duration",
                                min_value=1,
                                step=1,
                            )

                            initial_trend_value = st.number_input(
                                f"Initial Value ({trend_frequency_variable})",
                                key="initial-trend-value",
                                min_value=0.0,
                                step=0.1,
                            )

                            # Store the first condition values
                            initial_condition_values = {
                                "trend_percent": initial_trend_percent,
                                "duration": initial_trend_duration,
                                "value": initial_trend_value,
                            }

                            conditions.append(initial_condition_values)

                        # Subsequent condition inputs with toggle
                        for i in range(1, number_of_conditions):
                            with tabs[i]:
                                st.write(f"Condition {i+1}")

                                # Toggle to use own values or inherit from the first condition
                                use_own_values = st.toggle(
                                    f"Use own values?", key=f"use-own-values-{i}"
                                )

                                if use_own_values:
                                    trend_percent_variable = st.number_input(
                                        f"% Trend ({trend_frequency_variable})",
                                        key=f"trend-percent-variable-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                    )

                                    duration_variable = st.number_input(
                                        f"Duration ({trend_frequency_variable})",
                                        key=f"duration-variable-{i+1}",
                                        min_value=1,
                                        step=1,
                                    )

                                    value_variable = st.number_input(
                                        f"Initial Value ({trend_frequency_variable})",
                                        key=f"value-variable-{i+1}",
                                        min_value=0.0,
                                        step=0.1,
                                    )
                                    after_conditions = {
                                        "trend_percent": trend_percent_variable,
                                        "duration": duration_variable,
                                        "value": value_variable,
                                    }

                                    conditions.append(after_conditions)
                                else:
                                    trend_percent_variable = st.number_input(
                                        f"% Trend ({trend_frequency_variable})",
                                        key=f"trend-percent-variable-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                    )

                                    duration_variable = st.number_input(
                                        f"Duration ({trend_frequency_variable})",
                                        key=f"duration-variable-{i+1}",
                                        min_value=1,
                                        step=1,
                                    )

                                    after_conditions = {
                                        "trend_percent": trend_percent_variable,
                                        "duration": duration_variable,
                                        "value": None,
                                    }

                                    conditions.append(after_conditions)

                    # Action button
                    add_variable = st.button("Add", key="add-variable", use_container_width=True)
                    if add_variable:
                        if not input_name or not input_description:
                            st.warning(
                                "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                            )
                        else:
                            db_list = [
                                "constant_inputs",
                                "variable_inputs",
                                "upload_inputs",
                                "outputs",
                            ]

                            # Check if the input name is already used by another node in any of the databases
                            node_exist = any(
                                (input_name == node["input_name"])
                                for db in db_list  # Iterate over the list of databases
                                for node in st.session_state.get(
                                    db, []
                                )  # Access each database in session_state
                            )
                            if node_exist:
                                st.warning(
                                    "The input name you entered is already in use. Please choose a different name."
                                )
                            else:
                                if unit_variable == "Others" and not unit_others_variable:
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    add_input_var(
                                        input_name=input_name,
                                        descriptions=input_description,
                                        type=input_type,
                                        unit=unit_variable,
                                        unit_others=unit_others_variable
                                        if unit_variable == "Others"
                                        else None,
                                        as_multiplier=as_multiplier_variable,
                                        starting_date=start_date_variable,
                                        trend_frequency=trend_frequency_variable,
                                        num_conditions=number_of_conditions,
                                        conditions=conditions,
                                    )

                if input_type == "Upload":

                    # File uploader for Excel file
                    uploaded_file = st.file_uploader(
                        "Choose an Excel file", type=["xlsx"]
                    )

                    if uploaded_file is not None:
                        try:
                            # Read the Excel file with multiple sheets
                            df = pd.read_excel(uploaded_file, sheet_name=None)

                            # Get list of sheet names
                            sheet_names = list(df.keys())

                            # Dropdown to select the sheet
                            selected_sheet = st.selectbox("Select sheet", sheet_names)

                            # Extract data from the selected sheet
                            data = df[selected_sheet]

                            st.write(f"Preview of sheet '{selected_sheet}'")
                            st.dataframe(data)

                            # Slider for selecting column index range
                            st.subheader("Select Column Index Range")
                            start_col, end_col = st.slider(
                                "Select column range",
                                min_value=0,
                                max_value=len(data.columns) - 1,
                                value=(0, len(data.columns) - 1),
                                step=1,
                                key="col_slider",
                            )

                            # Slider for selecting row index range
                            st.subheader("Select Row Index Range")
                            start_row, end_row = st.slider(
                                "Select row range",
                                min_value=0,
                                max_value=len(data) - 1,
                                value=(0, len(data) - 1),
                                step=1,
                                key="row_slider",
                            )

                            # Filter data based on selected rows and columns
                            filtered_data = data.iloc[
                                start_row : end_row + 1, start_col : end_col + 1
                            ]

                            # Choose the orientation of the data
                            orientation = st.radio(
                                "Select the data orientation for the date index",
                                ("Horizontal", "Vertical"),
                                key="orientation",
                            )

                            # Input for starting date and frequency
                            start_date_upload = st.date_input(
                                "Starting Date", key="starting-date-upload"
                            )
                            frequency_upload = st.selectbox(
                                "Frequency",
                                [
                                    "Daily",
                                    "Monthly",
                                    "Quarterly",
                                    "Semi-Annual",
                                    "Annually",
                                ],
                                key="frequency-upload",
                            )

                            # Define frequency mapping for date increments
                            freq_mapping = {
                                "Daily": lambda d, x: d + timedelta(days=x),
                                "Monthly": lambda d, x: d + relativedelta(months=x),
                                "Quarterly": lambda d, x: d
                                + relativedelta(months=3 * x),
                                "Semi-Annual": lambda d, x: d
                                + relativedelta(months=6 * x),
                                "Annually": lambda d, x: d + relativedelta(years=x),
                            }

                            date_increment_fn = freq_mapping.get(frequency_upload)

                            current_date = start_date_upload

                            periods = max(
                                end_row - start_row + 1, end_col - start_col + 1
                            )

                            date_index = []

                            for period in range(periods):
                                date_index.append(current_date)
                                current_date = date_increment_fn(current_date, 1)

                            # Apply the date index based on the selected orientation
                            if orientation == "Horizontal":
                                filtered_data.columns = date_index
                                filtered_data.index = ["Value"]
                                st.subheader("Data Preview with Date Index as Columns")
                                st.dataframe(filtered_data)
                            if orientation == "Vertical":
                                filtered_data.index = date_index
                                filtered_data.columns = ["Value"]
                                st.subheader("Data Preview with Date Index as Rows")
                                st.dataframe(filtered_data)

                            as_multiplier_upload = st.toggle(
                                "As Multiplier", key="as-multiplier-upload"
                            )

                            # Additional unit selection if needed
                            unit_upload = st.selectbox(
                                "Unit", ["USD", "IDR", "Others"], key="unit-upload"
                            )

                            if unit_upload == "Others":
                                unit_others_upload = st.text_input(
                                    "Others", key="unit-others-upload"
                                )

                            add_upload = st.button(
                                "Add", key="add-upload", use_container_width=True
                            )

                            if add_upload:
                                if not input_name or not input_description:
                                    st.warning(
                                        "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                                    )
                                else:
                                    db_list = [
                                        "constant_inputs",
                                        "variable_inputs",
                                        "upload_inputs",
                                        "outputs",
                                    ]

                                    # Check if the input name is already used by another node in any of the databases
                                    node_exist = any(
                                        (input_name == node["input_name"])
                                        for db in db_list  # Iterate over the list of databases
                                        for node in st.session_state.get(
                                            db, []
                                        )  # Access each database in session_state
                                    )
                                    if node_exist:
                                        st.warning(
                                            "The input name you entered is already in use. Please choose a different name."
                                        )
                                    else:
                                        if unit_upload == "Others" and not unit_others_upload:
                                            st.warning(
                                                "Please fill in the 'Others' field before proceeding."
                                            )
                                        else:
                                            add_input_upl(
                                                input_name=input_name,
                                                descriptions=input_description,
                                                type=input_type,
                                                as_multiplier=as_multiplier_upload,
                                                unit=unit_upload,
                                                unit_others=unit_others_upload
                                                if unit_upload == "Others"
                                                else None,
                                                starting_date=start_date_upload,
                                                trend_frequency=frequency_upload,
                                                filtered_data=filtered_data,
                                                orientation=orientation,
                                            )

                        except Exception as e:
                            st.error("Please select a valid range.")

                # Tab output
                with output_tab:
                    output_name = st.text_input("Output Name", key="output-name")
                    out_description = st.text_input("Descriptions", key="output-descriptions")

                    # Action button
                    add_out = st.button("Add", key="add-out", use_container_width=True)

                    if add_out:
                        add_output(
                            input_name=input_name, descriptions=input_description, type=input_type
                        )

                with rule_tab:
                    rule_name = st.text_input(
                        "Rule Name",
                        key="rule-name",
                    )
                    
                    rule_descriptions = st.text_input(
                        "Rule Descriptions",
                        key="rule-descriptions",
                    )
                    
                    rule_type = st.selectbox(
                        "Select Rules",
                        options=["Math", "Financial Modelling"],
                        key="rule-type",
                    )

                    if rule_type == "Math":
                        sub_rule_type = st.selectbox(
                            "Rules",
                            options=[
                                "Multiply",
                                "Division",
                                "Addition",
                                "Subtraction",
                            ],
                        )

                    # Action button
                    add_rules = st.button(
                        "Add", key="add-rules", use_container_width=True
                    )

                    if add_rules:
                        add_rule(
                            rule_type,
                            sub_rule_type,
                        )

    # Streamlit flow layout
    selected_node = streamlit_flow(
        st.session_state["flow_key"],
        st.session_state["nodes"],
        st.session_state["edges"],
        fit_view=True,
        allow_new_edges=True,
        animate_new_edges=False,
        enable_pane_menu=False,
        enable_edge_menu=False,
        enable_node_menu=False,
        get_node_on_click=True,
        get_edge_on_click=True,
        hide_watermark=True,
        pan_on_drag=True,
    )

    # st.write(selected_node)

    db_list = [
        "constant_inputs",
        "variable_inputs",
        "upload_inputs",
        "outputs",
        "rules",
    ]

    # Search for the selected_node in all databases
    node_selected_data = next(
        (
            node_data
            for db in db_list  # Iterate over the list of databases
            for node_data in st.session_state.get(db, [])  # Check each database
            if node_data["node_id"] == selected_node  # Check for matching node_id
        ),
        None,  # Default value if no match is found
    )

    if node_selected_data and node_selected_data["type"] == "Constant":
        with st.expander("Preview Constant Input", expanded=True):
            col1, col2, col3, col4 = st.columns(4)  # 4 equally spaced columns
            with col1:
                edit_input_name = st.text_input(
                    "Input Name",
                    key="edit-input-name",
                    value=node_selected_data["input_name"],
                )
            with col2:
                edit_input_description = st.text_input(
                    "Descriptions",
                    key="edit-input-descriptions",
                    value=node_selected_data["input_description"],
                )
            with col3:
                edit_value_constant = st.number_input(
                    "Value",
                    key="edit-value-constant",
                    value=node_selected_data["value"],
                )
            with col4:
                edit_unit_constant = st.selectbox(
                    "Unit",
                    ["USD", "IDR", "Others"],
                    key="edit-unit-cons",
                    index=["USD", "IDR", "Others"].index(node_selected_data["unit"]),
                )

                if edit_unit_constant == "Others":
                    edit_unit_others = st.text_input(
                        "Others",
                        key="edit-others-cons",
                        value=node_selected_data["unit_others"]
                        if unit_constant == "Others"
                        else None,
                    )
                else:
                    edit_unit_others = None

                cupd_1, cupd_2 = st.columns(2)

                with cupd_1:
                    # Action button
                    edit_cons = st.button(
                        "Update", key="edit-cons", use_container_width=True
                    )

                    update_node_data = {
                        "node_id": selected_node,
                        "input_name": edit_input_name,
                        "input_description": edit_input_description,
                        "type": node_selected_data["type"],
                        "value": edit_value_constant,
                        "unit": edit_unit_constant,
                        "unit_others": edit_unit_others,
                    }
                    if edit_cons:
                        if not edit_input_name or not edit_input_description:
                            st.warning(
                                "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                            )
                        else:
                            if edit_unit_constant == "Others" and not edit_unit_others:
                                st.warning(
                                    "Please fill in the 'Others' field before proceeding."
                                )
                            else:
                                update_node(
                                    selected_node,
                                    node_selected_data,
                                    update_node_data,
                                    edit_input_name,
                                )
                with cupd_2:
                    del_cons = st.button(
                        "Delete", key="delete-cons", use_container_width=True
                    )

                # If the session state is True, show the confirmation options
                if del_cons:
                    st.session_state["confirm_delete_constant"] = True

                if st.session_state["confirm_delete_constant"]:
                    st.error(
                        "Are you sure you want to delete this item? This action cannot be undone."
                    )

                    cdel_1, cdel_2 = st.columns(2)

                    with cdel_1:
                        if st.button("Yes", use_container_width=True):
                            delete_node(selected_node, node_selected_data)

                    with cdel_2:
                        if st.button("No", use_container_width=True):
                            st.warning("Node deletion canceled")

                            st.session_state["confirm_delete_constant"] = False

    if node_selected_data and node_selected_data["type"] == "Variable":
        with st.expander("Preview Variable Input", expanded=True):
            tab_data, tab_chart, tab_edit = st.tabs(["Data", "Chart", "Edit"])
            with tab_data:
                df = generate_value_dataframe(node_selected_data).T
                # Apply multiple styles with custom main color #1AA3A3
                styled_html = style_dataframe(df, "#1AA3A3")
                st.markdown(
                    f'<div style="overflow-x: auto;">{styled_html}</div>',
                    unsafe_allow_html=True,
                )

            with tab_chart:
                df_plot = generate_value_dataframe(node_selected_data)
                fig = plot_bar_chart(
                    df_plot, main_color="#1AA3A3", title="Node Data Bar Chart"
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)

            with tab_edit:
                # Create a 2-column layout for the basic input fields
                col1, col2, col3 = st.columns(3)

                with col1:
                    var_edit_input_name = st.text_input(
                        "Input Name",
                        key="var-edit-input-name",
                        value=node_selected_data["input_name"],
                    )

                    edit_number_of_conditions = st.number_input(
                        "Number of Conditions",
                        min_value=1,
                        max_value=10,
                        step=1,  # Limits for the number of conditions
                        key="edit-conditions-num",
                        value=node_selected_data["num_conditions"],
                    )

                with col2:
                    var_edit_input_description = st.text_input(
                        "Descriptions",
                        key="var-edit-input-descriptions",
                        value=node_selected_data["input_description"],
                    )
                    edit_unit_variable = st.selectbox(
                        "Unit",
                        ["USD", "IDR", "Others"],
                        key="edit-unit-var",
                        index=["USD", "IDR", "Others"].index(
                            node_selected_data["unit"]
                        ),
                    )
                    if edit_unit_variable == "Others":
                        edit_unit_others_variable = st.text_input(
                            "Others",
                            key="edit-unit-others-var",
                            value=node_selected_data["unit_others"],
                        )

                with col3:
                    edit_start_date_variable = st.date_input(
                        "Starting Date",
                        key="edit-var-start-date",
                        value=node_selected_data["starting_date"],
                    )
                    # Separate section for the number of conditions
                    edit_trend_frequency_variable = st.selectbox(
                        "Trend Frequency",
                        ["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"],
                        key="edit-trend-frequency-var",
                        index=[
                            "Daily",
                            "Monthly",
                            "Quarterly",
                            "Semi-Annual",
                            "Annually",
                        ].index(node_selected_data["trend_frequency"]),
                    )

                edit_as_multiplier_variable = st.toggle(
                    "As Multiplier",
                    key="edit-as-multiplier-var",
                    value=node_selected_data["as_multiplier"],
                )

                # Dynamically create tabs based on the number of conditions
                if edit_number_of_conditions > 0:
                    tab_names = [f"Condition {i+1}" for i in range(edit_number_of_conditions)]
                    tabs = st.tabs(tab_names)
                    edit_conditions = []

                    # Base Condition (First Condition)
                    with tabs[0]:
                        st.write("Base Condition")

                        # 3-column layout for the first condition inputs
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            edit_initial_trend_percent = st.number_input(
                                f"% Trend ({edit_trend_frequency_variable})",
                                key="edit-trend-percent-var-1",
                                min_value=0.0,
                                max_value=100.0,
                                step=0.1,
                                value=node_selected_data["conditions"][0][
                                    "trend_percent"
                                ],
                            )
                        with col2:
                            edit_initial_trend_duration = st.number_input(
                                f"Duration ({edit_trend_frequency_variable})",
                                key="edit-duration-var-1",
                                min_value=1,
                                step=1,
                                value=node_selected_data["conditions"][0]["duration"],
                            )
                        with col3:
                            edit_initial_trend_value = st.number_input(
                                f"Initial Value ({edit_trend_frequency_variable})",
                                key="edit-value-var-1",
                                min_value=0.0,
                                step=0.1,
                                value=node_selected_data["conditions"][0]["value"],
                            )

                        # Store the first condition values
                        edit_initial_condition_values = {
                            "trend_percent": edit_initial_trend_percent,
                            "duration": edit_initial_trend_duration,
                            "value": edit_initial_trend_value,
                        }
                        edit_conditions.append(edit_initial_condition_values)

                    # Subsequent Condition Inputs
                    for i in range(1, edit_number_of_conditions):
                        if i < node_selected_data["num_conditions"]:
                            with tabs[i]:
                                st.write(f"Condition {i+1}")

                                # Toggle to use own values or inherit from the first condition
                                edit_use_own_values = st.toggle(
                                    f"Use own values?",
                                    key=f"edit-use-own-values-{i}",
                                    value=False
                                    if (
                                        node_selected_data["conditions"][i]["value"]
                                        == None
                                    )
                                    else True,
                                )

                                # 3-column layout for subsequent conditions
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    edit_trend_percent_variable = st.number_input(
                                        f"% Trend ({edit_trend_frequency_variable})",
                                        key=f"edit-trend-percent-var-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                        value=node_selected_data["conditions"][i][
                                            "trend_percent"
                                        ],
                                    )
                                with col2:
                                    edit_duration_variable = st.number_input(
                                        f"Duration ({edit_trend_frequency_variable})",
                                        key=f"edit-duration-var-{i+1}",
                                        min_value=1,
                                        step=1,
                                        value=node_selected_data["conditions"][i][
                                            "duration"
                                        ],
                                    )
                                with col3:
                                    if edit_use_own_values:
                                        edit_value_variable = st.number_input(
                                            f"Initial Value ({edit_trend_frequency_variable})",
                                            key=f"edit-value-var-{i+1}",
                                            min_value=0.0,
                                            step=0.1,
                                            value=0.0
                                            if not node_selected_data["conditions"][i][
                                                "value"
                                            ]
                                            else node_selected_data["conditions"][i][
                                                "value"
                                            ],
                                        )
                                        edit_after_conditions = {
                                            "trend_percent": edit_trend_percent_variable,
                                            "duration": edit_duration_variable,
                                            "value": edit_value_variable,
                                        }
                                    else:
                                        edit_after_conditions = {
                                            "trend_percent": edit_trend_percent_variable,
                                            "duration": edit_duration_variable,
                                            "value": None,
                                        }

                                edit_conditions.append(edit_after_conditions)
                        else:
                            with tabs[i]:
                                st.write(f"Condition {i+1}")

                                # Toggle to use own values or inherit from the first condition
                                edit_use_own_values = st.toggle(
                                    f"Use own values?", key=f"edit-use-own-values-{i}"
                                )

                                # 3-column layout for subsequent conditions
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    edit_trend_percent_variable = st.number_input(
                                        f"% Trend ({trend_frequency_variable})",
                                        key=f"edit-trend-percent-var-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                    )
                                with col2:
                                    edit_duration_variable = st.number_input(
                                        f"Duration ({trend_frequency_variable})",
                                        key=f"edit-duration-var-{i+1}",
                                        min_value=1,
                                        step=1,
                                    )
                                with col3:
                                    if edit_use_own_values:
                                        edit_value_variable = st.number_input(
                                            f"Initial Value ({trend_frequency_variable})",
                                            key=f"edit-value-var-{i+1}",
                                            min_value=0.0,
                                            step=0.1,
                                        )
                                        edit_after_conditions = {
                                            "trend_percent": edit_trend_percent_variable,
                                            "duration": edit_duration_variable,
                                            "value": edit_value_variable,
                                        }
                                    else:
                                        edit_after_conditions = {
                                            "trend_percent": trend_percent_variable,
                                            "duration": duration_variable,
                                            "value": None,
                                        }

                                edit_conditions.append(edit_after_conditions)

                _, _, _, cl4 = st.columns(4)

                with cl4:
                    cupd_1, cupd_2 = st.columns(2)

                    with cupd_1:
                        # Action button
                        edit_var = st.button(
                            "Update", key="edit-var", use_container_width=True
                        )

                        var_update_node_data = {
                            "node_id": node_selected_data["node_id"],
                            "input_name": var_edit_input_name,
                            "input_description": var_edit_input_description,
                            "type": node_selected_data["type"],
                            "as_multiplier": edit_as_multiplier_variable,
                            "unit": edit_unit_variable,
                            "unit_others": edit_unit_others_variable
                            if edit_unit_variable == "Others"
                            else None,
                            "starting_date": edit_start_date_variable,
                            "trend_frequency": edit_trend_frequency_variable,
                            "num_conditions": edit_number_of_conditions,
                            "conditions": edit_conditions,
                        }

                        if edit_var:
                            if not var_edit_input_name or not var_edit_input_description:
                                st.warning(
                                    "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                                )
                            else:
                                if (
                                    edit_unit_variable == "Others"
                                    and not edit_unit_others_variable
                                ):
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    update_node(
                                        selected_node,
                                        node_selected_data,
                                        var_update_node_data,
                                        var_edit_input_name,
                                    )
                    with cupd_2:
                        del_var = st.button(
                            "Delete", key="delete-cons", use_container_width=True
                        )

                    # If the session state is True, show the confirmation options
                    if del_var:
                        st.session_state["confirm_delete_variable"] = True

                    if st.session_state["confirm_delete_variable"]:
                        st.error(
                            "Are you sure you want to delete this item? This action cannot be undone."
                        )

                        cdel_1, cdel_2 = st.columns(2)

                        with cdel_1:
                            if st.button("Yes", use_container_width=True):
                                delete_node(selected_node, node_selected_data)

                        with cdel_2:
                            if st.button("No", use_container_width=True):
                                st.warning("Node deletion canceled")

                                st.session_state["confirm_delete_variable"] = False

    if node_selected_data and node_selected_data["type"] == "Upload":
        with st.expander("Preview Upload Input", expanded=True):
            tab_data, tab_chart, tab_edit = st.tabs(["Data", "Chart", "Edit"])

            with tab_data:
                if node_selected_data["orientation"] == "Horizontal":
                    df = node_selected_data["filtered_data"]
                if node_selected_data["orientation"] == "Vertical":
                    df = node_selected_data["filtered_data"].T
                # Apply multiple styles with custom main color #5A6D8A
                styled_html = style_dataframe(df, "#5A6D8A")
                st.markdown(
                    f'<div style="overflow-x: auto;">{styled_html}</div>',
                    unsafe_allow_html=True,
                )

            with tab_chart:

                if node_selected_data["orientation"] == "Horizontal":
                    df_plot = node_selected_data["filtered_data"].T
                if node_selected_data["orientation"] == "Vertical":
                    df_plot = node_selected_data["filtered_data"]
                fig = plot_bar_chart(
                    df_plot, main_color="#5A6D8A", title="Node Data Bar Chart"
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)

            with tab_edit:
                # Create a 2-column layout for the basic input fields
                col1, col2, col3 = st.columns(3)

                with col1:
                    upl_edit_input_name = st.text_input(
                        "Input Name",
                        key="upl-edit-input-name",
                        value=node_selected_data["input_name"],
                    )

                with col2:
                    upl_edit_input_description = st.text_input(
                        "Descriptions",
                        key="upl-edit-input-descriptions",
                        value=node_selected_data["input_description"],
                    )

                    edit_unit_upload = st.selectbox(
                        "Unit",
                        ["USD", "IDR", "Others"],
                        key="edit-unit-upl",
                        index=["USD", "IDR", "Others"].index(
                            node_selected_data["unit"]
                        ),
                    )

                    if edit_unit_upload == "Others":
                        edit_unit_others_upload = st.text_input(
                            "Others",
                            key="edit-unit-others-upl",
                            value=node_selected_data["unit_others"],
                        )
                    else:
                        edit_unit_others_upload = None

                with col3:
                    edit_start_date_upload = st.date_input(
                        "Starting Date",
                        key="edit-upl-start-date",
                        value=node_selected_data["starting_date"],
                    )

                    # Separate section for the number of conditions
                    edit_trend_frequency_upload = st.selectbox(
                        "Trend Frequency",
                        ["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"],
                        key="edit-trend-frequency-upl",
                        index=[
                            "Daily",
                            "Monthly",
                            "Quarterly",
                            "Semi-Annual",
                            "Annually",
                        ].index(node_selected_data["trend_frequency"]),
                    )

                edit_as_multiplier_upload = st.toggle(
                    "As Multiplier",
                    key="edit-as-multiplier-upl",
                    value=node_selected_data["as_multiplier"],
                )

                edit_confirmation = st.toggle("Re-upload?", key="confirm-reupload")

                if edit_confirmation:
                    edit_uploaded_file = st.file_uploader(
                        "Choose an Excel file", type=["xlsx"], key="upl"
                    )

                    if edit_uploaded_file is not None:
                        try:
                            # Read the Excel file with multiple sheets
                            df = pd.read_excel(uploaded_file, sheet_name=None)

                            # Get list of sheet names
                            sheet_names = list(df.keys())

                            # Dropdown to select the sheet
                            selected_sheet = st.selectbox(
                                "Select sheet", sheet_names, key="upl-upload"
                            )

                            # Extract data from the selected sheet
                            data = df[selected_sheet]

                            st.write(f"Preview of sheet '{selected_sheet}'")
                            st.dataframe(data)

                            # Slider for selecting column index range
                            st.subheader("Select Column Index Range")
                            start_col, end_col = st.slider(
                                "Select column range",
                                min_value=0,
                                max_value=len(data.columns) - 1,
                                value=(0, len(data.columns) - 1),
                                step=1,
                                key="col_slider-upl",
                            )

                            # Slider for selecting row index range
                            st.subheader("Select Row Index Range")
                            start_row, end_row = st.slider(
                                "Select row range",
                                min_value=0,
                                max_value=len(data) - 1,
                                value=(0, len(data) - 1),
                                step=1,
                                key="row_slider-upl",
                            )

                            # Filter data based on selected rows and columns
                            edit_filtered_data = data.iloc[
                                start_row : end_row + 1, start_col : end_col + 1
                            ]

                            # Choose the orientation of the data
                            edit_orientation = st.radio(
                                "Select the data orientation for the date index",
                                ("Horizontal", "Vertical"),
                                key="orientation-upl",
                            )

                            # Define frequency mapping for date increments
                            freq_mapping = {
                                "Daily": lambda d, x: d + timedelta(days=x),
                                "Monthly": lambda d, x: d + relativedelta(months=x),
                                "Quarterly": lambda d, x: d
                                + relativedelta(months=3 * x),
                                "Semi-Annual": lambda d, x: d
                                + relativedelta(months=6 * x),
                                "Annually": lambda d, x: d + relativedelta(years=x),
                            }

                            date_increment_fn = freq_mapping.get(
                                edit_trend_frequency_upload
                            )

                            current_date = edit_start_date_upload

                            edit_periods = max(
                                end_row - start_row + 1, end_col - start_col + 1
                            )
                            edit_date_index = []

                            for period in range(edit_periods):
                                edit_date_index.append(current_date)
                                current_date = date_increment_fn(current_date, 1)

                            # Apply the date index based on the selected orientation
                            if edit_orientation == "Horizontal":
                                edit_filtered_data.columns = edit_date_index
                                edit_filtered_data.index = ["Value"]
                                df = edit_filtered_data
                                styled_html = style_dataframe(df, "#5A6D8A")
                                st.markdown(
                                    f'<div style="overflow-x: auto;">{styled_html}</div>',
                                    unsafe_allow_html=True,
                                )

                            if edit_orientation == "Vertical":
                                edit_filtered_data.index = edit_date_index
                                edit_filtered_data.columns = ["Value"]
                                df = edit_filtered_data.T
                                styled_html = style_dataframe(df, "#5A6D8A")
                                st.markdown(
                                    f'<div style="overflow-x: auto;">{styled_html}</div>',
                                    unsafe_allow_html=True,
                                )

                            upl_update_node_data = {
                                "node_id": node_selected_data["node_id"],
                                "input_name": upl_edit_input_name,
                                "input_description": upl_edit_input_description,
                                "type": node_selected_data["type"],
                                "as_multiplier": edit_as_multiplier_upload,
                                "unit": edit_unit_upload,
                                "unit_others": edit_unit_others_upload,
                                "starting_date": edit_start_date_upload,
                                "trend_frequency": edit_trend_frequency_upload,
                                "filtered_data": edit_filtered_data,
                                "orientation": edit_orientation,
                            }

                        except Exception as e:
                            st.error("Please select a valid range.")

                else:
                    edit_orientation = node_selected_data["orientation"]
                    edit_filtered_data = node_selected_data["filtered_data"]

                    # Define frequency mapping for date increments
                    freq_mapping = {
                        "Daily": lambda d, x: d + timedelta(days=x),
                        "Monthly": lambda d, x: d + relativedelta(months=x),
                        "Quarterly": lambda d, x: d + relativedelta(months=3 * x),
                        "Semi-Annual": lambda d, x: d + relativedelta(months=6 * x),
                        "Annually": lambda d, x: d + relativedelta(years=x),
                    }

                    date_increment_fn = freq_mapping.get(edit_trend_frequency_upload)

                    current_date = edit_start_date_upload
                    edit_date_index = []

                    # Apply the date index based on the selected orientation
                    if edit_orientation == "Horizontal":
                        edit_periods = len(edit_filtered_data.columns)
                        for period in range(edit_periods):
                            edit_date_index.append(current_date)
                            current_date = date_increment_fn(current_date, 1)
                        edit_filtered_data.columns = edit_date_index
                        edit_filtered_data.index = ["Value"]
                        df = edit_filtered_data.copy()
                        styled_html = style_dataframe(df, "#5A6D8A")
                        st.markdown(
                            f'<div style="overflow-x: auto;">{styled_html}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        edit_periods = len(edit_filtered_data.index)
                        for period in range(edit_periods):
                            edit_date_index.append(current_date)
                            current_date = date_increment_fn(current_date, 1)
                        edit_filtered_data.index = edit_date_index
                        edit_filtered_data.columns = ["Value"]
                        df = edit_filtered_data.T
                        styled_html = style_dataframe(df, "#5A6D8A")
                        st.markdown(
                            f'<div style="overflow-x: auto;">{styled_html}</div>',
                            unsafe_allow_html=True,
                        )

                    upl_update_node_data = {
                        "node_id": node_selected_data["node_id"],
                        "input_name": upl_edit_input_name,
                        "input_description": upl_edit_input_description,
                        "type": node_selected_data["type"],
                        "as_multiplier": edit_as_multiplier_upload,
                        "unit": edit_unit_upload,
                        "unit_others": edit_unit_others_upload,
                        "starting_date": edit_start_date_upload,
                        "trend_frequency": edit_trend_frequency_upload,
                        "filtered_data": edit_filtered_data,
                        "orientation": edit_orientation,
                    }

                _, _, _, cl4 = st.columns(4)

                with cl4:
                    cupd_1, cupd_2 = st.columns(2)

                    with cupd_1:
                        # Action button
                        edit_upl = st.button(
                            "Update", key="edit-upl", use_container_width=True
                        )

                        if edit_upl:
                            if not upl_edit_input_name or not upl_edit_input_description:
                                st.warning(
                                    "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                                )
                            else:
                                if (
                                    edit_unit_upload == "Others"
                                    and not edit_unit_others_upload
                                ):
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    update_node(
                                        selected_node,
                                        node_selected_data,
                                        upl_update_node_data,
                                        upl_edit_input_name,
                                    )
                    with cupd_2:
                        del_upl = st.button(
                            "Delete", key="delete-upl", use_container_width=True
                        )

                    # If the session state is True, show the confirmation options
                    if del_upl:
                        st.session_state["confirm_delete_upload"] = True

                    if st.session_state["confirm_delete_upload"]:
                        st.error(
                            "Are you sure you want to delete this item? This action cannot be undone."
                        )

                        cdel_1, cdel_2 = st.columns(2)

                        with cdel_1:
                            if st.button("Yes", use_container_width=True):
                                delete_node(selected_node, node_selected_data)

                        with cdel_2:
                            if st.button("No", use_container_width=True):
                                st.warning("Node deletion canceled")

                                st.session_state["confirm_delete_upload"] = False

    if node_selected_data and node_selected_data["type"] == "Rule":
        with st.expander("Preview Rule", expanded=True):
            flow_key = st.session_state["flow_key"]
            connected_input_node = []
            existing_nodes = st.session_state[flow_key]["nodes"]
            existing_edges = st.session_state[flow_key]["edges"]
            for edge in existing_edges:
                if edge["target"] == node_selected_data["node_id"]:
                    for node in existing_nodes:
                        if node["id"] == edge["source"] and node["type"] == "input":
                            connected_input_node.append(edge["source"])

            dataset_node = []
            for con_node in connected_input_node:
                if "Cons" in con_node:
                    for cons_node in st.session_state["constant_inputs"]:
                        if cons_node["node_id"] == con_node:
                            data_node = {
                                "node_id": cons_node["node_id"],
                                "node_name": cons_node["input_name"],
                                "as_multiplier": True,
                                "type": "Cons",
                                "data": cons_node["value"],
                            }

                            dataset_node.append(data_node)

                if "Upl" in con_node:
                    for upl_node in st.session_state["upload_inputs"]:
                        if upl_node["node_id"] == con_node:

                            frequency = upl_node["trend_frequency"]

                            if frequency in [
                                "Monthly",
                                "Quarterly",
                                "Semi-Annual",
                                "Annually",
                            ]:
                                # Generate the data based on the current node's frequency

                                if upl_node["orientation"] == "Vertical":
                                    period_data = upl_node["filtered_data"]
                                    period_data.index = pd.to_datetime(
                                        period_data.index
                                    )
                                if upl_node["orientation"] == "Horizontal":
                                    period_data = upl_node["filtered_data"].T
                                    period_data.index = pd.to_datetime(
                                        period_data.index
                                    )

                                # Create an empty DataFrame to hold daily data
                                daily_data = pd.DataFrame()

                                # Determine the number of months to shift based on the frequency
                                freq_offset = {
                                    "Monthly": 1,
                                    "Quarterly": 3,
                                    "Semi-Annual": 6,
                                    "Annually": 12,
                                }

                                # Iterate through the data and distribute values across days
                                for i in range(len(period_data) - 1):
                                    start_date = period_data.index[i]
                                    end_date = period_data.index[
                                        i + 1
                                    ]  # The next date (depends on the frequency)

                                    # Create a date range for the days between the current and next date
                                    date_range = pd.date_range(
                                        start=start_date,
                                        end=end_date - pd.Timedelta(days=1),
                                        freq="D",
                                    )

                                    # Get the value for the current period
                                    value = period_data["Value"].iloc[i]

                                    # Calculate the number of days in the period
                                    days_in_period = (end_date - start_date).days

                                    if upl_node["as_multiplier"] == True:
                                        # Create a DataFrame for the daily values
                                        daily_period_data = pd.DataFrame(
                                            {"Date": date_range, "Daily Value": value}
                                        )
                                    else:
                                        daily_period_data = pd.DataFrame(
                                            {
                                                "Date": date_range,
                                                "Daily Value": value / days_in_period,
                                            }
                                        )

                                    # Append to the daily_data DataFrame
                                    daily_data = pd.concat(
                                        [daily_data, daily_period_data],
                                        ignore_index=True,
                                    )

                                # Handle the last period (from the last entry to the end of the next offset period)
                                last_period_start = period_data.index[-1]
                                last_period_end = last_period_start + pd.DateOffset(
                                    months=freq_offset[frequency]
                                )  # Adjust based on the frequency
                                date_range = pd.date_range(
                                    start=last_period_start,
                                    end=last_period_end - pd.Timedelta(days=1),
                                    freq="D",
                                )
                                value = period_data["Value"].iloc[-1]

                                days_in_last_period = (
                                    last_period_end - last_period_start
                                ).days  # Number of days for the last period
                                if upl_node["as_multiplier"] == True:
                                    daily_last_period_data = pd.DataFrame(
                                        {"Date": date_range, "Daily Value": value}
                                    )
                                else:
                                    daily_last_period_data = pd.DataFrame(
                                        {
                                            "Date": date_range,
                                            "Daily Value": value / days_in_last_period,
                                        }
                                    )
                                # Append last period data to the daily_data DataFrame
                                daily_data = pd.concat(
                                    [daily_data, daily_last_period_data],
                                    ignore_index=True,
                                )

                                # Sort daily data by date
                                daily_data.sort_values(by="Date", inplace=True)

                                data_node = {
                                    "node_id": upl_node["node_id"],
                                    "node_name": upl_node["input_name"],
                                    "as_multiplier": upl_node["as_multiplier"],
                                    "type": "Upl",
                                    "data": daily_data,
                                }

                                dataset_node.append(data_node)
                            else:
                                # Generate the data based on the current node's frequency
                                if upl_node["orientation"] == "Vertical":
                                    period_data = upl_node["filtered_data"]
                                    period_data.index = pd.to_datetime(
                                        period_data.index
                                    )
                                if upl_node["orientation"] == "Horizontal":
                                    period_data = upl_node["filtered_data"].T
                                    period_data.index = pd.to_datetime(
                                        period_data.index
                                    )

                                # Create an empty DataFrame to hold daily data
                                daily_data = period_data
                                data_node = {
                                    "node_id": upl_node["node_id"],
                                    "node_name": upl_node["input_name"],
                                    "as_multiplier": upl_node["as_multiplier"],
                                    "type": "Upl",
                                    "data": daily_data,
                                }

                                dataset_node.append(data_node)

                if "Var" in con_node:
                    for var_node in st.session_state["variable_inputs"]:
                        if var_node["node_id"] == con_node:

                            frequency = var_node["trend_frequency"]  # Get the frequency

                            if frequency in [
                                "Monthly",
                                "Quarterly",
                                "Semi-Annual",
                                "Annually",
                            ]:
                                # Generate the data based on the current node's frequency
                                period_data = generate_value_dataframe(var_node)

                                # Create an empty DataFrame to hold daily data
                                daily_data = pd.DataFrame()

                                # Determine the number of months to shift based on the frequency
                                freq_offset = {
                                    "Monthly": 1,
                                    "Quarterly": 3,
                                    "Semi-Annual": 6,
                                    "Annually": 12,
                                }

                                # Iterate through the data and distribute values across days
                                for i in range(len(period_data) - 1):
                                    start_date = period_data.index[i]
                                    end_date = period_data.index[
                                        i + 1
                                    ]  # The next date (depends on the frequency)

                                    # Create a date range for the days between the current and next date
                                    date_range = pd.date_range(
                                        start=start_date,
                                        end=end_date - pd.Timedelta(days=1),
                                        freq="D",
                                    )

                                    # Get the value for the current period
                                    value = period_data["Value"].iloc[i]

                                    # Calculate the number of days in the period
                                    days_in_period = (end_date - start_date).days

                                    if var_node["as_multiplier"] == True:
                                        # Create a DataFrame for the daily values
                                        daily_period_data = pd.DataFrame(
                                            {"Date": date_range, "Daily Value": value}
                                        )
                                    else:
                                        daily_period_data = pd.DataFrame(
                                            {
                                                "Date": date_range,
                                                "Daily Value": value / days_in_period,
                                            }
                                        )

                                    # Append to the daily_data DataFrame
                                    daily_data = pd.concat(
                                        [daily_data, daily_period_data],
                                        ignore_index=True,
                                    )

                                # Handle the last period (from the last entry to the end of the next offset period)
                                last_period_start = period_data.index[-1]
                                last_period_end = last_period_start + pd.DateOffset(
                                    months=freq_offset[frequency]
                                )  # Adjust based on the frequency
                                date_range = pd.date_range(
                                    start=last_period_start,
                                    end=last_period_end - pd.Timedelta(days=1),
                                    freq="D",
                                )
                                value = period_data["Value"].iloc[-1]

                                days_in_last_period = (
                                    last_period_end - last_period_start
                                ).days  # Number of days for the last period
                                if var_node["as_multiplier"] == True:
                                    daily_last_period_data = pd.DataFrame(
                                        {"Date": date_range, "Daily Value": value}
                                    )
                                else:
                                    daily_last_period_data = pd.DataFrame(
                                        {
                                            "Date": date_range,
                                            "Daily Value": value / days_in_last_period,
                                        }
                                    )
                                # Append last period data to the daily_data DataFrame
                                daily_data = pd.concat(
                                    [daily_data, daily_last_period_data],
                                    ignore_index=True,
                                )

                                # Sort daily data by date
                                daily_data.sort_values(by="Date", inplace=True)
                                daily_data.set_index("Date", inplace=True)

                                data_node = {
                                    "node_id": var_node["node_id"],
                                    "node_name": var_node["input_name"],
                                    "as_multiplier": var_node["as_multiplier"],
                                    "type": "Var",
                                    "data": daily_data,
                                }

                                dataset_node.append(data_node)

                            else:
                                daily_data = generate_value_dataframe(var_node)

                                # Sort daily data by date
                                daily_data.sort_values(by="Date", inplace=True)

                                data_node = {
                                    "node_id": var_node["node_id"],
                                    "node_name": var_node["input_name"],
                                    "as_multiplier": var_node["as_multiplier"],
                                    "type": "Var",
                                    "data": daily_data,
                                }

                                dataset_node.append(data_node)

            frequency_rule = st.selectbox(
                "Select Frequency",
                options=["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"],
                key="frequency-rule",
            )

            unify_dateset = join_datasets_on_date(
                dataset_node,
            )

            df = unify_dateset.T

            df_input = transform_based_on_frequency(
                dataset=unify_dateset,
                dataset_node=dataset_node,
                frequency=frequency_rule,
            )

            if node_selected_data["sub_rule_type"] == "Addition":
                df_results = df_input.copy()
                df_results["Addition"] = df_results.sum(axis=1)

                styled_html = auto_style_dataframe(df_results.T).to_html()
                st.markdown(
                    f'<div style="overflow-x: auto;">{styled_html}</div>',
                    unsafe_allow_html=True,
                )

                plot_transformed_data(df_results)
            
            if node_selected_data["sub_rule_type"] == "Multiplication":
                st.write("Nice")

    # Monitoring for debugging
    # flow_key = st.session_state["flow_key"]
    # if flow_key in st.session_state and flow_key and st.session_state[flow_key]:
    #     st.dataframe(st.session_state["constant_inputs"], use_container_width=True)
    #     st.dataframe(st.session_state["variable_inputs"], use_container_width=True)
    #     st.dataframe(st.session_state["upload_inputs"], use_container_width=True)
    #     st.dataframe(st.session_state["outputs"], use_container_width=True)
    #     st.dataframe(st.session_state["rules"], use_container_width=True)
    #     st.dataframe(st.session_state[flow_key]["nodes"], use_container_width=True)
    #     st.dataframe(st.session_state[flow_key]["edges"], use_container_width=True)
    #     st.dataframe(st.session_state["nodes"], use_container_width=True)
    #     st.dataframe(st.session_state["edges"], use_container_width=True)


if __name__ == "__main__":
    decision_flow_page()
