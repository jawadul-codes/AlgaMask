"""Search contracts, importable without the optional native retrieval libraries."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    chunk_tag: Literal["diagnosis", "intervention"] | None = None
    species: Literal["spirulina", "chlorella"] | None = None
    matrix: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    min_score: float = Field(default=0.2, ge=-1, le=1)


class EvidenceHit(BaseModel):
    chunk_id: str
    source_id: str
    source_title: str
    source_url: str | None
    source_location: str
    claim_summary: str
    chunk_tag: str
    matrix: str
    species: list[str]
    review_status: str
    source_review_status: str
    support_class: str
    evidence_type: str
    evidence_status: str
    score: float
    rerank_score: float | None = None


class SearchResult(BaseModel):
    status: Literal["evidence_found", "insufficient_evidence"]
    dataset_version: str
    dataset_hash: str
    index_version: str
    development_only: bool
    reranker: dict[str, str] | None = None
    hits: list[EvidenceHit]
