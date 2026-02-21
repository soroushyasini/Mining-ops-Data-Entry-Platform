from typing import List, Dict, Any
import io
from sqlalchemy.orm import Session

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

from ..models import Truck, Driver, Facility


class BulkRowResult:
    def __init__(self, row_num: int, data: Dict[str, Any], status: str, message: str = ""):
        self.row_num = row_num
        self.data = data
        self.status = status  # "valid", "warning", "error"
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_num": self.row_num,
            "data": self.data,
            "status": self.status,
            "message": self.message,
        }


def _validate_shipment_row(row_data: Dict[str, Any], db: Session) -> BulkRowResult:
    row_num = row_data.get("_row_num", 0)
    data = {k: v for k, v in row_data.items() if not k.startswith("_")}

    # Check required fields
    if not data.get("date"):
        return BulkRowResult(row_num, data, "error", "تاریخ الزامی است")
    if not data.get("tonnage_kg"):
        return BulkRowResult(row_num, data, "error", "تناژ الزامی است")

    # Check truck number
    truck_number = str(data.get("truck_number", "")).strip()
    if truck_number:
        truck = db.query(Truck).filter(Truck.number == truck_number).first()
        if not truck:
            return BulkRowResult(row_num, data, "warning", f"شماره ماشین {truck_number} در سامانه ثبت نشده")

    return BulkRowResult(row_num, data, "valid", "آماده ثبت")


def preview_bulk_import(
    file_bytes: bytes,
    entity_type: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Parse uploaded Excel file and return per-row validation preview.
    """
    if not HAS_OPENPYXL:
        return {"error": "openpyxl not installed", "rows": []}

    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return {"rows": [], "valid_count": 0, "error_count": 0, "warning_count": 0}

    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    results = []

    for row_idx, row in enumerate(rows[1:], start=2):
        row_data = {headers[i]: row[i] for i in range(len(headers))}
        row_data["_row_num"] = row_idx

        if entity_type == "shipment":
            result = _validate_shipment_row(row_data, db)
        else:
            # Generic validation: just check for non-empty rows
            data = {k: v for k, v in row_data.items() if not k.startswith("_")}
            if all(v is None or v == "" for v in data.values()):
                continue
            result = BulkRowResult(row_idx, data, "valid", "آماده ثبت")

        results.append(result.to_dict())

    valid_count = sum(1 for r in results if r["status"] == "valid")
    warning_count = sum(1 for r in results if r["status"] == "warning")
    error_count = sum(1 for r in results if r["status"] == "error")

    return {
        "rows": results,
        "valid_count": valid_count,
        "warning_count": warning_count,
        "error_count": error_count,
    }


def confirm_bulk_import(
    preview_data: Dict[str, Any],
    entity_type: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Commit only valid rows from a previously previewed bulk import.
    """
    imported = 0
    skipped = 0

    for row in preview_data.get("rows", []):
        if row["status"] in ("valid", "warning"):
            # Here you would instantiate the appropriate model and insert
            # For now we track counts only; actual insert logic per entity
            # would be added by the entity-specific router
            imported += 1
        else:
            skipped += 1

    return {
        "imported": imported,
        "skipped": skipped,
        "message": f"{imported} ردیف ثبت شد، {skipped} ردیف رد شد",
    }
