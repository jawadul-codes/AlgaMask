from math import isfinite

from pydantic import BaseModel, ConfigDict, Field

from .dataset import DatasetSnapshot
from .schemas import Formulation


NUTRIENTS = ("protein_g", "energy_kcal", "carbohydrate_g", "fat_g", "fibre_g", "iron_mg")


def calculate_nutrient(amounts: list[tuple[float, float | None]]) -> float | None:
    """Amounts are grams and nutrient values per 100 g; unknown stays unknown."""
    for grams, value in amounts:
        if not isfinite(grams) or grams < 0:
            raise ValueError("ingredient grams must be finite and nonnegative")
        if value is not None and (not isfinite(value) or value < 0):
            raise ValueError("nutrient values must be finite and nonnegative")
    active = [(g, v) for g, v in amounts if g > 0]
    if not active or any(value is None for _, value in active):
        return None
    total = sum(grams * value / 100 for grams, value in active if value is not None)
    if not isfinite(total):
        raise ValueError("nutrient total overflow")
    return total


class NutritionEstimate(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    formulation_id: str
    serving_g: float
    per_serving: dict[str, float | None]
    per_100g: dict[str, float | None]
    protein_g_per_100_kcal: float | None
    missing: dict[str, list[str]]
    records: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    status: str = "composition estimate, not a measured prototype"


def estimate_nutrition(formula: Formulation, snapshot: DatasetSnapshot,
                       *, approved_only: bool = True) -> NutritionEstimate:
    """Use exact ingredient-form IDs; never substitute names or choose ambiguous rows.

    Development callers must explicitly opt into extracted records. The snapshot
    must come from the run's verified dataset; this function does not publish it.
    """
    forms = {r.ingredient_form_id for r in snapshot.records("ingredient_forms")}
    unknown = [i.ingredient_id for i in formula.ingredients if i.ingredient_id not in forms]
    if unknown:
        raise ValueError(f"Unknown ingredient-form IDs: {', '.join(unknown)}")
    rows = {}
    for row in snapshot.records("ingredient_nutrition", approved_only=approved_only):
        if row.basis == "per_100g" and row.review_status in {"approved", "verified", "extracted"}:
            rows.setdefault(row.ingredient_form_id, []).append(row)
    selected = {}
    warnings = ["Database/literature composition is not a measurement of the prototype lot.",
                "Sugar and total omega-3 are not calculated: sugar is absent and some omega-3 entries describe ALA only."]
    for ingredient in formula.ingredients:
        candidates = rows.get(ingredient.ingredient_id, [])
        selected[ingredient.ingredient_id] = candidates[0] if len(candidates) == 1 else None
        if len(candidates) > 1:
            warnings.append(f"Ambiguous nutrition records for {ingredient.ingredient_id}; no record selected.")
    missing = {}
    totals = {}
    for nutrient in NUTRIENTS:
        missing[nutrient] = [i.ingredient_id for i in formula.ingredients
                             if selected[i.ingredient_id] is None
                             or getattr(selected[i.ingredient_id], nutrient) is None]
        totals[nutrient] = calculate_nutrient([
            (i.grams, getattr(selected[i.ingredient_id], nutrient) if selected[i.ingredient_id] else None)
            for i in formula.ingredients])
    # These fields cannot be inferred from carbohydrate or component fatty acids.
    for nutrient in ("sugar_g", "total_omega3_g"):
        totals[nutrient] = None
        missing[nutrient] = [i.ingredient_id for i in formula.ingredients]
    records = [row.model_dump(mode="json") for row in selected.values() if row is not None]
    if any(row["review_status"] != "approved" for row in records):
        warnings.append("Development calculation includes records not yet approved at row level.")
    energy, protein = totals["energy_kcal"], totals["protein_g"]
    return NutritionEstimate(
        formulation_id=formula.id, serving_g=formula.total_g, per_serving=totals,
        per_100g={key: value * 100 / formula.total_g if value is not None else None
                  for key, value in totals.items()},
        protein_g_per_100_kcal=protein * 100 / energy if protein is not None and energy and energy > 0 else None,
        missing=missing, records=records, warnings=warnings)
