import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

pytest.importorskip("faiss", reason="Install the rag extra to test vector retrieval")
pytest.importorskip("numpy")

from algamask.rag import EvidenceSearch, SearchRequest, build_index, vectors

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "data/candidates/0.1.0-rc.1"


class TestEmbeddings:
    """Deterministic test vectors; never used by the application or quality evaluation."""
    identity = {"model": "test-only", "revision": "1", "dimensions": 8}

    def embed(self, texts):
        return [[(v - 127) / 128 for v in hashlib.sha256(t.encode()).digest()[:8]] for t in texts]


@pytest.fixture
def built(tmp_path):
    provider = TestEmbeddings()
    path = build_index(DATASET, tmp_path, "test-1", provider, development=True)
    return path, provider


def test_metadata_filters_and_citations(built):
    path, provider = built
    search = EvidenceSearch(DATASET, path, provider, development=True)
    response = search.search(SearchRequest(query="chlorella hexanal", chunk_tag="diagnosis", species="chlorella",
                                          source_ids=["SRC-BJDV-2021-662"], min_score=-1))
    assert response.development_only
    assert response.hits
    for hit in response.hits:
        assert hit.source_id == "SRC-BJDV-2021-662"
        assert hit.chunk_tag == "diagnosis"
        assert "chlorella" in hit.species
        assert hit.source_location and hit.source_title
        assert hit.review_status == "extracted"
        assert -1 <= hit.score <= 1
    matrix = response.hits[0].matrix
    filtered = search.search(SearchRequest(query="hexanal", matrix=matrix, min_score=-1))
    assert all(h.matrix == matrix for h in filtered.hits)


def test_empty_filter_does_not_embed_query(built, monkeypatch):
    path, provider = built
    search = EvidenceSearch(DATASET, path, provider, development=True)
    def unexpected(texts):
        pytest.fail("No eligible documents should not call the embedding provider")
    monkeypatch.setattr(provider, "embed", unexpected)
    response = search.search(SearchRequest(query="something", source_ids=["unknown-source"]))
    assert response.status == "insufficient_evidence" and not response.hits


def test_threshold_and_exact_match(built):
    path, provider = built
    search = EvidenceSearch(DATASET, path, provider, development=True)
    document = search.documents[0]
    response = search.search(SearchRequest(query=document["text"], min_score=0.99, top_k=1))
    assert response.hits[0].chunk_id == document["chunk_id"]
    assert response.hits[0].score == pytest.approx(1, abs=1e-5)


def test_candidate_and_model_mismatch_rejected(built):
    path, provider = built
    with pytest.raises(ValueError, match="approved runtime"):
        EvidenceSearch(DATASET, path, provider)
    provider.identity = {**provider.identity, "revision": "different"}
    with pytest.raises(ValueError, match="model/revision"):
        EvidenceSearch(DATASET, path, provider, development=True)


def test_build_refuses_candidate_without_opt_in(tmp_path):
    with pytest.raises(ValueError, match="approved runtime"):
        build_index(DATASET, tmp_path, "test", TestEmbeddings())


def test_tampering_and_overwrite(built):
    path, provider = built
    with pytest.raises(FileExistsError):
        build_index(DATASET, path.parent, path.name, provider, development=True)
    target = path / "documents.json"
    target.write_bytes(target.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="integrity"):
        EvidenceSearch(DATASET, path, provider, development=True)


def test_dataset_hash_mismatch(built):
    path, provider = built
    target = path / "manifest.json"
    manifest = json.loads(target.read_text())
    manifest["dataset_hash"] = "wrong"
    target.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="version mismatch"):
        EvidenceSearch(DATASET, path, provider, development=True)


def test_reranking_keeps_cosine_and_provenance_separate(built):
    path, provider = built
    class Reranker:
        identity = {"model": "test", "revision": "1"}
        def score(self, query, passages):
            return [10.0 if "FD 2048" in p else -10.0 for p in passages]
    search = EvidenceSearch(DATASET, path, provider, development=True, reranker=Reranker())
    response = search.search(SearchRequest(query="FD factors", chunk_tag="diagnosis", min_score=-1))
    assert response.hits[0].chunk_id == "CHK-AEDA-POTENT"
    assert response.hits[0].rerank_score == 10
    assert -1 <= response.hits[0].score <= 1
    assert response.hits[0].review_status == "extracted"
    assert response.reranker == Reranker.identity


def test_invalid_reranker_output_is_rejected(built):
    path, provider = built
    class BrokenReranker:
        identity = {"model": "test", "revision": "1"}
        def score(self, query, passages):
            return [float("nan")] * len(passages)
    search = EvidenceSearch(DATASET, path, provider, development=True, reranker=BrokenReranker())
    with pytest.raises(ValueError, match="reranker"):
        search.search(SearchRequest(query="test", min_score=-1))


@pytest.mark.parametrize("output", [[[0] * 8], [[float("nan")] * 8], [[1, 2]], []])
def test_invalid_vectors(output, monkeypatch):
    provider = TestEmbeddings()
    monkeypatch.setattr(provider, "embed", lambda texts: output)
    with pytest.raises(ValueError):
        vectors(provider, ["test"])


@pytest.mark.parametrize("options", [{"query": " "}, {"query": "x", "top_k": 0}, {"query": "x", "min_score": float("nan")}, {"query": "x", "unknown_filter": "value"}])
def test_invalid_search_requests(options):
    with pytest.raises(ValidationError):
        SearchRequest(**options)
