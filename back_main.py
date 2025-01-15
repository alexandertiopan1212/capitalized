import streamlit as st
from sidebar import render_page_based_on_sidebar
from streamlit_flow import streamlit_flow
from streamlit_flow.layouts import TreeLayout
from decision_flow_function import (
    setup_node_input,
    calculate_output_for_nodes,
    resample_data_output,
)
import pandas as pd
import plotly.express as px


def decision_flow_page():
    """Render the main decision flow page."""
    render_page_based_on_sidebar()

    st.session_state.setdefault("input_database", [])
    st.session_state.setdefault("output_database", {})

    streamlit_flow(
        "fully_interactive_flow",
        [],
        [],
        fit_view=True,
        show_controls=True,
        allow_new_edges=True,
        animate_new_edges=True,
        layout=TreeLayout("right"),
        enable_pane_menu=True,
        enable_edge_menu=True,
        enable_node_menu=True,
        get_node_on_click=True,
        get_edge_on_click=True,
    )

    if "fully_interactive_flow" in st.session_state:
        nodes_data = pd.DataFrame(st.session_state["fully_interactive_flow"]["nodes"])
        edges_data = pd.DataFrame(st.session_state["fully_interactive_flow"]["edges"])
    else:
        None

    if nodes_data.empty:
        st.warning("Input database is empty. Please add nodes to generate output.")
        return

    calculate_output_for_nodes(nodes_data, edges_data)

    for idx in range(len(nodes_data)):
        node_selected = nodes_data["selected"][idx]
        node_type = nodes_data["type"][idx]

        if node_selected and node_type == "input":
            setup_node_input(nodes_data, idx)
        elif node_selected and node_type == "output":
            with st.expander(f"Output {nodes_data['id'][idx]}"):
                output_id = nodes_data["id"][idx]
                if output_id in st.session_state["output_database"]:
                    output_df = st.session_state["output_database"][output_id]
                    freq = st.selectbox(
                        "Select frequency",
                        ["Monthly", "Quarterly", "Semiannually", "Annually"],
                        key=f"freq_{idx}",
                    )
                    resampled_df = resample_data_output(output_df, freq)
                    st.dataframe(
                        resampled_df.T.round(2), use_container_width=True
                    )  # Round to 2 decimal places when displaying
                    st.plotly_chart(
                        px.bar(output_df).update_traces(
                            marker_line_width=2, texttemplate="%{y:.2f}"
                        )
                    )  # Ensure plot is formatted to 2 decimal places


if __name__ == "__main__":
    decision_flow_page()
