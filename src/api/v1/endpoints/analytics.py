"""
Analytical Data Mart Endpoints for granular sales, customer, and product slices.
"""

import json
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, Query

from ml.common.db import execute_query
from src.api.dependencies import get_current_user
from src.api.schemas.analytics_schemas import PaginatedResponse
from src.api.schemas.auth_schemas import UserRead
from src.security.sql_guard import sql_guard

router = APIRouter(prefix="/analytics", tags=["Analytical Data Marts"])


def _clean_df_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Clean DataFrame NaN and Infinite values to JSON-compliant None using pandas to_json."""
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records"))


@router.get("/sales", summary="Query sales mart daily trends")
def get_sales_mart(
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=500),
    current_user: UserRead = Depends(get_current_user),
):
    """Returns daily order volume, revenue, freight, and AOV trends."""
    conditions = []
    if start_date:
        conditions.append(f"sales_date >= '{start_date}'")
    if end_date:
        conditions.append(f"sales_date <= '{end_date}'")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    offset = (page - 1) * page_size

    count_df = execute_query(f"SELECT COUNT(*) AS total FROM sales_mart {where};")
    total_records = int(count_df.iloc[0]["total"]) if not count_df.empty else 0

    query = f"SELECT * FROM sales_mart {where} ORDER BY sales_date DESC LIMIT {page_size} OFFSET {offset};"
    df = execute_query(sql_guard.validate_and_sanitize(query))
    data = _clean_df_records(df)

    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 0

    return PaginatedResponse(
        total_records=total_records,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        data=data,
    )


@router.get("/delivery", summary="Query delivery mart SLA performance")
def get_delivery_mart(
    current_user: UserRead = Depends(get_current_user),
):
    """Returns delivery fulfillment status and latency distribution."""
    df = execute_query("SELECT * FROM delivery_mart;")
    return {"data": _clean_df_records(df)}


@router.get("/products", summary="Query product performance mart")
def get_product_mart(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=500),
    current_user: UserRead = Depends(get_current_user),
):
    """Returns product catalog units sold, revenue, and pricing metrics."""
    offset = (page - 1) * page_size
    count_df = execute_query("SELECT COUNT(*) AS total FROM product_mart;")
    total_records = int(count_df.iloc[0]["total"]) if not count_df.empty else 0

    query = f"""
    SELECT pm.*, dp.category_name_english
    FROM product_mart pm
    LEFT JOIN dim_product dp ON pm.product_key = dp.product_key
    ORDER BY pm.total_revenue DESC
    LIMIT {page_size} OFFSET {offset};
    """
    df = execute_query(sql_guard.validate_and_sanitize(query))
    data = _clean_df_records(df)

    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 0

    return PaginatedResponse(
        total_records=total_records,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        data=data,
    )


@router.get("/sellers", summary="Query merchant performance mart")
def get_seller_mart(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=500),
    current_user: UserRead = Depends(get_current_user),
):
    """Returns merchant volume, orders fulfilled, and revenue ranking."""
    offset = (page - 1) * page_size
    count_df = execute_query("SELECT COUNT(*) AS total FROM seller_mart;")
    total_records = int(count_df.iloc[0]["total"]) if not count_df.empty else 0

    query = f"SELECT * FROM seller_mart ORDER BY total_revenue DESC LIMIT {page_size} OFFSET {offset};"
    df = execute_query(sql_guard.validate_and_sanitize(query))
    data = _clean_df_records(df)

    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 0

    return PaginatedResponse(
        total_records=total_records,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        data=data,
    )


@router.get("/reviews", summary="Query customer review ratings distribution")
def get_review_mart(
    current_user: UserRead = Depends(get_current_user),
):
    """Returns review score counts, percentages, and sentiment categories."""
    df = execute_query("SELECT * FROM review_mart ORDER BY review_score ASC;")
    return {"data": _clean_df_records(df)}
