"""
Agent Query and Provenance Audit Response Schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    """Natural language query request for the multi-agent system."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language question, analytical request, or diagnostic inquiry",
    )
    force_offline: bool = Field(
        default=False,
        description="Set to true to use the deterministic offline mock engine instead of live LLM API",
    )


class EvidenceItemSchema(BaseModel):
    """Single evidence record in the provenance audit trail."""

    evidence_type: str
    title: str
    source: str
    details: dict[str, Any]
    latency_ms: float | None = None
    confidence_score: float | None = None
    timestamp: str | None = None


class AgentQueryResponse(BaseModel):
    """Structured response from LangGraph multi-agent supervisor with provenance audit trail."""

    sanitized_query: str
    final_response: str
    audit_trail: str
    provenance_data: list[dict[str, Any]]
    intent: str | None = None
    is_self_healed: bool | None = False
