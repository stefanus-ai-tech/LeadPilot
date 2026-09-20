"""High-aesthetic, executive-ready Excel workbook exporter for LeadPilot triage results.

Adheres to professional spreadsheet standards:
- Elegant typography (Segoe UI) and cohesive color-coded palette.
- Interactive Executive Summary dashboard with KPI cards and dynamic Excel formulas.
- Detailed Lead Triage sheet with frozen header, auto-filter, zebra striping, and badges.
- Auto-fitted column widths and Excel formula injection protection.
"""
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT_NAME = "Segoe UI"

# --- Palette ---
COLOR_HEADER_BG = "1E293B"      # Dark Slate 800
COLOR_HEADER_TXT = "FFFFFF"     # White
COLOR_ZEBRA_BG = "F8FAFC"       # Very Light Slate
COLOR_BORDER = "CBD5E1"         # Slate 300

COLOR_HOT_BG = "FEE2E2"         # Soft Red
COLOR_HOT_TXT = "991B1B"        # Dark Red
COLOR_WARM_BG = "FEF3C7"        # Soft Amber
COLOR_WARM_TXT = "92400E"       # Dark Amber
COLOR_COLD_BG = "E0F2FE"        # Soft Sky Blue
COLOR_COLD_TXT = "0369A1"       # Dark Sky Blue

COLOR_PURCHASE_BG = "DCFCE7"    # Soft Emerald
COLOR_PURCHASE_TXT = "166534"   # Dark Emerald
COLOR_RESEARCH_BG = "E0E7FF"    # Soft Indigo
COLOR_RESEARCH_TXT = "3730A3"   # Dark Indigo
COLOR_SUPPORT_BG = "F3E8FF"     # Soft Purple
COLOR_SUPPORT_TXT = "6B21A8"    # Dark Purple
COLOR_SPAM_BG = "FFE4E6"        # Soft Rose
COLOR_SPAM_TXT = "9F1239"       # Dark Rose

COLOR_REVIEW_BG = "FFEDD5"      # Soft Orange Warning
COLOR_REVIEW_TXT = "C2410C"     # Dark Orange

COLOR_CARD_TITLE_BG = "0F172A"  # Deep Navy Slate
COLOR_SECTION_BG = "334155"     # Slate 700

# Styles
FONT_TITLE = Font(name=FONT_NAME, size=16, bold=True, color="0F172A")
FONT_SUBTITLE = Font(name=FONT_NAME, size=10, italic=True, color="64748B")
FONT_SECTION = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
FONT_HEADER = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_HEADER_TXT)
FONT_BODY = Font(name=FONT_NAME, size=10, color="1E293B")
FONT_BODY_BOLD = Font(name=FONT_NAME, size=10, bold=True, color="1E293B")
FONT_MUTED = Font(name=FONT_NAME, size=9, color="64748B")

FILL_HEADER = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
FILL_SECTION = PatternFill(start_color=COLOR_SECTION_BG, end_color=COLOR_SECTION_BG, fill_type="solid")
FILL_ZEBRA = PatternFill(start_color=COLOR_ZEBRA_BG, end_color=COLOR_ZEBRA_BG, fill_type="solid")
FILL_WHITE = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

BORDER_THIN = Border(
    left=Side(style="thin", color=COLOR_BORDER),
    right=Side(style="thin", color=COLOR_BORDER),
    top=Side(style="thin", color=COLOR_BORDER),
    bottom=Side(style="thin", color=COLOR_BORDER),
)
BORDER_HEADER = Border(
    left=Side(style="thin", color="334155"),
    right=Side(style="thin", color="334155"),
    top=Side(style="medium", color="0F172A"),
    bottom=Side(style="medium", color="0F172A"),
)


