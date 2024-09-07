import numpy as np
import plotly.graph_objs as go
import streamlit as st


def binomial_tree_pricing(S, K, T, r, sigma, steps, q=0):
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p_up = (np.exp((r * dt) - (q * dt)) - d) / (u - d)
    p_down = 1 - p_up

    asset_prices = np.zeros((steps + 1, steps + 1))
    edv_values = np.zeros((steps + 1, steps + 1))
    iv_values = np.zeros((steps + 1, steps + 1))
    fv_values = np.zeros((steps + 1, steps + 1))

    for i in range(steps + 1):
        for j in range(i + 1):
            asset_prices[j, i] = S * (u ** (i - j)) * (d**j)

    for j in range(steps + 1):
        edv_values[j, steps] = max(0, asset_prices[j, steps] - K)

    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            edv_values[j, i] = (
                p_up * edv_values[j, i + 1] + p_down * edv_values[j + 1, i + 1]
            ) / np.exp(r * dt)

    for i in range(steps + 1):
        for j in range(i + 1):
            iv_values[j, i] = max(asset_prices[j, i] - K, 0)

    for i in range(steps + 1):
        for j in range(i + 1):
            fv_values[j, i] = max(edv_values[j, i], iv_values[j, i])

    final_option_price = fv_values[0, 0]

    def plot_tree(tree_df, title):
        edge_x = []
        edge_y = []
        node_x = []
        node_y = []
        node_text = []
        midpoint = steps / 2

        for i in range(steps + 1):
            for j in range(i + 1):
                x_pos = i
                y_pos = j - (i / 2) + midpoint
                value = tree_df[j, i]
                node_x.append(x_pos)
                node_y.append(y_pos)
                node_text.append(f"{value:.2f}")

                if i < steps:
                    edge_x.extend([x_pos, x_pos + 1, None])
                    edge_y.extend([y_pos, y_pos - 0.5, None])
                    edge_x.extend([x_pos, x_pos + 1, None])
                    edge_y.extend([y_pos, y_pos + 0.5, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=2, color="blue"),
            hoverinfo="none",
            mode="lines",
        )
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            hoverinfo="text",
            marker=dict(size=10, color="red", line_width=2),
        )

        layout = go.Layout(
            title=title,
            showlegend=False,
            height=800,
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            template="plotly_white",
        )

        return go.Figure(data=[edge_trace, node_trace], layout=layout)

    asset_fig = plot_tree(asset_prices, "Asset Price Tree")
    edv_fig = plot_tree(edv_values, "EDV Option Tree")
    iv_fig = plot_tree(iv_values, "IV Option Tree")
    fv_fig = plot_tree(fv_values, "FV Option Tree")

    st.plotly_chart(asset_fig)
    st.plotly_chart(edv_fig)
    st.plotly_chart(iv_fig)
    st.plotly_chart(fv_fig)

    st.write(f"**Final Option Price**: ${final_option_price:.2f}")
