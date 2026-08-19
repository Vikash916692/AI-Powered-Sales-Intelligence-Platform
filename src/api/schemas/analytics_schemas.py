"""
Analytics & Data Mart Pagination and Filtering Schemas.
"""

from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=25, ge=1, le=500, description="Records per page (max 500)")


class PaginatedResponse[T](BaseModel):
    """Standardized paginated data response."""

    total_records: int
    page: int
    page_size: int
    total_pages: int
    data: list[T]


class MartQueryFilter(BaseModel):
    """Generic query filter for analytical data marts."""

    start_date: str | None = Field(None, description="Start date filter (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="End date filter (YYYY-MM-DD)")
    state: str | None = Field(None, description="State code (e.g. SP, RJ, MG)")
    category: str | None = Field(None, description="Product category name")
    limit: int = Field(default=50, ge=1, le=1000)
