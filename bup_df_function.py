import streamlit as st
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import random
from typing import Tuple, Dict, Union
import uuid
import pandas as pd
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go


def add_input_cons(
        input_name, 
        descriptions, 
        type, 
        value, 
        unit, 
        unit_others
        ):

    data = {"content": f"{input_name}"}

    style = {
        "color": "white",
        "backgroundColor": "#4D4D4D",
        "border": "1px solid white",
    }

    node_id = f"Cons Node-{uuid.uuid4()}"
    node_data = {
        "node_id": node_id,
        "input_name": input_name,
        "input_description": descriptions,
        "type": type,
        "value": value,
        "unit": unit,
        "unit_others": unit_others,
    }
    add_node(
        id=node_id,
        data=data,
        style=style,
        node_type="input",
        source_position="right",
        target_position="left",
        node_data=node_data,
        input_type=type,
    )


def add_input_var(
        input_name, 
        descriptions, 
        type,
        unit,
        unit_others,
        as_multiplier,
        starting_date,
        trend_frequency,
        num_conditions,
        conditions,
        ):

    data = {"content": f"{input_name}"}
    style = {
        "color": "white",
        "backgroundColor": "#1AA3A3",
        "border": "1px solid white",
    }
    node_id = f"Var Node-{uuid.uuid4()}"

    node_data = {
        "node_id": node_id,
        "input_name": input_name,
        "input_description": descriptions,
        "type": type,
        "as_multiplier": as_multiplier,
        "unit": unit,
        "unit_others": unit_others,
        "starting_date": starting_date,
        "trend_frequency": trend_frequency,
        "num_conditions": num_conditions,
        "conditions": conditions,
    }

    add_node(
        id=node_id,
        data=data,
        style=style,
        node_type="input",
        source_position="right",
        target_position="left",
        node_data=node_data,
        input_type=type
    )


def add_input_upl(input_name, descriptions, type):

    data = {"content": f"{input_name}"}
    style = {
        "color": "white",
        "backgroundColor": "#5A6D8A",
        "border": "1px solid white",
    }
    add_node(
        # id=input_name,
        data=data,
        style=style,
        node_type="input",
        source_position="right",
        target_position="left",
    )


def add_output(input_name, descriptions, type):

    data = {"content": f"{input_name}"}
    style = {
        "color": "white",
        "backgroundColor": "#2E8B57",
        "border": "1px solid white",
    }
    add_node(
        # id=input_name,
        data=data,
        style=style,
        node_type="output",
        source_position="right",
        target_position="left",
    )


def add_rule(input_name, descriptions, type):

    data = {"content": f"{input_name}"}
    style = {
        "color": "white",
        "backgroundColor": "#003366",
        "border": "1px solid white",
    }
    add_node(
        # id=input_name,
        data=data,
        style=style,
        node_type="default",
        source_position="right",
        target_position="left",
    )


# Add node
def add_node(
    id: str = None,
    pos: Tuple[float, float] = (100, 100),
    data: Dict[str, any] = {"content": "New Node"},
    node_type: str = "default",
    source_position: str = "bottom",
    target_position: str = "top",
    hidden: bool = False,
    selected: bool = False,
    dragging: bool = False,
    draggable: bool = True,
    selectable: bool = True,
    connectable: bool = True,
    resizing: bool = False,
    deletable: bool = True,
    width: Union[float, None] = None,
    height: Union[float, None] = None,
    z_index: float = 0,
    focusable: bool = True,
    style: Dict[str, any] = {},
    node_data: Dict = {},
    input_type: str = None,
    **kwargs,
):
    """Function to add a node to the flow with all configuration options."""

    # Generate a unique ID for the node if not provided
    # node_id = id if id else str(len(st.session_state['nodes']) + 1)

    # Create a new node with all the given settings
    new_node = StreamlitFlowNode(
        id=id,
        pos=pos,
        data=data,
        node_type=node_type,
        source_position=source_position,
        target_position=target_position,
        hidden=hidden,
        selected=selected,
        dragging=dragging,
        draggable=draggable,
        selectable=selectable,
        connectable=connectable,
        resizing=resizing,
        deletable=deletable,
        width=width,
        height=height,
        z_index=z_index,
        focusable=focusable,
        style=style,
        **kwargs,
    )

    # Retrieve the current flow key
    flow_key = st.session_state["flow_key"]

    if flow_key in st.session_state and flow_key:
        # Fetch the existing nodes and edges from the flow state
        new_nodes = [
            StreamlitFlowNode.from_dict(node)
            for node in st.session_state[flow_key]["nodes"]
        ]
        new_nodes.append(new_node)  # Append the new node

        new_edges = [
            StreamlitFlowEdge.from_dict(edge)
            for edge in st.session_state[flow_key]["edges"]
        ]

        # Update session state with new nodes and edges
        st.session_state["nodes"] = new_nodes
        st.session_state["edges"] = new_edges

        if input_type == "Constant":
            st.session_state["input_cons_db"].append(node_data)
        
        if input_type == "Variable":
            st.session_state["input_var_db"].append(node_data)

        if input_type == "Upload":
            st.session_state["input_upl_db"].append(node_data)

        # Recreate the flow key to force re-render
        del st.session_state[flow_key]
        st.session_state["flow_key"] = f"hackable_flow_{random.randint(0, 1000)}"

        # Rerun the app to update the view
        st.rerun()


