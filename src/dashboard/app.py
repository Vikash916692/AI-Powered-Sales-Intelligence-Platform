import os
import sys
from pathlib import Path

# Ensure workspace root and cwd are always in sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
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

# Page Configuration
st.set_page_config(
    page_title="AI-Powered Sales Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Custom CSS Tokens & Theme
apply_custom_theme()

# Sidebar: Authentication & Global Filters
render_auth_sidebar()
filters = render_global_sidebar_filters()

# Title Header
st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="font-size: 2.2rem; margin-bottom: 0.2rem; color: #F8FAFC;">
                    🚀 Sales Intelligence Command Center
                </h1>
                <p style="color: #94A3B8; font-size: 1rem; margin: 0;">
                    Enterprise Data Warehousing • Predictive ML • Agentic AI & RAG Ecosystem
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">● SYSTEM ONLINE</span>
                <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">FastAPI @ Port 8000</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# Fetch Live Macro KPIs via Dedicated API Client
# ----------------------------------------------------
try:
    with st.spinner("Fetching executive metrics from Data Warehouse..."):
        overview = api_client.get_executive_overview()
        customer_econ = api_client.get_customer_economics()
        sla_data = api_client.get_logistics_sla()
        sales_resp = api_client.get_sales_mart(
            start_date=filters["start_date"],
            end_date=filters["end_date"],
            page=1,
            page_size=60,
        )
        top_cats = api_client.get_top_categories(limit=8)

    # 4-Column High-Impact KPI Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rev = float(overview.get("total_gross_revenue", 0.0))
        render_metric_card(
            label="Total Gross Revenue",
            value=f"${rev:,.2f}",
            delta="+14.2% YoY Growth",
            delta_type="positive",
            icon="💰",
        )

    with col2:
        orders = int(overview.get("total_orders", 0))
        render_metric_card(
            label="Completed Orders",
            value=f"{orders:,}",
            delta="98.6K Transactions",
            delta_type="neutral",
            icon="📦",
        )

    with col3:
        aov = float(overview.get("executive_aov", 0.0))
        render_metric_card(
            label="Average Order Value",
            value=f"${aov:,.2f}",
            delta="Basket Depth: 1.14 items",
            delta_type="neutral",
            icon="🛒",
        )

    with col4:
        sla_pct = float(sla_data.get("on_time_delivery_rate_pct", 0.0))
        render_metric_card(
            label="On-Time Delivery SLA",
            value=f"{sla_pct:.2f}%",
            delta="Target: >= 95.0%",
            delta_type="positive",
            icon="🚚",
        )

    st.markdown("---")

    # 2-Column Chart Layout
    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.markdown("### 📈 Historical Sales Revenue Velocity")
        sales_records = sales_resp.get("data", [])
        if sales_records:
            df_sales = pd.DataFrame(sales_records)
            df_sales = df_sales.sort_values("sales_date")
            fig_area = create_daily_revenue_area_chart(df_sales)
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("No sales records match the selected date filter.")

    with c_right:
        st.markdown("### 🎯 Category Revenue Pareto (80/20)")
        fig_pareto = create_pareto_category_chart(top_cats)
        st.plotly_chart(fig_pareto, use_container_width=True)

except APIClientError as e:
    render_error_banner("Backend API Connectivity Issue", error_details=str(e))
    st.info("Ensure the FastAPI backend server is active at `http://localhost:8000`.")
except Exception as e:
    render_error_banner("Unexpected Error", error_details=str(e))
