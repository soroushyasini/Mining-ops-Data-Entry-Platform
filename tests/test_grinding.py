import pytest


GRINDING_MINIMAL = {
    "date_jalali": "1404/11/04",
    "facility": "robat_sefid",
    "input_tonnage_kg": 23560,
}

GRINDING_FULL = {
    "date_jalali": "1404/11/05",
    "facility": "shen_beton",
    "input_tonnage_kg": 18900,
    "output_tonnage_kg": 18200,
    "grinding_cost_rials": 38000000,
    "total_cost_rials": 38000000,
    "receipt_number": 5001,
    "notes": "Test entry",
}


@pytest.mark.asyncio
async def test_create_grinding_entry(async_client):
    resp = await async_client.post("/api/v1/grinding/", json=GRINDING_MINIMAL)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "registered"
    assert data["date_gregorian"] is not None
    assert data["facility"] == "robat_sefid"
    assert data["input_tonnage_kg"] == 23560


@pytest.mark.asyncio
async def test_create_grinding_without_receipt_number(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/11/10"}
    resp = await async_client.post("/api/v1/grinding/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["receipt_number"] is None


@pytest.mark.asyncio
async def test_create_grinding_duplicate_receipt_number(async_client):
    payload = {**GRINDING_MINIMAL, "receipt_number": 5002, "date_jalali": "1404/11/11"}
    await async_client.post("/api/v1/grinding/", json=payload)
    payload2 = {**GRINDING_MINIMAL, "receipt_number": 5002, "date_jalali": "1404/11/12"}
    resp = await async_client.post("/api/v1/grinding/", json=payload2)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_grinding_entry_by_id(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/11/13"}
    create_resp = await async_client.post("/api/v1/grinding/", json=payload)
    entry_id = create_resp.json()["id"]

    resp = await async_client.get(f"/api/v1/grinding/{entry_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == entry_id
    assert "attachments" in data
    assert isinstance(data["attachments"], list)


@pytest.mark.asyncio
async def test_list_grinding_pagination(async_client):
    for i in range(3):
        payload = {**GRINDING_MINIMAL, "date_jalali": f"1404/09/{i + 1:02d}"}
        await async_client.post("/api/v1/grinding/", json=payload)

    resp = await async_client.get("/api/v1/grinding/?page=1&size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_list_grinding_facility_filter(async_client):
    payload = {**GRINDING_MINIMAL, "facility": "kavian", "date_jalali": "1404/08/01"}
    await async_client.post("/api/v1/grinding/", json=payload)

    resp = await async_client.get("/api/v1/grinding/?facility=kavian")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["facility"] == "kavian"


@pytest.mark.asyncio
async def test_list_grinding_status_filter(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/07/01"}
    await async_client.post("/api/v1/grinding/", json=payload)

    resp = await async_client.get("/api/v1/grinding/?status=registered")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "registered"


@pytest.mark.asyncio
async def test_list_grinding_date_range_filter(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/11/15"}
    await async_client.post("/api/v1/grinding/", json=payload)

    resp = await async_client.get("/api/v1/grinding/?date_from=1404/11/01&date_to=1404/11/30")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_grinding_adds_cost_transitions_to_costed(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/06/01"}
    create_resp = await async_client.post("/api/v1/grinding/", json=payload)
    entry_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "registered"

    update_resp = await async_client.put(
        f"/api/v1/grinding/{entry_id}",
        json={"grinding_cost_rials": 45000000, "total_cost_rials": 45000000},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "costed"


@pytest.mark.asyncio
async def test_update_grinding_total_cost_transitions_to_costed(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/06/02"}
    create_resp = await async_client.post("/api/v1/grinding/", json=payload)
    entry_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/grinding/{entry_id}",
        json={"total_cost_rials": 50000000},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "costed"


@pytest.mark.asyncio
async def test_delete_grinding_registered(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/05/01"}
    create_resp = await async_client.post("/api/v1/grinding/", json=payload)
    entry_id = create_resp.json()["id"]

    resp = await async_client.delete(f"/api/v1/grinding/{entry_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_grinding_costed_fails(async_client):
    payload = {**GRINDING_MINIMAL, "date_jalali": "1404/05/02"}
    create_resp = await async_client.post("/api/v1/grinding/", json=payload)
    entry_id = create_resp.json()["id"]

    # Transition to costed
    await async_client.put(
        f"/api/v1/grinding/{entry_id}",
        json={"grinding_cost_rials": 45000000},
    )

    resp = await async_client.delete(f"/api/v1/grinding/{entry_id}")
    assert resp.status_code == 409
