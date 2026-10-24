"""Engineering regression measurements; not a scientific approval mechanism."""
from .generation import generate_explanation, critique_explanation
from .search_schemas import SearchRequest


def evaluate_cases(search, suite):
    if not suite.get("cases"):
        raise ValueError("Evaluation suite must not be empty")
    ids = [case["id"] for case in suite["cases"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate evaluation IDs")
    results = []
    for case in suite["cases"]:
        if case["kind"] not in {"qualified_context", "no_context"}:
            raise ValueError("Unknown evaluation kind")
        request = SearchRequest(**case["request"])
        response = search.search(request)
        rows = [hit.model_dump() for hit in response.hits]
        errors = []
        for hit in response.hits:
            if ((request.species and request.species not in hit.species)
                or (request.matrix and request.matrix.casefold() != hit.matrix.casefold())
                or (request.chunk_tag and request.chunk_tag != hit.chunk_tag)
                or (request.source_ids and hit.source_id not in request.source_ids)):
                errors.append("metadata_filter_violation")
            if not all((hit.source_id, hit.source_title, hit.source_location, hit.review_status)):
                errors.append("incomplete_provenance")
        rank = next((i for i, hit in enumerate(response.hits, 1)
                     if hit.chunk_id == case.get("expected_chunk")), None)
        if case["kind"] == "no_context":
            if response.hits or response.status != "insufficient_evidence":
                errors.append("unexpected_context")
            generation = generate_explanation(case["request"], rows, response.dataset_hash)
            if generation.status != "blocked" or generation.claims:
                errors.append("empty_context_did_not_block")
        else:
            if rank is None or rank > case["max_rank"]:
                errors.append("expected_note_missing_or_low_rank")
            if rank and case["required_text"] not in response.hits[rank - 1].claim_summary:
                errors.append("required_qualification_missing")
            generation = generate_explanation(case["request"], rows, response.dataset_hash)
            if critique_explanation(generation, rows, response.dataset_hash):
                errors.append("generation_grounding_failed")
            if not any(c.citation.chunk_id == case["expected_chunk"] for c in generation.claims):
                errors.append("expected_note_omitted_from_explanation")
        results.append({"id": case["id"], "kind": case["kind"], "passed": not errors,
                        "errors": errors, "expected_rank": rank, "request": request.model_dump(),
                        "hits": rows, "generation_status": generation.status})
    return {"suite_version": suite["version"], "review_status": suite["review_status"],
            "dataset_hash": search.manifest["dataset_hash"],
            "index_version": search.manifest["index_version"],
            "development_only": search.manifest["development_only"],
            "case_count": len(results), "passed": sum(r["passed"] for r in results),
            "results": results,
            "limitation": "Engineering regression suite, not independently reviewed or held-out. Context retrieval is not proof of efficacy or safety."}