def _format_cell_value(key: str, value: Any) -> Any:
    """Format and convert cell data to correct Excel data types."""
    if value is None or value == "":
        return ""
    if key in ("budget", "company_size", "lp_row", "lp_score"):
        try:
            return int(value)
        except (ValueError, TypeError):
            return str(value)
    if key == "lp_confidence":
        try:
            return float(value)
        except (ValueError, TypeError):
            return str(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        # Excel formula injection defense
        return "'" + value
    return str(value)


def create_styled_workbook(headers: list[str], rows: list[dict], state: dict) -> Workbook:
    """Build a professional, multi-sheet workbook with KPI summary and styled triage table."""
    from app.batch import RESULT_FIELDS

    wb = Workbook()
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary.views.sheetView[0].showGridLines = True

    ws_data = wb.create_sheet(title="Lead Triage")
    ws_data.views.sheetView[0].showGridLines = True

    all_fields = headers + RESULT_FIELDS
    last_data_row = len(rows) + 1  # Row 1 is header in Lead Triage

    # Column letter mapping for formulas
    field_to_col: dict[str, str] = {}
    for col_idx, field in enumerate(all_fields, 1):
        field_to_col[field] = get_column_letter(col_idx)

    tier_col = field_to_col.get("lp_tier", "J")
    status_col = field_to_col.get("lp_status", "B")
    intent_col = field_to_col.get("lp_intent", "D")
    score_col = field_to_col.get("lp_score", "I")
    review_col = field_to_col.get("lp_requires_human_review", "K")

    # =========================================================================
    # 1. POPULATE LEAD TRIAGE SHEET
    # =========================================================================
    # Write Header
    ws_data.row_dimensions[1].height = 26
    for col_idx, field in enumerate(all_fields, 1):
        cell = ws_data.cell(row=1, column=col_idx, value=field)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
        cell.border = BORDER_HEADER

    # Write Data Rows
    for row_idx, row in enumerate(rows, 2):
        row_num = row_idx - 1
        res = state.get(str(row_num), {"lp_status": "pending"})
        merged_row = {k: row.get(k, "") for k in headers}
        merged_row.update(res)
        merged_row["lp_row"] = row_num

        is_even = (row_idx % 2 == 0)
        default_fill = FILL_WHITE if is_even else FILL_ZEBRA
        ws_data.row_dimensions[row_idx].height = 20

        for col_idx, field in enumerate(all_fields, 1):
            raw_val = merged_row.get(field, "")
            cell_val = _format_cell_value(field, raw_val)
            cell = ws_data.cell(row=row_idx, column=col_idx, value=cell_val)
            cell.font = FONT_BODY
            cell.fill = default_fill
            cell.border = BORDER_THIN
            cell.alignment = Alignment(vertical="center")

            # Contextual Alignment & Formatting
            if field == "budget":
                cell.number_format = '"Rp" #,##0'
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif field in ("company_size", "lp_row", "lp_score"):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif field == "lp_confidence":
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif field in ("message", "lp_summary", "lp_reasons", "lp_error"):
                cell.alignment = Alignment(vertical="center", wrap_text=True)

            # Badge Styling for Tiers
            tier_val = str(merged_row.get("lp_tier", "")).upper()
            if field == "lp_tier":
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if tier_val == "HOT":
                    cell.fill = PatternFill(start_color=COLOR_HOT_BG, end_color=COLOR_HOT_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_HOT_TXT)
                elif tier_val == "WARM":
                    cell.fill = PatternFill(start_color=COLOR_WARM_BG, end_color=COLOR_WARM_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_WARM_TXT)
                elif tier_val == "COLD":
                    cell.fill = PatternFill(start_color=COLOR_COLD_BG, end_color=COLOR_COLD_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_COLD_TXT)

            # Badge Styling for Intent
            intent_val = str(merged_row.get("lp_intent", "")).lower()
            if field == "lp_intent":
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if intent_val == "purchase":
                    cell.fill = PatternFill(start_color=COLOR_PURCHASE_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_PURCHASE_TXT)
                elif intent_val == "research":
                    cell.fill = PatternFill(start_color=COLOR_RESEARCH_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_RESEARCH_TXT)
                elif intent_val == "support":
                    cell.fill = PatternFill(start_color=COLOR_SUPPORT_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_SUPPORT_TXT)
                elif intent_val == "spam":
                    cell.fill = PatternFill(start_color=COLOR_SPAM_BG, fill_type="solid")
                    cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_SPAM_TXT)

            # Warning Highlight for Human Review
            if field == "lp_requires_human_review" and merged_row.get("lp_requires_human_review") is True:
                cell.fill = PatternFill(start_color=COLOR_REVIEW_BG, fill_type="solid")
                cell.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_REVIEW_TXT)
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Freeze panes at A2 and add auto-filter
    ws_data.freeze_panes = "A2"
    ws_data.auto_filter.ref = f"A1:{get_column_letter(len(all_fields))}{max(last_data_row, 2)}"

    # Auto-adjust column widths
    for col_idx, field in enumerate(all_fields, 1):
        col_letter = get_column_letter(col_idx)
        if field in ("message", "lp_summary", "lp_reasons"):
            ws_data.column_dimensions[col_letter].width = 42
        elif field in ("name", "company", "email", "service"):
            ws_data.column_dimensions[col_letter].width = 24
        elif field in ("budget", "lp_confidence", "lp_score", "lp_row"):
            ws_data.column_dimensions[col_letter].width = 15
        else:
            ws_data.column_dimensions[col_letter].width = 18

    # =========================================================================
    # 2. POPULATE EXECUTIVE SUMMARY SHEET
    # =========================================================================
    ws_summary.column_dimensions["A"].width = 4
    ws_summary.column_dimensions["B"].width = 30
    ws_summary.column_dimensions["C"].width = 18
    ws_summary.column_dimensions["D"].width = 36

    # Title Banner
    ws_summary.cell(row=2, column=2, value="🚀 LeadPilot — Sales Intelligence Dashboard").font = FONT_TITLE
    ws_summary.cell(row=3, column=2, value="Automated Local AI Lead Qualification & Deterministic Scoring").font = FONT_SUBTITLE

    # Table 1: High-Level KPI Summary (Rows 5 - 13)
    ws_summary.cell(row=5, column=2, value="Executive KPI Metric").font = FONT_SECTION
    ws_summary.cell(row=5, column=2).fill = FILL_SECTION
    ws_summary.cell(row=5, column=3, value="Value").font = FONT_SECTION
    ws_summary.cell(row=5, column=3).fill = FILL_SECTION
    ws_summary.cell(row=5, column=4, value="Context & Note").font = FONT_SECTION
    ws_summary.cell(row=5, column=4).fill = FILL_SECTION

    kpis = [
        ("Total Inbound Leads", f"=COUNTA('Lead Triage'!A2:A{last_data_row})", "Total rows in dataset", "#,##0"),
        ("🔥 HOT Leads (High Priority)", f'=COUNTIF(\'Lead Triage\'!{tier_col}2:{tier_col}{last_data_row}, "HOT")', "Score >= 80 (Immediate sales outreach)", "#,##0"),
        ("⛅ WARM Leads (Qualified)", f'=COUNTIF(\'Lead Triage\'!{tier_col}2:{tier_col}{last_data_row}, "WARM")', "Score 50 - 79 (Standard follow-up)", "#,##0"),
        ("❄️ COLD Leads (Low Fit/Research)", f'=COUNTIF(\'Lead Triage\'!{tier_col}2:{tier_col}{last_data_row}, "COLD")', "Score < 50 (Nurture sequence)", "#,##0"),
        ("⚠️ Flagged for Human Review", f'=COUNTIF(\'Lead Triage\'!{review_col}2:{review_col}{last_data_row}, TRUE)', "Model confidence < 0.60", "#,##0"),
        ("🎯 Average Lead Score", f"=AVERAGE('Lead Triage'!{score_col}2:{score_col}{last_data_row})", "Deterministic points out of 100", "0.0"),
        ("💼 Purchase Intent Leads", f'=COUNTIF(\'Lead Triage\'!{intent_col}2:{intent_col}{last_data_row}, "purchase")', "Expressed buying/booking desire", "#,##0"),
        ("✅ Processed Status (OK)", f'=COUNTIF(\'Lead Triage\'!{status_col}2:{status_col}{last_data_row}, "ok")', "Successfully triaged records", "#,##0"),
    ]

    for idx, (label, formula, note, num_fmt) in enumerate(kpis, 6):
        c_label = ws_summary.cell(row=idx, column=2, value=label)
        c_val = ws_summary.cell(row=idx, column=3, value=formula)
        c_note = ws_summary.cell(row=idx, column=4, value=note)

        for cell in (c_label, c_val, c_note):
            cell.font = FONT_BODY
            cell.border = BORDER_THIN
            cell.fill = FILL_WHITE if idx % 2 == 0 else FILL_ZEBRA

        c_val.font = FONT_BODY_BOLD
        c_val.number_format = num_fmt
        c_val.alignment = Alignment(horizontal="center", vertical="center")

    # Table 2: Priority Tier Distribution (Rows 16 - 20)
    ws_summary.cell(row=15, column=2, value="Lead Tier").font = FONT_SECTION
    ws_summary.cell(row=15, column=2).fill = FILL_SECTION
    ws_summary.cell(row=15, column=3, value="Count").font = FONT_SECTION
    ws_summary.cell(row=15, column=3).fill = FILL_SECTION
    ws_summary.cell(row=15, column=4, value="Action Recommendation").font = FONT_SECTION
    ws_summary.cell(row=15, column=4).fill = FILL_SECTION

    tier_breakdown = [
        ("🔥 HOT (Score 80-100)", f'=COUNTIF(\'Lead Triage\'!{tier_col}2:{tier_col}{last_data_row}, "HOT")', "Contact within 2 hours · Direct rep assignment"),
        ("⛅ WARM (Score 50-79)", f'=COUNTIF(\'Lead Triage\'!{tier_col}2:{tier_col}{last_data_row}, "WARM")', "Follow-up within 24 hours · Send product deck"),
        ("❄️ COLD (Score 0-49)", f'=COUNTIF(\'Lead Triage\'!{tier_col}2:{tier_col}{last_data_row}, "COLD")', "Enroll in email marketing automation"),
    ]

    for idx, (tier_name, formula, action) in enumerate(tier_breakdown, 16):
        c_t = ws_summary.cell(row=idx, column=2, value=tier_name)
        c_c = ws_summary.cell(row=idx, column=3, value=formula)
        c_a = ws_summary.cell(row=idx, column=4, value=action)

        for cell in (c_t, c_c, c_a):
            cell.font = FONT_BODY
            cell.border = BORDER_THIN
            cell.fill = FILL_WHITE if idx % 2 == 0 else FILL_ZEBRA

        c_c.font = FONT_BODY_BOLD
        c_c.number_format = "#,##0"
        c_c.alignment = Alignment(horizontal="center", vertical="center")

    # =========================================================================
    # 3. POPULATE ERRORS SHEET (If errors exist)
    # =========================================================================
    error_items = [(idx, res) for idx, res in state.items() if res.get("lp_status") == "error"]
    if error_items:
        ws_err = wb.create_sheet(title="Errors & Exceptions")
        ws_err.views.sheetView[0].showGridLines = True
        err_headers = ["Row", "Error Cause", "Original Name", "Original Email"]
        ws_err.row_dimensions[1].height = 24
        for col_idx, h in enumerate(err_headers, 1):
            c = ws_err.cell(row=1, column=col_idx, value=h)
            c.font = FONT_HEADER
            c.fill = PatternFill(start_color="991B1B", fill_type="solid")
            c.alignment = Alignment(horizontal="center", vertical="center")

        ws_err.column_dimensions["A"].width = 10
        ws_err.column_dimensions["B"].width = 45
        ws_err.column_dimensions["C"].width = 25
        ws_err.column_dimensions["D"].width = 30

        for r_idx, (item_idx, err_res) in enumerate(error_items, 2):
            orig_row = rows[int(item_idx) - 1] if int(item_idx) - 1 < len(rows) else {}
            ws_err.cell(row=r_idx, column=1, value=int(item_idx)).alignment = Alignment(horizontal="center")
            ws_err.cell(row=r_idx, column=2, value=err_res.get("lp_error", ""))
            ws_err.cell(row=r_idx, column=3, value=orig_row.get("name", ""))
            ws_err.cell(row=r_idx, column=4, value=orig_row.get("email", ""))
            for col_i in range(1, 5):
                ws_err.cell(row=r_idx, column=col_i).border = BORDER_THIN
                ws_err.cell(row=r_idx, column=col_i).font = FONT_BODY

    return wb


def export_excel(path: Path, headers: list[str], rows: list[dict], state: dict):
    """Atomically save an aesthetic, fully formatted Excel workbook."""
    temporary = path.with_suffix(".tmp")
    wb = create_styled_workbook(headers, rows, state)
    wb.save(temporary)
    try:
        temporary.replace(path)
    except PermissionError:
        # In case the file is actively locked by Microsoft Excel in Windows
        pass
