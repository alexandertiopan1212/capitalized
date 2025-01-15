import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import random
from sidebar import render_page_based_on_sidebar

import streamlit as st
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import random
from typing import Tuple, Dict, Union

from df_function import *
import pandas as pd


def decision_flow_page():
    # Sidebar
    # render_page_based_on_sidebar()

    if "nodes" not in st.session_state:
        st.session_state.setdefault("input_cons_db", [])
        st.session_state.setdefault("input_var_db", [])
        st.session_state.setdefault("input_upl_db", [])
        st.session_state.setdefault("output_db", [])
        st.session_state.setdefault("rule_db", [])
        st.session_state.setdefault("nodes", [])
        st.session_state.setdefault("edges", [])
        st.session_state["flow_key"] = f"hackable_flow_{random.randint(0, 1000)}"
        st.session_state["confirm_delete_cons"] = False
        st.session_state["confirm_delete_var"] = False

    new_node = None  # Initialize new_node

    # Config
    with st.sidebar:
        # Add item
        with st.expander("Add Item", expanded=True):

            tab1_add, tab2_add, tab3_add = st.tabs(["Input", "Output", "Rule"])

            # Tab input
            with tab1_add:

                # General setup
                st.subheader("General Setup", divider=True)
                inp_name = st.text_input("Input Name", key="input-name")

                inp_desc = st.text_input("Descriptions", key="input-descriptions")

                # Type setup
                st.subheader("Type Setup", divider=True)
                inp_type = st.radio(
                    "Type", ["Constant", "Variable", "Upload"], key="input-type"
                )

                # Constant input
                if inp_type == "Constant":

                    # Parameter
                    st.subheader("Parameter", divider=True)

                    val_cons = st.number_input("Value", key="value-constant")

                    unit_cons = st.selectbox(
                        "Unit", ["USD", "IDR", "Others"], key="unit-cons"
                    )

                    if unit_cons == "Others":
                        unit_others = st.text_input("Others", key="others-cons")

                    # Action button
                    add_cons = st.button(
                        "Add", key="add-cons", use_container_width=True
                    )

                    if add_cons:
                        if not inp_name or not inp_desc:
                            st.warning(
                                "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                            )
                        else:
                            db_list = ["input_cons_db", "input_var_db", "input_upl_db", "output_db", "rule_db"]

                            # Check if the input name is already used by another node in any of the databases
                            node_exist = any(
                                (inp_name == node["input_name"])
                                for db in db_list  # Iterate over the list of databases
                                for node in st.session_state.get(db, [])  # Access each database in session_state
                            )
    
                            if node_exist:
                                st.warning(
                                    "The input name you entered is already in use. Please choose a different name."
                                )
                            else:
                                if unit_cons == "Others" and not unit_others:
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    add_input_cons(
                                        input_name=inp_name,
                                        descriptions=inp_desc,
                                        type=inp_type,
                                        value=val_cons,
                                        unit=unit_cons,
                                        unit_others=unit_others
                                        if unit_cons == "Others"
                                        else None,
                                    )

                # Variable Input
                if inp_type == "Variable":

                    # Trend setup
                    st.subheader("Parameter", divider=True)

                    as_multiplier_var = st.toggle(
                        "As Multiplier", key="as-multiplier-var"
                    )

                    unit_var = st.selectbox(
                        "Unit", ["USD", "IDR", "Others"], key="unit-var"
                    )

                    if unit_var == "Others":
                        unit_others_var = st.text_input(
                            "Others",
                            key="unit-others-var"
                        )

                    start_date_var = st.date_input(
                        "Starting Date", key="var-start-date"
                    )

                    trend_frequency_var = st.selectbox(
                        "Trend Frequency",
                        ["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"],
                        key="trend-frequency-var",
                    )

                    conditions_num = st.number_input(
                        "Number of Conditions",
                        min_value=1,
                        max_value=10,
                        step=1,  # Limits for the number of conditions
                        key="conditions-num",
                    )

                    st.subheader("Conditions")

                    # Dynamically create tabs based on the number of conditions
                    if conditions_num > 0:
                        tab_names = [f"{i+1}" for i in range(int(conditions_num))]
                        tabs = st.tabs(tab_names)
                        conditions = []
                        # First condition inputs
                        with tabs[0]:
                            st.write(f"Base Condition")
                            trend_percent_var_1 = st.number_input(
                                f"% Trend ({trend_frequency_var})",
                                key="trend-percent-var-1",
                                min_value=0.0,
                                max_value=100.0,
                                step=0.1,
                            )

                            duration_var_1 = st.number_input(
                                f"Duration ({trend_frequency_var})",
                                key="duration-var-1",
                                min_value=1,
                                step=1,
                            )

                            value_var_1 = st.number_input(
                                f"Initial Value ({trend_frequency_var})",
                                key="value-var-1",
                                min_value=0.0,
                                step=0.1,
                            )

                            # Store the first condition values
                            first_condition_values = {
                                "trend_percent": trend_percent_var_1,
                                "duration": duration_var_1,
                                "value": value_var_1,
                            }

                            conditions.append(first_condition_values)

                        # Subsequent condition inputs with toggle
                        for i in range(1, conditions_num):
                            with tabs[i]:
                                st.write(f"Condition {i+1}")

                                # Toggle to use own values or inherit from the first condition
                                use_own_values = st.toggle(
                                    f"Use own values?", key=f"use-own-values-{i}"
                                )

                                if use_own_values:
                                    trend_percent_var = st.number_input(
                                        f"% Trend ({trend_frequency_var})",
                                        key=f"trend-percent-var-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                    )

                                    duration_var = st.number_input(
                                        f"Duration ({trend_frequency_var})",
                                        key=f"duration-var-{i+1}",
                                        min_value=1,
                                        step=1,
                                    )

                                    value_var = st.number_input(
                                        f"Initial Value ({trend_frequency_var})",
                                        key=f"value-var-{i+1}",
                                        min_value=0.0,
                                        step=0.1,
                                    )
                                    after_conditions = {
                                        "trend_percent": trend_percent_var,
                                        "duration": duration_var,
                                        "value": value_var,
                                    }

                                    conditions.append(after_conditions)
                                else:
                                    trend_percent_var = st.number_input(
                                        f"% Trend ({trend_frequency_var})",
                                        key=f"trend-percent-var-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                    )

                                    duration_var = st.number_input(
                                        f"Duration ({trend_frequency_var})",
                                        key=f"duration-var-{i+1}",
                                        min_value=1,
                                        step=1,
                                    )

                                    after_conditions = {
                                        "trend_percent": trend_percent_var,
                                        "duration": duration_var,
                                        "value": None,
                                    }

                                    conditions.append(after_conditions)

                    # Action button
                    add_var = st.button("Add", key="add-var", use_container_width=True)
                    if add_var:
                        if not inp_name or not inp_desc:
                            st.warning(
                                "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                            )
                        else:
                            db_list = ["input_cons_db", "input_var_db", "input_upl_db", "output_db", "rule_db"]

                            # Check if the input name is already used by another node in any of the databases
                            node_exist = any(
                                (inp_name == node["input_name"])
                                for db in db_list  # Iterate over the list of databases
                                for node in st.session_state.get(db, [])  # Access each database in session_state
                            )
                            if node_exist:
                                st.warning(
                                    "The input name you entered is already in use. Please choose a different name."
                                )
                            else: 
                                if unit_var == "Others" and not unit_others_var:
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    add_input_var(
                                        input_name=inp_name, 
                                        descriptions=inp_desc, 
                                        type=inp_type,
                                        unit=unit_var,
                                        unit_others=unit_others_var 
                                        if unit_var == "Others"
                                        else None,
                                        as_multiplier=as_multiplier_var,
                                        starting_date=start_date_var,
                                        trend_frequency=trend_frequency_var,
                                        num_conditions=conditions_num,
                                        conditions=conditions,
                                        )

                if inp_type == "Upload":

                    uploaded_file = st.file_uploader(
                        "Choose an Excel file", type=["xlsx"]
                    )

                    if uploaded_file is not None:
                        try:
                            df = pd.read_excel(uploaded_file, sheet_name=None)

                            sheet_names = list(df.keys())

                            selected_sheet = st.selectbox("Select sheet", sheet_names)

                            data = df[selected_sheet]

                            st.write(f"Preview of sheet '{selected_sheet}'")
                            st.dataframe(data)

                            st.subheader("Select Columns and Rows")

                            selected_columns = st.multiselect(
                                "Select columns",
                                data.columns.tolist(),
                                default=data.columns.tolist(),
                            )

                            num_rows = st.slider(
                                "Select number of rows to display",
                                1,
                                len(data),
                                value=min(10, len(data)),
                            )

                            selected_data = data[selected_columns].head(num_rows)

                            st.write("Selected Data:")

                            st.dataframe(selected_data)

                            unit_upl = st.selectbox(
                                "Unit", ["USD", "IDR", "Others"], key="unit-upl"
                            )

                        except Exception as e:

                            st.error(f"Error loading file: {e}")

                    # Action button
                    add_upl = st.button("Add", key="add-upl", use_container_width=True)

                    if add_upl:
                        add_input_upl(
                            input_name=inp_name, descriptions=inp_desc, type=inp_type
                        )

                # Tab output
                with tab2_add:
                    out_name = st.text_input("Output Name", key="output-name")
                    out_desc = st.text_input("Descriptions", key="output-descriptions")

                    # Action button
                    add_out = st.button("Add", key="add-out", use_container_width=True)

                    if add_out:
                        add_output(
                            input_name=inp_name, descriptions=inp_desc, type=inp_type
                        )

                with tab3_add:
                    # with st.container(height=400, border=None):
                    multi_rule = st.multiselect(
                        "Select Rules",
                        options=["Payback Period", "Profit Loss", "IRR", "Cash Flow"],
                    )

                    # Action button
                    add_rules = st.button(
                        "Add", key="add-rules", use_container_width=True
                    )

                    if add_rules:
                        add_rule(
                            input_name=inp_name, descriptions=inp_desc, type=inp_type
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

    st.write(selected_node)

    db_list = ["input_cons_db", "input_var_db", "input_upl_db", "output_db", "rule_db"]

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
                edit_inp_name = st.text_input(
                    "Input Name",
                    key="edit-input-name",
                    value=node_selected_data["input_name"],
                )
            with col2:
                edit_inp_desc = st.text_input(
                    "Descriptions",
                    key="edit-input-descriptions",
                    value=node_selected_data["input_description"],
                )
            with col3:
                edit_val_cons = st.number_input(
                    "Value",
                    key="edit-value-constant",
                    value=node_selected_data["value"],
                )
            with col4:
                edit_unit_cons = st.selectbox(
                    "Unit",
                    ["USD", "IDR", "Others"],
                    key="edit-unit-cons",
                    index=["USD", "IDR", "Others"].index(node_selected_data["unit"]),
                )

                if edit_unit_cons == "Others":
                    edit_unit_others = st.text_input(
                        "Others",
                        key="edit-others-cons",
                        value=node_selected_data["unit_others"]
                        if unit_cons == "Others"
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
                        "input_name": edit_inp_name,
                        "input_description": edit_inp_desc,
                        "type": node_selected_data["type"],
                        "value": edit_val_cons,
                        "unit": edit_unit_cons,
                        "unit_others": edit_unit_others,
                    }
                    if edit_cons:
                        if not edit_inp_name or not edit_inp_desc:
                            st.warning(
                                "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                            )
                        else:
                            if edit_unit_cons == "Others" and not edit_unit_others:
                                st.warning(
                                    "Please fill in the 'Others' field before proceeding."
                                )
                            else:
                                update_node(
                                    selected_node,
                                    node_selected_data,
                                    update_node_data,
                                    edit_inp_name,
                                )
                with cupd_2:
                    del_cons = st.button(
                        "Delete", key="delete-cons", use_container_width=True
                    )

                # If the session state is True, show the confirmation options
                if del_cons:
                    st.session_state["confirm_delete_cons"] = True

                if st.session_state["confirm_delete_cons"]:
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
    
                            st.session_state["confirm_delete_cons"] = False


    if node_selected_data and node_selected_data["type"] == "Variable":
        with st.expander("Preview Variable Input", expanded=True):
            tab_data, tab_chart, tab_edit = st.tabs(["Data", "Chart", "Edit"])
            with tab_data:
                df = generate_value_dataframe(node_selected_data).T
                # Apply multiple styles with custom main color #1AA3A3
                styled_html = style_dataframe(df, "#1AA3A3")

                # Display the styled DataFrame using st.write with unsafe_allow_html=True
                st.write(styled_html, unsafe_allow_html=True)

            with tab_chart:
                df_plot = generate_value_dataframe(node_selected_data)
                fig = plot_bar_chart(df_plot, main_color="#1AA3A3", title="Node Data Bar Chart")

                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)
            
            with tab_edit:
                # Create a 2-column layout for the basic input fields
                col1, col2, col3 = st.columns(3)

                with col1:
                    var_edit_inp_name = st.text_input(
                        "Input Name", 
                        key="var-edit-input-name",
                        value=node_selected_data["input_name"])
                    
                    edit_conditions_num = st.number_input(
                        "Number of Conditions",
                        min_value=1,
                        max_value=10,
                        step=1,  # Limits for the number of conditions
                        key="edit-conditions-num",
                        value=node_selected_data["num_conditions"],
                    )

                with col2:
                    var_edit_inp_desc = st.text_input(
                        "Descriptions", 
                        key="var-edit-input-descriptions",
                        value=node_selected_data["input_description"])
                    edit_unit_var = st.selectbox(
                        "Unit", 
                        ["USD", "IDR", "Others"], 
                        key="edit-unit-var",
                        index=["USD", "IDR", "Others"].index(node_selected_data["unit"])
                        )
                    if edit_unit_var == "Others":
                        edit_unit_others_var = st.text_input(
                            "Others", 
                            key="edit-unit-others-var",
                            value=node_selected_data["unit_others"])
                        
                with col3:
                    edit_start_date_var = st.date_input(
                        "Starting Date", 
                        key="edit-var-start-date",
                        value=node_selected_data["starting_date"])
                    # Separate section for the number of conditions
                    edit_trend_frequency_var = st.selectbox(
                        "Trend Frequency",
                        ["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"],
                        key="edit-trend-frequency-var",
                        index=["Daily", "Monthly", "Quarterly", "Semi-Annual", "Annually"].index(node_selected_data["trend_frequency"])
                    )
                

                edit_as_multiplier_var = st.toggle(
                        "As Multiplier", 
                        key="edit-as-multiplier-var",
                        value=node_selected_data["as_multiplier"])

                # Dynamically create tabs based on the number of conditions
                if edit_conditions_num > 0:
                    tab_names = [f"Condition {i+1}" for i in range(edit_conditions_num)]
                    tabs = st.tabs(tab_names)
                    edit_conditions = []

                    # Base Condition (First Condition)
                    with tabs[0]:
                        st.write("Base Condition")

                        # 3-column layout for the first condition inputs
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            edit_trend_percent_var_1 = st.number_input(
                                f"% Trend ({edit_trend_frequency_var})",
                                key="edit-trend-percent-var-1",
                                min_value=0.0,
                                max_value=100.0,
                                step=0.1,
                                value=node_selected_data["conditions"][0]["trend_percent"]
                            )
                        with col2:
                            edit_duration_var_1 = st.number_input(
                                f"Duration ({edit_trend_frequency_var})",
                                key="edit-duration-var-1",
                                min_value=1,
                                step=1,
                                value=node_selected_data["conditions"][0]["duration"]
                            )
                        with col3:
                            edit_value_var_1 = st.number_input(
                                f"Initial Value ({edit_trend_frequency_var})",
                                key="edit-value-var-1",
                                min_value=0.0,
                                step=0.1,
                                value=node_selected_data["conditions"][0]["value"]
                            )

                        # Store the first condition values
                        edit_first_condition_values = {
                            "trend_percent": edit_trend_percent_var_1,
                            "duration": edit_duration_var_1,
                            "value": edit_value_var_1,
                        }
                        edit_conditions.append(edit_first_condition_values)

                    # Subsequent Condition Inputs
                    for i in range(1, edit_conditions_num):
                        if i < node_selected_data["num_conditions"]:
                            with tabs[i]:
                                st.write(f"Condition {i+1}")

                                # Toggle to use own values or inherit from the first condition
                                edit_use_own_values = st.toggle(
                                    f"Use own values?", 
                                    key=f"edit-use-own-values-{i}",
                                    value=False if (node_selected_data["conditions"][i]["value"] == None) else True)

                                # 3-column layout for subsequent conditions
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    edit_trend_percent_var = st.number_input(
                                        f"% Trend ({edit_trend_frequency_var})",
                                        key=f"edit-trend-percent-var-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                        value=node_selected_data["conditions"][i]["trend_percent"]
                                    )
                                with col2:
                                    edit_duration_var = st.number_input(
                                        f"Duration ({edit_trend_frequency_var})",
                                        key=f"edit-duration-var-{i+1}",
                                        min_value=1,
                                        step=1,
                                        value=node_selected_data["conditions"][i]["duration"]
                                    )
                                with col3:
                                    if edit_use_own_values:
                                        edit_value_var = st.number_input(
                                            f"Initial Value ({edit_trend_frequency_var})",
                                            key=f"edit-value-var-{i+1}",
                                            min_value=0.0,
                                            step=0.1,
                                            value= 0.0 if not node_selected_data["conditions"][i]["value"] else node_selected_data["conditions"][i]["value"]
                                        )
                                        edit_after_conditions = {
                                            "trend_percent": edit_trend_percent_var,
                                            "duration": edit_duration_var,
                                            "value": edit_value_var,
                                        }
                                    else:
                                        edit_after_conditions = {
                                            "trend_percent": edit_trend_percent_var,
                                            "duration": edit_duration_var,
                                            "value": None,
                                        }

                                edit_conditions.append(edit_after_conditions)
                        else:
                            with tabs[i]:
                                st.write(f"Condition {i+1}")

                                # Toggle to use own values or inherit from the first condition
                                edit_use_own_values = st.toggle(
                                    f"Use own values?", 
                                    key=f"edit-use-own-values-{i}")

                                # 3-column layout for subsequent conditions
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    edit_trend_percent_var = st.number_input(
                                        f"% Trend ({trend_frequency_var})",
                                        key=f"edit-trend-percent-var-{i+1}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=0.1,
                                    )
                                with col2:
                                    edit_duration_var = st.number_input(
                                        f"Duration ({trend_frequency_var})",
                                        key=f"edit-duration-var-{i+1}",
                                        min_value=1,
                                        step=1,
                                    )
                                with col3:
                                    if edit_use_own_values:
                                        edit_value_var = st.number_input(
                                            f"Initial Value ({trend_frequency_var})",
                                            key=f"edit-value-var-{i+1}",
                                            min_value=0.0,
                                            step=0.1,
                                        )
                                        edit_after_conditions = {
                                            "trend_percent": edit_trend_percent_var,
                                            "duration": edit_duration_var,
                                            "value": edit_value_var,
                                        }
                                    else:
                                        edit_after_conditions = {
                                            "trend_percent": trend_percent_var,
                                            "duration": duration_var,
                                            "value": None,
                                        }

                                edit_conditions.append(edit_after_conditions)
                
                _,_,_,cl4 = st.columns(4)

                with cl4:
                    cupd_1, cupd_2 = st.columns(2)

                    with cupd_1:
                        # Action button
                        edit_var = st.button(
                            "Update", key="edit-var", use_container_width=True
                        )

                        var_update_node_data = {
                            "node_id": node_selected_data["node_id"],
                            "input_name": var_edit_inp_name,
                            "input_description": var_edit_inp_desc,
                            "type": node_selected_data["type"],
                            "as_multiplier": edit_as_multiplier_var,
                            "unit": edit_unit_var,
                            "unit_others": edit_unit_others_var if edit_unit_var == "Others" else None,
                            "starting_date": edit_start_date_var,
                            "trend_frequency": edit_trend_frequency_var,
                            "num_conditions": edit_conditions_num,
                            "conditions": edit_conditions,
                        }

                        if edit_var:
                            if not var_edit_inp_name or not var_edit_inp_desc:
                                st.warning(
                                    "Please ensure both 'Input Name' and 'Description' fields are filled in before proceeding."
                                )
                            else:
                                if edit_unit_var == "Others" and not edit_unit_others_var:
                                    st.warning(
                                        "Please fill in the 'Others' field before proceeding."
                                    )
                                else:
                                    update_node(
                                        selected_node,
                                        node_selected_data,
                                        var_update_node_data,
                                        var_edit_inp_name,
                                    )
                    with cupd_2:
                        del_var = st.button(
                            "Delete", key="delete-cons", use_container_width=True
                        )

                    # If the session state is True, show the confirmation options
                    if del_var:
                        st.session_state["confirm_delete_var"] = True

                    if st.session_state["confirm_delete_var"]:
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
        
                                st.session_state["confirm_delete_var"] = False

    # Monitoring for debugging
    flow_key = st.session_state["flow_key"]
    if flow_key in st.session_state and flow_key and st.session_state[flow_key]:
        st.dataframe(st.session_state["input_cons_db"], use_container_width=True)
        st.write(st.session_state["input_var_db"], use_container_width=True)
        st.dataframe(st.session_state["input_upl_db"], use_container_width=True)
        st.dataframe(st.session_state["output_db"], use_container_width=True)
        st.dataframe(st.session_state["rule_db"], use_container_width=True)
        st.dataframe(st.session_state[flow_key]["nodes"], use_container_width=True)
        st.dataframe(st.session_state[flow_key]["edges"], use_container_width=True)
        st.dataframe(st.session_state["nodes"], use_container_width=True)
        st.dataframe(st.session_state["edges"], use_container_width=True)


if __name__ == "__main__":
    decision_flow_page()
