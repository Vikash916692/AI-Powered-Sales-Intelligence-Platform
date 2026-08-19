"""
Dual-Collection RAG subsystem for technical schemas and business knowledge.
"""

from src.rag.business_knowledge import BUSINESS_DOCUMENTS
from src.rag.config import (
    BUSINESS_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    SCHEMA_COLLECTION_NAME,
)
from src.rag.schema_knowledge import SCHEMA_DOCUMENTS
from src.rag.vector_store import VectorStoreManager, vector_store

__all__ = [
    "BUSINESS_COLLECTION_NAME",
    "BUSINESS_DOCUMENTS",
    "CHROMA_PERSIST_DIR",
    "SCHEMA_COLLECTION_NAME",
    "SCHEMA_DOCUMENTS",
    "VectorStoreManager",
    "vector_store",
]
