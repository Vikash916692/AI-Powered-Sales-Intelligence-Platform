"""
LangGraph Multi-Agent Supervisor & Hybrid Workflow Orchestrator.

Routes user business questions across specialized subgraphs and agents:
- Text-to-SQL Agent (Schema RAG + Self-Healing SQL)
- KPI Intelligence Engine (Deterministic validated formulas)
- Predictive ML Suite (Delay, Forecasting, Recs, Sentiment)
- Autonomous Root-Cause Analysis Agent (Dimensional Drilldown)
- Business Knowledge RAG (Domain rules & SLA policies)
- Executive Synthesizer & Provenance Audit Trail Formatter
"""

from typing import Any, Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from src.agents.kpi_engine import kpi_engine
from src.agents.llm_factory import get_llm
from src.agents.nl_sql_agent import nl_sql_agent
from src.agents.rca_agent import rca_agent
from src.agents.state import AgentState
from src.agents.tools.ml_tools import (
    tool_analyze_review_sentiment,
    tool_forecast_sales,
    tool_predict_delivery_delay,
    tool_recommend_products,
)
from src.provenance.tracker import ProvenanceTracker
from src.rag.vector_store import vector_store
from src.security.prompt_guard import PromptSecurityError, prompt_guard


class SalesIntelligenceSupervisor:
    """Multi-Agent Orchestrator powered by LangGraph."""

    def __init__(self, force_offline: bool = False, preferred_provider: str | None = None):
        self.force_offline = force_offline
        self.preferred_provider = preferred_provider
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Constructs the stateful multi-agent DAG."""
        builder = StateGraph(AgentState)

        # 1. Register Nodes
        builder.add_node("input_guard", self._input_guard_node)
        builder.add_node("router", self._router_node)
        builder.add_node("sql_agent", self._sql_node)
        builder.add_node("kpi_engine", self._kpi_node)
        builder.add_node("ml_agent", self._ml_node)
        builder.add_node("rca_agent", self._rca_node)
        builder.add_node("rag_agent", self._rag_node)
        builder.add_node("hybrid_workflow", self._hybrid_workflow_node)
        builder.add_node("synthesizer", self._synthesizer_node)

        # 2. Define Edges
        builder.set_entry_point("input_guard")

        builder.add_conditional_edges(
            "input_guard",
            self._check_guard_status,
            {
                "valid": "router",
                "blocked": "synthesizer",
            },
        )

        builder.add_conditional_edges(
            "router",
            self._route_intent,
            {
                "sql": "sql_agent",
                "kpi": "kpi_engine",
                "ml": "ml_agent",
                "rca": "rca_agent",
                "rag": "rag_agent",
                "hybrid": "hybrid_workflow",
            },
        )

        builder.add_edge("sql_agent", "synthesizer")
        builder.add_edge("kpi_engine", "synthesizer")
        builder.add_edge("ml_agent", "synthesizer")
        builder.add_edge("rca_agent", "synthesizer")
        builder.add_edge("rag_agent", "synthesizer")
        builder.add_edge("hybrid_workflow", "synthesizer")
        builder.add_edge("synthesizer", END)

        return builder.compile()

    # --- Node Implementations ---

    def _input_guard_node(self, state: AgentState) -> dict[str, Any]:
        """Validates query safety against prompt injection."""
        query = state.get("user_query", "")
        try:
            clean = prompt_guard.sanitize(query)
            return {"sanitized_query": clean, "error_message": None}
        except PromptSecurityError as e:
            return {
                "sanitized_query": query,
                "error_message": str(e),
                "final_response": f"⚠️ **Security Violation**: {e!s}",
            }

    def _check_guard_status(self, state: AgentState) -> Literal["valid", "blocked"]:
        if state.get("error_message"):
            return "blocked"
        return "valid"

    def _router_node(self, state: AgentState) -> dict[str, Any]:
        """Classifies intent into appropriate specialized sub-agent."""
        query = state.get("sanitized_query", "").lower()

        # Hybrid composite check
        if ("why" in query or "diagnose" in query) and ("forecast" in query or "recommend" in query or "sql" in query):
            return {"intent": "hybrid"}

        # Predictive ML intent
        if any(kw in query for kw in ["forecast", "predict", "sentiment", "cross-sell", "recommend product", "delay risk"]):
            return {"intent": "ml"}

        # Root Cause Analysis intent
        if any(kw in query for kw in ["why did", "root cause", "diagnose", "drop in revenue", "spike in delays", "anomaly"]):
            return {"intent": "rca"}

        # Standard KPI intent
        if any(kw in query for kw in ["overview", "executive kpi", "repeat rate", "sla compliance", "rfm breakdown", "customer ltv"]):
            return {"intent": "kpi"}

        # Business knowledge RAG intent
        if any(kw in query for kw in ["what is rfm", "sla policy", "definition of", "pareto rule", "business rule"]):
            return {"intent": "rag"}

        # Default to Text-to-SQL
        return {"intent": "sql"}

    def _route_intent(
        self, state: AgentState
    ) -> Literal["sql", "kpi", "ml", "rca", "rag", "hybrid"]:
        return state.get("intent", "sql")  # type: ignore

    def _sql_node(self, state: AgentState) -> dict[str, Any]:
        """Invokes Text-to-SQL Agent with self-healing."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "")
        res = nl_sql_agent.generate_and_execute(
            query,
            tracker=tracker,
            preferred_provider=self.preferred_provider,
        )
        return {
            "generated_sql": res.get("sql"),
            "sql_result": res,
            "is_self_healed": res.get("is_self_healed", False),
            "retries": res.get("retries", 0),
        }

    def _kpi_node(self, state: AgentState) -> dict[str, Any]:
        """Invokes deterministic KPI Intelligence Engine."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "").lower()

        if "logistics" in query or "sla" in query or "delivery" in query:
            kpis = kpi_engine.get_logistics_sla(tracker=tracker)
        elif "customer" in query or "repeat" in query or "ltv" in query:
            kpis = kpi_engine.get_customer_economics(tracker=tracker)
        elif "rfm" in query or "segment" in query:
            kpis = {"rfm_segments": kpi_engine.get_rfm_segmentation(tracker=tracker)}
        elif "top" in query and ("category" in query or "product" in query):
            kpis = {"top_categories": kpi_engine.get_top_categories(top_n=5, tracker=tracker)}
        else:
            kpis = kpi_engine.get_executive_overview(tracker=tracker)

        return {"kpi_result": kpis}

    def _ml_node(self, state: AgentState) -> dict[str, Any]:
        """Invokes Predictive ML Suite."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "").lower()

        if "forecast" in query:
            ml_res = tool_forecast_sales(horizon_days=30, tracker=tracker)
        elif "sentiment" in query:
            ml_res = tool_analyze_review_sentiment(review_text=state.get("sanitized_query", ""), tracker=tracker)
        elif "recommend" in query or "cross-sell" in query:
            ml_res = tool_recommend_products(top_n=5, tracker=tracker)
        else:
            ml_res = tool_predict_delivery_delay(tracker=tracker)

        return {"ml_result": ml_res}

    def _rca_node(self, state: AgentState) -> dict[str, Any]:
        """Invokes Autonomous Root Cause Analysis Agent."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "")
        res = rca_agent.diagnose_anomaly(
            query,
            tracker=tracker,
            preferred_provider=self.preferred_provider,
        )
        return {"rca_result": res}

    def _rag_node(self, state: AgentState) -> dict[str, Any]:
        """Invokes Business Knowledge RAG retriever."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "")
        docs = vector_store.retrieve_business_context(query, top_k=3)
        tracker.record_rag(
            collection_name="business_knowledge",
            query=query,
            retrieved_documents=docs,
        )
        return {"business_context": docs, "rag_result": {"retrieved_docs": docs}}

    def _hybrid_workflow_node(self, state: AgentState) -> dict[str, Any]:
        """Executes composite multi-agent pipeline."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "")

        # 1. Run RCA Diagnostic
        rca_res = rca_agent.diagnose_anomaly(query, tracker=tracker, preferred_provider=self.preferred_provider)
        # 2. Run Forward Forecast
        fc_res = tool_forecast_sales(horizon_days=30, tracker=tracker)
        # 3. Run Product Cross-Sell Recs
        rec_res = tool_recommend_products(top_n=3, tracker=tracker)

        return {
            "rca_result": rca_res,
            "ml_result": {"forecast": fc_res, "recommendations": rec_res},
        }

    def _synthesizer_node(self, state: AgentState) -> dict[str, Any]:
        """Assembles executive-ready briefing and provenance audit trail."""
        tracker = state.get("_tracker", ProvenanceTracker())
        query = state.get("sanitized_query", "")

        if state.get("error_message"):
            return {
                "final_response": state.get("final_response", ""),
                "audit_trail": tracker.format_markdown_audit_trail(),
                "provenance_data": tracker.to_dict(),
            }

        # Build prompt for LLM synthesizer
        evidence_summary = []
        if state.get("sql_result"):
            sr = state["sql_result"]
            evidence_summary.append(f"SQL Query: {sr.get('sql')}\nReturned {sr.get('row_count')} rows:\n{sr.get('data')[:5]}")
        if state.get("kpi_result"):
            evidence_summary.append(f"KPI Calculations: {state['kpi_result']}")
        if state.get("ml_result"):
            evidence_summary.append(f"ML Model Output: {state['ml_result']}")
        if state.get("rca_result"):
            evidence_summary.append(f"RCA Diagnostic Findings: {state['rca_result']}")
        if state.get("rag_result"):
            evidence_summary.append(f"Business Knowledge Documents: {state['rag_result']}")

        llm = get_llm(
            temperature=0.0,
            force_offline=self.force_offline,
            preferred_provider=self.preferred_provider,
        )

        synth_prompt = (
            f"### USER BUSINESS QUESTION:\n{query}\n\n"
            f"### VERIFIED DATA & ML EVIDENCE:\n"
            f"{' '.join(evidence_summary)}\n\n"
            "Synthesize this evidence into a clean, executive-ready sales intelligence report. "
            "Highlight key numbers, operational takeaways, and strategic recommendations."
        )

        messages = [
            SystemMessage(content="You are an Executive Sales Intelligence Assistant. Deliver crisp, numbers-backed answers."),
            HumanMessage(content=synth_prompt),
        ]

        response = llm.invoke(messages)
        content = str(response.content)

        audit_trail = tracker.format_markdown_audit_trail()

        full_output = f"{content}\n\n---\n\n{audit_trail}"

        return {
            "final_response": full_output,
            "audit_trail": audit_trail,
            "provenance_data": tracker.to_dict(),
        }

    def run(
        self, query: str, user_messages: list[BaseMessage] | None = None
    ) -> dict[str, Any]:
        """
        Public entry point to execute the multi-agent graph.

        Args:
            query: Business question or instruction.
            user_messages: Optional conversation history.

        Returns:
            Dict with final_response, audit_trail, intent, and provenance records.
        """
        tracker = ProvenanceTracker()
        initial_state: AgentState = {
            "user_query": query,
            "messages": user_messages or [HumanMessage(content=query)],
            "_tracker": tracker,  # Internal tracker reference
        }

        final_state = self.graph.invoke(initial_state)
        return final_state


# Global supervisor instance
supervisor = SalesIntelligenceSupervisor()
