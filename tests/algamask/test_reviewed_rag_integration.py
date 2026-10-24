"""Opt-in checks against the real cached model and corrected rc.4/dev.3 pair.

Run with ALGAMASK_TEST_REVIEWED_RAG=1; no model downloads or live database writes.
"""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from algamask.api import app
from algamask.runtime import RetrievalRuntime, Settings
from algamask.search_schemas import SearchRequest

pytestmark = pytest.mark.skipif(
    os.environ.get("ALGAMASK_TEST_REVIEWED_RAG") != "1",
    reason="Opt in to the real offline rc.4/dev.3 integration checks",
)
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def reviewed_runtime():
    runtime = RetrievalRuntime(Settings(
        mode="development",
        dataset_path=ROOT / "data/candidates/0.1.0-rc.4",
        index_path=ROOT / "indexes/reviewed_evidence/0.1.0-dev.3",
    ))
    runtime.get_search()
    return runtime


@pytest.mark.parametrize("query,source,chunk,qualification", [
    ("cinnamon powder spirulina cookies flakes noodles", "SRC-JFS-2018-35546",
     "CHK-CIN-OTHER-FOODS", "does not validate 1% cinnamon"),
    ("hexanal green grassy relative area", "SRC-FOODS-2024-1257",
     "CHK-SPI-HEXANAL", "not measured sensory responses"),
    ("geosmin methylisoborneol FD factor", "SRC-IJMS-2025-6767",
     "CHK-GEOSMIN-GAP", "does not establish its absence"),
    ("recipe quantities 100 g percentage denominator", "SRC-ITEPA-2024",
     "CHK-BOUND-LIMIT", "cannot be treated as confirmed"),
])
def test_corrected_claims_retrievable(reviewed_runtime, query, source, chunk, qualification):
    result = reviewed_runtime.get_search().search(SearchRequest(
        query=query, species="spirulina", source_ids=[source], top_k=5))
    hit = next(hit for hit in result.hits if hit.chunk_id == chunk)
    assert qualification in hit.claim_summary
    assert hit.review_status == "extracted"
    assert result.development_only
    assert result.dataset_version == "0.1.0-rc.4"
    assert result.index_version == "0.1.0-dev.3"


@pytest.mark.parametrize("algae", ["spirulina", "chlorella", "blend"])
def test_real_api_generation_reports_and_persistence(reviewed_runtime, monkeypatch, algae):
    monkeypatch.setattr(app.state, "retrieval_runtime", reviewed_runtime)
    client = TestClient(app)
    assert client.get("/rag/ready").json()["index_version"] == "0.1.0-dev.3"
    response = client.post("/runs", json={"algae": algae, "inclusion_pct": 2})
    assert response.status_code == 200
    run = response.json()
    assert run["status"] == "report_ready"
    assert len(run["trace"]) == 6
    assert run["mode"] == "rag_development"
    assert run["generation"]["method"] == "extractive"
    assert run["generation"]["claims"]
    evidence = {row["chunk_id"]: row for row in run["evidence"]}
    for claim in run["generation"]["claims"]:
        row = evidence[claim["citation"]["chunk_id"]]
        assert claim["text"] == row["claim_summary"]
        assert claim["citation"]["source_id"] == row["source_id"]
    assert client.get(f"/runs/{run['run_id']}").json() == run
    report = client.get(f"/runs/{run['run_id']}/report")
    assert report.status_code == 200
    for text in ["0.1.0-rc.4", "0.1.0-dev.3", "Development data",
                 "not production eligible", "Sensory change: unknown", "NUT-OAT-DRY"]:
        assert text in report.text
    assert run["impact"]["dataset_hash"] == run["retrieval"]["dataset_hash"]


def test_corrected_pair_rejects_production_and_old_index(reviewed_runtime):
    from algamask.rag import EvidenceSearch
    from algamask.embeddings import LocalSentenceEmbeddings
    provider = LocalSentenceEmbeddings()
    settings = reviewed_runtime.settings
    with pytest.raises(ValueError, match="approved runtime"):
        EvidenceSearch(settings.dataset_path, settings.index_path, provider)
    with pytest.raises(ValueError, match="version mismatch"):
        EvidenceSearch(settings.dataset_path, ROOT / "indexes/reviewed_evidence/0.1.0-dev.2",
                       provider, development=True)


def test_unknown_source_returns_no_evidence(reviewed_runtime):
    result = reviewed_runtime.get_search().search(SearchRequest(
        query="spirulina", source_ids=["DOES-NOT-EXIST"]))
    assert result.status == "insufficient_evidence"
    assert not result.hits


def test_fixed_experiment_api_report_and_history(reviewed_runtime, monkeypatch):
    monkeypatch.setattr(app.state, "retrieval_runtime", reviewed_runtime)
    client = TestClient(app)
    payload = dict(experiment="spirulina-proof-v1", algae="spirulina", inclusion_pct=2,
                   serving_g=45, flavour="cocoa-spice")
    response = client.post('/runs', json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result['status'] == 'report_ready'
    assert [f['id'] for f in result['controls'] + result['formulations']] == ['B0', 'A0', 'A1']
    assert result['impact']['screening']['search_version'] == 'spirulina-proof-v1'
    assert client.get(f"/runs/{result['run_id']}").json() == result
    report = client.get(f"/runs/{result['run_id']}/report").text
    assert 'Experiment: spirulina-proof-v1' in report
    assert 'not verified finished serving' in report
    assert 'Not approved for physical testing' in report
    assert client.post('/runs', json={**payload, 'inclusion_pct': 5}).status_code == 422
    blocked = client.post('/runs', json={**payload, 'max_sugar_g': 5}).json()
    assert blocked['status'] == 'insufficient_data'
    assert not blocked['controls'] and not blocked['formulations']
