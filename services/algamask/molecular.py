def mock_sensory_map(algae: str) -> list[dict]:
    return [
        {"category": category, "species": algae, "relative_risk": risk, "compound_id": None, "status": "assumed for demo", "confidence": "unavailable"}
        for category, risk in [("Earthy / muddy", 0.7), ("Grassy / green", 0.6), ("Marine / fishy", 0.5), ("Sulfurous", 0.3), ("Bitter", 0.6)]
    ]
