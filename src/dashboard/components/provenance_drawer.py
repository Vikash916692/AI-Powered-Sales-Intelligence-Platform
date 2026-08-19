"""
Verifiable Provenance & Evidence Audit Trail Drawer Component.
"""

from typing import Any

import streamlit as st


def render_provenance_drawer(provenance_data: list[dict[str, Any]], audit_trail_text: str = ""):
    """
    Renders an expandable drawer displaying exact SQL executions, row counts,
    latencies, and ML confidence scores.
    """
    with st.expander("🔍 Inspect Verifiable Provenance & Evidence Audit Trail", expanded=False):
        if audit_trail_text:
            st.markdown(audit_trail_text)

        if provenance_data:
            st.markdown("#### 📑 Machine-Readable Execution Evidence")
            for idx, item in enumerate(provenance_data, 1):
                ev_type = item.get("evidence_type", "EVIDENCE")
                title = item.get("title", f"Step {idx}")
                source = item.get("source", "Unknown")
                latency = item.get("latency_ms")
                latency_str = f" • ⚡ {latency:.1f}ms" if latency else ""

                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; color: #38BDF8; font-size: 0.9rem;">
                            Step {idx}: [{ev_type}] {title} <span style="color: #94A3B8; font-size: 0.8rem;">({source}{latency_str})</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if item.get("details"):
                    st.json(item["details"])
