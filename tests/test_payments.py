import pytest


# ---------------------------------------------------------------------------
# Helpers to create / transition entities
# ---------------------------------------------------------------------------

TRUCK_PAYLOAD = {
    "date_jalali": "1404/11/12",
    "truck_plate_number": "14978",
    "receipt_number": 19001,
    "tonnage_kg": 27170,
    "destination": "robat_sefid",
    "cost_per_ton_rials": 8700000,
    "driver_name": "محمد احمد آبادی",
}

BUNKER_PAYLOAD = {
    "date_jalali": "1404/11/04",
    "source_facility": "robat_sefid",
    "receipt_number": 19101,
    "tonnage_kg": 23560,
    "truck_plate_number": "14978",
    "driver_name": "محمد احمد آبادی",
}

GRINDING_PAYLOAD = {
    "date_jalali": "1404/11/04",
    "facility": "robat_sefid",
    "input_tonnage_kg": 23560,
}


async def create_costed_truck(async_client, receipt_number: int) -> int:
    payload = {**TRUCK_PAYLOAD, "receipt_number": receipt_number}
    resp = await async_client.post("/api/v1/trucks/", json=payload)
    assert resp.status_code == 201
    truck_id = resp.json()["id"]
    update_resp = await async_client.put(
        f"/api/v1/trucks/{truck_id}",
        json={"total_cost_rials": 236379000},
    )
    assert update_resp.json()["status"] == "costed"
    return truck_id


async def create_costed_bunker(async_client, receipt_number: int) -> int:
    payload = {**BUNKER_PAYLOAD, "receipt_number": receipt_number}
    resp = await async_client.post("/api/v1/bunkers/", json=payload)
    assert resp.status_code == 201
    bunker_id = resp.json()["id"]
    update_resp = await async_client.put(
        f"/api/v1/bunkers/{bunker_id}",
        json={"total_cost_rials": 118000000},
    )
    assert update_resp.json()["status"] == "costed"
    return bunker_id


async def create_costed_grinding(async_client, date_jalali: str) -> int:
    payload = {**GRINDING_PAYLOAD, "date_jalali": date_jalali}
    resp = await async_client.post("/api/v1/grinding/", json=payload)
    assert resp.status_code == 201
    entry_id = resp.json()["id"]
    update_resp = await async_client.put(
        f"/api/v1/grinding/{entry_id}",
        json={"grinding_cost_rials": 45000000, "total_cost_rials": 45000000},
    )
    assert update_resp.json()["status"] == "costed"
    return entry_id


def payment_group_payload(entity_type: str, entity_id: int, amount: int = 100000000) -> dict:
    return {
        "payment_date_jalali": "1404/11/15",
        "payer_name": "شرکت معدن",
        "bank_name": "بانک ملی",
        "total_amount_rials": amount,
        "payments": [
            {"entity_type": entity_type, "entity_id": entity_id, "amount_rials": amount}
        ],
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_payment_group_with_truck(async_client):
    truck_id = await create_costed_truck(async_client, 19001)
    payload = payment_group_payload("truck", truck_id, 236379000)
    resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["payer_name"] == "شرکت معدن"
    assert len(data["payments"]) == 1
    assert data["payments"][0]["entity_type"] == "truck"
    assert data["payments_count"] == 1

    # Verify truck status is now "paid"
    truck_resp = await async_client.get(f"/api/v1/trucks/{truck_id}")
    assert truck_resp.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_create_payment_group_with_grinding(async_client):
    grinding_id = await create_costed_grinding(async_client, "1404/10/01")
    payload = payment_group_payload("grinding", grinding_id, 45000000)
    resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["payments"]) == 1
    assert data["payments"][0]["entity_type"] == "grinding"

    # Verify grinding status is "paid"
    gr_resp = await async_client.get(f"/api/v1/grinding/{grinding_id}")
    assert gr_resp.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_create_payment_group_entity_not_found(async_client):
    payload = payment_group_payload("truck", 999999)
    resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_payment_group_entity_registered_fails(async_client):
    # Create a truck but don't transition to costed
    payload = {**TRUCK_PAYLOAD, "receipt_number": 19002}
    resp = await async_client.post("/api/v1/trucks/", json=payload)
    truck_id = resp.json()["id"]
    assert resp.json()["status"] == "registered"

    pg_payload = payment_group_payload("truck", truck_id)
    resp2 = await async_client.post("/api/v1/payments/groups/", json=pg_payload)
    assert resp2.status_code in (400, 409)


