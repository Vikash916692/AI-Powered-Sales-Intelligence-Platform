"""
Multi-Provider LLM Factory and Deterministic Mock Engine.

Supports:
1. Groq (ChatGroq with llama-3.3-70b-versatile / llama-3.1-8b-instant)
2. OpenAI (ChatOpenAI with gpt-4o / gpt-4o-mini)
3. Deterministic Mock LLM (for offline testing, CI/CD, and zero-cost local verification)
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult

load_dotenv()


class MockDeterministicChatModel(BaseChatModel):
    """
    Deterministic Mock ChatModel implementing LangChain BaseChatModel interface.
    Generates syntactically correct SQL, diagnostic RCA responses, and executive summaries
    without external API calls or latency.
    """

    model_name: str = "mock-deterministic-v1"

    @property
    def _llm_type(self) -> str:
        return "mock_deterministic_chat"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Extract user prompt content
        user_content = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage) or m.type == "human":
                user_content = str(m.content)
                break
            elif isinstance(m, SystemMessage) or m.type == "system":
                if not user_content:
                    user_content = str(m.content)

        response_text = self._route_mock_response(user_content, messages)
        message = AIMessage(content=response_text)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _route_mock_response(
        self, prompt: str, all_messages: list[BaseMessage]
    ) -> str:
        lower = prompt.lower()
        full_text = " ".join(str(m.content) for m in all_messages).lower()

        # 1. Self-Correction handling (if SQL error feedback is present in prompt)
        if "sql error" in full_text or "operationalerror" in full_text or "retry" in full_text:
            return (
                "```sql\n"
                "SELECT sales_date, revenue, total_orders \n"
                "FROM sales_mart \n"
                "ORDER BY sales_date DESC \n"
                "LIMIT 10;\n"
                "```"
            )

        # 2. Text-to-SQL generation patterns
        if "generate sql" in full_text or "sql query" in full_text or "write a query" in full_text or "daily" in lower or "trends" in lower:
            if ("daily" in lower or "trend" in lower or "revenue" in lower) and not ("category" in lower or "product" in lower or "delivery" in lower or "rfm" in lower):
                return (
                    "```sql\n"
                    "SELECT sales_date, revenue, total_orders, average_order_value \n"
                    "FROM sales_mart \n"
                    "ORDER BY sales_date DESC \n"
                    "LIMIT 10;\n"
                    "```"
                )
            elif "top" in lower and ("product" in lower or "category" in lower):
                return (
                    "```sql\n"
                    "SELECT dp.category_name_english, \n"
                    "       SUM(pm.items_sold) AS total_units, \n"
                    "       ROUND(SUM(pm.total_revenue), 2) AS total_revenue \n"
                    "FROM product_mart pm \n"
                    "JOIN dim_product dp ON pm.product_key = dp.product_key \n"
                    "GROUP BY dp.category_name_english \n"
                    "ORDER BY total_revenue DESC \n"
                    "LIMIT 5;\n"
                    "```"
                )
            elif "delivery" in lower or "delay" in lower or "sla" in lower:
                return (
                    "```sql\n"
                    "SELECT order_status, \n"
                    "       total_orders, \n"
                    "       delivered_orders, \n"
                    "       average_delivery_days \n"
                    "FROM delivery_mart;\n"
                    "```"
                )
            elif "rfm" in lower or "champion" in lower:
                return (
                    "```sql\n"
                    "SELECT rfm_segment, \n"
                    "       COUNT(*) AS customer_count, \n"
                    "       ROUND(AVG(monetary_value), 2) AS avg_monetary \n"
                    "FROM rfm_mart \n"
                    "GROUP BY rfm_segment \n"
                    "ORDER BY avg_monetary DESC \n"
                    "LIMIT 10;\n"
                    "```"
                )
            else:
                return (
                    "```sql\n"
                    "SELECT sales_date, revenue, total_orders, average_order_value \n"
                    "FROM sales_mart \n"
                    "ORDER BY sales_date DESC \n"
                    "LIMIT 10;\n"
                    "```"
                )

        # 3. Root Cause Analysis (RCA) requests
        if "root cause" in lower or "diagnose" in lower or "why did" in lower or "drop in" in lower:
            return (
                "### 🔍 Root-Cause Diagnostic Analysis\n\n"
                "**1. Anomaly Overview:**\n"
                "- Detected variance in target performance metrics.\n\n"
                "**2. Primary Contributing Drivers:**\n"
                "- **Logistics SLA Drift:** 62% of metric drag attributed to interstate shipping bottlenecks in Southeast routes.\n"
                "- **Category Concentration:** Catalog sales in 'bed_bath_table' experienced seasonal contraction (-14.2%).\n\n"
                "**3. Recommended Remediation:**\n"
                "- Shift high-volume merchant inventory to regional fulfillment hubs.\n"
                "- Launch targeted cross-sell promotion to revitalize category volume."
            )

        # 4. General Executive Synthesis
        return (
            "### 📊 Executive Sales Intelligence Briefing\n\n"
            "Based on verified data warehouse records and predictive analytics:\n"
            "- **Revenue Performance:** Stable gross sales velocity with robust average order values.\n"
            "- **Customer Engagement:** High contribution from top RFM tiers (Champions & Loyalists).\n"
            "- **Actionable Insight:** Maintain proactive delivery tracking to sustain customer CSAT ratings."
        )


class LLMFactory:
    """Creates appropriate LLM client based on configuration and availability."""

    @staticmethod
    def get_chat_model(
        temperature: float = 0.0,
        force_offline: bool = False,
        preferred_provider: str | None = None,
    ) -> BaseChatModel:
        """
        Returns configured ChatModel:
        1. MockDeterministicChatModel if force_offline or no API keys
        2. ChatGroq if GROQ_API_KEY is available (or requested)
        3. ChatOpenAI if OPENAI_API_KEY is available
        """
        if force_offline or os.getenv("TEST_OFFLINE_MODE", "0") == "1":
            return MockDeterministicChatModel()

        groq_api_key = os.getenv("GROQ_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        # Preferred provider checks
        if preferred_provider == "groq" and groq_api_key:
            try:
                from langchain_groq import ChatGroq

                return ChatGroq(
                    model_name=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                    temperature=temperature,
                    groq_api_key=groq_api_key,
                )
            except Exception as e:  # noqa: BLE001
                logger.debug("Failed to initialize requested Groq provider: %s", e)

        if groq_api_key:
            try:
                from langchain_groq import ChatGroq

                return ChatGroq(
                    model_name=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                    temperature=temperature,
                    groq_api_key=groq_api_key,
                )
            except Exception as e:  # noqa: BLE001
                logger.debug("Failed to initialize Groq provider: %s", e)

        if openai_api_key:
            try:
                from langchain_openai import ChatOpenAI

                return ChatOpenAI(
                    model_name=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    temperature=temperature,
                    openai_api_key=openai_api_key,
                )
            except Exception as e:  # noqa: BLE001
                logger.debug("Failed to initialize OpenAI provider: %s", e)

        # Fallback to deterministic mock
        return MockDeterministicChatModel()


# Global factory helper
get_llm = LLMFactory.get_chat_model
