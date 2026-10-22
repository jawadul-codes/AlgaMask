import pytest
from fastapi.testclient import TestClient

from algamask.api import app, runs
from algamask.runtime import RetrievalRuntime, RetrievalUnavailable, Settings
from algamask.search_schemas import EvidenceHit, SearchResult


class SearchDouble:
    manifest = {"dataset_version": "test-candidate", "dataset_hash": "a" * 64,
                "index_version": "test-index", "embedding": {"model": "test"}, "development_only": True}

    def __init__(self, empty_tag=None, fail=False):
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
    assert run["trace"][2]["status"] == "mock"
    assert [q.species for q in runtime._search.queries if q.chunk_tag == "diagnosis"] == expected
    assert runtime._search.queries[-1].chunk_tag == "intervention"
    assert run["retrieval"]["dataset_hash"] == "a" * 64
    assert all(e["source_id"] == "SRC-TEST" for e in run["evidence"])
    assert all(not i["chunk_ids"] for f in run["formulations"] for i in f["ingredients"])
    assert "chunk_ids" not in run["trace"][2]["output"]
    assert api.get(f"/runs/{run['run_id']}").json() == run
    report = api.get(f"/runs/{run['run_id']}/report").text
    assert "LOCAL RETRIEVAL" in report and "test-index" in report
    assert "&lt;script&gt;" in report and "<script>" not in report


@pytest.mark.parametrize("missing", ["diagnosis", "intervention"])
def test_missing_evidence_blocks_downstream(client, missing):
    api, runtime = client
    runtime._search = SearchDouble(empty_tag=missing)
    result = api.post("/runs", json={}).json()
    assert result["status"] == "insufficient_data"
    assert not result["formulations"] and not result["controls"]
    assert all(s["status"] == "blocked" for s in result["trace"][1:])


def test_api_readiness_search_validation_and_failures(client):
    api, runtime = client
    assert api.get("/rag/ready").json()["development_only"]
    assert api.get("/health").json()["mode"] == "development"
    assert api.post("/rag/search", json={"query": "hexanal", "chunk_tag": "diagnosis"}).status_code == 200
    assert api.post("/rag/search", json={"query": " "}).status_code == 422
    runtime._search = SearchDouble(fail=True)
    before = set(runs)
    assert api.post("/runs", json={}).status_code == 503
    assert set(runs) == before
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
