"""
Dual-Collection RAG Subsystem Test Suite.

Verifies:
1. Isolated Schema Catalog & Business Knowledge Collections
2. Schema Retrieval Accuracy for Text-to-SQL
3. Business Context & KPI Definition Retrieval
"""

from src.rag.vector_store import vector_store


def test_vector_store_collections_initialized():
    """Verify both ChromaDB collections are populated."""
    stats = vector_store.get_stats()
    assert stats["schema_catalog_count"] >= 10
    assert stats["business_knowledge_count"] >= 5


def test_schema_retrieval_for_sales():
    """Verify querying sales topics returns sales_mart schema."""
    results = vector_store.retrieve_schema("daily revenue and order counts", top_k=2)
    assert len(results) > 0
    table_names = [r["metadata"].get("table_name") for r in results]
    assert "sales_mart" in table_names


def test_schema_retrieval_for_rfm():
    """Verify querying customer segments returns rfm_mart schema."""
    results = vector_store.retrieve_schema("customer segmentation and monetary scores", top_k=2)
    assert len(results) > 0
    table_names = [r["metadata"].get("table_name") for r in results]
    assert "rfm_mart" in table_names or "customer_mart" in table_names


def test_business_context_retrieval_sla():
    """Verify querying delivery SLAs retrieves logistics SLA policy."""
    results = vector_store.retrieve_business_context("on-time delivery SLA target", top_k=2)
    assert len(results) > 0
    domains = [r["metadata"].get("domain") for r in results]
    assert any("logistics" in str(d) or "kpi" in str(d) for d in domains)
