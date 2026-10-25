def mock_sensory_map(algae: str) -> list[dict]:
    return [
        {"category": category, "species": algae, "relative_risk": None, "compound_id": None, "status": "unmeasured", "confidence": "unavailable"}
        for category in ["Earthy / muddy", "Grassy / green", "Marine / fishy", "Sulfurous", "Bitter"]
    ]
