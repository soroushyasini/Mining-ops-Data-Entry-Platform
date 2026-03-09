import pytest


BUNKER_MINIMAL = {
    "date_jalali": "1404/11/04",
    "source_facility": "robat_sefid",
    "receipt_number": 8001,
    "tonnage_kg": 23560,
    "truck_plate_number": "14978",
    "driver_name": "محمد احمد آبادی",
}


@pytest.mark.asyncio
async def test_create_bunker(async_client):
    resp = await async_client.post("/api/v1/bunkers/", json=BUNKER_MINIMAL)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "registered"
    assert data["date_gregorian"] is not None
    assert data["receipt_number"] == 8001


@pytest.mark.asyncio
async def test_create_bunker_duplicate_receipt_number(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8002}
    await async_client.post("/api/v1/bunkers/", json=payload)
    resp = await async_client.post("/api/v1/bunkers/", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_bunker_by_id(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8003}
    create_resp = await async_client.post("/api/v1/bunkers/", json=payload)
    bunker_id = create_resp.json()["id"]

    resp = await async_client.get(f"/api/v1/bunkers/{bunker_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == bunker_id
    assert "attachments" in data
    assert isinstance(data["attachments"], list)


@pytest.mark.asyncio
async def test_list_bunkers_pagination(async_client):
    for i in range(3):
        payload = {**BUNKER_MINIMAL, "receipt_number": 8100 + i}
        await async_client.post("/api/v1/bunkers/", json=payload)

    resp = await async_client.get("/api/v1/bunkers/?page=1&size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_list_bunkers_status_filter(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8200}
    await async_client.post("/api/v1/bunkers/", json=payload)

    resp = await async_client.get("/api/v1/bunkers/?status=registered")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "registered"


@pytest.mark.asyncio
async def test_list_bunkers_source_facility_filter(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8201}
    await async_client.post("/api/v1/bunkers/", json=payload)

    resp = await async_client.get("/api/v1/bunkers/?source_facility=robat_sefid")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["source_facility"] == "robat_sefid"


@pytest.mark.asyncio
async def test_list_bunkers_date_range_filter(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8202}
    await async_client.post("/api/v1/bunkers/", json=payload)

    resp = await async_client.get("/api/v1/bunkers/?date_from=1404/11/01&date_to=1404/11/30")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_bunker_adds_cost_transitions_to_costed(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8300}
    create_resp = await async_client.post("/api/v1/bunkers/", json=payload)
    bunker_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/bunkers/{bunker_id}",
        json={"cost_per_ton_rials": 5000000, "total_cost_rials": 117800000},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "costed"


@pytest.mark.asyncio
async def test_delete_bunker_registered(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8400}
    create_resp = await async_client.post("/api/v1/bunkers/", json=payload)
    bunker_id = create_resp.json()["id"]

    resp = await async_client.delete(f"/api/v1/bunkers/{bunker_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_bunker_costed_fails(async_client):
    payload = {**BUNKER_MINIMAL, "receipt_number": 8401}
    create_resp = await async_client.post("/api/v1/bunkers/", json=payload)
    bunker_id = create_resp.json()["id"]

    # Transition to costed by adding cost fields
    await async_client.put(
        f"/api/v1/bunkers/{bunker_id}",
        json={"cost_per_ton_rials": 5000000},
    )

    resp = await async_client.delete(f"/api/v1/bunkers/{bunker_id}")
    assert resp.status_code == 409
