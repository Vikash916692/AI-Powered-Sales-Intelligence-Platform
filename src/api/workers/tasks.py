"""
Celery Background Tasks for long-running analytical and ML workloads.
"""

import logging
from typing import Any

from src.agents.kpi_engine import kpi_engine
from src.agents.rca_agent import rca_agent
from src.agents.tools.ml_tools import tool_forecast_sales
from src.api.workers.celery_app import celery_app, update_task
from src.provenance.tracker import ProvenanceTracker

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.async_run_rca", bind=True)
def async_run_rca(self, inquiry: str, task_id: str | None = None) -> dict[str, Any]:
    """Execute asynchronous Root Cause Analysis diagnostic in background."""
    tid = task_id or (self.request.id if hasattr(self, "request") else "task_direct")
    update_task(tid, "STARTED")
    try:
        tracker = ProvenanceTracker()
        result = rca_agent.diagnose_anomaly(query=inquiry, tracker=tracker)
        output = {
            "inquiry": inquiry,
            "result": result,
            "provenance": tracker.to_dict(),
        }
        update_task(tid, "SUCCESS", result=output)
        return output
    except Exception as e:
        logger.error("Async RCA failed: %s", e)
        update_task(tid, "FAILURE", error=str(e))
        raise


@celery_app.task(name="tasks.async_retrain_forecast", bind=True)
def async_retrain_forecast(self, horizon_days: int = 30, task_id: str | None = None) -> dict[str, Any]:
    """Execute batch multi-horizon forecast computation in background."""
    tid = task_id or (self.request.id if hasattr(self, "request") else "task_direct")
    update_task(tid, "STARTED")
    try:
        tracker = ProvenanceTracker()
        result = tool_forecast_sales(horizon_days=horizon_days, tracker=tracker)
        output = {
            "horizon_days": horizon_days,
            "forecast": result,
            "provenance": tracker.to_dict(),
        }
        update_task(tid, "SUCCESS", result=output)
        return output
    except Exception as e:
        logger.error("Async Forecast failed: %s", e)
        update_task(tid, "FAILURE", error=str(e))
        raise


@celery_app.task(name="tasks.async_export_kpi_summary", bind=True)
def async_export_kpi_summary(self, task_id: str | None = None) -> dict[str, Any]:
    """Compile comprehensive executive report snapshot."""
    tid = task_id or (self.request.id if hasattr(self, "request") else "task_direct")
    update_task(tid, "STARTED")
    try:
        overview = kpi_engine.get_executive_overview()
        customer = kpi_engine.get_customer_economics()
        logistics = kpi_engine.get_logistics_sla()
        rfm = kpi_engine.get_rfm_segmentation()
        categories = kpi_engine.get_top_categories(5)

        summary = {
            "overview": overview,
            "customer_economics": customer,
            "logistics_sla": logistics,
            "rfm_segments": rfm,
            "top_categories": categories,
        }
        update_task(tid, "SUCCESS", result=summary)
        return summary
    except Exception as e:
        logger.error("Async KPI Export failed: %s", e)
        update_task(tid, "FAILURE", error=str(e))
        raise