def delete_node(selected_node, node_selected_data):

    # Check for the current flow key in session state
    flow_key = st.session_state.get("flow_key")
    if flow_key and flow_key in st.session_state:

        # Gather current nodes and filter out the one to be deleted
        del_nodes_dict = [node for node in st.session_state[flow_key]["nodes"]]
        new_n = [nodes for nodes in del_nodes_dict if nodes["id"] != selected_node]

        # Recreate the node and edge lists
        new_nodes = [StreamlitFlowNode.from_dict(node) for node in new_n]
        new_edges = [
            StreamlitFlowEdge.from_dict(edge)
            for edge in st.session_state[flow_key]["edges"]
        ]

        # Update session state with new node and edge lists
        st.session_state["nodes"] = new_nodes
        st.session_state["edges"] = new_edges

        # Remove the selected node from input_cons_db
        if node_selected_data["type"] == "Constant":
            node_rem = [
                nd
                for nd in st.session_state["input_cons_db"]
                if nd != node_selected_data
            ]
            st.session_state["input_cons_db"] = node_rem
            st.session_state["confirm_delete_cons"] = False

        if node_selected_data["type"] == "Variable":
            node_rem = [
                nd
                for nd in st.session_state["input_var_db"]
                if nd != node_selected_data
            ]
            st.session_state["input_var_db"] = node_rem
            st.session_state["confirm_delete_var"] = False

        # Reset the flow key to force re-rendering
        del st.session_state[flow_key]
        st.session_state["flow_key"] = f"hackable_flow_{random.randint(0, 1000)}"

        # Set confirm_delete to False and rerun
        
        st.rerun()


def update_node(selected_node, node_selected_data, update_node_data, edit_inp_name):

    flow_key = st.session_state.get("flow_key")

    if flow_key and flow_key in st.session_state:
        # Get existing nodes
        ext_nodes_dict = [node for node in st.session_state[flow_key]["nodes"]]

        db_list = ["input_cons_db", "input_var_db", "input_upl_db", "output_db", "rule_db"]

        # Check if the input name is already used by another node in any of the databases
        up_node_exist = any(
            (edit_inp_name == node["input_name"] and selected_node != node["node_id"])
            for db in db_list  # Iterate over the list of databases
            for node in st.session_state.get(db, [])  # Access each database in session_state
        )

        if up_node_exist:
            st.warning("Name already used in other nodes. Please change!")
        else:
            # Update the selected node's content
            for nodes in ext_nodes_dict:
                if nodes["id"] == selected_node:
                    content_new = {"content": f"{edit_inp_name}"}
                    nodes["data"] = content_new

            # Update nodes and edges
            new_nodes = [StreamlitFlowNode.from_dict(node) for node in ext_nodes_dict]
            new_edges = [
                StreamlitFlowEdge.from_dict(edge)
                for edge in st.session_state[flow_key]["edges"]
            ]

            # Update session state with new nodes and edges
            st.session_state["nodes"] = new_nodes
            st.session_state["edges"] = new_edges

            # Update input_cons_db with the new node data
            if node_selected_data["type"] == "Constant":
                node_rem = [
                    nd
                    for nd in st.session_state["input_cons_db"]
                    if nd != node_selected_data
                ]
                node_rem.append(update_node_data)
                st.session_state["input_cons_db"] = node_rem

            if node_selected_data["type"] == "Variable":
                node_rem = [
                    nd
                    for nd in st.session_state["input_var_db"]
                    if nd != node_selected_data
                ]
                node_rem.append(update_node_data)
                st.session_state["input_var_db"] = node_rem

            # Reset the flow_key to force re-render
            del st.session_state[flow_key]
            st.session_state["flow_key"] = f"hackable_flow_{random.randint(0, 1000)}"

            # Rerun the Streamlit app to reflect the updates
            st.rerun()


