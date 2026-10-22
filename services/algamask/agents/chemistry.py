from ..generation import generate_explanation


def explain(request, evidence, dataset_hash, provider=None):
    return generate_explanation(request.model_dump(mode="json"), evidence, dataset_hash, provider)


def run(request, evidence):
    return {"strategy": request.flavour, "chunk_ids": [row["chunk_id"] for row in evidence], "score": None, "status": "assumed for demo"}
