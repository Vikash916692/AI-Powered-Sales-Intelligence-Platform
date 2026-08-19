"""
Standardized UI States: Skeletons, Error Banners, and Empty States.
"""


import streamlit as st


def render_error_banner(message: str, error_details: str | None = None):
    """Renders a visually clear error alert with retry context."""
    st.error(f"⚠️ **{message}**")
    if error_details:
        with st.expander("🔍 View Technical Diagnostics"):
            st.code(error_details, language="text")


def render_empty_state(title: str = "No Records Found", description: str = "Try adjusting your date range or filters."):
    """Renders a clean empty-state placeholder."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2.5rem; background: rgba(15, 23, 42, 0.4); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 12px; margin: 1.5rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
            <h4 style="color: #F8FAFC; margin-bottom: 0.25rem; font-weight: 600;">{title}</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin: 0;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
