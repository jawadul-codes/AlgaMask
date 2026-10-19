def run(request, evidence):
    return {"strategy": request.flavour, "chunk_ids": [row["chunk_id"] for row in evidence], "score": None, "status": "assumed for demo"}
