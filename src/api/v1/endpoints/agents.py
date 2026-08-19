"""
Agentic AI and LangGraph Multi-Agent Endpoints.
"""

from fastapi import APIRouter, Depends

from src.agents.supervisor import SalesIntelligenceSupervisor
from src.api.dependencies import get_current_user
from src.api.schemas.agent_schemas import AgentQueryRequest, AgentQueryResponse
from src.api.schemas.auth_schemas import UserRead
from src.security.prompt_guard import PromptSecurityError

router = APIRouter(prefix="/agents", tags=["Agentic AI & Natural Language Querying"])


@router.post(
    "/query",
    response_model=AgentQueryResponse,
    summary="Query the multi-agent system with natural language",
)
def query_agent(
    request: AgentQueryRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Executes the LangGraph Multi-Agent Supervisor:
    - Analyzes intent (Text-to-SQL, KPI calculation, ML inference, RCA diagnosis, or Hybrid)
    - Executes guarded workflows with schema and business RAG retrieval
    - Attaches verifiable Evidence & Provenance audit trail with exact SQL and row counts.
    """
    supervisor = SalesIntelligenceSupervisor(force_offline=request.force_offline)
    state = supervisor.run(request.query)

    if state.get("error_message"):
        raise PromptSecurityError(state["error_message"])

    return AgentQueryResponse(
        sanitized_query=state.get("sanitized_query", request.query),
        final_response=state.get("final_response", "No response generated."),
        audit_trail=state.get("audit_trail", ""),
        provenance_data=state.get("provenance_data", []),
        intent=state.get("intent"),
        is_self_healed=state.get("is_self_healed", False),
    )
