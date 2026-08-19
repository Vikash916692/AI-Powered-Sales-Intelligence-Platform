"""
Evidence & Provenance Tracking Layer.

Collects granular audit trails for every analytical assertion made by the AI system,
including executed SQL queries, execution latency, row counts, ML model versions,
confidence metrics, and cited RAG knowledge chunks.
"""

import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class EvidenceItem:
    """A discrete verifiable evidence record."""

    evidence_type: str  # 'SQL_QUERY', 'ML_INFERENCE', 'RAG_CHUNK', 'KPI_CALCULATION', 'RCA_DIAGNOSTIC'
    title: str
    source: str
    details: dict[str, Any]
    latency_ms: float | None = None
    confidence_score: float | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class ProvenanceTracker:
    """Accumulates and formats verification evidence throughout the agent lifecycle."""

    def __init__(self):
        self.evidence: list[EvidenceItem] = []
        self._start_time = time.perf_counter()

    def record_sql(
        self,
        query: str,
        row_count: int,
        columns: list[str],
        sample_rows: list[dict[str, Any]],
        latency_ms: float,
        table_sources: list[str] | None = None,
    ) -> EvidenceItem:
        """Record an executed SQL query and its execution profile."""
        item = EvidenceItem(
            evidence_type="SQL_QUERY",
            title="Database Query Execution",
            source=f"MySQL Warehouse ({', '.join(table_sources or ['sales_intelligence'])})",
            details={
                "sql_query": query,
                "row_count": row_count,
                "columns": columns,
                "sample_rows": sample_rows[:5],
            },
            latency_ms=round(latency_ms, 2),
            confidence_score=1.0,
        )
        self.evidence.append(item)
        return item

    def record_ml(
        self,
        model_name: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        confidence: float | None = None,
        latency_ms: float | None = None,
    ) -> EvidenceItem:
        """Record a Machine Learning model inference."""
        item = EvidenceItem(
            evidence_type="ML_INFERENCE",
            title=f"Predictive Inference ({model_name})",
            source=f"ml.{model_name}",
            details={
                "inputs": inputs,
                "outputs": outputs,
            },
            latency_ms=round(latency_ms, 2) if latency_ms else None,
            confidence_score=confidence,
        )
        self.evidence.append(item)
        return item

    def record_rag(
        self,
        collection_name: str,
        query: str,
        retrieved_documents: list[dict[str, Any]],
        latency_ms: float | None = None,
    ) -> EvidenceItem:
        """Record chunks retrieved from ChromaDB vector storage."""
        item = EvidenceItem(
            evidence_type="RAG_CHUNK",
            title=f"Vector Retrieval ({collection_name})",
            source=f"ChromaDB::{collection_name}",
            details={
                "query": query,
                "retrieved_count": len(retrieved_documents),
                "chunks": retrieved_documents,
            },
            latency_ms=round(latency_ms, 2) if latency_ms else None,
            confidence_score=1.0,
        )
        self.evidence.append(item)
        return item

    def record_kpi(
        self,
        kpi_name: str,
        formula: str,
        value: Any,
        benchmark: str | None = None,
    ) -> EvidenceItem:
        """Record a validated KPI engine computation."""
        item = EvidenceItem(
            evidence_type="KPI_CALCULATION",
            title=f"KPI Calculation ({kpi_name})",
            source="KPI Intelligence Engine",
            details={
                "kpi_name": kpi_name,
                "formula": formula,
                "computed_value": value,
                "benchmark": benchmark,
            },
            confidence_score=1.0,
        )
        self.evidence.append(item)
        return item

    def record_rca(
        self,
        anomaly_metric: str,
        primary_driver: str,
        variance_breakdown: dict[str, Any],
        recommendation: str,
    ) -> EvidenceItem:
        """Record an autonomous root-cause diagnostic findings."""
        item = EvidenceItem(
            evidence_type="RCA_DIAGNOSTIC",
            title=f"Root-Cause Diagnostic ({anomaly_metric})",
            source="Autonomous RCA Agent",
            details={
                "anomaly_metric": anomaly_metric,
                "primary_driver": primary_driver,
                "variance_breakdown": variance_breakdown,
                "recommendation": recommendation,
            },
            confidence_score=0.92,
        )
        self.evidence.append(item)
        return item

    def format_markdown_audit_trail(self) -> str:
        """Render a readable executive audit trail in GitHub-flavored markdown."""
        if not self.evidence:
            return "_No execution evidence recorded._"

        lines = [
            "### 🔍 Verifiable Evidence & Provenance Trail",
            "",
            "| Step | Type | Source | Latency / Confidence | Details |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        for i, ev in enumerate(self.evidence, 1):
            lat_conf = []
            if ev.latency_ms is not None:
                lat_conf.append(f"`{ev.latency_ms}ms`")
            if ev.confidence_score is not None:
                lat_conf.append(f"`{int(ev.confidence_score * 100)}% conf`")
            lat_conf_str = " / ".join(lat_conf) if lat_conf else "-"

            # Summarize details
            if ev.evidence_type == "SQL_QUERY":
                summary = f"SQL: `{ev.details.get('sql_query', '')[:60]}...` ({ev.details.get('row_count', 0)} rows)"
            elif ev.evidence_type == "ML_INFERENCE":
                summary = f"Outputs: `{str(ev.details.get('outputs', {}))[:60]}...`"
            elif ev.evidence_type == "RAG_CHUNK":
                summary = f"Retrieved {ev.details.get('retrieved_count', 0)} semantic context chunks"
            elif ev.evidence_type == "KPI_CALCULATION":
                summary = f"{ev.details.get('kpi_name')}: **{ev.details.get('computed_value')}**"
            elif ev.evidence_type == "RCA_DIAGNOSTIC":
                summary = f"Driver: **{ev.details.get('primary_driver')}**"
            else:
                summary = str(ev.details)[:60]

            lines.append(
                f"| {i} | `{ev.evidence_type}` | {ev.source} | {lat_conf_str} | {summary} |"
            )

        lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> list[dict[str, Any]]:
        """Serialize all evidence to list of dictionaries."""
        return [asdict(item) for item in self.evidence]
