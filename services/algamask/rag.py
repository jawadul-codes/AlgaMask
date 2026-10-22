"""Version-bound local vector retrieval. Candidate mode requires explicit opt-in."""
import json
import re
import shutil
import tempfile
from pathlib import Path

from .embeddings import EmbeddingProvider

import faiss
import numpy as np

from .dataset import load_dataset
from .publication import canonical, digest, verify
from .search_schemas import EvidenceHit, SearchRequest, SearchResult

TEXT_VERSION = "claim-source-location-matrix-species-v2"


def documents(dataset: Path, development: bool) -> list[dict]:
    snapshot = load_dataset(dataset / "reviewed")
    sources = {s.source_id: s for s in snapshot.records("sources")}
    materials = {m.material_id: m for m in snapshot.records("algae_materials")}
    result = []
    seen = set()
    for chunk in sorted(snapshot.records("evidence_chunks"), key=lambda c: c.chunk_id):
        source = sources[chunk.source_id]
        allowed = {"approved", "verified", "extracted"} if development else {"approved"}
        if chunk.review_status not in allowed or source.review_status not in allowed:
            continue
        if not all((chunk.claim_summary, chunk.source_location, chunk.matrix, chunk.support_class, chunk.evidence_type, chunk.evidence_status, source.title)):
            raise ValueError(f"Incomplete retrieval provenance: {chunk.chunk_id}")
        key = (chunk.source_id, chunk.source_location, chunk.claim_summary)
        if key in seen:
            raise ValueError(f"Duplicate evidence: {chunk.chunk_id}")
        seen.add(key)
        species = sorted({materials[key].species_material for key in chunk.related_material_ids or ()})
        text = (f"{chunk.claim_summary}\nSource: {source.title}\nLocation: {chunk.source_location}"
                f"\nMatrix: {chunk.matrix}\nSpecies: {', '.join(species)}")
        result.append(dict(chunk_id=chunk.chunk_id, source_id=source.source_id, source_title=source.title,
                           source_url=source.url, source_location=chunk.source_location, claim_summary=chunk.claim_summary,
                           chunk_tag=chunk.chunk_tag, matrix=chunk.matrix, species=species, review_status=chunk.review_status,
                           source_review_status=source.review_status, support_class=chunk.support_class,
                           evidence_type=chunk.evidence_type, evidence_status=chunk.evidence_status, text=text))
    return result


def vectors(provider: EmbeddingProvider, texts: list[str]) -> np.ndarray:
    values = np.asarray(provider.embed(texts), dtype="float32")
    if values.shape != (len(texts), provider.identity["dimensions"]) or not np.isfinite(values).all():
        raise ValueError("Embedding provider returned invalid dimensions or nonfinite values")
    norms = np.linalg.norm(values, axis=1)
    if (norms <= 0).any():
        raise ValueError("Embedding provider returned a zero vector")
    values = np.ascontiguousarray(values / norms[:, None], dtype="float32")
    return values


def build_index(dataset: Path, output: Path, version: str, provider: EmbeddingProvider, *, development: bool = False) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", version):
        raise ValueError("Invalid index version")
    release = verify(dataset, require_release=not development)
    docs = documents(dataset, development)
    if not docs:
        raise ValueError("No eligible evidence to index")
    values = vectors(provider, [d["text"] for d in docs])
    index = faiss.IndexFlatIP(values.shape[1])
    index.add(values)
    output.mkdir(parents=True, exist_ok=True)
    destination = output / version
    lock = output / f".{version}.lock"
    with lock.open("x"):
        pass
    temporary = None
    try:
        if destination.exists():
            raise FileExistsError(f"Index version already exists: {version}")
        temporary = Path(tempfile.mkdtemp(prefix=f".{version}-", dir=output))
        (temporary / "documents.json").write_bytes(canonical(docs))
        faiss.write_index(index, str(temporary / "vectors.faiss"))
        hashes = {name: digest((temporary / name).read_bytes()) for name in ("documents.json", "vectors.faiss")}
        manifest = {"format_version": 1, "index_version": version, "dataset_version": release["dataset_version"],
                    "dataset_hash": release["content_hash"], "embedding": provider.identity, "text_version": TEXT_VERSION,
                    "development_only": development, "count": len(docs), "metric": "cosine", "index_type": "IndexFlatIP",
                    "files": hashes, "content_hash": digest(canonical(hashes))}
        (temporary / "manifest.json").write_bytes(canonical(manifest))
        temporary.rename(destination)
        temporary = None
        return destination
    finally:
        if temporary:
            shutil.rmtree(temporary)
        lock.unlink()


