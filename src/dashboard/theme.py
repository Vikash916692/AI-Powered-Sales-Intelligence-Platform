"""
Design System, Glassmorphism Styling, and Custom CSS Tokens for Streamlit.
"""

import streamlit as st


def apply_custom_theme():
    """Injects high-end dark mode design tokens, glassmorphism card surfaces, and glowing accents."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, .stTitle, .stHeader {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 95% !important;
    }

    /* Glassmorphism Metric Card */
    .metric-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 240, 255, 0.4);
    }

    .metric-label {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        color: #F8FAFC;
        font-size: 1.85rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }

    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.35rem;
    }

    .delta-positive { color: #10B981; }
    .delta-neutral { color: #38BDF8; }
    .delta-warning { color: #F59E0B; }

    /* Custom Badges */
    .badge-primary {
        background: rgba(2, 132, 199, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(2, 132, 199, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Provenance Audit Box */
    .provenance-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }

    /* Modern Table Headers */
    thead th {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
