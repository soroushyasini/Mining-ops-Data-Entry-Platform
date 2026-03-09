from app.shared.sample_parser import parse_sample_code


def test_parse_standard_facility_type_seq():
    result = parse_sample_code("A-1404/11/08-K-1")
    assert result["source_facility"] == "robat_sefid"
    assert result["sample_date_jalali"] == "1404/11/08"
    assert result["sample_type"] == "K"
    assert result["sequence_number"] == 1


def test_parse_shen_beton_facility():
    result = parse_sample_code("B-1404/11/10-L-3")
    assert result["source_facility"] == "shen_beton"
    assert result["sample_date_jalali"] == "1404/11/10"
    assert result["sample_type"] == "L"
    assert result["sequence_number"] == 3


def test_parse_multi_char_type_cr():
    result = parse_sample_code("A-1404/11/08-CR-2")
    assert result["source_facility"] == "robat_sefid"
    assert result["sample_date_jalali"] == "1404/11/08"
    assert result["sample_type"] == "CR"
    assert result["sequence_number"] == 2


def test_parse_rc_no_facility():
    result = parse_sample_code("RC-1404/11/08-1")
    assert result["source_facility"] is None
    assert result["sample_date_jalali"] == "1404/11/08"
    assert result["sample_type"] == "RC"
    assert result["sequence_number"] == 1


def test_parse_malformed_returns_none_fields():
    result = parse_sample_code("BADCODE")
    assert result["source_facility"] is None
    assert result["sample_date_jalali"] is None
    assert result["sample_type"] is None
    assert result["sequence_number"] is None


def test_parse_empty_string():
    result = parse_sample_code("")
    assert result["source_facility"] is None
    assert result["sample_date_jalali"] is None
    assert result["sample_type"] is None
    assert result["sequence_number"] is None


def test_facility_mapping_a():
    result = parse_sample_code("A-1404/11/08-K-1")
    assert result["source_facility"] == "robat_sefid"


def test_facility_mapping_b():
    result = parse_sample_code("B-1404/11/08-K-1")
    assert result["source_facility"] == "shen_beton"


def test_facility_mapping_c():
    result = parse_sample_code("C-1404/11/08-K-1")
    assert result["source_facility"] == "kavian"
