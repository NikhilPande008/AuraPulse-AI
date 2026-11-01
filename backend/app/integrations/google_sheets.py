import os
from typing import Any, Dict, List

from ..config import settings

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    build = None
    service_account = None


class SheetsNotConfiguredError(Exception):
    """Raised when Google Sheets credentials are not configured."""
    pass


class SheetsExportError(Exception):
    """Raised when Google Sheets export encounters an API failure."""
    pass


def is_sheets_configured() -> bool:
    """Returns True only if service account credentials file actually exists on disk."""
    creds_file = settings.GOOGLE_APPLICATION_CREDENTIALS
    return bool(creds_file and os.path.exists(creds_file) and build and service_account)


def export_event_to_google_sheets(
    spreadsheet_title: str,
    boq_items: List[Dict[str, Any]],
    currency: str = "INR"
) -> Dict[str, Any]:
    """
    Creates an interactive, formula-driven Google Sheets workbook.
    If credentials are not configured, raises SheetsNotConfiguredError.
    Never manufactures fake docs.google.com URLs.
    """
    if not is_sheets_configured():
        raise SheetsNotConfiguredError(
            "Google Sheets credentials are not configured. Please configure GOOGLE_APPLICATION_CREDENTIALS."
        )

    rows_data = []
    # Header row
    rows_data.append([
        "Item ID",
        "Category",
        "Procurement Name",
        "Specification",
        "Quantity",
        "Unit",
        f"Rate ({currency})",
        f"Total Cost ({currency})",
        "Priority Tier",
        "Status"
    ])

    for item in boq_items:
        rows_data.append([
            item.get("item_id", ""),
            item.get("category", ""),
            item.get("name", ""),
            item.get("specification", ""),
            item.get("quantity", 0),
            item.get("unit", ""),
            item.get("estimated_rate_inr", 0),
            item.get("total_cost_inr", 0),
            str(item.get("priority", "")),
            item.get("status", "ACTIVE")
        ])

    num_items = len(boq_items)
    last_data_row = num_items + 1
    total_formula = f"=SUM(H2:H{last_data_row})"

    # Summary grand total row
    rows_data.append([
        "TOTAL",
        "-",
        "-",
        "-",
        "-",
        "-",
        "GRAND TOTAL",
        total_formula,
        "-",
        "-"
    ])

    # Dynamic formula calculations written directly into sheet rows
    rows_data.append([
        "CRITICAL SUBTOTAL",
        "-",
        "-",
        "-",
        "-",
        "-",
        "SUMIF CRITICAL",
        f'=SUMIF(I2:I{last_data_row}, "Critical", H2:H{last_data_row})',
        "Critical",
        "-"
    ])
    rows_data.append([
        "OPERATIONAL SUBTOTAL",
        "-",
        "-",
        "-",
        "-",
        "-",
        "SUMIF OPERATIONAL",
        f'=SUMIF(I2:I{last_data_row}, "Operational", H2:H{last_data_row})',
        "Operational",
        "-"
    ])
    rows_data.append([
        "DISCRETIONARY SUBTOTAL",
        "-",
        "-",
        "-",
        "-",
        "-",
        "SUMIF DISCRETIONARY",
        f'=SUMIF(I2:I{last_data_row}, "Discretionary", H2:H{last_data_row})',
        "Discretionary",
        "-"
    ])

    priority_breakdown = {
        "Critical Tier Formula": f'=SUMIF(I2:I{last_data_row}, "Critical", H2:H{last_data_row})',
        "Operational Tier Formula": f'=SUMIF(I2:I{last_data_row}, "Operational", H2:H{last_data_row})',
        "Discretionary Tier Formula": f'=SUMIF(I2:I{last_data_row}, "Discretionary", H2:H{last_data_row})',
    }

    creds_file = settings.GOOGLE_APPLICATION_CREDENTIALS
    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        sheets_service = build("sheets", "v4", credentials=creds)
        spreadsheet = {
            "properties": {"title": f"AuraPulse - {spreadsheet_title}"},
            "sheets": [
                {
                    "properties": {
                        "title": "Master BOQ & Budget",
                        "gridProperties": {"frozenRowCount": 1}
                    }
                }
            ]
        }
        sheet_create_res = sheets_service.spreadsheets().create(
            body=spreadsheet,
            fields="spreadsheetId,spreadsheetUrl"
        ).execute()

        spreadsheet_id = sheet_create_res.get("spreadsheetId")
        web_url = sheet_create_res.get("spreadsheetUrl")

        # Update sheet values with raw formulas enabled (USER_ENTERED)
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="Master BOQ & Budget!A1",
            valueInputOption="USER_ENTERED",
            body={"values": rows_data}
        ).execute()

        return {
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_title": spreadsheet_title,
            "spreadsheet_url": web_url,
            "total_rows_created": len(rows_data),
            "grand_total_formula": total_formula,
            "priority_formulas": priority_breakdown,
            "items_exported": num_items,
            "status": "SUCCESS",
            "api_target": "Google Sheets API v4"
        }
    except Exception as e:
        raise SheetsExportError(f"Google Sheets API call failed: {e}") from e
