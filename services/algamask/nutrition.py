def calculate_nutrient(amounts: list[tuple[float, float | None]]) -> float | None:
    """Amounts are grams and nutrient values per 100 g; unknown stays unknown."""
    if not amounts or any(value is None for _, value in amounts):
        return None
    return sum(grams * value / 100 for grams, value in amounts if value is not None)
