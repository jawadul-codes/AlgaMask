from .fixtures import INGREDIENTS
from .schemas import Formulation, RunRequest


def validate_formula(formula: Formulation, request: RunRequest) -> list[str]:
    errors = []
    if any(getattr(request, field) is not None for field in ("min_protein_g", "max_energy_kcal", "max_sugar_g")):
        errors.append("Nutrition targets cannot be verified in mock mode.")
    if abs(sum(item.grams for item in formula.ingredients) - request.serving_g) > 0.001:
        errors.append("Recipe mass does not match serving mass.")
    for item in formula.ingredients:
        record = INGREDIENTS.get(item.ingredient_id)
        if record is None:
            errors.append(f"Unknown ingredient: {item.ingredient_id}")
        elif set(record["allergens"]) & set(request.exclusions):
            errors.append(f"Excluded ingredient: {item.ingredient_id}")
        if item.grams <= 0:
            errors.append("Ingredient mass must be positive.")
    return errors