def generate_value_dataframe(node_data):
    # Extract relevant fields from node_data
    starting_date = node_data["starting_date"]
    conditions = node_data["conditions"]
    trend_frequency = node_data["trend_frequency"]
    
    # Parse starting_date to datetime
    current_date = pd.to_datetime(starting_date)

    # Define frequency mapping for date increments
    freq_mapping = {
        "Daily": lambda d, x: d + timedelta(days=x),
        "Monthly": lambda d, x: d + relativedelta(months=x),
        "Quarterly": lambda d, x: d + relativedelta(months=3 * x),
        "Semi-Annual": lambda d, x: d + relativedelta(months=6 * x),
        "Annually": lambda d, x: d + relativedelta(years=x)
    }

    # Get the function to increment dates based on the trend frequency
    date_increment_fn = freq_mapping.get(trend_frequency)
    
    # If trend frequency is invalid, return None
    if not date_increment_fn:
        raise ValueError(f"Invalid trend frequency: {trend_frequency}")

    # Prepare a list to collect the results (dates and values)
    result_data = {"Date": [], "Value": []}

    # Initialize the value with the first condition's initial value
    last_value = conditions[0]["value"]
    
    # Iterate through each condition and generate data
    for condition in conditions:
        trend_percent = condition["trend_percent"]
        duration = condition["duration"]
        initial_value = condition["value"]
        
        # If the initial value is None, continue from the last value
        if initial_value is None:
            initial_value = last_value
        
        # Generate dates and values for the current condition's duration
        for period in range(duration):
            result_data["Date"].append(current_date)
            result_data["Value"].append(initial_value)
            
            # Update date and value for the next period
            current_date = date_increment_fn(current_date, 1)  # Increment date based on trend frequency
            initial_value = initial_value * (1 + trend_percent / 100)  # Apply the trend to update the value
            
        # Update the last_value after this condition
        last_value = initial_value

    # Convert the result data to a DataFrame
    df = pd.DataFrame(result_data)

    # Set the Date column as the index
    df.set_index("Date", inplace=True)

    return df



def style_dataframe(df: pd.DataFrame, main_color: str) -> str:
    styled_df = (
        df.style
        .format("{:,.0f}")  # Format values with thousand separators and no decimals
        .background_gradient(cmap='Blues')  # Use a blue gradient for the background
        .set_properties(**{
            'border': '1px solid black', 
            'color': 'black', 
            'font-size': '12px', 
            'text-align': 'center',  # Center align text
            'vertical-align': 'middle',  # Center align vertically
            'width': '150px'  # Add cell width
        })
        .set_caption("Node Data: Trend and Duration Over Time")  # Add a caption for context
        .set_table_styles([
            {
                'selector': 'thead th',
                'props': [
                    ('background-color', main_color),  # Use the main color for the header
                    ('color', 'white'), 
                    ('font-size', '14px'), 
                    ('padding', '10px'),
                    ('text-align', 'center')  # Center align headers
                ]
            },
            {
                'selector': 'tbody td',
                'props': [
                    ('padding', '10px'), 
                    ('border', '1px solid #ddd'), 
                    ('font-size', '14px'),
                    ('text-align', 'center'),  # Center align cells
                    ('vertical-align', 'middle')  # Center align vertically
                ]
            },
            {
                'selector': 'tbody tr:hover',
                'props': [('background-color', '#f1f1f1')]  # Highlight rows on hover
            },
            {
                'selector': 'caption',
                'props': [
                    ('caption-side', 'bottom'), 
                    ('font-size', '14px'), 
                    ('color', main_color)  # Use the main color for the caption text
                ]
            }
        ])
    )

    # Convert the styled DataFrame to HTML and hide the index
    styled_html = styled_df.to_html(index=False)

    return styled_html


def plot_bar_chart(df: pd.DataFrame, main_color: str, title: str = "Bar Chart") -> go.Figure:
    # Assuming df is transposed and the index contains the category labels
    # and the columns represent the values to plot
    date = df.index  # Category labels
    values = df.iloc[:, 0]  # Assuming single column for values (modify for multiple columns if needed)

    # Create a bar chart using Plotly
    fig = go.Figure(
        data=[
            go.Bar(
                x=date,  # Categories on the x-axis
                y=values,  # Values on the y-axis
                marker_color=main_color,  # Use the provided main color
                text=values.map('{:,.0f}'.format),  # Format values with thousand separators, no decimals
                textposition='outside',  # Position the text on top of the bars
                insidetextanchor='end'  # Adjust the text anchor to keep it outside
            )
        ]
    )

    # Update layout with title and additional styling
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="",  # Remove the y-axis title
        plot_bgcolor="white",  # Set background color to white
        showlegend=False,  # Hide legend
        bargap=0.1,  # Gap between bars
        template="simple_white",  # Clean plot template
        xaxis=dict(showline=False, showgrid=False),  # Remove x-axis line and grid
        yaxis=dict(visible=False),  # Completely hide the y-axis
    )

    return fig