@pytest.mark.asyncio
async def test_create_payment_group_entity_already_paid_fails(async_client):
    truck_id = await create_costed_truck(async_client, 19003)
    payload = payment_group_payload("truck", truck_id)
    resp1 = await async_client.post("/api/v1/payments/groups/", json=payload)
    assert resp1.status_code == 201

    # Try to pay again — should fail
    resp2 = await async_client.post("/api/v1/payments/groups/", json=payment_group_payload("truck", truck_id))
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_get_payment_group_includes_payments(async_client):
    truck_id = await create_costed_truck(async_client, 19004)
    payload = payment_group_payload("truck", truck_id)
    create_resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    group_id = create_resp.json()["id"]

    resp = await async_client.get(f"/api/v1/payments/groups/{group_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == group_id
    assert "payments" in data
    assert len(data["payments"]) == 1
    assert "attachments" in data


@pytest.mark.asyncio
async def test_list_payment_groups_pagination(async_client):
    for i in range(2):
        truck_id = await create_costed_truck(async_client, 19010 + i)
        payload = payment_group_payload("truck", truck_id)
        await async_client.post("/api/v1/payments/groups/", json=payload)

    resp = await async_client.get("/api/v1/payments/groups/?page=1&size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_list_payment_groups_date_filter(async_client):
    truck_id = await create_costed_truck(async_client, 19020)
    payload = payment_group_payload("truck", truck_id)
    await async_client.post("/api/v1/payments/groups/", json=payload)

    resp = await async_client.get("/api/v1/payments/groups/?date_from=1404/11/01&date_to=1404/11/30")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_delete_payment_group_reverts_entity_status(async_client):
    truck_id = await create_costed_truck(async_client, 19030)
    payload = payment_group_payload("truck", truck_id)
    create_resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    group_id = create_resp.json()["id"]

    # Verify truck is paid
    truck_resp = await async_client.get(f"/api/v1/trucks/{truck_id}")
    assert truck_resp.json()["status"] == "paid"

    # Delete group
    del_resp = await async_client.delete(f"/api/v1/payments/groups/{group_id}")
    assert del_resp.status_code == 204

    # Verify truck reverted to costed
    truck_resp2 = await async_client.get(f"/api/v1/trucks/{truck_id}")
    assert truck_resp2.json()["status"] == "costed"


@pytest.mark.asyncio
async def test_list_payment_items_with_group_id_filter(async_client):
    truck_id = await create_costed_truck(async_client, 19040)
    payload = payment_group_payload("truck", truck_id)
    create_resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    group_id = create_resp.json()["id"]

    resp = await async_client.get(f"/api/v1/payments/items/?group_id={group_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["group_id"] == group_id


@pytest.mark.asyncio
async def test_list_payment_items_with_entity_type_filter(async_client):
    bunker_id = await create_costed_bunker(async_client, 19101)
    payload = payment_group_payload("bunker", bunker_id)
    await async_client.post("/api/v1/payments/groups/", json=payload)

    resp = await async_client.get("/api/v1/payments/items/?entity_type=bunker")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["entity_type"] == "bunker"


@pytest.mark.asyncio
async def test_delete_single_payment_item_reverts_entity(async_client):
    truck_id = await create_costed_truck(async_client, 19050)
    payload = payment_group_payload("truck", truck_id)
    create_resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    payment_id = create_resp.json()["payments"][0]["id"]

    # Verify truck is paid
    truck_resp = await async_client.get(f"/api/v1/trucks/{truck_id}")
    assert truck_resp.json()["status"] == "paid"

    # Delete single payment item
    del_resp = await async_client.delete(f"/api/v1/payments/items/{payment_id}")
    assert del_resp.status_code == 204

    # Verify truck reverted
    truck_resp2 = await async_client.get(f"/api/v1/trucks/{truck_id}")
    assert truck_resp2.json()["status"] == "costed"


@pytest.mark.asyncio
async def test_update_payment_group_metadata(async_client):
    truck_id = await create_costed_truck(async_client, 19060)
    payload = payment_group_payload("truck", truck_id)
    create_resp = await async_client.post("/api/v1/payments/groups/", json=payload)
    group_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/payments/groups/{group_id}",
        json={"note": "Updated note", "bank_name": "بانک صادرات"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["note"] == "Updated note"
    assert update_resp.json()["bank_name"] == "بانک صادرات"
