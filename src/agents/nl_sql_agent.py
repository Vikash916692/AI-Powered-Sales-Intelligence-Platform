"""
Text-to-SQL Agent with Schema-Aware RAG and Self-Healing Error Recovery.

Translates natural language questions into secure MySQL queries,
validates syntax and permissions via SQLGuard, and autonomously fixes errors.
"""

import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.llm_factory import get_llm
from src.agents.tools.sql_tools import execute_analytical_sql
from src.provenance.tracker import ProvenanceTracker
from src.rag.vector_store import vector_store

SYSTEM_SQL_PROMPT = """
You are an expert Data Architect and MySQL Analytics Specialist for an E-Commerce Sales Intelligence Platform.
Your mission is to generate clean, accurate, and performant MySQL 8.4 SQL queries based on the user's inquiry and the provided warehouse schema context.

### CRITICAL RULES:
1. Generate ONLY ONE valid MySQL SELECT or WITH query. Do NOT generate DROP, DELETE, UPDATE, INSERT, ALTER, or administrative commands.
2. Rely strictly on the tables present in the warehouse schema provided below (primarily data marts like sales_mart, customer_mart, rfm_mart, product_mart, delivery_mart, review_mart, retention_mart, or facts/dims).
3. Do NOT make up column names. Use exact column names from the provided schema.
4. For revenue or financial sums, always use ROUND(SUM(column), 2).
5. Output ONLY the raw SQL query inside a markdown ```sql code block. No extraneous conversation.
"""


class NLSQLAgent:
    """Natural Language to SQL generator with autonomous self-healing capability."""

    def __init__(self, max_retries: int = 3, force_offline: bool = False):
        self.max_retries = max_retries
        self.force_offline = force_offline

    def generate_and_execute(
        self,
        query: str,
        tracker: ProvenanceTracker | None = None,
        preferred_provider: str | None = None,
    ) -> dict[str, Any]:
        """
        Translates query to SQL, validates security, executes, and self-heals if needed.

        Args:
            query: User natural language question.
            tracker: ProvenanceTracker instance.
            preferred_provider: Optional LLM provider override.

        Returns:
            Dict containing generated SQL, execution result, rows, and retry stats.
        """
        # 1. Retrieve relevant schema context from ChromaDB
        schema_chunks = vector_store.retrieve_schema(query, top_k=4)
        if tracker:
            tracker.record_rag(
                collection_name="schema_catalog",
                query=query,
                retrieved_documents=schema_chunks,
            )

        schema_text = "\n\n".join([f"--- {c['id']} ---\n{c['text']}" for c in schema_chunks])

        llm = get_llm(
            temperature=0.0,
            force_offline=self.force_offline,
            preferred_provider=preferred_provider,
        )

        current_prompt = (
            f"### WAREHOUSE SCHEMA CONTEXT:\n{schema_text}\n\n"
            f"### USER BUSINESS QUESTION:\n{query}\n\n"
            "Please generate the most accurate MySQL 8.4 query to answer this business question."
        )

        history_messages = [
            SystemMessage(content=SYSTEM_SQL_PROMPT),
            HumanMessage(content=current_prompt),
        ]

        attempt = 0
        last_error = None
        is_self_healed = False

        while attempt < self.max_retries:
            attempt += 1

            # Invoke LLM to generate SQL
            response = llm.invoke(history_messages)
            raw_sql = self._extract_sql(str(response.content))

            # Execute via guarded SQL tool
            exec_result = execute_analytical_sql(raw_sql, tracker=tracker)

            if exec_result["status"] == "success":
                return {
                    "status": "success",
                    "sql": exec_result["sql"],
                    "data": exec_result["data"],
                    "columns": exec_result["columns"],
                    "row_count": exec_result["row_count"],
                    "latency_ms": exec_result["latency_ms"],
                    "retries": attempt - 1,
                    "is_self_healed": is_self_healed,
                    "error": None,
                }

            # If failed, prepare self-healing prompt
            last_error = exec_result["error"]
            is_self_healed = True

            healing_prompt = (
                f"Your previously generated SQL query encountered an error:\n"
                f"SQL: ```sql\n{raw_sql}\n```\n"
                f"ERROR: {last_error}\n\n"
                f"Please analyze the error against the schema and output a corrected, valid MySQL SELECT query."
            )
            history_messages.append(HumanMessage(content=healing_prompt))

        # Max retries exhausted
        return {
            "status": "failed",
            "sql": raw_sql,
            "data": [],
            "columns": [],
            "row_count": 0,
            "latency_ms": 0.0,
            "retries": attempt,
            "is_self_healed": False,
            "error": f"Failed after {self.max_retries} attempts. Last error: {last_error}",
        }

    def _extract_sql(self, text: str) -> str:
        """Extract SQL query from markdown code blocks or raw text."""
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text.strip()


# Global singleton instance
nl_sql_agent = NLSQLAgent()