class EvidenceSearch:
    def __init__(self, dataset: Path, index_path: Path, provider: EmbeddingProvider, *, development: bool = False, reranker=None):
        release = verify(dataset, require_release=not development)
        manifest = json.loads((index_path / "manifest.json").read_text())
        if manifest["format_version"] != 1 or manifest["text_version"] != TEXT_VERSION or manifest["index_type"] != "IndexFlatIP" or manifest["metric"] != "cosine":
            raise ValueError("Unsupported index configuration")
        if manifest["dataset_hash"] != release["content_hash"] or manifest["dataset_version"] != release["dataset_version"]:
            raise ValueError("Dataset/index version mismatch")
        if manifest["embedding"] != provider.identity:
            raise ValueError("Embedding model/revision mismatch")
        if not development and manifest["development_only"]:
            raise ValueError("Development index cannot serve production retrieval")
        hashes = {name: digest((index_path / name).read_bytes()) for name in ("documents.json", "vectors.faiss")}
        if hashes != manifest["files"] or digest(canonical(hashes)) != manifest["content_hash"]:
            raise ValueError("Index integrity mismatch")
        docs = json.loads((index_path / "documents.json").read_text())
        if docs != documents(dataset, manifest["development_only"]):
            raise ValueError("Index metadata does not match dataset")
        index = faiss.read_index(str(index_path / "vectors.faiss"))
        if not isinstance(index, faiss.IndexFlatIP) or index.d != provider.identity["dimensions"] or index.ntotal != len(docs) or len(docs) != manifest["count"]:
            raise ValueError("Invalid index shape/type")
        values = index.reconstruct_n(0, index.ntotal)
        if not np.isfinite(values).all() or not np.allclose(np.linalg.norm(values, axis=1), 1, atol=1e-5):
            raise ValueError("Invalid normalized index vectors")
        self.documents, self.values, self.manifest, self.provider = docs, values, manifest, provider
        self.reranker = reranker
        # Retain the exact verified dataset for downstream numerical work.
        self.snapshot = load_dataset(dataset / "reviewed")

    def search(self, request: SearchRequest) -> SearchResult:
        eligible = [i for i, d in enumerate(self.documents)
                    if (request.chunk_tag is None or d["chunk_tag"] == request.chunk_tag)
                    and (request.species is None or request.species in d["species"])
                    and (request.matrix is None or d["matrix"].casefold() == request.matrix.casefold())
                    and (not request.source_ids or d["source_id"] in request.source_ids)]
        hits = []
        if eligible:
            # Filter before ranking: exact cosine search over only eligible rows.
            subset = faiss.IndexFlatIP(self.values.shape[1])
            subset.add(np.ascontiguousarray(self.values[eligible]))
            scores, ids = subset.search(vectors(self.provider, [request.query]), len(eligible))
            ranked = sorted(zip(scores[0], ids[0]), key=lambda pair: (-float(pair[0]), self.documents[eligible[pair[1]]]["chunk_id"]))
            ranked = [(score, i) for score, i in ranked if float(score) >= request.min_score]
            rerank_scores = {}
            if ranked and self.reranker:
                passages = [self.documents[eligible[i]]["text"] for _, i in ranked]
                values = self.reranker.score(request.query, passages)
                if len(values) != len(ranked) or not np.isfinite(values).all():
                    raise ValueError("Invalid reranker scores")
                rerank_scores = {int(i): float(value) for (_, i), value in zip(ranked, values)}
                ranked.sort(key=lambda pair: (-rerank_scores[int(pair[1])], -float(pair[0]), self.documents[eligible[pair[1]]]["chunk_id"]))
            for score, i in ranked:
                if float(score) < request.min_score:
                    continue
                data = {k: v for k, v in self.documents[eligible[i]].items() if k != "text"}
                hits.append(EvidenceHit(**data, score=float(np.clip(score, -1, 1)), rerank_score=rerank_scores.get(int(i))))
                if len(hits) == request.top_k:
                    break
        return SearchResult(status="evidence_found" if hits else "insufficient_evidence", hits=hits,
                            dataset_version=self.manifest["dataset_version"], dataset_hash=self.manifest["dataset_hash"],
                            index_version=self.manifest["index_version"], development_only=self.manifest["development_only"],
                            reranker=self.reranker.identity if self.reranker else None)
