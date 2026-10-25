"""Finite engineering screening search, not a scientifically validated recipe solver."""
from .nutrition import estimate_nutrition
from .schemas import Formulation, IngredientAmount
from .experiments import PROOF_VERSION, proof_amounts

SEARCH_VERSION = "exact-form-grid-v1"
WARNING = "Experimental proportions; no validated protein-bar bounds, process or sensory performance. Not production eligible."
ALGAE = {"spirulina": "IF-SPI-PWD", "chlorella": "IF-CHL-PWD"}
FLAVOURS = {"cocoa-spice": ("IF-COCOA-PWD", "IF-CINN-PWD"),
            "vanilla": ("IF-VAN-EXT",), "citrus": ("IF-ORANGE-PEEL",)}
ALLERGENS = {"milk": {"ALG-MILK"}, "soy": {"ALG-SOY"}, "peanut": {"ALG-PEANUT"},
             "tree_nut": {"ALG-ALMOND"}, "sesame": {"ALG-SESAME"}}
EXCLUDED_FORMS = {'oats': {'IF-OAT-DRY'}, 'coconut': {'IF-COCO-OIL'},
                  'milk': {'IF-WHEY-PWD'}, 'soy': {'IF-SOY-ISO'},
                  'peanut': {'IF-PEANUT-BUTTER'}, 'tree_nut': {'IF-ALMOND-BUTTER'},
                  'sesame': {'IF-TAHINI'}}


def candidate(request, code, date_pct, flavour_pct):
    amounts = {"IF-DATE-DRIED": request.serving_g * date_pct / 100}
    species = list(ALGAE) if request.algae == "blend" else [request.algae.value]
    for species_name in species:
        amounts[ALGAE[species_name]] = request.serving_g * request.inclusion_pct / 100 / len(species)
    flavours = FLAVOURS[request.flavour]
    for form_id in flavours:
        amounts[form_id] = request.serving_g * flavour_pct / 100 / len(flavours)
    amounts["IF-OAT-DRY"] = request.serving_g - sum(amounts.values())
    return make_formula(code, amounts, request.serving_g)


def make_formula(code, amounts, mass):
    return Formulation(id=code, name=f"Experimental screening {code}", total_g=mass,
        status="computational_screening", warnings=[WARNING, "Dried whole dates, not date paste; raw orange peel, not citrus oil. Manufacturing feasibility is untested."],
        ingredients=[IngredientAmount(ingredient_id=key, grams=value,
            role="algae" if key in ALGAE.values() else "matrix") for key, value in amounts.items() if value > 0])


def matched_controls(formula):
    """Replace removed components with oats; all other masses remain constant."""
    amounts = {i.ingredient_id: i.grams for i in formula.ingredients}
    unmasked = dict(amounts)
    flavour_ids = {key for group in FLAVOURS.values() for key in group}
    removed = sum(unmasked.pop(key, 0) for key in flavour_ids)
    unmasked["IF-OAT-DRY"] += removed
    baseline = dict(unmasked)
    baseline["IF-OAT-DRY"] += sum(baseline.pop(key, 0) for key in ALGAE.values())
    return [make_formula("B0", baseline, formula.total_g), make_formula("A0", unmasked, formula.total_g)]


def check_formula(formula, request, snapshot, *, baseline=False, check_targets=True, check_grid=True):
    """Independent checks against actual amounts, not generator-declared roles."""
    errors = []
    forms = {r.ingredient_form_id for r in snapshot.records("ingredient_forms")}
    amounts = {i.ingredient_id: i.grams for i in formula.ingredients}
    if set(amounts) - forms:
        return ["Unknown ingredient forms."]
    if abs(sum(amounts.values()) - request.serving_g) > 1e-6:
        errors.append("Serving mass constraint failed.")
    if request.experiment == PROOF_VERSION:
        expected_amounts = proof_amounts(formula.id)
        if expected_amounts is None or set(amounts) != set(expected_amounts) or any(
            abs(amounts[key] - value) > 1e-6 for key, value in (expected_amounts or {}).items()
            if key in amounts
        ):
            errors.append("Fixed experiment quantities or ingredient forms do not match spirulina-proof-v1.")
    elif check_grid:
        allowed = {"IF-OAT-DRY", "IF-DATE-DRIED", *ALGAE.values(), *FLAVOURS[request.flavour]}
        if set(amounts) - allowed:
            errors.append("Ingredient outside declared engineering grid.")
        dates = amounts.get("IF-DATE-DRIED", 0) * 100 / request.serving_g
        if not any(abs(dates - pct) < 1e-6 for pct in (25, 30, 35)):
            errors.append("Date proportion outside declared engineering grid.")
        flavour_amounts = [amounts.get(key, 0) for key in FLAVOURS[request.flavour]]
        pct = sum(flavour_amounts) * 100 / request.serving_g
        if not any(abs(pct - value) < 1e-6 for value in (1, 2, 3)) or max(flavour_amounts) - min(flavour_amounts) > 1e-6:
            errors.append("Flavour proportion outside declared engineering grid.")
    species = list(ALGAE) if request.algae == "blend" else [request.algae.value]
    for species_name, form_id in ALGAE.items():
        expected = request.serving_g * request.inclusion_pct / 100 / len(species) if species_name in species and not baseline else 0
        if abs(amounts.get(form_id, 0) - expected) > 1e-6:
            errors.append(f"Algae inclusion constraint failed: {form_id}.")
    for exclusion in sorted(set(request.exclusions)):
        known = set(amounts) & EXCLUDED_FORMS[exclusion]
        known.update(r.ingredient_form_id for r in snapshot.records('ingredient_allergens')
                     if r.ingredient_form_id in amounts and r.allergen_id in ALLERGENS.get(exclusion, set())
                     and r.relationship == 'contains')
        if known:
            errors.append(f"Excluded ingredient: {', '.join(sorted(known))}." +
                          (' Every current recipe uses oats; no oat-free recipe is available.' if exclusion == 'oats' else ''))
        elif request.exclusion_mode == 'verified_free_from':
            # No complete supplier/lot verification exists for ANY selected group.
            errors.append(f"Verified exclusion {exclusion.replace('_', ' ')}: free-from coverage unknown; "
                          'supplier verification is needed. Changing nutrition targets will not resolve this.')
    if check_targets:
        estimate = estimate_nutrition(formula, snapshot, approved_only=False)
        for field, nutrient, minimum in (("min_protein_g", "protein_g", True),
                                         ("max_energy_kcal", "energy_kcal", False),
                                         ("max_sugar_g", "sugar_g", False)):
            target = getattr(request, field)
            if target is None:
                continue
            value = estimate.per_serving[nutrient]
            if value is None:
                errors.append(f"Cannot verify {field}: {nutrient} unknown.")
            elif (minimum and value < target - 1e-8) or (not minimum and value > target + 1e-8):
                errors.append(f"Target not met: {field}.")
    return errors


