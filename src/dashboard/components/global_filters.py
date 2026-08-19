"""
Global Sidebar Filters Component for cross-dashboard analytical slicing.
"""

from datetime import date

import streamlit as st


def render_global_sidebar_filters() -> dict[str, any]:
    """
    Renders global filters in the sidebar:
    - Date range slider (2016-09 to 2018-10)
    - State filter selector
    - Category filter selector
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Global Analytics Filters")

    # Date Range Slider
    min_date = date(2016, 9, 1)
    max_date = date(2018, 9, 3)

    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(date(2017, 1, 1), max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter historical sales orders by checkout date",
    )

    if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
        start_date = selected_date_range[0].isoformat()
        end_date = selected_date_range[1].isoformat()
    elif isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 1:
        start_date = selected_date_range[0].isoformat()
        end_date = max_date.isoformat()
    else:
        start_date = "2017-01-01"
        end_date = "2018-09-03"

    # State Dropdown
    states = ["All States", "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "PE"]
    selected_state = st.sidebar.selectbox("Customer Destination State", options=states, index=0)

    # Top Categories
    categories = [
        "All Categories",
        "bed_bath_table",
        "health_beauty",
        "sports_leisure",
        "computers_accessories",
        "furniture_decor",
        "housewares",
        "watches_gifts",
        "telephony",
        "auto",
        "toys",
    ]
    selected_category = st.sidebar.selectbox("Product Category", options=categories, index=0)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "state": None if selected_state == "All States" else selected_state,
        "category": None if selected_category == "All Categories" else selected_category,
    }
