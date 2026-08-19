"""
Agent State Schema for LangGraph multi-agent orchestration.
"""

from collections.abc import Sequence
from typing import Any

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Unified state passed across all LangGraph nodes in the workflow.
    """

    # Messages history
    messages: Sequence[BaseMessage]

    # User Input
    user_query: str
    sanitized_query: str

    # Intent Routing
    intent: str  # 'sql', 'kpi', 'ml', 'rca', 'rag', 'hybrid'
    sub_tasks: list[str]

    # RAG Context
    schema_context: list[dict[str, Any]]
    business_context: list[dict[str, Any]]

    # Tool & Agent Outputs
    generated_sql: str | None
    sql_result: dict[str, Any] | None
    kpi_result: dict[str, Any] | None
    ml_result: dict[str, Any] | None
    rca_result: dict[str, Any] | None
    rag_result: dict[str, Any] | None

    # Self-Healing & Error Tracking
    retries: int
    error_message: str | None
    is_self_healed: bool

    # Executive Output
    final_response: str
    audit_trail: str
    provenance_data: list[dict[str, Any]]

    # Internal reference
    _tracker: Any
