from fastapi.testclient import TestClient

from algamask.api import app

client = TestClient(app)


def test_day1_route_returns_structured_mock_workflow():
    response = client.post("/day1/preview", json={"algae": "spirulina", "serving_g": 45, "inclusion_pct": 5, "flavour": "cocoa-spice", "exclusions": []})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "mock"
    assert body["request"]["algae"] == "spirulina"
    assert body["request"]["serving_g"] == 45
    assert body["request"]["inclusion_pct"] == 5
    assert [step["agent"] for step in body["trace"]] == ["Profile", "Retrieval", "Chemistry", "Recipe", "Critic", "Impact"]
    assert body["sensory_map"]
    assert body["formulations"]
    assert body["controls"]


def test_day1_rejects_percentage_outside_the_control():
    assert client.post("/day1/preview", json={"inclusion_pct": 0}).status_code == 422


def test_day1_preview_result_is_retrievable_and_has_structured_agent_outputs():
    response = client.post("/day1/preview", json={"algae": "spirulina", "inclusion_pct": 2})
    assert response.status_code == 200
    run = response.json()
    assert client.get(f"/runs/{run['run_id']}").json() == run
    assert all(set(step) >= {"agent", "state", "summary", "output", "status"} for step in run["trace"])
