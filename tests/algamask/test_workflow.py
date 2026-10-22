import pytest
from fastapi.testclient import TestClient

from algamask.api import app
from algamask.nutrition import calculate_nutrient
from algamask.retrieval import approved_chunks

client = TestClient(app)


@pytest.mark.parametrize("algae", ["spirulina", "chlorella", "blend"])
@pytest.mark.parametrize("mass,inclusion", [(40, 1), (45, 5), (50, 15)])
def test_complete_slice(algae, mass, inclusion):
    response = client.post("/runs", json={"algae": algae, "serving_g": mass, "inclusion_pct": inclusion})
    assert response.status_code == 200
    run = response.json()
    assert [step["agent"] for step in run["trace"]] == ["Profile", "Retrieval", "Chemistry", "Recipe", "Critic", "Impact"]
    assert run["status"] == "report_ready"
    assert len(run["formulations"]) == 3
    assert len({f["name"] for f in run["formulations"]}) == 3
    for formula in run["formulations"] + run["controls"]:
        assert sum(item["grams"] for item in formula["ingredients"]) == pytest.approx(mass)
        algae_mass = sum(i["grams"] for i in formula["ingredients"] if i["role"] == "algae")
        assert algae_mass == pytest.approx(0 if formula["id"] == "B0" else mass * inclusion / 100)
    assert run["impact"]["nutrition_change_pct"] is None
    assert run["impact"]["sensory_change_pct"] is None
    assert client.get(f"/runs/{run['run_id']}").json() == run
    report = client.get(f"/runs/{run['run_id']}/report")
    assert report.status_code == 200
    assert "MOCK" in report.text and "unknown" in report.text


def test_excluded_matrix_rejects_all_formulas():
    run = client.post("/runs", json={"exclusions": ["oats"]}).json()
    assert run["status"] == "insufficient_data"
    assert run["formulations"] == []
    assert run["controls"] == []
    assert run["trace"][4]["state"] == "REJECTED"


def test_mock_does_not_silently_ignore_nutrition_targets():
    run = client.post("/runs", json={"min_protein_g": 5}).json()
    assert run["status"] == "insufficient_data"
    assert not run["formulations"]


@pytest.mark.parametrize("payload", [{"inclusion_pct": 0}, {"inclusion_pct": 16}, {"serving_g": 0}, {"algae": "unknown"}, {"exclusions": ["unknown"]}])
def test_invalid_requests(payload):
    assert client.post("/runs", json=payload).status_code == 422


def test_provenance_gate_and_unknown_nutrients():
    assert approved_chunks([{"review_status": "draft", "source_id": "x"}, {"review_status": "approved"}]) == []
    assert calculate_nutrient([(50, 20), (20, None)]) is None
    assert calculate_nutrient([(50, 20), (20, 10)]) == 12
    assert client.get("/runs/missing").status_code == 404
