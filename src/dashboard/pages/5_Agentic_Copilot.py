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
from src.dashboard.components.provenance_drawer import render_provenance_drawer
from src.dashboard.components.ui_states import render_error_banner
from src.dashboard.theme import apply_custom_theme

apply_custom_theme()
render_auth_sidebar()

st.title("🤖 Agentic AI Executive Copilot")
st.markdown("Natural language decision intelligence backed by LangGraph Supervisor, Text-to-SQL, Predictive ML, and ChromaDB RAG.")

# Initialize chat session history
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": "Hello! I am your **Sales Intelligence Executive Copilot**. You can ask me to compute KPIs, generate SQL analyses, run ML forecasts, or diagnose metric anomalies.",
            "provenance": [],
            "audit_trail": "",
        }
    ]

# Offline Mode Switcher
col_title, col_toggle = st.columns([3, 1])
with col_toggle:
    force_offline = st.toggle("Deterministic Mock Engine (Offline)", value=False)

# Quick Prompts
st.markdown("##### 💡 Suggested Strategic Inquiries:")
q_cols = st.columns(4)
with q_cols[0]:
    if st.button("📊 Executive KPI Summary", use_container_width=True):
        st.session_state["selected_prompt"] = "Show me the executive overview of revenue, order volume, and AOV"
with q_cols[1]:
    if st.button("📈 30-Day Sales Forecast", use_container_width=True):
        st.session_state["selected_prompt"] = "Forecast our sales revenue for the next 30 days"
with q_cols[2]:
    if st.button("🔍 Diagnose Delivery Delays", use_container_width=True):
        st.session_state["selected_prompt"] = "Diagnose why customer delivery delays are spiking in Southeast routes"
with q_cols[3]:
    if st.button("🎯 Top 5 Categories & Prices", use_container_width=True):
        st.session_state["selected_prompt"] = "What are our top 5 revenue product categories and their average price?"

# Display Conversation History
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("provenance") or msg.get("audit_trail"):
            render_provenance_drawer(
                provenance_data=msg.get("provenance", []),
                audit_trail_text=msg.get("audit_trail", ""),
            )

# Input Box
user_prompt = st.chat_input("Ask a business or analytical question...")

# Handle pre-selected button prompt or user chat input
prompt_to_send = st.session_state.pop("selected_prompt", None) or user_prompt

if prompt_to_send:
    # 1. Append User Message
    st.session_state["chat_messages"].append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    # 2. Query Multi-Agent API
    with st.chat_message("assistant"):
        with st.spinner("Multi-Agent Supervisor is coordinating analytical subgraphs & ML models..."):
            try:
                res = api_client.query_agent(query=prompt_to_send, force_offline=force_offline)
                response_text = res.get("final_response", "No response generated.")
                prov_data = res.get("provenance_data", [])
                audit_trail = res.get("audit_trail", "")

                st.markdown(response_text)
                render_provenance_drawer(provenance_data=prov_data, audit_trail_text=audit_trail)

                st.session_state["chat_messages"].append({
                    "role": "assistant",
                    "content": response_text,
                    "provenance": prov_data,
                    "audit_trail": audit_trail,
                })
            except APIClientError as e:
                render_error_banner("Agent Execution Failed", str(e))
