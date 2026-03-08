import pytest


@pytest.mark.asyncio
async def test_create_car(async_client):
    response = await async_client.post(
        "/api/v1/cars/", json={"plate_number": "TEST01"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plate_number"] == "TEST01"


@pytest.mark.asyncio
async def test_create_car_duplicate_plate(async_client):
    await async_client.post("/api/v1/cars/", json={"plate_number": "DUPL01"})
    response = await async_client.post("/api/v1/cars/", json={"plate_number": "DUPL01"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_car_with_driver(async_client):
    driver_resp = await async_client.post(
        "/api/v1/drivers/", json={"full_name": "Car Driver"}
    )
    driver_id = driver_resp.json()["id"]

    car_resp = await async_client.post(
        "/api/v1/cars/", json={"plate_number": "WDRV01", "current_driver_id": driver_id}
    )
    car_id = car_resp.json()["id"]

    response = await async_client.get(f"/api/v1/cars/{car_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["current_driver"] is not None
    assert data["current_driver"]["id"] == driver_id


@pytest.mark.asyncio
async def test_update_car_driver(async_client):
    driver_resp = await async_client.post(
        "/api/v1/drivers/", json={"full_name": "Update Car Driver"}
    )
    driver_id = driver_resp.json()["id"]

    car_resp = await async_client.post(
        "/api/v1/cars/", json={"plate_number": "UPD001"}
    )
    car_id = car_resp.json()["id"]

    response = await async_client.put(
        f"/api/v1/cars/{car_id}", json={"current_driver_id": driver_id}
    )
    assert response.status_code == 200
    assert response.json()["current_driver_id"] == driver_id


@pytest.mark.asyncio
async def test_list_cars_with_driver_filter(async_client):
    driver_resp = await async_client.post(
        "/api/v1/drivers/", json={"full_name": "Filter Driver"}
    )
    driver_id = driver_resp.json()["id"]

    await async_client.post(
        "/api/v1/cars/", json={"plate_number": "FLT001", "current_driver_id": driver_id}
    )
    await async_client.post(
        "/api/v1/cars/", json={"plate_number": "FLT002"}
    )

    response = await async_client.get(f"/api/v1/cars/?driver_id={driver_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["current_driver_id"] == driver_id
