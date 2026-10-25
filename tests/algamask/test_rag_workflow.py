import pytest
from fastapi.testclient import TestClient

from algamask.api import app
from algamask.runtime import RetrievalRuntime, RetrievalUnavailable, Settings
from algamask.search_schemas import EvidenceHit, SearchResult


class SearchDouble:
    manifest = {"dataset_version": "test-candidate", "dataset_hash": "a" * 64,
                "index_version": "test-index", "embedding": {"model": "test"}, "development_only": True}

    def __init__(self, empty_tag=None, fail=False):
        from algamask.dataset import load_dataset
        self.snapshot = load_dataset(Settings().dataset_path / "reviewed")
        self.queries = []
        self.empty_tag, self.fail = empty_tag, fail

    def search(self, query):
        self.queries.append(query)
        if self.fail:
            raise ValueError("test failure")
        hits = [] if query.chunk_tag == self.empty_tag else [EvidenceHit(
            chunk_id=f"{query.chunk_tag}-{query.species or 'general'}", source_id="SRC-TEST",
            source_title="Test source <script>", source_url="https://example.org", source_location="Table 1",
            claim_summary="Test context", chunk_tag=query.chunk_tag or "diagnosis", matrix="related matrix",
            species=[query.species] if query.species else [], review_status="extracted", source_review_status="extracted",
            support_class="indirect", evidence_type="related_food_matrix", evidence_status="literature_derived", score=0.8)]
        return SearchResult(status="evidence_found" if hits else "insufficient_evidence", hits=hits,
                            **{k: self.manifest[k] for k in ("dataset_version", "dataset_hash", "index_version", "development_only")})


@pytest.fixture
def client(monkeypatch):
    runtime = RetrievalRuntime(Settings(mode="development"))
    runtime._search = SearchDouble()
    runtime.status = "ready"
    monkeypatch.setattr(app.state, "retrieval_runtime", runtime)
    return TestClient(app), runtime


@pytest.mark.parametrize("algae,expected", [("spirulina", ["spirulina"]), ("chlorella", ["chlorella"]), ("blend", ["spirulina", "chlorella"])])
def test_real_retrieval_runs_and_trace(client, algae, expected):
    api, runtime = client
    response = api.post("/runs", json={"algae": algae})
    assert response.status_code == 200
    run = response.json()
    assert run["mode"] == "rag_development"
    assert len(run["trace"]) == 6
    assert run["trace"][1]["status"] == "complete"
    assert run["trace"][2]["status"] == "complete"
    assert run["generation"]["method"] == "extractive"
    assert run["generation"]["claims"]
    assert len(run["formulations"]) == 3
    assert run["impact"]["nutrition"]
    assert run["impact"]["dataset_hash"] == run["retrieval"]["dataset_hash"]
    assert [q.species for q in runtime._search.queries if q.chunk_tag == "diagnosis"] == expected * 2
    assert runtime._search.queries[-1].chunk_tag == "intervention"
    assert run["retrieval"]["dataset_hash"] == "a" * 64
    assert all(e["source_id"] == "SRC-TEST" for e in run["evidence"])
    assert all(not i["chunk_ids"] for f in run["formulations"] for i in f["ingredients"])
    assert "chunk_ids" not in run["trace"][2]["output"]
    assert api.get(f"/runs/{run['run_id']}").json() == run
    report = api.get(f"/runs/{run['run_id']}/report").text
    assert "LOCAL RETRIEVAL" in report and "test-index" in report
    assert "&lt;script&gt;" in report and "<script>" not in report
    assert "estimated composition" in report
    assert "NUT-OAT-DRY" in report


def test_unverifiable_targets_block_before_creating_job(client):
    api, _ = client
    response = api.post("/runs", json={"max_sugar_g": 5})
    assert response.status_code == 422
    assert not response.json()['detail']['preflight']['can_run']
    assert not app.state.run_store.history()


@pytest.mark.parametrize("missing", ["diagnosis", "intervention"])
def test_missing_evidence_blocks_downstream(client, missing):
    api, runtime = client
    runtime._search = SearchDouble(empty_tag=missing)
    response = api.post("/runs", json={})
    assert response.status_code == 422
    assert not response.json()['detail']['preflight']['can_run']
    assert not app.state.run_store.history()


def test_api_readiness_search_validation_and_failures(client):
    api, runtime = client
    assert api.get("/rag/ready").json()["development_only"]
    assert api.get("/health").json()["mode"] == "development"
    assert api.post("/rag/search", json={"query": "hexanal", "chunk_tag": "diagnosis"}).status_code == 200
    assert api.post("/rag/search", json={"query": " "}).status_code == 422
    runtime._search = SearchDouble(fail=True)
    before = app.state.run_store.history()
    assert api.post("/runs", json={}).status_code == 503
    after = app.state.run_store.history()
    assert after == before
    assert api.post("/rag/search", json={"query": "hexanal"}).status_code == 503


def test_unavailable_runtime_does_not_fallback(client, monkeypatch):
    api, runtime = client
    def unavailable():
        raise RetrievalUnavailable("Missing cached model")
    monkeypatch.setattr(runtime, "get_search", unavailable)
    for method, url, data in [("get", "/rag/ready", None), ("post", "/runs", {}), ("post", "/rag/search", {"query": "test"})]:
        response = api.request(method, url, json=data)
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "retrieval_unavailable"


