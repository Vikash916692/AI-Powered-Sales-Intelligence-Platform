"""
RAG and Vector Store configuration settings.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_PERSIST_DIR = BASE_DIR / "data" / "chroma_db"

# Collections
SCHEMA_COLLECTION_NAME = "schema_catalog"
BUSINESS_COLLECTION_NAME = "business_knowledge"

# Retrieval Settings
DEFAULT_TOP_K = 4
SIMILARITY_THRESHOLD = 0.65
