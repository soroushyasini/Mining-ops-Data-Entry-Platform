import pytest


BATCH_1 = {"issue_date_jalali": "1404/11/20"}
BATCH_2 = {"issue_date_jalali": "1404/11/21"}

RESULT_K1 = {"sample_code": "A-1404/11/20-K-1", "gold_ppm": 1.45}
RESULT_L1 = {"sample_code": "A-1404/11/20-L-1", "gold_ppm": 0.28}
RESULT_CR1 = {"sample_code": "A-1404/11/20-CR-1", "gold_ppm": 485.0}
RESULT_RC = {"sample_code": "RC-1404/11/20-1", "gold_ppm": 0.02}
RESULT_MALFORMED = {"sample_code": "BADCODE", "gold_ppm": 0.5}


# ---------------------------------------------------------------------------
# Batch tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_lab_batch(async_client):
    resp = await async_client.post("/api/v1/lab/batches/", json=BATCH_1)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "registered"
    assert data["issue_date_gregorian"] is not None


@pytest.mark.asyncio
async def test_create_batch_duplicate_issue_date(async_client):
    await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/11/22"})
    resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/11/22"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_batch_includes_results(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/11/23"})
    batch_id = create_resp.json()["id"]

    # Add a result
    await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "A-1404/11/23-K-1", "gold_ppm": 1.50},
    )

    resp = await async_client.get(f"/api/v1/lab/batches/{batch_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["results_count"] >= 1


@pytest.mark.asyncio
async def test_list_batches_pagination(async_client):
    for d in ["1404/11/24", "1404/11/25", "1404/11/26"]:
        await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": d})

    resp = await async_client.get("/api/v1/lab/batches/?page=1&size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_list_batches_status_filter(async_client):
    resp = await async_client.get("/api/v1/lab/batches/?status=registered")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "registered"


@pytest.mark.asyncio
async def test_update_batch_transitions_to_invoiced(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/11/27"})
    batch_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/lab/batches/{batch_id}",
        json={"analysis_count": 5, "total_cost_rials": 2500000},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "invoiced"


@pytest.mark.asyncio
async def test_delete_batch_with_results_fails(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/11/28"})
    batch_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "A-1404/11/28-K-1", "gold_ppm": 1.2},
    )

    resp = await async_client.delete(f"/api/v1/lab/batches/{batch_id}")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_delete_empty_batch_succeeds(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/11/29"})
    batch_id = create_resp.json()["id"]

    resp = await async_client.delete(f"/api/v1/lab/batches/{batch_id}")
    assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Result tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_single_result_auto_parsed(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/12/01"})
    batch_id = create_resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "A-1404/12/01-K-1", "gold_ppm": 1.45},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_facility"] == "robat_sefid"
    assert data["sample_type"] == "K"
    assert data["sequence_number"] == 1
    assert data["sample_date_jalali"] == "1404/12/01"


@pytest.mark.asyncio
async def test_bulk_create_lab_results(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/12/02"})
    batch_id = create_resp.json()["id"]

    bulk_payload = {
        "batch_id": batch_id,
        "results": [
            {"sample_code": "A-1404/12/02-K-1", "gold_ppm": 1.45},
            {"sample_code": "A-1404/12/02-L-1", "gold_ppm": 0.28},
            {"sample_code": "A-1404/12/02-CR-1", "gold_ppm": 485.0},
        ],
    }
    resp = await async_client.post("/api/v1/lab/results/bulk", json=bulk_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_malformed_sample_code_saves_with_nulls(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/12/03"})
    batch_id = create_resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "BADCODE", "gold_ppm": 0.5},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["sample_code"] == "BADCODE"
    # Parsed fields should be None
    assert data["source_facility"] is None
    assert data["sample_type"] is None
    assert data["sequence_number"] is None


@pytest.mark.asyncio
async def test_list_results_batch_id_filter(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/12/04"})
    batch_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "A-1404/12/04-K-1", "gold_ppm": 1.1},
    )

    resp = await async_client.get(f"/api/v1/lab/results/?batch_id={batch_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["batch_id"] == batch_id


@pytest.mark.asyncio
async def test_list_results_sample_type_filter(async_client):
    create_resp = await async_client.post("/api/v1/lab/batches/", json={"issue_date_jalali": "1404/12/05"})
    batch_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "A-1404/12/05-K-1", "gold_ppm": 1.2},
    )
    await async_client.post(
        f"/api/v1/lab/results/?batch_id={batch_id}",
        json={"sample_code": "A-1404/12/05-L-1", "gold_ppm": 0.3},
    )

    resp = await async_client.get("/api/v1/lab/results/?sample_type=K")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["sample_type"] == "K"
