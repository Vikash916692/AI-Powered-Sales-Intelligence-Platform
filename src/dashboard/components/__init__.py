"""
Components package for the interactive dashboard.
"""

from src.dashboard.components.auth_widget import init_session_auth, render_auth_sidebar
from src.dashboard.components.charts import (
    create_daily_revenue_area_chart,
    create_forecast_confidence_chart,
    create_pareto_category_chart,
    create_rfm_sunburst_chart,
)
from src.dashboard.components.global_filters import render_global_sidebar_filters
from src.dashboard.components.kpi_cards import render_metric_card
from src.dashboard.components.ml_explainer import render_delivery_risk_explanation
from src.dashboard.components.provenance_drawer import render_provenance_drawer
from src.dashboard.components.ui_states import render_empty_state, render_error_banner

__all__ = [
    "create_daily_revenue_area_chart",
    "create_forecast_confidence_chart",
    "create_pareto_category_chart",
    "create_rfm_sunburst_chart",
    "init_session_auth",
    "render_auth_sidebar",
    "render_delivery_risk_explanation",
    "render_empty_state",
    "render_error_banner",
    "render_global_sidebar_filters",
    "render_metric_card",
    "render_provenance_drawer",
]
