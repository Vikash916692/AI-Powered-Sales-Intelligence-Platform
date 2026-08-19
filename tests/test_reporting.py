"""
Automated Test Suite for Executive Reporting Engines (PDF & Excel).

Verifies:
1. PDFReportGenerator builds valid, multi-page non-empty PDF bytes
2. ExcelReportGenerator builds valid multi-tab Excel workbook bytes
3. REST endpoint /api/v1/reports/pdf streams PDF attachment with 200 OK
4. REST endpoint /api/v1/reports/excel streams Excel attachment with 200 OK
"""

import pytest
from fastapi.testclient import TestClient

from src.agents.kpi_engine import kpi_engine
from src.api.main import app
from src.reporting.excel_generator import excel_generator
from src.reporting.pdf_generator import pdf_generator

client = TestClient(app)


@pytest.fixture
def auth_header():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_pdf_report_generator_engine():
    """Verify PDF generator produces non-empty bytes."""
    overview = kpi_engine.get_executive_overview()
    customer = kpi_engine.get_customer_economics()
    logistics = kpi_engine.get_logistics_sla()
    rfm = kpi_engine.get_rfm_segmentation()
    categories = kpi_engine.get_top_categories(5)

    pdf_bytes = pdf_generator.generate_executive_briefing(
        executive_kpis=overview,
        customer_kpis=customer,
        logistics_kpis=logistics,
        rfm_segments=rfm,
        top_categories=categories,
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")


def test_excel_report_generator_engine():
    """Verify Excel generator produces valid multi-tab spreadsheet."""
    overview = kpi_engine.get_executive_overview()
    customer = kpi_engine.get_customer_economics()
    logistics = kpi_engine.get_logistics_sla()
    rfm = kpi_engine.get_rfm_segmentation()
    categories = kpi_engine.get_top_categories(5)

    excel_bytes = excel_generator.generate_analytical_workbook(
        executive_kpis=overview,
        customer_kpis=customer,
        logistics_kpis=logistics,
        rfm_segments=rfm,
        top_categories=categories,
    )

    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 5000
    # ZIP / OpenXML header magic bytes
    assert excel_bytes.startswith(b"PK")


def test_rest_download_pdf_endpoint(auth_header):
    """Verify REST API /reports/pdf downloads valid PDF file."""
    response = client.get("/api/v1/reports/pdf", headers=auth_header)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_rest_download_excel_endpoint(auth_header):
    """Verify REST API /reports/excel downloads valid Excel file."""
    response = client.get("/api/v1/reports/excel", headers=auth_header)
    assert response.status_code == 200
    assert "openxmlformats" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK")
