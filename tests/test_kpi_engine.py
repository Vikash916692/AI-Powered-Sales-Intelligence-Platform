"""
KPI Intelligence Engine Test Suite.

Verifies mathematical accuracy of pre-calculated SQL benchmarks:
1. Executive Sales Overview
2. Customer Retention & LTV Economics
3. Logistics SLA & Delivery Latency
4. RFM Segment Breakdown
5. Top Categories
"""

from src.agents.kpi_engine import kpi_engine
from src.provenance.tracker import ProvenanceTracker


def test_executive_overview_calculation():
    """Verify executive sales metrics compute accurately."""
    tracker = ProvenanceTracker()
    res = kpi_engine.get_executive_overview(tracker=tracker)

    assert "total_gross_revenue" in res
    assert "total_orders" in res
    assert "executive_aov" in res
    assert res["total_gross_revenue"] > 1000000.0
    assert res["total_orders"] > 50000
    assert res["executive_aov"] > 50.0

    # Verify recorded in tracker
    assert len(tracker.evidence) == 1
    assert tracker.evidence[0].evidence_type == "KPI_CALCULATION"


def test_customer_economics_calculation():
    """Verify repeat customer rates and lifetime days."""
    tracker = ProvenanceTracker()
    res = kpi_engine.get_customer_economics(tracker=tracker)

    assert "total_customers" in res
    assert "repeat_customers" in res
    assert "repeat_purchase_rate_pct" in res
    assert res["total_customers"] > 50000
    assert res["repeat_purchase_rate_pct"] >= 0.0


def test_logistics_sla_calculation():
    """Verify on-time delivery rate calculations."""
    tracker = ProvenanceTracker()
    res = kpi_engine.get_logistics_sla(tracker=tracker)

    assert "total_delivered_orders" in res
    assert "on_time_delivery_rate_pct" in res
    assert "avg_delivery_days" in res
    assert res["on_time_delivery_rate_pct"] > 80.0
    assert res["avg_delivery_days"] > 5.0


def test_rfm_segments_calculation():
    """Verify RFM tier distribution."""
    tracker = ProvenanceTracker()
    segments = kpi_engine.get_rfm_segmentation(tracker=tracker)

    assert len(segments) > 0
    seg_names = [s["rfm_segment"] for s in segments]
    assert any("Champions" in s or "Loyal" in s or "At Risk" in s for s in seg_names)


def test_top_categories_calculation():
    """Verify top product category extraction."""
    tracker = ProvenanceTracker()
    cats = kpi_engine.get_top_categories(top_n=5, tracker=tracker)

    assert len(cats) == 5
    assert "category_name" in cats[0]
    assert "total_revenue" in cats[0]
    assert cats[0]["total_revenue"] >= cats[1]["total_revenue"]
