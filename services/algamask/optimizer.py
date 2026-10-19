from .schemas import Formulation, IngredientAmount, RunRequest


def build_formula(request: RunRequest, code: str, flavour: str | None, algae: bool = True) -> Formulation:
    mass = round(request.serving_g, 4)
    algae_g = round(mass * request.inclusion_pct / 100, 4) if algae else 0
    aroma_g = round(mass * 0.02, 4) if flavour else 0
    ingredients = []
    if algae_g:
        if request.algae == "blend":
            first = round(algae_g / 2, 4)
            ingredients.extend([IngredientAmount(ingredient_id="spirulina", grams=first, role="algae"), IngredientAmount(ingredient_id="chlorella", grams=round(algae_g-first, 4), role="algae")])
        else:
            ingredients.append(IngredientAmount(ingredient_id=request.algae.value, grams=algae_g, role="algae"))
    if flavour:
        ingredients.append(IngredientAmount(ingredient_id=flavour, grams=aroma_g, role="aroma", chunk_ids=["demo-aroma"]))
    binder_g = round(mass * 0.3, 4)
    ingredients.append(IngredientAmount(ingredient_id="date_paste", grams=binder_g, role="binder"))
    ingredients.append(IngredientAmount(ingredient_id="oats", grams=round(mass-algae_g-aroma_g-binder_g, 4), role="matrix"))
    return Formulation(id=code, name={"B0": "Baseline bar", "A0": "Unmasked algae control"}.get(code, f"{flavour.title()} concept" if flavour else code), ingredients=ingredients, total_g=round(sum(i.grams for i in ingredients), 4), warnings=["Synthetic proportions for software demonstration; formulation review is pending."])


def generate_mock(request: RunRequest) -> list[Formulation]:
    flavours = {"cocoa-spice": ["cocoa", "cinnamon", "vanilla"], "vanilla": ["vanilla", "cocoa", "citrus"], "citrus": ["citrus", "vanilla", "cinnamon"]}[request.flavour]
    return [build_formula(request, f"A{index+1}", flavour) for index, flavour in enumerate(flavours)]
