"""
Multi-Tab Excel Executive Workbook Generator using XlsxWriter.

Generates a formatted multi-tab spreadsheet with:
1. Executive Overview Tab (Styled KPI summary table)
2. Daily Sales Trends Tab (Date & Currency formatted data mart)
3. RFM Customer Segments Tab (With conditional formatting)
4. Logistics SLA & Delivery Latencies Tab
5. Product Performance Rankings Tab
"""

import io
from datetime import UTC, datetime
from typing import Any

import pandas as pd
import xlsxwriter

from ml.common.db import execute_query


class ExcelReportGenerator:
    """Generates formatted multi-tab Excel workbooks."""

    def generate_analytical_workbook(
        self,
        executive_kpis: dict[str, Any],
        customer_kpis: dict[str, Any],
        logistics_kpis: dict[str, Any],
        rfm_segments: list[dict[str, Any]],
        top_categories: list[dict[str, Any]],
    ) -> bytes:
        """
        Builds multi-tab Excel workbook.
        Returns binary bytes.
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        # Format Styles
        header_fmt = workbook.add_format({
            "bold": True,
            "bg_color": "#0F172A",
            "font_color": "#FFFFFF",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "font_name": "Calibri",
            "font_size": 11,
        })
        title_fmt = workbook.add_format({
            "bold": True,
            "font_size": 16,
            "font_color": "#0284C7",
            "font_name": "Calibri",
        })
        subtitle_fmt = workbook.add_format({
            "italic": True,
            "font_size": 10,
            "font_color": "#64748B",
            "font_name": "Calibri",
        })
        cell_fmt = workbook.add_format({
            "border": 1,
            "font_name": "Calibri",
            "font_size": 10,
        })
        bold_cell_fmt = workbook.add_format({
            "bold": True,
            "border": 1,
            "font_name": "Calibri",
            "font_size": 10,
        })
        currency_fmt = workbook.add_format({
            "num_format": "$#,##0.00",
            "border": 1,
            "font_name": "Calibri",
            "font_size": 10,
        })
        integer_fmt = workbook.add_format({
            "num_format": "#,##0",
            "border": 1,
            "font_name": "Calibri",
            "font_size": 10,
        })
        pct_fmt = workbook.add_format({
            "num_format": "0.00%",
            "border": 1,
            "font_name": "Calibri",
            "font_size": 10,
        })

        now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

        # ----------------------------------------------------
        # TAB 1: EXECUTIVE OVERVIEW
        # ----------------------------------------------------
        ws1 = workbook.add_worksheet("Executive Overview")
        ws1.set_column("A:A", 30)
        ws1.set_column("B:B", 25)
        ws1.set_column("C:C", 40)

        ws1.write("A1", "AI-Powered Sales Intelligence Platform", title_fmt)
        ws1.write("A2", f"Executive Analytics Snapshot — Generated {now_str}", subtitle_fmt)

        headers_ws1 = ["Strategic Business Metric", "Calculated Value", "Operational Benchmark / Context"]
        for col_idx, text in enumerate(headers_ws1):
            ws1.write(3, col_idx, text, header_fmt)

        metrics_rows = [
            ("Total Gross Revenue", float(executive_kpis.get("total_gross_revenue", 0.0)), currency_fmt, "Cumulative gross marketplace revenue"),
            ("Total Completed Orders", int(executive_kpis.get("total_orders", 0)), integer_fmt, "Distinct customer order transactions"),
            ("Total Items Sold", int(executive_kpis.get("total_items_sold", 0)), integer_fmt, "Total physical product units shipped"),
            ("Average Order Value (AOV)", float(executive_kpis.get("executive_aov", 0.0)), currency_fmt, "Mean customer expenditure per checkout"),
            ("Average Unit Price", float(executive_kpis.get("average_item_value", 0.0)), currency_fmt, "Mean catalog SKU unit price"),
            ("Registered Customer Base", int(executive_kpis.get("total_registered_customers", 0)), integer_fmt, "Total registered buyer accounts"),
            ("Registered Seller Base", int(executive_kpis.get("total_registered_sellers", 0)), integer_fmt, "Total active merchant partners"),
            ("Customer Repeat Buying Rate", float(customer_kpis.get("repeat_purchase_rate_pct", 0.0)) / 100.0, pct_fmt, "Percentage of buyers with > 1 order"),
            ("Customer Mean LTV", float(customer_kpis.get("customer_ltv_mean", 0.0)), currency_fmt, "Mean customer lifetime value"),
            ("On-Time SLA Delivery Rate", float(logistics_kpis.get("on_time_delivery_rate_pct", 0.0)) / 100.0, pct_fmt, "Percentage of orders delivered by SLA promise"),
            ("Average Delivery Latency (Days)", float(logistics_kpis.get("avg_delivery_days", 0.0)), cell_fmt, "Mean shipping duration in calendar days"),
        ]

        for row_idx, (name, val, fmt, context) in enumerate(metrics_rows, start=4):
            ws1.write(row_idx, 0, name, bold_cell_fmt)
            ws1.write(row_idx, 1, val, fmt)
            ws1.write(row_idx, 2, context, cell_fmt)

        # ----------------------------------------------------
        # TAB 2: DAILY SALES MART TRENDS
        # ----------------------------------------------------
        ws2 = workbook.add_worksheet("Daily Sales Mart")
        df_sales = execute_query("SELECT * FROM sales_mart ORDER BY sales_date DESC LIMIT 100;")
        
        ws2.set_column("A:A", 14)
        ws2.set_column("B:G", 16)
        ws2.set_column("H:K", 18)

        if not df_sales.empty:
            for col_idx, col_name in enumerate(df_sales.columns):
                ws2.write(0, col_idx, col_name, header_fmt)
            for row_idx, row in df_sales.iterrows():
                for col_idx, val in enumerate(row):
                    if "revenue" in df_sales.columns[col_idx] or "value" in df_sales.columns[col_idx] or "freight" in df_sales.columns[col_idx]:
                        ws2.write(row_idx + 1, col_idx, float(val) if pd.notnull(val) else 0.0, currency_fmt)
                    elif isinstance(val, (int, float)) and "orders" in df_sales.columns[col_idx]:
                        ws2.write(row_idx + 1, col_idx, int(val) if pd.notnull(val) else 0, integer_fmt)
                    else:
                        ws2.write(row_idx + 1, col_idx, str(val) if pd.notnull(val) else "", cell_fmt)

        # ----------------------------------------------------
        # TAB 3: RFM CUSTOMER SEGMENTS
        # ----------------------------------------------------
        ws3 = workbook.add_worksheet("RFM Customer Segments")
        ws3.set_column("A:A", 22)
        ws3.set_column("B:C", 16)
        ws3.set_column("D:E", 20)
        ws3.set_column("F:F", 16)

        headers_rfm = ["RFM Segment", "Customer Count", "Share (%)", "Total Spend (USD)", "Avg Spend/User (USD)", "Avg Recency (Days)"]
        for col_idx, text in enumerate(headers_rfm):
            ws3.write(0, col_idx, text, header_fmt)

        for row_idx, seg in enumerate(rfm_segments, start=1):
            ws3.write(row_idx, 0, str(seg.get("rfm_segment", "N/A")), bold_cell_fmt)
            ws3.write(row_idx, 1, int(seg.get("customer_count", 0)), integer_fmt)
            ws3.write(row_idx, 2, float(seg.get("customer_share_pct", 0.0)) / 100.0, pct_fmt)
            ws3.write(row_idx, 3, float(seg.get("total_segment_spend", 0.0)), currency_fmt)
            ws3.write(row_idx, 4, float(seg.get("avg_spend_per_customer", 0.0)), currency_fmt)
            ws3.write(row_idx, 5, float(seg.get("avg_recency_days", 0.0)), cell_fmt)

        # ----------------------------------------------------
        # TAB 4: PRODUCT CATEGORY RANKINGS
        # ----------------------------------------------------
        ws4 = workbook.add_worksheet("Top Product Categories")
        ws4.set_column("A:A", 10)
        ws4.set_column("B:B", 30)
        ws4.set_column("C:C", 16)
        ws4.set_column("D:D", 22)
        ws4.set_column("E:E", 18)

        headers_cat = ["Rank", "Category Name (English)", "Units Sold", "Total Revenue (USD)", "Avg Unit Price (USD)"]
        for col_idx, text in enumerate(headers_cat):
            ws4.write(0, col_idx, text, header_fmt)

        for row_idx, cat in enumerate(top_categories, start=1):
            ws4.write(row_idx, 0, f"#{row_idx}", bold_cell_fmt)
            ws4.write(row_idx, 1, str(cat.get("category_name", "N/A")), bold_cell_fmt)
            ws4.write(row_idx, 2, int(cat.get("total_units_sold", 0)), integer_fmt)
            ws4.write(row_idx, 3, float(cat.get("total_revenue", 0.0)), currency_fmt)
            ws4.write(row_idx, 4, float(cat.get("avg_category_price", 0.0)), currency_fmt)

        workbook.close()
        excel_bytes = output.getvalue()
        output.close()
        return excel_bytes


excel_generator = ExcelReportGenerator()
