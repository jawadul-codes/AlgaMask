from ..retrieval import retrieve_mock
from ..search_schemas import SearchRequest


def run(request, search=None):
    if search is None:
        return retrieve_mock(), []
    species = ["spirulina", "chlorella"] if request.algae.value == "blend" else [request.algae.value]
    queries = [SearchRequest(query=f"What volatile compounds and sensory off-notes are reported for {name}?",
                             chunk_tag="diagnosis", species=name, top_k=3) for name in species]
    # Related-food interventions need to remain discoverable; exact protein-bar
    # filtering would hide the current corpus's explicitly qualified related evidence.
    queries.append(SearchRequest(query=f"Evidence and limitations for {request.flavour} masking {request.algae.value} in a protein bar at {request.inclusion_pct:g} percent inclusion",
                                 chunk_tag="intervention", top_k=3))
    results = []
    unique = {}
    for query in queries:
        response = search.search(query)
        results.append({"request": query.model_dump(), "result": response.model_dump()})
        for hit in response.hits:
            previous = unique.get(hit.chunk_id)
            if previous is None or hit.score > previous["score"]:
                unique[hit.chunk_id] = hit.model_dump()
    return list(unique.values()), results
