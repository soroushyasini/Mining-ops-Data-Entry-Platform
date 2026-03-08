import pytest


TRUCK_MINIMAL = {
    "date_jalali": "1404/11/12",
    "truck_plate_number": "14978",
    "receipt_number": 9001,
    "tonnage_kg": 27000,
    "destination": "robat_sefid",
    "driver_name": "Test Driver",
}

TRUCK_WITH_COST = {
    **TRUCK_MINIMAL,
    "receipt_number": 9002,
    "cost_per_ton_rials": 8700000,
    "total_cost_rials": 234900000,
}


@pytest.mark.asyncio
async def test_create_truck_minimal(async_client):
    resp = await async_client.post("/api/v1/trucks/", json=TRUCK_MINIMAL)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "registered"
    assert data["date_gregorian"] is not None


@pytest.mark.asyncio
async def test_create_truck_with_cost(async_client):
    resp = await async_client.post("/api/v1/trucks/", json=TRUCK_WITH_COST)
    assert resp.status_code == 201
    data = resp.json()
    # Status stays registered unless explicitly set
    assert data["status"] == "registered"
    assert data["cost_per_ton_rials"] == 8700000


@pytest.mark.asyncio
async def test_get_truck_includes_attachments(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9003}
    create_resp = await async_client.post("/api/v1/trucks/", json=payload)
    truck_id = create_resp.json()["id"]

    resp = await async_client.get(f"/api/v1/trucks/{truck_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "attachments" in data
    assert isinstance(data["attachments"], list)


@pytest.mark.asyncio
async def test_list_trucks_status_filter(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9004}
    await async_client.post("/api/v1/trucks/", json=payload)

    resp = await async_client.get("/api/v1/trucks/?status=registered")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "registered"


@pytest.mark.asyncio
async def test_list_trucks_destination_filter(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9005}
    await async_client.post("/api/v1/trucks/", json=payload)

    resp = await async_client.get("/api/v1/trucks/?destination=robat_sefid")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["destination"] == "robat_sefid"


@pytest.mark.asyncio
async def test_list_trucks_date_range_filter(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9006}
    await async_client.post("/api/v1/trucks/", json=payload)

    resp = await async_client.get(
        "/api/v1/trucks/?date_from=1404/11/01&date_to=1404/11/30"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_truck_adds_cost_transitions_to_costed(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9007}
    create_resp = await async_client.post("/api/v1/trucks/", json=payload)
    truck_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/trucks/{truck_id}",
        json={"cost_per_ton_rials": 8700000, "total_cost_rials": 234900000},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "costed"


@pytest.mark.asyncio
async def test_delete_truck_registered(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9008}
    create_resp = await async_client.post("/api/v1/trucks/", json=payload)
    truck_id = create_resp.json()["id"]

    resp = await async_client.delete(f"/api/v1/trucks/{truck_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_truck_costed_fails(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9009}
    create_resp = await async_client.post("/api/v1/trucks/", json=payload)
    truck_id = create_resp.json()["id"]

    # Transition to costed
    await async_client.put(
        f"/api/v1/trucks/{truck_id}",
        json={"cost_per_ton_rials": 8700000},
    )

    resp = await async_client.delete(f"/api/v1/trucks/{truck_id}")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_patch_truck_status(async_client):
    payload = {**TRUCK_MINIMAL, "receipt_number": 9010, "cost_per_ton_rials": 8700000}
    create_resp = await async_client.post("/api/v1/trucks/", json=payload)
    truck_id = create_resp.json()["id"]

    # First manually set to costed via update so cost fields are set
    await async_client.put(
        f"/api/v1/trucks/{truck_id}",
        json={"cost_per_ton_rials": 8700000, "total_cost_rials": 234900000},
    )

    # Now patch to paid
    resp = await async_client.patch(
        f"/api/v1/trucks/{truck_id}/status", json={"status": "paid"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_pagination(async_client):
    for i in range(3):
        payload = {**TRUCK_MINIMAL, "receipt_number": 9100 + i}
        await async_client.post("/api/v1/trucks/", json=payload)

    resp = await async_client.get("/api/v1/trucks/?page=1&size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "pages" in data
    assert len(data["items"]) <= 2