def screen(request, snapshot, *, development):
    if request.experiment == PROOF_VERSION:
        return screen_proof(request, snapshot, development=development)
    audit = {"search_version": SEARCH_VERSION, "production_eligible": False,
             "assumptions": {"date_pct": [25, 30, 35], "flavour_pct": [1, 2, 3],
                             "blend_split": "50:50", "remainder": "IF-OAT-DRY"},
             "scope": "Nine-point engineering grid only; not a global feasibility proof or safety assessment.",
             "verdicts": {}}
    if not development:
        audit["reason"] = "Engineering search is development-only; validated production bounds/process are not implemented."
        return [], [], audit
    valid = []
    for dates in (25, 30, 35):
        for flavour in (1, 2, 3):
            formula = candidate(request, f"S{dates}-{flavour}", dates, flavour)
            errors = check_formula(formula, request, snapshot)
            audit["verdicts"][formula.id] = errors
            if not errors:
                valid.append(formula)
    # Stable ordering by protein, then ID. Unknown protein always ranks last.
    def rank(formula):
        protein = estimate_nutrition(formula, snapshot, approved_only=False).per_serving["protein_g"]
        return (protein is None, -protein if protein is not None else 0, formula.id)
    valid.sort(key=rank)
    selected = valid[:3]
    controls = matched_controls(selected[0]) if selected else []
    for control in controls:
        errors = check_formula(control, request, snapshot, baseline=control.id == "B0", check_targets=False, check_grid=False)
        if errors:
            raise ValueError(f"Matched control failed checks: {errors}")
    audit["selected_ids"] = [f.id for f in selected]
    audit["control_parent_id"] = selected[0].id if selected else None
    audit["controls_basis"] = "Only matched to top candidate; flavour then algae replaced by oats. Nutrition targets apply to candidates, not controls."
    audit["status"] = "screening_candidates" if selected else "no_verified_candidate_in_grid"
    return selected, controls, audit


def screen_proof(request, snapshot, *, development):
    audit = {"search_version": PROOF_VERSION, "production_eligible": False,
             "scope": "Fixed engineering comparison; 45 g ingredient input, not verified finished serving. Not approved for physical testing.",
             "controls_basis": "B0/A0/A1 keep dates and cocoa fixed. A0 substitutes spirulina for oats; A1 substitutes cinnamon for oats. Not a pure cinnamon mechanism test.",
             "assumptions": {"scope_document": "FIRST_RELEASE_SCOPE.md v1.0", "input_mass_g": 45,
                             "finished_mass_g": None, "scientific_approval": "pending"},
             "verdicts": {}, "selected_ids": [], "control_parent_id": None}
    if not development:
        audit["reason"] = "Fixed experiment is development-only; scientific approval and physical validation are pending."
        return [], [], audit
    arms = [make_formula(code, proof_amounts(code), 45) for code in ("B0", "A0", "A1")]
    for arm in arms:
        arm.warnings = [WARNING, audit["scope"], audit["controls_basis"],
                        "Use dried dates, not date paste. Supplier lots and preparation feasibility are unverified."]
        audit["verdicts"][arm.id] = check_formula(
            arm, request, snapshot, baseline=arm.id == "B0", check_targets=arm.id == "A1")
    if any(audit["verdicts"].values()):
        audit["status"] = "fixed_experiment_blocked"
        return [], [], audit
    audit.update(status="fixed_experiment_candidate", selected_ids=["A1"], control_parent_id="A1")
    return [arms[2]], arms[:2], audit


def impact(formulas, controls, snapshot):
    estimates = {f.id: estimate_nutrition(f, snapshot, approved_only=False).model_dump() for f in controls + formulas}
    baseline = estimates.get("B0", {}).get("protein_g_per_100_kcal")
    top = estimates[formulas[0].id]["protein_g_per_100_kcal"] if formulas else None
    change = (top / baseline - 1) * 100 if top is not None and baseline is not None and baseline > 0 else None
    return {"primary_metric": "protein_g_per_100_kcal", "nutrition": estimates,
            "nutrition_change_pct": change, "sensory_change_pct": None, "panel_size": 0,
            "status": "estimated" if formulas else "unavailable",
            "explanation": "Composition estimates from exact dataset forms; not measured product values. Percentage change compares the top candidate with its B0 control. Sensory outcomes remain unknown."}
