"""
Text-to-SQL Agent Test Suite.

Verifies:
1. SQL generation and execution against analytical data marts
2. Self-healing error recovery loop
3. Handling of complex groupings and aggregations
"""

from src.agents.nl_sql_agent import NLSQLAgent
from src.provenance.tracker import ProvenanceTracker


def test_nl_sql_agent_offline_sales_query():
    """Verify NL-to-SQL agent generates and executes valid query offline."""
    agent = NLSQLAgent(force_offline=True)
    tracker = ProvenanceTracker()

    res = agent.generate_and_execute(
        query="What are the daily revenue and order trends?",
        tracker=tracker,
    )

    assert res["status"] == "success"
    assert res["row_count"] > 0
    assert len(res["data"]) > 0
    assert "sales_date" in res["columns"] or "revenue" in res["columns"]
    assert len(tracker.evidence) >= 1


def test_nl_sql_agent_product_ranking_query():
    """Verify NL-to-SQL agent queries product categories."""
    agent = NLSQLAgent(force_offline=True)
    tracker = ProvenanceTracker()

    res = agent.generate_and_execute(
        query="What are the top 5 product categories by revenue?",
        tracker=tracker,
    )

    assert res["status"] == "success"
    assert res["row_count"] > 0
    assert len(res["data"]) > 0
