"""
Autonomous Root-Cause Analysis (RCA) Agent.

Performs multi-dimensional drilldown and statistical variance decomposition
across time, product categories, merchant hubs, and logistics routes to diagnose
business metric anomalies and operational bottlenecks.
"""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.llm_factory import get_llm
from src.agents.tools.rca_tools import (
    drilldown_category_variance,
    drilldown_logistics_variance,
)
from src.provenance.tracker import ProvenanceTracker

RCA_SYSTEM_PROMPT = """
You are a Principal E-Commerce Business Intelligence & Operations Diagnostic Lead.
Your mission is to perform rigorous, data-driven Root-Cause Analysis (RCA) on business anomalies.

Synthesize the dimensional variance breakdown provided and output an executive diagnostic brief containing:
1. **Executive Anomaly Summary**: Clear statement of the primary metric deviation.
2. **Key Contributing Drivers**: The top 2-3 specific dimensions causing the deviation (with quantified figures).
3. **Actionable Remediation Roadmap**: Concrete, prioritized operational interventions.
"""


class RCAgent:
    """Autonomous Root Cause Analysis and Diagnostic Engine."""

    def __init__(self, force_offline: bool = False):
        self.force_offline = force_offline

    def diagnose_anomaly(
        self,
        query: str,
        tracker: ProvenanceTracker | None = None,
        preferred_provider: str | None = None,
    ) -> dict[str, Any]:
        """
        Executes multi-dimensional variance analysis and synthesizes root cause findings.

        Args:
            query: User's anomaly inquiry (e.g. "Why did revenue drop in August?").
            tracker: ProvenanceTracker instance.
            preferred_provider: Optional LLM provider.

        Returns:
            Dict containing diagnostic breakdown, primary driver, and executive brief.
        """
        # 1. Gather dimensional variance evidence
        category_data = drilldown_category_variance(tracker=tracker)
        logistics_data = drilldown_logistics_variance(tracker=tracker)

        evidence_payload = {
            "category_variance": category_data.get("top_categories", [])[:5],
            "logistics_bottlenecks": logistics_data.get("logistics_bottlenecks", [])[:5],
        }

        # 2. Determine primary driver
        worst_route = (
            logistics_data.get("logistics_bottlenecks", [{}])[0]
            if logistics_data.get("logistics_bottlenecks")
            else {}
        )
        primary_driver = (
            f"Logistics bottleneck along {worst_route.get('interstate_route', 'interstate')} "
            f"with {worst_route.get('delay_rate_pct', 0)}% delay rate"
            if worst_route
            else "Category demand contraction"
        )

        # 3. LLM Diagnostic Synthesis
        llm = get_llm(
            temperature=0.0,
            force_offline=self.force_offline,
            preferred_provider=preferred_provider,
        )

        prompt = (
            f"### BUSINESS ANOMALY INQUIRY:\n{query}\n\n"
            f"### DIMENSIONAL DRILLDOWN EVIDENCE:\n"
            f"- Top Product Categories & Freight: {evidence_payload['category_variance']}\n"
            f"- Interstate Logistics Hotspots: {evidence_payload['logistics_bottlenecks']}\n\n"
            "Please deliver a rigorous, numbers-backed Root-Cause Diagnostic Report."
        )

        messages = [
            SystemMessage(content=RCA_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = llm.invoke(messages)
        brief = str(response.content)

        output = {
            "status": "success",
            "anomaly_inquiry": query,
            "primary_driver": primary_driver,
            "evidence": evidence_payload,
            "diagnostic_report": brief,
        }

        if tracker:
            tracker.record_rca(
                anomaly_metric=query,
                primary_driver=primary_driver,
                variance_breakdown=evidence_payload,
                recommendation="Reallocate inventory & dispatch priority couriers",
            )

        return output


# Global singleton instance
rca_agent = RCAgent()
