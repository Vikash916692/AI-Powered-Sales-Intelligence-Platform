"""
Database connection pool and query executor for Phase 3 ML.
Reuses the central SQLAlchemy engine from src.ingestion.database with URL.create fallback.
"""

import logging
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

logger = logging.getLogger("ml.common.db")

_ENGINE: Engine | None = None


def get_engine() -> Engine:
    """
    Get or initialize a thread-safe SQLAlchemy engine connected to sales_intelligence.
    """
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    try:
        from src.ingestion.database import get_engine as get_src_engine

        _ENGINE = get_src_engine()
        logger.info("Successfully connected using central src.ingestion.database engine.")
        return _ENGINE
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Could not load central engine ({e}). Falling back to .env URL.create.")

    load_dotenv(BASE_DIR / ".env")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    db = os.getenv("MYSQL_DATABASE", "sales_intelligence")

    db_url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=db,
    )
    _ENGINE = create_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)
    logger.info(f"Initialized standalone SQLAlchemy engine for {db} on {host}:{port}.")
    return _ENGINE


def execute_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """
    Execute a SQL query against sales_intelligence and return the result as a Pandas DataFrame.
    """
    engine = get_engine()
    with engine.connect() as connection:
        df = pd.read_sql(text(sql), connection, params=params)
    return df
