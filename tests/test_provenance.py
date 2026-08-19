"""
Evidence & Provenance Tracking Test Suite.

Verifies:
1. Granular event recording (SQL, ML, RAG, KPI, RCA)
2. Execution latency and confidence metrics
3. Markdown audit trail formatting
4. Serialization to JSON/Dict
"""

from src.provenance.tracker import ProvenanceTracker


def test_provenance_recording_all_types():
    """Verify recording each category of evidence in the audit trail."""
    tracker = ProvenanceTracker()

    # 1. Record SQL
    tracker.record_sql(
        query="SELECT * FROM sales_mart LIMIT 10",
        row_count=10,
        columns=["sales_date", "revenue"],
        sample_rows=[{"sales_date": "2018-01-01", "revenue": 500.0}],
        latency_ms=12.5,
    )

    # 2. Record ML
    tracker.record_ml(
        model_name="sales_forecaster",
        inputs={"horizon_days": 30},
        outputs={"total_projected_revenue": 50000.0},
        confidence=0.92,
        latency_ms=45.0,
    )

    # 3. Record RAG
    tracker.record_rag(
        collection_name="schema_catalog",
        query="daily sales revenue",
        retrieved_documents=[{"id": "schema_sales_mart"}],
        latency_ms=8.0,
    )

    # 4. Record KPI
    tracker.record_kpi(
        kpi_name="Gross Revenue",
        formula="SUM(revenue)",
        value="$1,200,000",
        benchmark="Target: $1M",
    )

    # 5. Record RCA
    tracker.record_rca(
        anomaly_metric="August Revenue Drop",
        primary_driver="Interstate shipping bottleneck",
        variance_breakdown={"SP->RJ": 45.2},
        recommendation="Reroute couriers",
    )

    assert len(tracker.evidence) == 5

    # Test audit trail rendering
    audit_md = tracker.format_markdown_audit_trail()
    assert "Verifiable Evidence & Provenance Trail" in audit_md
    assert "SQL_QUERY" in audit_md
    assert "ML_INFERENCE" in audit_md
    assert "RAG_CHUNK" in audit_md
    assert "KPI_CALCULATION" in audit_md
    assert "RCA_DIAGNOSTIC" in audit_md

    # Test dictionary export
    dict_data = tracker.to_dict()
    assert len(dict_data) == 5
    assert dict_data[0]["evidence_type"] == "SQL_QUERY"
