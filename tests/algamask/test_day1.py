from fastapi.testclient import TestClient

from algamask.api import app

client = TestClient(app)


def test_day1_preview_reads_local_sprint_files():
    response = client.post("/day1/preview", json={"inclusion_pct": 5, "flavour": "cocoa-spice", "exclusions": []})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "day1_placeholder"
    assert body["product"] == "spirulina protein bar"
    assert body["serving_g"] == 45
    assert body["inclusion_pct"] == 5
    assert body["rows_loaded"]["algae_vocs"] >= 1
    assert body["rows_loaded"]["maskers"] >= 1
    assert body["rows_loaded"]["nutrition"] >= 1
    assert body["rows_loaded"]["sources"] >= 1
    assert body["sensory_risk"]["title"] == "Sensory risk"
    assert body["recommendation"]["title"] == "Recommendation"
    assert "Placeholder" in body["sensory_risk"]["text"]
    assert "Placeholder" in body["recommendation"]["text"]


def test_day1_rejects_percentage_outside_the_control():
    assert client.post("/day1/preview", json={"inclusion_pct": 0}).status_code == 422
