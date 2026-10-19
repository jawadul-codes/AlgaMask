"""Synthetic UI fixtures. These are not reviewed scientific records."""

INGREDIENTS = {
    "oats": {"allergens": ["oats"], "role": "matrix"},
    "date_paste": {"allergens": [], "role": "binder"},
    "seed_butter": {"allergens": ["sesame"], "role": "binder"},
    "coconut": {"allergens": ["coconut"], "role": "matrix"},
    "cocoa": {"allergens": [], "role": "aroma"},
    "cinnamon": {"allergens": [], "role": "aroma"},
    "vanilla": {"allergens": [], "role": "aroma"},
    "citrus": {"allergens": [], "role": "aroma"},
    "spirulina": {"allergens": [], "role": "algae"},
    "chlorella": {"allergens": [], "role": "algae"},
}

EVIDENCE = [
    {"chunk_id": "demo-aroma", "source_id": "demo-source", "title": "Synthetic aroma strategy example", "text": "Placeholder showing where reviewed intervention evidence will appear.", "status": "assumed for demo"},
    {"chunk_id": "demo-profile", "source_id": "demo-source", "title": "Synthetic algae profile example", "text": "Placeholder showing where species and sensory observations will appear.", "status": "assumed for demo"},
]
