"""
Dual-Collection Vector Store Manager powered by ChromaDB.

Manages isolated collections for:
1. `schema_catalog` (Technical DDL, column data types, table grains, join paths)
2. `business_knowledge` (KPI formulas, SLAs, RFM rules, domain guidelines)

Includes deterministic local embeddings and hybrid semantic search.
"""

from typing import Any

import chromadb
from chromadb.config import Settings

from src.rag.business_knowledge import BUSINESS_DOCUMENTS
from src.rag.config import (
    BUSINESS_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    DEFAULT_TOP_K,
    SCHEMA_COLLECTION_NAME,
)
from src.rag.schema_knowledge import SCHEMA_DOCUMENTS


class VectorStoreManager:
    """Manages ChromaDB collections and retrieval pipelines."""

    def __init__(self, persist_directory: str | None = None):
        self.persist_dir = str(persist_directory or CHROMA_PERSIST_DIR)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create isolated collections
        self.schema_collection = self.client.get_or_create_collection(
            name=SCHEMA_COLLECTION_NAME,
            metadata={"description": "Data warehouse table schemas, grains, and join paths"},
        )
        self.business_collection = self.client.get_or_create_collection(
            name=BUSINESS_COLLECTION_NAME,
            metadata={"description": "Business KPI formulas, SLAs, and domain definitions"},
        )

        # Populate or sync collections
        self._initialize_collections()

    def _initialize_collections(self) -> None:
        """Seed the ChromaDB collections with curated knowledge docs."""
        # 1. Populate Schema Catalog
        ids = [doc["id"] for doc in SCHEMA_DOCUMENTS]
        documents = [doc["text"] for doc in SCHEMA_DOCUMENTS]
        metadatas = [
            {"table_name": doc["table_name"], "category": doc["category"]}
            for doc in SCHEMA_DOCUMENTS
        ]
        self.schema_collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        # 2. Populate Business Knowledge
        biz_ids = [doc["id"] for doc in BUSINESS_DOCUMENTS]
        biz_documents = [doc["text"] for doc in BUSINESS_DOCUMENTS]
        biz_metadatas = [
            {"domain": doc["domain"], "category": doc["category"]}
            for doc in BUSINESS_DOCUMENTS
        ]
        self.business_collection.upsert(
            ids=biz_ids,
            documents=biz_documents,
            metadatas=biz_metadatas,
        )

    def retrieve_schema(
        self, query: str, top_k: int = DEFAULT_TOP_K, table_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant database schema and table definitions for Text-to-SQL.

        Args:
            query: Natural language query or table topic.
            top_k: Number of schema chunks to retrieve.
            table_filter: Optional exact table name to filter on.

        Returns:
            List of matched schema chunks with metadata and relevance scores.
        """
        where_clause = {"table_name": table_filter} if table_filter else None
        
        results = self.schema_collection.query(
            query_texts=[query],
            n_results=min(top_k, self.schema_collection.count() or 1),
            where=where_clause,
        )

        output = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
            ids = results["ids"][0] if results["ids"] else [""] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                output.append(
                    {
                        "id": doc_id,
                        "text": doc,
                        "metadata": meta,
                        "distance": dist,
                    }
                )
        return output

    def retrieve_business_context(
        self, query: str, top_k: int = DEFAULT_TOP_K, domain_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant business rules, KPI formulas, or operational guidelines.

        Args:
            query: Business question or metric concept.
            top_k: Number of knowledge chunks to return.
            domain_filter: Optional filter on domain metadata.

        Returns:
            List of matched business knowledge chunks.
        """
        where_clause = {"domain": domain_filter} if domain_filter else None

        results = self.business_collection.query(
            query_texts=[query],
            n_results=min(top_k, self.business_collection.count() or 1),
            where=where_clause,
        )

        output = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
            ids = results["ids"][0] if results["ids"] else [""] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                output.append(
                    {
                        "id": doc_id,
                        "text": doc,
                        "metadata": meta,
                        "distance": dist,
                    }
                )
        return output

    def get_stats(self) -> dict[str, int]:
        """Return document counts for each collection."""
        return {
            "schema_catalog_count": self.schema_collection.count(),
            "business_knowledge_count": self.business_collection.count(),
        }


# Global singleton instance
vector_store = VectorStoreManager()
