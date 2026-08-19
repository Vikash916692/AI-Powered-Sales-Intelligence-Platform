"""
Glassmorphic KPI Cards with Delta Indicators.
"""


import streamlit as st


def render_metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_type: str = "positive",
    icon: str | None = None,
):
    """
    Renders custom HTML glassmorphic KPI card.
    """
    icon_html = f"<span style='margin-right: 6px;'>{icon}</span>" if icon else ""
    delta_class = f"delta-{delta_type}"
    delta_html = f"<div class='metric-delta {delta_class}'>{delta}</div>" if delta else ""

    card_html = f"""
    <div class="metric-card">
        <div class="metric-label">{icon_html}{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
