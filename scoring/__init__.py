"""Day 1 placeholder cards. This is not the recommendation engine."""

from ingestion import load_sprint


def placeholder(inclusion_pct: float, exclusions: list[str], flavour: str) -> dict:
    data = load_sprint()
    scope = data["scope"]
    voc = data["algae_vocs"][0]
    masker = data["maskers"][0]
    return {
        "mode": "day1_placeholder",
        "product": scope["product"],
        "inclusion_pct": inclusion_pct,
        "serving_g": scope["serving_g"],
        "flavour": flavour,
        "exclusions": exclusions,
        "example_levels_pct": scope["spirulina_levels_pct"],
        "rows_loaded": {name: len(data[name]) for name in ("algae_vocs", "maskers", "nutrition", "sources")},
        "sensory_risk": {
            "title": "Sensory risk",
            "category": voc["sensory_category"],
            "compound": voc["voc_name"],
            "evidence_label": "literature-derived",
            "text": (
                f"Placeholder card. Local data lists {voc['voc_name']} under {voc['sensory_category']} "
                f"at spirulina inclusion {inclusion_pct:g}%. This is not a calculated risk score."
            ),
        },
        "recommendation": {
            "title": "Recommendation",
            "ingredient": masker["ingredient"],
            "evidence_label": "assumed",
            "text": (
                f"Placeholder card. Local data lists {masker['ingredient']} as a sample {masker['mechanism_class']} row. "
                "This is not a ranked strategy."
            ),
        },
    }