def test_mock_search_is_explicitly_disabled(monkeypatch):
    monkeypatch.setattr(app.state, "retrieval_runtime", RetrievalRuntime(Settings(mode="mock")))
    api = TestClient(app)
    assert api.post("/runs", json={}).json()["mode"] == "mock"
    assert api.post("/rag/search", json={"query": "test"}).status_code == 503


def test_generation_failure_is_stored_without_mock_result(client, monkeypatch):
    from algamask.generation import ExtractiveProvider
    class BadProvider(ExtractiveProvider):
        def generate(self, payload):
            return {"claims": []}
    api, runtime = client
    monkeypatch.setattr(runtime, "generation_provider", lambda: BadProvider())
    response = api.post("/runs", json={})
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "generation_failed"
    assert not result["formulations"] and not result["controls"]
    assert result["generation"]["attempts"] == 2
    assert api.get(f"/runs/{result['run_id']}").json() == result
    assert "blocked" in api.get(f"/runs/{result['run_id']}/report").text


def test_exact_chlorella_preflight_margins_and_adjustment(client):
    api, runtime = client
    payload = dict(algae='chlorella', inclusion_pct=3, serving_g=45, flavour='vanilla',
                   min_protein_g=12, max_energy_kcal=426, max_sugar_g=0)
    result = api.post('/runs/preflight', json=payload).json()
    assert not result['can_run']
    assert result['margins']['min_protein_g']['max'] == pytest.approx(5.01867)
    assert result['margins']['max_energy_kcal']['min'] is None
    assert result['margins']['max_sugar_g']['min'] is None
    assert len(result['messages']) == 3
    assert not runtime._search.queries  # Failed arithmetic needs no retrieval.
    assert not app.state.run_store.history()
    assert api.post('/runs', json=payload).status_code == 422
    assert not app.state.run_store.history()
    adjusted = {**payload, 'min_protein_g': 5.01, 'max_energy_kcal': None, 'max_sugar_g': None}
    preview = api.post('/runs/preflight', json=adjusted).json()
    assert preview['can_run'] and preview['candidate_count'] == 1
    run = api.post('/runs', json=adjusted).json()
    assert run['status'] == 'report_ready'
    assert len(run['formulations']) == 1


def test_replay_does_not_repeat_preflight(client):
    api, runtime = client
    headers = {'Idempotency-Key': 'preflight-replay-key-001'}
    first = api.post('/runs', json={'algae': 'spirulina'}, headers=headers)
    assert first.status_code == 200
    runtime._search = SearchDouble(fail=True)
    again = api.post('/runs', json={'algae': 'spirulina'}, headers=headers)
    assert again.json() == first.json()


def test_preflight_exclusion_and_fixed_controls(client):
    api, _ = client
    for payload in ({'exclusions': ['oats']}, {'exclusions': ['milk']},
                    {'experiment': 'spirulina-proof-v1', 'algae': 'spirulina',
                     'inclusion_pct': 2, 'exclusions': ['oats']}):
        result = api.post('/runs/preflight', json=payload).json()
        assert not result['can_run'] and result['messages']
    assert not app.state.run_store.history()


def test_invalid_old_attempt_cannot_be_retried(client):
    from algamask.schemas import RunRequest
    api, _ = client
    store = app.state.run_store
    job, token = store.reserve('old-invalid-submission', RunRequest(max_sugar_g=0), {})
    store.start(job['job_id'], token)
    store.finish(job['job_id'], token, None, 'run_failed')
    response = api.post(f"/jobs/{job['job_id']}/retry", json={'expected_attempt': 1})
    assert response.status_code == 422
    assert store.job(job['job_id'])['attempt'] == 1
    assert store.job(job['job_id'])['state'] == 'failed'


@pytest.mark.parametrize('excluded', ['peanut', 'tree_nut', 'sesame', 'milk', 'soy', 'coconut'])
def test_screenshot_preferences_pass_but_verified_exclusions_block(client, excluded):
    api, _ = client
    payload = dict(algae='spirulina', inclusion_pct=5, serving_g=50, flavour='vanilla',
                   min_protein_g=5, max_energy_kcal=175, exclusions=[excluded])
    strict = api.post('/runs/preflight', json=payload).json()
    assert not strict['can_run']
    assert not strict['margins']
    assert 'required data is missing' not in str(strict)
    preference = {**payload, 'exclusion_mode': 'ingredient_preference'}
    check = api.post('/runs/preflight', json=preference).json()
    assert check['can_run']
    assert check['margins']['min_protein_g']['min'] == pytest.approx(5.61415)
    assert check['margins']['max_energy_kcal']['max'] == pytest.approx(174.695)
    result = api.post('/runs', json=preference).json()
    assert result['status'] == 'report_ready'
    assert result['request']['exclusion_mode'] == 'ingredient_preference'
    assert 'allergy safety are not verified' in str(result['limitations'])
    assert 'Ingredient preferences (allergy safety not verified)' in api.get(f"/runs/{result['run_id']}/report").text


def test_oat_preference_explains_no_remaining_recipes(client):
    api, _ = client
    result = api.post('/runs/preflight', json=dict(exclusions=['oats'],
        exclusion_mode='ingredient_preference', min_protein_g=5, max_energy_kcal=175)).json()
    assert not result['can_run'] and not result['margins']
    assert 'no oat-free recipe' in str(result['messages'])
    assert 'Nutrition targets have not been evaluated' in str(result['messages'])
    assert 'required data is missing' not in str(result)
