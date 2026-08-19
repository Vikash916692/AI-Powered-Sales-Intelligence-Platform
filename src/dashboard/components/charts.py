"""
Standardized Plotly Dark-Themed Charts for Sales Analytics.
"""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Consistent color tokens
COLOR_CYAN = "#00F0FF"
COLOR_BLUE = "#38BDF8"
COLOR_EMERALD = "#10B981"
COLOR_AMBER = "#F59E0B"
COLOR_ROSE = "#F43F5E"
BG_DARK = "rgba(15, 23, 42, 0.0)"
GRID_COLOR = "rgba(255, 255, 255, 0.08)"


def create_daily_revenue_area_chart(df: pd.DataFrame) -> go.Figure:
    """Area chart with gradient fill for daily sales revenue trends."""
    if df.empty:
        return go.Figure()

    rev_col = None
    for candidate in ["revenue", "total_revenue", "total_sales_value", "total_sales"]:
        if candidate in df.columns:
            rev_col = candidate
            break

    if not rev_col:
        # Fallback to first numeric column if none matched
        numeric_cols = df.select_dtypes(include=["number"]).columns
        rev_col = numeric_cols[0] if len(numeric_cols) > 0 else None

    if not rev_col:
        return go.Figure()

    date_col = "sales_date" if "sales_date" in df.columns else df.columns[0]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[rev_col],
            mode="lines",
            name="Daily Revenue ($)",
            line={"color": COLOR_CYAN, "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(0, 240, 255, 0.12)",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_DARK,
        plot_bgcolor=BG_DARK,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        xaxis={"gridcolor": GRID_COLOR, "showgrid": True, "title": "Sales Date"},
        yaxis={"gridcolor": GRID_COLOR, "showgrid": True, "title": "Revenue (USD)", "tickprefix": "$"},
        hovermode="x unified",
    )
    return fig


def create_pareto_category_chart(categories: list[dict[str, Any]]) -> go.Figure:
    """Dual-axis Pareto 80/20 category chart (bar + cumulative % line)."""
    df = pd.DataFrame(categories)
    if df.empty:
        return go.Figure()

    df = df.sort_values("total_revenue", ascending=False)
    df["cumulative_pct"] = (df["total_revenue"].cumsum() / df["total_revenue"].sum()) * 100

    fig = go.Figure()

    # Bar trace for revenue
    fig.add_trace(
        go.Bar(
            x=df["category_name"],
            y=df["total_revenue"],
            name="Revenue ($)",
            marker_color=COLOR_BLUE,
            yaxis="y1",
        )
    )

    # Line trace for cumulative percentage
    fig.add_trace(
        go.Scatter(
            x=df["category_name"],
            y=df["cumulative_pct"],
            name="Cumulative %",
            mode="lines+markers",
            line={"color": COLOR_AMBER, "width": 2.5},
            marker={"size": 6},
            yaxis="y2",
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_DARK,
        plot_bgcolor=BG_DARK,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        xaxis={"gridcolor": GRID_COLOR, "tickangle": -30},
        yaxis={"title": "Gross Sales ($)", "gridcolor": GRID_COLOR, "tickprefix": "$"},
        yaxis2={"title": "Cumulative Share (%)", "overlaying": "y", "side": "right", "range": [0, 105], "ticksuffix": "%"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def create_rfm_sunburst_chart(rfm_segments: list[dict[str, Any]]) -> go.Figure:
    """Sunburst / Treemap representation of customer segment spend & share."""
    df = pd.DataFrame(rfm_segments)
    if df.empty:
        return go.Figure()

    fig = px.treemap(
        df,
        path=["rfm_segment"],
        values="total_segment_spend",
        color="avg_spend_per_customer",
        color_continuous_scale="Viridis",
        title="",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_DARK,
        plot_bgcolor=BG_DARK,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
    )
    return fig


def create_forecast_confidence_chart(daily_forecasts: list[dict[str, Any]]) -> go.Figure:
    """Forecast chart with point predictions and 95% confidence interval ribbons."""
    df = pd.DataFrame(daily_forecasts)
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    # Upper bound
    fig.add_trace(
        go.Scatter(
            x=df["forecast_date"],
            y=df["yhat_upper"],
            mode="lines",
            line={"width": 0},
            showlegend=False,
            name="95% Upper Bound",
        )
    )

    # Lower bound with fill
    fig.add_trace(
        go.Scatter(
            x=df["forecast_date"],
            y=df["yhat_lower"],
            mode="lines",
            line={"width": 0},
            fill="tonexty",
            fillcolor="rgba(16, 185, 129, 0.15)",
            name="95% Confidence Interval",
        )
    )

    # Point forecast line
    fig.add_trace(
        go.Scatter(
            x=df["forecast_date"],
            y=df["yhat"],
            mode="lines+markers",
            line={"color": COLOR_EMERALD, "width": 3},
            marker={"size": 4},
            name="Projected Revenue ($)",
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_DARK,
        plot_bgcolor=BG_DARK,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        xaxis={"gridcolor": GRID_COLOR, "title": "Forecast Horizon Date"},
        yaxis={"gridcolor": GRID_COLOR, "title": "Projected Daily Sales ($)", "tickprefix": "$"},
        hovermode="x unified",
    )
    return fig
