import os
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
cwd = os.getcwd()
for p in [project_root, cwd]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import streamlit as st

from src.dashboard.api_client import APIClientError, api_client
from src.dashboard.components.auth_widget import render_auth_sidebar
from src.dashboard.components.charts import create_daily_revenue_area_chart, create_pareto_category_chart
from src.dashboard.components.global_filters import render_global_sidebar_filters
from src.dashboard.components.kpi_cards import render_metric_card
from src.dashboard.components.ui_states import render_error_banner
from src.dashboard.theme import apply_custom_theme

apply_custom_theme()
render_auth_sidebar()
filters = render_global_sidebar_filters()

st.title("🏛️ Executive Overview & Macro Performance")
st.markdown("Top-line marketplace metrics, revenue trends, and category Pareto distribution.")

try:
    overview = api_client.get_executive_overview()
    sales_data = api_client.get_sales_mart(
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        page=1,
        page_size=100,
    )
    top_categories = api_client.get_top_categories(limit=10)

    # Metric Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Gross Revenue", f"${float(overview.get('total_gross_revenue', 0.0)):,.2f}", "+14.2% YoY", "positive", "💰")
    with c2:
        render_metric_card("Total Orders", f"{int(overview.get('total_orders', 0)):,}", "98.6K Completed", "neutral", "📦")
    with c3:
        render_metric_card("Average Order Value", f"${float(overview.get('executive_aov', 0.0)):,.2f}", "Basket: $137.75", "neutral", "🛒")
    with c4:
        render_metric_card("Ecosystem Size", f"{int(overview.get('total_registered_customers', 0)):,} Users", f"{int(overview.get('total_registered_sellers', 0)):,} Merchants", "positive", "👥")

    st.markdown("---")

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("### 📈 Daily Revenue & Volume Trajectory")
        records = sales_data.get("data", [])
        if records:
            df = pd.DataFrame(records).sort_values("sales_date")
            st.plotly_chart(create_daily_revenue_area_chart(df), use_container_width=True)
        else:
            st.info("No records match the current filter selection.")

    with col_b:
        st.markdown("### 🎯 80/20 Category Revenue Concentration")
        st.plotly_chart(create_pareto_category_chart(top_categories), use_container_width=True)

    # Detailed Table
    st.markdown("### 📊 Top 10 Product Categories Breakdown")
    df_cats = pd.DataFrame(top_categories)
    if not df_cats.empty:
        df_cats.columns = ["Category Name", "Units Sold", "Total Revenue ($)", "Average Price ($)"]
        st.dataframe(df_cats.style.format({"Total Revenue ($)": "${:,.2f}", "Average Price ($)": "${:,.2f}", "Units Sold": "{:,}"}), use_container_width=True)

except APIClientError as e:
    render_error_banner("Failed to load Executive Overview", str(e))
