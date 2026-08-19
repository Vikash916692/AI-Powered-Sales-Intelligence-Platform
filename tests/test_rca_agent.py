"""
Autonomous RCA Agent Test Suite.

Verifies:
1. Multi-dimensional variance analysis
2. Identification of logistics and product bottlenecks
3. Diagnostic synthesis and remediation recommendation
"""

from src.agents.rca_agent import RCAgent
from src.provenance.tracker import ProvenanceTracker


def test_rca_agent_diagnose_logistics_anomaly():
    """Verify RCA agent diagnoses delivery delay hotspots."""
    agent = RCAgent(force_offline=True)
    tracker = ProvenanceTracker()

    res = agent.diagnose_anomaly(
        query="Why are customer delivery delays spiking in Southeast routes?",
        tracker=tracker,
    )

    assert res["status"] == "success"
    assert "primary_driver" in res
    assert "diagnostic_report" in res
    assert len(res["evidence"]["category_variance"]) > 0
    assert len(res["evidence"]["logistics_bottlenecks"]) > 0
    assert len(tracker.evidence) >= 1
