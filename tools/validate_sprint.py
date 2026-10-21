"""Check the four Day 1 CSV schemas and their sample rows."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ingestion import SPRINT, load_scope, load_sprint

SCHEMAS = {
    "algae_vocs.csv": [
        "voc_id", "voc_name", "pubchem_cid", "sensory_category", "descriptor",
        "relative_level", "spirulina_relevance", "evidence_strength", "source_id",
        "evidence_note", "review_status",
    ],
    "maskers.csv": [
        "masker_id", "ingredient", "ingredient_form", "target_category", "mechanism_class",
        "protein_bar_compatibility", "evidence_strength", "starting_level", "allergen_warning",
        "flavour_warning", "colour_texture_warning", "source_id", "evidence_note", "review_status",
    ],
    "nutrition.csv": [
        "ingredient_id", "ingredient", "ingredient_form", "source_record_id",
        "protein_g_100g", "iron_mg_100g", "energy_kcal_100g", "fat_g_100g",
        "carbohydrate_g_100g", "fiber_g_100g", "source_id",
    ],
    "sources.csv": [
        "source_id", "title", "doi_or_database_id", "url", "source_type",
        "publication_year", "what_it_supports", "accessed_date", "reviewer",
    ],
}

LEVELS = {"high", "medium", "low"}
REVIEW = {"extracted", "verified", "approved"}
MECHANISMS = {
    "perceptual masking", "complementary flavour", "bitterness balancing",
    "volatile retention or binding", "encapsulation", "process-based reduction",
    "uncertain hypothesis",
}
COMPAT = {"high", "medium", "low"}


def main() -> int:
    errors = []
    for filename, columns in SCHEMAS.items():
        with (SPRINT / filename).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != columns:
                errors.append(f"{filename} columns {reader.fieldnames}")
    data = load_sprint()
    scope = load_scope()
    categories = set(scope["sensory_categories"])
    source_ids = {row["source_id"] for row in data["sources"]}
    if "" in source_ids or len(source_ids) != len(data["sources"]):
        errors.append("sources.csv needs unique source_id values")
    for row in data["algae_vocs"]:
        if row["sensory_category"] not in categories:
            errors.append(f"{row['voc_id']} category")
        if row["relative_level"] not in LEVELS or row["evidence_strength"] not in LEVELS:
            errors.append(f"{row['voc_id']} level")
        if row["review_status"] not in REVIEW or row["source_id"] not in source_ids:
            errors.append(f"{row['voc_id']} provenance")
        if not row["evidence_note"]:
            errors.append(f"{row['voc_id']} missing note")
    for row in data["maskers"]:
        if row["target_category"] not in categories or row["mechanism_class"] not in MECHANISMS:
            errors.append(f"{row['masker_id']} labels")
        if row["protein_bar_compatibility"] not in COMPAT or row["evidence_strength"] not in LEVELS:
            errors.append(f"{row['masker_id']} strength")
        if row["review_status"] not in REVIEW or row["source_id"] not in source_ids:
            errors.append(f"{row['masker_id']} provenance")
    number_fields = [
        "protein_g_100g", "iron_mg_100g", "energy_kcal_100g",
        "fat_g_100g", "carbohydrate_g_100g", "fiber_g_100g",
    ]
    for row in data["nutrition"]:
        if row["source_id"] not in source_ids:
            errors.append(f"{row['ingredient_id']} source")
        for field in number_fields:
            if row[field] == "":
                continue
            try:
                float(row[field])
            except ValueError:
                errors.append(f"{row['ingredient_id']} {field}")
    if errors:
        print("\n".join(errors))
        return 1
    counts = {name: len(data[name]) for name in ("algae_vocs", "maskers", "nutrition", "sources")}
    print(f"sprint sample ok {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
