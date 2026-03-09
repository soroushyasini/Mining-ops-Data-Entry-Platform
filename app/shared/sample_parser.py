"""
Parser for lab sample codes.

Sample code format: {FACILITY}-{DATE}-{TYPE}-{SEQ}

Examples:
  A-1404/11/08-K-1   → facility=robat_sefid, date=1404/11/08, type=K, seq=1
  B-1404/11/10-L-3   → facility=shen_beton, date=1404/11/10, type=L, seq=3
  A-1404/11/08-CR-2  → facility=robat_sefid, date=1404/11/08, type=CR, seq=2
  RC-1404/11/08-1    → no facility, date=1404/11/08, type=RC, seq=1
  F-1404/11/08-1     → no facility, date=1404/11/08, type=F, seq=1
"""

import re
from typing import Optional

# Facility letter → GrindingFacility enum value
FACILITY_MAP = {
    "A": "robat_sefid",
    "B": "shen_beton",
    "C": "kavian",
}

# Multi-char sample types that appear as a prefix (no facility letter)
PREFIX_TYPES = {"RC", "T"}

# All recognised sample types
KNOWN_TYPES = {"K", "L", "CR", "T", "RC", "F"}

_DATE_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")


def parse_sample_code(code: str) -> dict:
    """
    Parse a lab sample code into its components.

    Returns a dict with keys:
        source_facility      – GrindingFacility value or None
        sample_date_jalali   – str "YYYY/MM/DD" or None
        sample_type          – str sample type or None
        sequence_number      – int or None

    Never raises; unparseable fields are set to None.
    """
    result: dict = {
        "source_facility": None,
        "sample_date_jalali": None,
        "sample_type": None,
        "sequence_number": None,
    }

    if not code or not isinstance(code, str):
        return result

    parts = code.strip().split("-")
    if len(parts) < 3:
        return result

    try:
        # --- Try the compound-type prefix patterns first (RC, T when used as prefix) ---
        # Pattern: RC-DATE-SEQ  (3 parts)
        if len(parts) == 3 and _DATE_RE.match(parts[1]):
            sample_type = parts[0]
            date_str = parts[1]
            seq_str = parts[2]
            if sample_type in KNOWN_TYPES:
                result["sample_type"] = sample_type
                result["sample_date_jalali"] = date_str
                _try_set_seq(result, seq_str)
                return result

        # Pattern: FACILITY-DATE-TYPE-SEQ  (4 parts, CR or other two-char types)
        if len(parts) == 4 and _DATE_RE.match(parts[1]):
            facility_letter = parts[0]
            date_str = parts[1]
            sample_type = parts[2]
            seq_str = parts[3]

            if facility_letter in FACILITY_MAP:
                result["source_facility"] = FACILITY_MAP[facility_letter]
            result["sample_date_jalali"] = date_str
            if sample_type in KNOWN_TYPES:
                result["sample_type"] = sample_type
            _try_set_seq(result, seq_str)
            return result

        # Pattern: FACILITY-DATE-TYPE-SEQ where TYPE contains a slash (CR split?)
        # Fallback: try to find the date anywhere in parts
        date_index = None
        for i, part in enumerate(parts):
            if _DATE_RE.match(part):
                date_index = i
                break

        if date_index is None:
            return result

        result["sample_date_jalali"] = parts[date_index]

        # Parts before the date
        before = parts[:date_index]
        # Parts after the date
        after = parts[date_index + 1 :]

        if before:
            first = before[0]
            if first in FACILITY_MAP:
                result["source_facility"] = FACILITY_MAP[first]
            elif first in KNOWN_TYPES:
                result["sample_type"] = first

        if after:
            # Last part is sequence number
            _try_set_seq(result, after[-1])
            # Middle parts are the type
            if len(after) >= 2:
                sample_type = "-".join(after[:-1])
                if sample_type in KNOWN_TYPES:
                    result["sample_type"] = sample_type
            elif len(after) == 1 and result["sequence_number"] is None:
                # after[0] might be a type or a seq
                if after[0] in KNOWN_TYPES:
                    result["sample_type"] = after[0]
                    result["sequence_number"] = None

    except Exception:
        pass

    return result


def _try_set_seq(result: dict, seq_str: str) -> None:
    try:
        result["sequence_number"] = int(seq_str)
    except (ValueError, TypeError):
        pass
