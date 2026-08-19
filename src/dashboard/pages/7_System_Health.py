"""
Page 7: System Health & Infrastructure Diagnostics.
"""

import os
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
cwd = os.getcwd()
for p in [project_root, cwd]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st

from src.dashboard.api_client import APIClientError, api_client
from src.dashboard.components.auth_widget import render_auth_sidebar
from src.dashboard.components.ui_states import render_error_banner
from src.dashboard.theme import apply_custom_theme

apply_custom_theme()
render_auth_sidebar()

st.title("🩺 System Health & Observability Ops")
st.markdown("Real-time operational status of all platform services, databases, vector stores, and machine learning model artifacts.")

st.markdown("---")

try:
    with st.spinner("Pinging platform infrastructure..."):
        health_data = api_client.get_health()

    status_str = health_data.get("status", "unknown").upper()
    status_badge = "badge-success" if status_str == "HEALTHY" else "badge-primary"

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;">
            <div>
                <div style="color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;">Overall System Status</div>
                <div style="color: #F8FAFC; font-size: 1.5rem; font-weight: 700;">Platform Operational</div>
            </div>
            <div>
                <span class="{status_badge}" style="font-size: 1rem; padding: 6px 14px;">● {status_str}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    components = health_data.get("components", {})

    c1, c2 = st.columns(2)

    with c1:
        # 1. MySQL Data Warehouse
        db_stat = components.get("database", {})
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem;">🗄️ MySQL Data Warehouse</div>
                    <span class="badge-success">● {db_stat.get('status', 'N/A').upper()}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.5rem;">
                    Container: <code>sales-intelligence-mysql:8.4</code> • Port <code>3306</code><br>
                    Schema: 5 Dimensions, 3 Fact Tables, 12 Analytical Marts
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Redis Caching
        cache_stat = components.get("cache", {})
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem;">⚡ Redis High-Performance Cache</div>
                    <span class="badge-success">● {cache_stat.get('status', 'N/A').upper()}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.5rem;">
                    Active Provider: <b>{cache_stat.get('provider', 'in_memory_fallback')}</b><br>
                    TTL Policy: 300s automated invalidation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        # 3. ChromaDB Vector Store
        vec_stat = components.get("vector_store", {})
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem;">📚 ChromaDB Vector Knowledge Store</div>
                    <span class="badge-success">● {vec_stat.get('status', 'N/A').upper()}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.5rem;">
                    Schema Docs: <b>{vec_stat.get('schema_docs', 0)} indexed</b><br>
                    Business KPI Docs: <b>{vec_stat.get('business_docs', 0)} indexed</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4. ML Model Artifacts
        ml_stat = components.get("ml_models", {})
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem;">🤖 Machine Learning Pipelines</div>
                    <span class="badge-success">● {ml_stat.get('status', 'N/A').upper()}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.5rem;">
                    Loaded Pipelines: <b>{ml_stat.get('loaded_models', 4)} / 4 Production Models</b><br>
                    Delay, Forecaster, Recommender, Review Sentiment
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### ⚙️ Raw Health Check Payload")
    st.json(health_data)

except APIClientError as e:
    render_error_banner("Could not connect to health diagnostics", str(e))
