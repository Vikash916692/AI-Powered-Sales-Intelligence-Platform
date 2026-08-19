"""
Machine Learning Explanations and Logistics Risk Decomposition Component.
"""

import streamlit as st


def render_delivery_risk_explanation(
    delay_prob: float,
    is_interstate: bool,
    weight_g: float,
    freight_val: float,
    sla_days: float,
):
    """
    Decomposes why an order was scored with a specific delay risk probability.
    """
    risk_level = "High" if delay_prob >= 0.50 else ("Moderate" if delay_prob >= 0.25 else "Low")
    risk_color = "#F43F5E" if risk_level == "High" else ("#F59E0B" if risk_level == "Moderate" else "#10B981")

    st.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.85); border-left: 4px solid {risk_color}; border-radius: 8px; padding: 1rem 1.25rem; margin-top: 1rem;">
            <div style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem; margin-bottom: 0.5rem;">
                🧠 ML Risk Factor Decomposition ({risk_level} Risk — {delay_prob*100:.1f}%)
            </div>
            <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.5;">
                Key contributing factors driving this prediction:
                <ul style="margin-top: 0.4rem; padding-left: 1.2rem; color: #94A3B8;">
                    <li><b>Route Transit:</b> {"Interstate shipping adds +12-18% baseline risk variance." if is_interstate else "Intra-state routing (low geographic friction)."}</li>
                    <li><b>Package Weight ({weight_g:,.0f}g):</b> {"Heavy cargo (>1.5kg) requires freight hub staging." if weight_g > 1500 else "Standard parcel dimensions."}</li>
                    <li><b>Committed SLA Window ({sla_days:.0f} days):</b> {"Compressed delivery timeline increases SLA breach sensitivity." if sla_days < 12 else "Standard SLA buffer."}</li>
                    <li><b>Freight Ratio (${freight_val:.2f}):</b> Freight-to-value ratio is consistent with carrier SLAs.</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
