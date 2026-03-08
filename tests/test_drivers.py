import pytest


@pytest.mark.asyncio
async def test_create_driver(async_client):
    response = await async_client.post(
        "/api/v1/drivers/",
        json={"full_name": "Test Driver", "iban": "IR290190000000102529858002", "phone": "9155188319"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Test Driver"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_driver_missing_required(async_client):
    response = await async_client.post("/api/v1/drivers/", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_driver(async_client):
    create_resp = await async_client.post(
        "/api/v1/drivers/", json={"full_name": "Get Driver Test"}
    )
    driver_id = create_resp.json()["id"]

    response = await async_client.get(f"/api/v1/drivers/{driver_id}")
    assert response.status_code == 200
    assert response.json()["id"] == driver_id


@pytest.mark.asyncio
async def test_get_driver_not_found(async_client):
    response = await async_client.get("/api/v1/drivers/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_drivers_pagination(async_client):
    # Create a couple drivers
    for i in range(3):
        await async_client.post("/api/v1/drivers/", json={"full_name": f"Paginate Driver {i}"})

    response = await async_client.get("/api/v1/drivers/?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_update_driver(async_client):
    create_resp = await async_client.post(
        "/api/v1/drivers/", json={"full_name": "Old Name"}
    )
    driver_id = create_resp.json()["id"]

    response = await async_client.put(
        f"/api/v1/drivers/{driver_id}", json={"full_name": "New Name"}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_driver(async_client):
    create_resp = await async_client.post(
        "/api/v1/drivers/", json={"full_name": "To Delete"}
    )
    driver_id = create_resp.json()["id"]

    response = await async_client.delete(f"/api/v1/drivers/{driver_id}")
    assert response.status_code == 204

    get_resp = await async_client.get(f"/api/v1/drivers/{driver_id}")
    assert get_resp.status_code == 404
