import re
from datetime import date

import jdatetime


_JALALI_PATTERN = re.compile(r"^\d{4}/\d{2}/\d{2}$")


def jalali_to_gregorian(jalali_str: str) -> date:
    """Convert a Jalali date string (1404/11/12) to a Python date."""
    if not _JALALI_PATTERN.match(jalali_str):
        raise ValueError(f"Invalid Jalali date format: '{jalali_str}'. Expected YYYY/MM/DD")
    year, month, day = (int(p) for p in jalali_str.split("/"))
    try:
        jdate = jdatetime.date(year, month, day)
        greg = jdate.togregorian()
        return greg
    except Exception as exc:
        raise ValueError(f"Invalid Jalali date '{jalali_str}': {exc}") from exc


def gregorian_to_jalali(greg_date: date) -> str:
    """Convert a Python date to a Jalali date string (1404/11/12)."""
    jdate = jdatetime.date.fromgregorian(date=greg_date)
    return jdate.strftime("%Y/%m/%d")
