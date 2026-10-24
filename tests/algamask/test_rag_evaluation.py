from copy import deepcopy

import pytest

from algamask.rag_evaluation import evaluate_cases
from algamask.search_schemas import EvidenceHit, SearchResult


class Search:
    manifest = {"dataset_hash": "a" * 64, "index_version": "test", "development_only": True}

    def __init__(self, hits):
        self.hits = hits

    def search(self, request):
        return SearchResult(**self.manifest, dataset_version="test",
                            status="evidence_found" if self.hits else "insufficient_evidence", hits=self.hits)


def hit():
    return EvidenceHit(chunk_id="C1", source_id="S1", source_title="Study", source_url=None,
        source_location="Table 1", claim_summary="Related food only; not proof for this bar.",
        chunk_tag="intervention", matrix="cookies", species=["spirulina"], review_status="extracted",
        source_review_status="extracted", support_class="indirect", evidence_type="related_food_matrix",
        evidence_status="literature_derived", score=.7)


def suite():
    return {"version": "test", "review_status": "draft_engineering", "cases": [
        {"id": "one", "kind": "qualified_context", "request": {"query": "test", "species": "spirulina"},
         "expected_chunk": "C1", "required_text": "not proof", "max_rank": 1}]}


def test_valid_qualified_context():
    result = evaluate_cases(Search([hit()]), suite())
    assert result["passed"] == 1
    assert result["results"][0]["generation_status"] == "complete"


@pytest.mark.parametrize("mutation,error", [
    ("wrong_species", "metadata_filter_violation"),
    ("missing_note", "expected_note_missing_or_low_rank"),
    ("lost_caveat", "required_qualification_missing"),
    ("missing_source", "incomplete_provenance"),
])
def test_evaluator_detects_failures(mutation, error):
    row = hit()
    if mutation == "wrong_species": row.species = ["chlorella"]
    if mutation == "missing_note": row.chunk_id = "C2"
    if mutation == "lost_caveat": row.claim_summary = "This bar is proven effective."
    if mutation == "missing_source": row.source_location = ""
    result = evaluate_cases(Search([row]), suite())
    assert result["passed"] == 0
    assert error in result["results"][0]["errors"]


def test_no_context_is_not_replaced_by_fake_empty_context():
    cases = suite()
    cases["cases"][0]["kind"] = "no_context"
    failed = evaluate_cases(Search([hit()]), cases)
    assert failed["passed"] == 0
    assert failed["results"][0]["generation_status"] == "complete"
    passed = evaluate_cases(Search([]), cases)
    assert passed["passed"] == 1
    assert passed["results"][0]["generation_status"] == "blocked"


def test_suite_requires_unique_nonempty_cases():
    cases = suite()
    cases["cases"].append(deepcopy(cases["cases"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        evaluate_cases(Search([]), cases)
    cases["cases"] = []
    with pytest.raises(ValueError, match="empty"):
        evaluate_cases(Search([]), cases)
