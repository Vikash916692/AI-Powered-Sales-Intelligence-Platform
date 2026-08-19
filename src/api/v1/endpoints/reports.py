"""
Executive Report Export REST Endpoints for PDF and Excel generation.
"""

from fastapi import APIRouter, Depends, Response

from src.agents.kpi_engine import kpi_engine
from src.api.dependencies import get_current_user
from src.api.schemas.auth_schemas import UserRead
from src.reporting.excel_generator import excel_generator
from src.reporting.pdf_generator import pdf_generator

router = APIRouter(prefix="/reports", tags=["Executive Reports & Briefing Books"])


@router.get(
    "/pdf",
    summary="Download Executive PDF Briefing Book",
    responses={200: {"content": {"application/pdf": {}}}},
)
def download_pdf_report(
    current_user: UserRead = Depends(get_current_user),
):
    """Generates and downloads multi-page executive PDF briefing document."""
    overview = kpi_engine.get_executive_overview()
    customer = kpi_engine.get_customer_economics()
    logistics = kpi_engine.get_logistics_sla()
    rfm = kpi_engine.get_rfm_segmentation()
    categories = kpi_engine.get_top_categories(10)

    pdf_bytes = pdf_generator.generate_executive_briefing(
        executive_kpis=overview,
        customer_kpis=customer,
        logistics_kpis=logistics,
        rfm_segments=rfm,
        top_categories=categories,
        generated_by=f"{current_user.full_name or current_user.username} ({current_user.role})",
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Executive_Sales_Intelligence_Briefing.pdf"},
    )


@router.get(
    "/excel",
    summary="Download Multi-Tab Financial Analytics Excel Model",
    responses={200: {"content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}}}},
)
def download_excel_report(
    current_user: UserRead = Depends(get_current_user),
):
    """Generates and downloads multi-tab financial and analytical Excel workbook."""
    overview = kpi_engine.get_executive_overview()
    customer = kpi_engine.get_customer_economics()
    logistics = kpi_engine.get_logistics_sla()
    rfm = kpi_engine.get_rfm_segmentation()
    categories = kpi_engine.get_top_categories(10)

    excel_bytes = excel_generator.generate_analytical_workbook(
        executive_kpis=overview,
        customer_kpis=customer,
        logistics_kpis=logistics,
        rfm_segments=rfm,
        top_categories=categories,
    )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Sales_Intelligence_Analytics_Model.xlsx"},
    )
