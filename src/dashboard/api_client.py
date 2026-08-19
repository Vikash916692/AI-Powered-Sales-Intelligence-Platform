"""
Dedicated HTTP REST API Client for Streamlit Dashboard.

Enforces strict Streamlit -> FastAPI architecture, handles JWT authentication,
session tokens, connection pooling, and structured error handling.
"""

import os
from typing import Any

import httpx

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


class APIClientError(Exception):
    """Custom exception wrapping API errors."""

    def __init__(self, message: str, status_code: int | None = None, details: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class SalesIntelligenceAPIClient:
    """Client for interacting with the Sales Intelligence REST API."""

    def __init__(self, base_url: str = DEFAULT_API_BASE_URL, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._timeout = 45.0  # seconds for LLM/ML calls

    def set_token(self, token: str | None) -> None:
        """Update active session token."""
        self.token = token

    def _get_headers(self) -> dict[str, str]:
        """Build headers with Authorization if token is set."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Execute synchronous HTTP request."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        req_headers = self._get_headers()
        if headers:
            req_headers.update(headers)

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=req_headers,
                )

                if response.status_code >= 400:
                    try:
                        err_data = response.json()
                        err_msg = err_data.get("detail") or err_data.get("message") or response.text
                    except Exception:
                        err_msg = response.text
                    raise APIClientError(
                        message=f"API Request Failed ({response.status_code}): {err_msg}",
                        status_code=response.status_code,
                        details=response.text,
                    )

                if response.headers.get("content-type", "").startswith("application/json"):
                    return response.json()
                return response.content

        except httpx.RequestError as e:
            raise APIClientError(
                message=f"Could not connect to Backend API at {self.base_url}. Ensure FastAPI server is running.",
                details=str(e),
            ) from e

    # ----------------------------------------------------
    # 1. AUTHENTICATION
    # ----------------------------------------------------
    def login(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate user and obtain JWT token."""
        data = self._request("POST", "/auth/login", json={"username": username, "password": password})
        self.token = data.get("access_token")
        return data

    def get_current_user(self) -> dict[str, Any]:
        """Retrieve profile of authenticated user."""
        return self._request("GET", "/auth/me")

    # ----------------------------------------------------
    # 2. EXECUTIVE KPIS
    # ----------------------------------------------------
    def get_executive_overview(self) -> dict[str, Any]:
        return self._request("GET", "/kpis/executive")

    def get_customer_economics(self) -> dict[str, Any]:
        return self._request("GET", "/kpis/customer-economics")

    def get_logistics_sla(self) -> dict[str, Any]:
        return self._request("GET", "/kpis/logistics-sla")

    def get_rfm_segments(self) -> list[dict[str, Any]]:
        return self._request("GET", "/kpis/rfm")

    def get_top_categories(self, limit: int = 5) -> list[dict[str, Any]]:
        return self._request("GET", "/kpis/top-categories", params={"limit": limit})

    # ----------------------------------------------------
    # 3. ANALYTICAL DATA MARTS
    # ----------------------------------------------------
    def get_sales_mart(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = 1,
        page_size: int = 30,
    ) -> dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/analytics/sales", params=params)

    def get_delivery_mart(self) -> dict[str, Any]:
        return self._request("GET", "/analytics/delivery")

    def get_product_mart(self, page: int = 1, page_size: int = 25) -> dict[str, Any]:
        return self._request("GET", "/analytics/products", params={"page": page, "page_size": page_size})

    def get_seller_mart(self, page: int = 1, page_size: int = 25) -> dict[str, Any]:
        return self._request("GET", "/analytics/sellers", params={"page": page, "page_size": page_size})

    def get_review_mart(self) -> dict[str, Any]:
        return self._request("GET", "/analytics/reviews")

    # ----------------------------------------------------
    # 4. MACHINE LEARNING & PREDICTIVE TOOLS
    # ----------------------------------------------------
    def predict_delivery_delay(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/ml/predict-delay", json=payload)

    def predict_delay(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Alias for predict_delivery_delay."""
        return self.predict_delivery_delay(payload)

    def forecast_sales(self, horizon_days: int = 30) -> dict[str, Any]:
        return self._request("POST", "/ml/forecast", json={"horizon_days": horizon_days})

    def recommend_products(self, product_id: str | None = None, top_n: int = 5) -> dict[str, Any]:
        payload: dict[str, Any] = {"top_n": top_n}
        if product_id:
            payload["product_id"] = product_id
        return self._request("POST", "/ml/recommend", json=payload)

    def analyze_sentiment(self, review_text: str) -> dict[str, Any]:
        return self._request("POST", "/ml/sentiment", json={"review_text": review_text})

    # ----------------------------------------------------
    # 5. AGENTIC AI COPILOT
    # ----------------------------------------------------
    def query_agent(self, query: str, force_offline: bool = False) -> dict[str, Any]:
        return self._request("POST", "/agents/query", json={"query": query, "force_offline": force_offline})

    # ----------------------------------------------------
    # 6. SYSTEM HEALTH & DIAGNOSTICS
    # ----------------------------------------------------
    def get_health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    # ----------------------------------------------------
    # 7. EXECUTIVE REPORTS
    # ----------------------------------------------------
    def download_pdf_report(self) -> bytes:
        return self._request("GET", "/reports/pdf", headers={"Accept": "application/pdf"})

    def download_excel_report(self) -> bytes:
        return self._request(
            "GET",
            "/reports/excel",
            headers={"Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        )


# Singleton client instance
api_client = SalesIntelligenceAPIClient()
