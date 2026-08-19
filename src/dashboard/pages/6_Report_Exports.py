"""
Page 6: Executive Briefing Book & Report Export Center.
"""

import os
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
cwd = os.getcwd()
for p in [project_root, cwd]:
    if p not in sys.path:
        sys.path.insert(0, p)

from datetime import UTC, datetime

import streamlit as st

from src.dashboard.api_client import APIClientError, api_client
from src.dashboard.components.auth_widget import render_auth_sidebar
from src.dashboard.components.ui_states import render_error_banner
from src.dashboard.theme import apply_custom_theme

apply_custom_theme()
render_auth_sidebar()

st.title("📑 Executive Report Export Center")
st.markdown("Download publication-ready, formatted Executive Briefing Books (PDF) and Multi-Tab Financial Analytics Workbooks (Excel).")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(2, 132, 199, 0.3); border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📄</div>
            <h3 style="color: #F8FAFC; margin-bottom: 0.5rem; font-weight: 700;">Executive PDF Briefing Book</h3>
            <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                A multi-page, branded C-Suite briefing document containing:
            </p>
            <ul style="color: #CBD5E1; font-size: 0.85rem; padding-left: 1.2rem;">
                <li>Executive Macro Overview & KPIs ($13.59M Revenue, 98.6K Orders)</li>
                <li>Customer Acquisition, LTV & Repeat Buyer Economics</li>
                <li>Logistics SLA Compliance (97.78% on-time performance)</li>
                <li>RFM Customer Segmentation Quintiles Breakdown</li>
                <li>Top 10 Category Rankings with Units Sold</li>
                <li>Document Security Signature & Verifiable Provenance Checksum</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with st.spinner("Generating Executive PDF Briefing..."):
            pdf_data = api_client.download_pdf_report()

        st.download_button(
            label="⬇️ Download Executive Briefing (PDF)",
            data=pdf_data,
            file_name=f"Executive_Sales_Intelligence_Briefing_{datetime.now(UTC).strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except APIClientError as e:
        render_error_banner("Could not compile PDF Report", str(e))

with col2:
    st.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📊</div>
            <h3 style="color: #F8FAFC; margin-bottom: 0.5rem; font-weight: 700;">Multi-Tab Excel Financial Model</h3>
            <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                A formatted multi-tab spreadsheet workbook containing:
            </p>
            <ul style="color: #CBD5E1; font-size: 0.85rem; padding-left: 1.2rem;">
                <li><b>Tab 1:</b> Executive Overview (Formatted KPI Model)</li>
                <li><b>Tab 2:</b> Daily Sales Mart (Date & Currency formatting)</li>
                <li><b>Tab 3:</b> RFM Customer Segments (Conditional color formatting)</li>
                <li><b>Tab 4:</b> Top Product Categories (Ranking & Unit Prices)</li>
                <li>Formulas & Number Formatting pre-applied for Excel & Google Sheets</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with st.spinner("Compiling Multi-Tab Excel Workbook..."):
            excel_data = api_client.download_excel_report()

        st.download_button(
            label="⬇️ Download Analytical Workbook (Excel)",
            data=excel_data,
            file_name=f"Sales_Intelligence_Analytics_Model_{datetime.now(UTC).strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except APIClientError as e:
        render_error_banner("Could not compile Excel Workbook", str(e))
