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
from src.dashboard.components.charts import create_rfm_sunburst_chart
from src.dashboard.components.global_filters import render_global_sidebar_filters
from src.dashboard.components.kpi_cards import render_metric_card
from src.dashboard.components.ui_states import render_error_banner
from src.dashboard.theme import apply_custom_theme

apply_custom_theme()
render_auth_sidebar()
filters = render_global_sidebar_filters()

st.title("👥 Customer Economics & RFM Segmentation")
st.markdown("Buyer acquisition, lifetime value (LTV) economics, repeat purchasing velocity, and 10-tier RFM segmentation.")

try:
    econ = api_client.get_customer_economics()
    rfm = api_client.get_rfm_segments()

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Customers", f"{int(econ.get('total_customers', 0)):,}", "Registered", "neutral", "👤")
    with c2:
        rep_rate = float(econ.get("repeat_purchase_rate_pct", 0.0))
        render_metric_card("Repeat Buyer Rate", f"{rep_rate:.2f}%", f"{int(econ.get('repeat_customers', 0)):,} Repeat Buyers", "positive" if rep_rate > 3.0 else "neutral", "🔄")
    with c3:
        ltv = float(econ.get("customer_ltv_mean", 0.0))
        render_metric_card("Mean Customer LTV", f"${ltv:,.2f}", "Lifetime Spend", "positive", "💎")
    with c4:
        lifetime = float(econ.get("avg_customer_lifetime_days", 0.0))
        render_metric_card("Avg Customer Lifetime", f"{lifetime:.1f} Days", "Purchase Cycle", "neutral", "⏳")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("### 🌳 RFM Spend Concentration Treemap")
        st.plotly_chart(create_rfm_sunburst_chart(rfm), use_container_width=True)

    with col_right:
        st.markdown("### 📋 Segment Definitions & Action Playbook")
        st.markdown(
            """
            - **🏆 Champions / Loyal:** Top spenders with recent purchases. *Action: VIP rewards & early catalog access.*
            - **🌱 Promising / Recent:** New buyers with moderate spend. *Action: Cross-sell recommendation emails.*
            - **⚠️ At Risk / Need Attention:** High historical spend, but inactive > 120 days. *Action: Personalized win-back vouchers.*
            - **❄️ Hibernating / Lost:** Inactive > 250 days with low frequency. *Action: Discount re-engagement campaigns.*
            """
        )

    st.markdown("### 📊 RFM Segment Distribution Table")
    df_rfm = pd.DataFrame(rfm)
    if not df_rfm.empty:
        st.dataframe(
            df_rfm.style.format({
                "customer_count": "{:,}",
                "customer_share_pct": "{:.1f}%",
                "total_segment_spend": "${:,.2f}",
                "avg_spend_per_customer": "${:,.2f}",
                "avg_recency_days": "{:.1f}d",
            }),
            use_container_width=True,
        )

except APIClientError as e:
    render_error_banner("Failed to load Customer Economics", str(e))
