"""Finite engineering screening search, not a scientifically validated recipe solver."""
import math

from .nutrition import estimate_nutrition
from .schemas import Formulation, IngredientAmount
from .experiments import PROOF_VERSION, proof_amounts

LEGACY_SEARCH_VERSION = "exact-form-grid-v1"
PROTEIN_BASE_SEARCH_VERSION = "protein-base-grid-v2"
ACTIVE_SEARCH_VERSION = "protein-source-grid-v3"
SEARCH_VERSION = ACTIVE_SEARCH_VERSION
MASS_TOLERANCE = 1e-6
TARGET_TOLERANCE = 1e-8
WARNING = "Experimental proportions; no validated protein-bar bounds, process or sensory performance. Not production eligible."
ALGAE = {"spirulina": "IF-SPI-PWD", "chlorella": "IF-CHL-PWD"}
FLAVOURS = {"cocoa-spice": ("IF-COCOA-PWD", "IF-CINN-PWD"),
            "vanilla": ("IF-VAN-EXT",), "citrus": ("IF-ORANGE-PEEL",)}
PROTEIN_BASE = "IF-WHEY-PWD"
REFERENCE_WHEY = "IF-MP-WHEY-AU"
REFERENCE_PLANT = "IF-MP-PEAFAVA-UK"
PROTEIN_PATHS = {PROTEIN_BASE: "milk", REFERENCE_WHEY: "milk", REFERENCE_PLANT: "plant"}
ALLERGENS = {"milk": {"ALG-MILK"}, "soy": {"ALG-SOY"}, "peanut": {"ALG-PEANUT"},
             "tree_nut": {"ALG-ALMOND"}, "sesame": {"ALG-SESAME"}}
EXCLUDED_FORMS = {'oats': {'IF-OAT-DRY'}, 'coconut': {'IF-COCO-OIL'},
                  'milk': {'IF-WHEY-PWD'}, 'soy': {'IF-SOY-ISO'},
                  'peanut': {'IF-PEANUT-BUTTER'}, 'tree_nut': {'IF-ALMOND-BUTTER'},
                  'sesame': {'IF-TAHINI'}}
NOT_ENABLED = {
    "IF-SOY-ISO": "Audited. USDA soy protein isolate is 88.32 g protein per 100 g, but total sugar is an assumed-zero derivation and stays unknown. Not added.",
    "IF-RICE-PUFF": "No nutrition profile, so it is not an oat replacement. Oat exclusion still blocks.",
}


def _policy(version):
    shared = {"date_pct": (25, 30, 35), "flavour_pct": (1, 2, 3), "remainder": "IF-OAT-DRY",
              "blend_split": "50:50"}
    if version == LEGACY_SEARCH_VERSION:
        return {**shared, "protein_base_form": None, "protein_base_pct": (0,), "candidate_budget": 9,
                "scope": "Nine-point engineering grid only; not a global feasibility proof or safety assessment.",
                "controls_basis": "Only matched to top candidate; flavour then algae replaced by oats. Nutrition targets apply to candidates, not controls."}
    if version == PROTEIN_BASE_SEARCH_VERSION:
        return {**shared, "protein_base_form": PROTEIN_BASE, "protein_base_pct": (0, 10, 20), "candidate_budget": 27,
                "scope": ("Twenty-seven-point engineering grid: dried dates at 25/30/35%, flavour ingredients at 1/2/3%, "
                          "and USDA beverage whey-protein powder isolate at 0/10/20% of input mass replacing rolled oats. "
                          "Not a global feasibility proof, sensory ranking, or food-safety limit."),
                "controls_basis": ("Only matched to the top candidate. Flavour mass, then algae mass, is replaced by rolled oats. "
                                   "Whey, when present, stays in the controls because it is part of the matrix, not the flavour or algae. "
                                   "Nutrition targets apply to candidates, not controls.")}
    if version == ACTIVE_SEARCH_VERSION:
        return {**shared, "protein_base_form": None, "protein_base_forms": tuple(PROTEIN_PATHS),
                "protein_base_pct": (0, 10, 20, 30), "candidate_budget": 90,
                "scope": ("Ninety-point engineering grid: dates at 25/30/35%, flavour at 1/2/3%, "
                          "with no powder or USDA beverage whey, Myprotein AU unflavoured whey, or Myprotein UK "
                          "unflavoured pea–fava at 10/20/30% of ingredient input replacing oats. "
                          "Reference-product development estimates; not a global feasibility proof or validated dose, texture, taste or safe-use limit."),
                "controls_basis": "Matched to the first selected candidate only. Flavour then algae replaced by oats; protein powder retained. Nutrition targets apply to candidates, not controls."}
    raise ValueError(f"Unsupported search policy: {version}")


def bound_search_version(context):
    """Jobs saved before the policy field keep the original nine-recipe grid."""
    value = (context or {}).get("search_version")
    if value is None:
        return LEGACY_SEARCH_VERSION
    _policy(value)
    return value


def grid_points(version):
    policy = _policy(version)
    for dates in policy["date_pct"]:
        for flavour in policy["flavour_pct"]:
            if version == ACTIVE_SEARCH_VERSION:
                yield f"S{dates}-{flavour}", dates, flavour, 0, None
                for form, suffix in ((PROTEIN_BASE, "W"), (REFERENCE_WHEY, "MW"), (REFERENCE_PLANT, "PF")):
                    for protein in (10, 20, 30):
                        yield f"S{dates}-{flavour}-{suffix}{protein}", dates, flavour, protein, form
                continue
            for protein in policy["protein_base_pct"]:
                code = f"S{dates}-{flavour}" if protein == 0 else f"S{dates}-{flavour}-W{protein}"
                yield code, dates, flavour, protein, PROTEIN_BASE if protein else None


def candidate(request, code, date_pct, flavour_pct, protein_pct=0, protein_form=PROTEIN_BASE):
    amounts = {"IF-DATE-DRIED": request.serving_g * date_pct / 100}
    species = list(ALGAE) if request.algae == "blend" else [request.algae.value]
    for species_name in species:
        amounts[ALGAE[species_name]] = request.serving_g * request.inclusion_pct / 100 / len(species)
    flavours = FLAVOURS[request.flavour]
    for form_id in flavours:
        amounts[form_id] = request.serving_g * flavour_pct / 100 / len(flavours)
    if protein_pct:
        amounts[protein_form] = request.serving_g * protein_pct / 100
    amounts["IF-OAT-DRY"] = request.serving_g - sum(amounts.values())
    return make_formula(code, amounts, request.serving_g)


def make_formula(code, amounts, mass):
    warnings = [WARNING, "Dried whole dates, not date paste; raw orange peel, not citrus oil. Manufacturing feasibility is untested."]
    if amounts.get(PROTEIN_BASE, 0) > 0:
        warnings.append("Includes USDA beverage whey-protein powder isolate (FDC 173177; 58.14 g protein, 359 kcal and 1.16 g total sugar per 100 g). This is a milk ingredient, not a named high-protein supplier isolate and not an approved dose.")
    if amounts.get(REFERENCE_WHEY, 0) > 0:
        warnings.append("Myprotein Impact Whey Isolate Unflavoured 1 kg AU reference contains milk and soy. Published rounded label, not a confirmed local supplier lot.")
    if amounts.get(REFERENCE_PLANT, 0) > 0:
        warnings.append("Myprotein Vegan Protein Blend Unflavoured pea–fava 250 g UK reference: facility also handles milk. Declared 0 g sugar is label-rounded, not proof of zero sugar in a finished bar or verified free-from status.")
    if any(amounts.get(form, 0) > 0 for form in (REFERENCE_WHEY, REFERENCE_PLANT)):
        warnings.append("Powder proportions are software search levels; texture, processing, taste and safe use require physical and scientific review.")
    return Formulation(id=code, name=f"Experimental screening {code}", total_g=mass,
        status="computational_screening", warnings=warnings,
        ingredients=[IngredientAmount(ingredient_id=key, grams=value,
            role="algae" if key in ALGAE.values() else "protein_base" if key in PROTEIN_PATHS else "matrix")
            for key, value in amounts.items() if value > 0])


def matched_controls(formula):
    """Replace removed components with oats; all other masses remain constant."""
    amounts = {i.ingredient_id: i.grams for i in formula.ingredients}
    unmasked = dict(amounts)
    flavour_ids = {key for group in FLAVOURS.values() for key in group}
    removed = sum(unmasked.pop(key, 0) for key in flavour_ids)
    unmasked["IF-OAT-DRY"] = unmasked.get("IF-OAT-DRY", 0) + removed
    baseline = dict(unmasked)
    baseline["IF-OAT-DRY"] = baseline.get("IF-OAT-DRY", 0) + sum(baseline.pop(key, 0) for key in ALGAE.values())
    return [make_formula("B0", baseline, formula.total_g), make_formula("A0", unmasked, formula.total_g)]


def check_formula(formula, request, snapshot, *, baseline=False, check_targets=True, check_grid=True, version=None):
    """Independent checks against actual amounts, not generator-declared roles."""
    version = version or ACTIVE_SEARCH_VERSION
    errors = []
    forms = {r.ingredient_form_id for r in snapshot.records("ingredient_forms")}
    amounts = {i.ingredient_id: i.grams for i in formula.ingredients}
    if any(not math.isfinite(value) or value < 0 for value in amounts.values()):
        return ["Quantities must be finite and nonnegative."]
    if set(amounts) - forms:
        return ["Unknown ingredient forms."]
    if abs(sum(amounts.values()) - request.serving_g) > MASS_TOLERANCE:
        errors.append("Serving mass constraint failed.")
    if request.experiment == PROOF_VERSION:
        expected_amounts = proof_amounts(formula.id)
        if expected_amounts is None or set(amounts) != set(expected_amounts) or any(
            abs(amounts[key] - value) > MASS_TOLERANCE for key, value in (expected_amounts or {}).items()
            if key in amounts
        ):
            errors.append("Fixed experiment quantities or ingredient forms do not match spirulina-proof-v1.")
    elif check_grid:
        policy = _policy(version)
        allowed = {"IF-OAT-DRY", "IF-DATE-DRIED", *ALGAE.values(), *FLAVOURS[request.flavour]}
        protein_forms = policy.get("protein_base_forms", (policy["protein_base_form"],) if policy["protein_base_form"] else ())
        allowed.update(protein_forms)
        if set(amounts) - allowed:
            errors.append("Ingredient outside declared engineering grid.")
        if amounts.get("IF-OAT-DRY", 0) <= MASS_TOLERANCE:
            errors.append("Every recipe in this policy uses rolled oats; no oat-free recipe is available.")
        dates = amounts.get("IF-DATE-DRIED", 0) * 100 / request.serving_g
        if not any(abs(dates - pct) < MASS_TOLERANCE for pct in policy["date_pct"]):
            errors.append("Date proportion outside declared engineering grid.")
        flavour_amounts = [amounts.get(key, 0) for key in FLAVOURS[request.flavour]]
        pct = sum(flavour_amounts) * 100 / request.serving_g
        if not any(abs(pct - value) < MASS_TOLERANCE for value in policy["flavour_pct"]) or max(flavour_amounts) - min(flavour_amounts) > MASS_TOLERANCE:
            errors.append("Flavour proportion outside declared engineering grid.")
        if protein_forms:
            if sum(amounts.get(form, 0) > 0 for form in protein_forms) > 1:
                errors.append("Only one protein powder is allowed per recipe.")
            actual = sum(amounts.get(form, 0) for form in protein_forms) * 100 / request.serving_g
            if not any(abs(actual - value) < MASS_TOLERANCE for value in policy["protein_base_pct"]):
                errors.append("Protein-base proportion outside declared engineering grid.")
    if request.protein_source != "auto":
        if request.experiment == PROOF_VERSION or version != ACTIVE_SEARCH_VERSION:
            errors.append("This historical or fixed policy does not support a protein source selection.")
        elif not any(amounts.get(form, 0) > 0 for form, path in PROTEIN_PATHS.items() if path == request.protein_source):
            errors.append(f"A {request.protein_source} protein powder is required.")
        elif any(amounts.get(form, 0) > 0 for form, path in PROTEIN_PATHS.items() if path != request.protein_source):
            errors.append("Protein powder does not match the requested source.")
    species = list(ALGAE) if request.algae == "blend" else [request.algae.value]
    for species_name, form_id in ALGAE.items():
        expected = request.serving_g * request.inclusion_pct / 100 / len(species) if species_name in species and not baseline else 0
        if abs(amounts.get(form_id, 0) - expected) > MASS_TOLERANCE:
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
            elif (minimum and value < target - TARGET_TOLERANCE) or (not minimum and value > target + TARGET_TOLERANCE):
                errors.append(f"Target not met: {field}.")
    return errors


def _rank(formula, snapshot):
    protein = estimate_nutrition(formula, snapshot, approved_only=False).per_serving["protein_g"]
    return (protein is None, -protein if protein is not None else 0, formula.id)


def protein_path(formula):
    return next((PROTEIN_PATHS[i.ingredient_id] for i in formula.ingredients
                 if i.ingredient_id in PROTEIN_PATHS), "none")


def select_options(passing, request, version):
    if not passing or version != ACTIVE_SEARCH_VERSION or request.protein_source != "auto":
        return passing[:3]
    selected = [passing[0]]
    opposite = {"milk": "plant", "plant": "milk"}.get(protein_path(passing[0]))
    alternative = next((f for f in passing[1:] if protein_path(f) == opposite), None)
    if alternative:
        selected.append(alternative)
    selected.extend(f for f in passing if f.id not in {item.id for item in selected})
    return selected[:3]


def run_grid(request, snapshot, *, version=None, candidate_budget=None, development=True):
    """One candidate set for preflight and execution."""
    version = version or ACTIVE_SEARCH_VERSION
    policy = _policy(version)
    budget = policy["candidate_budget"] if candidate_budget is None else candidate_budget
    if budget < 0:
        raise ValueError("candidate budget must be nonnegative")
    specs = list(grid_points(version))
    truncated = len(specs) > budget
    audit = {"search_version": version, "production_eligible": False,
             "assumptions": {"date_pct": list(policy["date_pct"]), "flavour_pct": list(policy["flavour_pct"]),
                             "blend_split": policy["blend_split"], "remainder": policy["remainder"],
                             "protein_base_form": policy["protein_base_form"],
                             "protein_base_pct": list(policy["protein_base_pct"]),
                             "bounds_are": "software engineering levels, not reviewed food-safety, dose, or sensory limits",
                             "protein_base_record": ("IF-WHEY-PWD is USDA SR Legacy FDC 173177, Beverages, Whey protein powder isolate: "
                                                     "58.14 g protein, 359 kcal, 1.16 g total sugar per 100 g. Not a named 80-90% supplier isolate. It contains milk.")
                             if policy["protein_base_form"] else None,
                             "not_enabled": NOT_ENABLED},
             "scope": policy["scope"], "controls_basis": policy["controls_basis"],
             "candidate_budget": budget, "grid_size": len(specs), "truncated": truncated, "verdicts": {}}
    if not development:
        audit["reason"] = "Engineering search is development-only; validated production bounds/process are not implemented."
        return {"audit": audit, "policy": policy, "generated": [], "eligible": [], "passing": [],
                "selected": [], "controls": [], "control_errors": []}
    structural = request.model_copy(update={"min_protein_g": None, "max_energy_kcal": None, "max_sugar_g": None})
    generated, eligible, passing = [], [], []
    if version == ACTIVE_SEARCH_VERSION:
        audit["assumptions"].update(protein_base_forms=list(PROTEIN_PATHS), protein_source=request.protein_source)
        audit["selection"] = "Highest estimated protein first; auto reserves the second slot for the other passing protein path when available, then fills by protein and ID."
    for code, dates, flavour, protein, form in specs[:budget]:
        formula = candidate(request, code, dates, flavour, protein, form)
        generated.append(formula)
        audit["verdicts"][formula.id] = check_formula(formula, request, snapshot, version=version)
        if not check_formula(formula, structural, snapshot, version=version):
            eligible.append(formula)
        if not audit["verdicts"][formula.id]:
            passing.append(formula)
    passing.sort(key=lambda formula: _rank(formula, snapshot))
    selected = select_options(passing, request, version)
    controls, control_errors = [], []
    if selected:
        controls = matched_controls(selected[0])
        for control in controls:
            control_errors.extend(check_formula(control, request, snapshot, baseline=control.id == "B0",
                                                check_targets=False, check_grid=False, version=version))
        if control_errors:
            audit["status"] = "control_construction_failed"
            audit["reason"] = "Matched controls could not be built without breaking a rule: " + "; ".join(control_errors)
            selected, controls = [], []
    if "status" not in audit:
        if selected:
            audit["status"] = "screening_candidates"
        elif truncated:
            audit["status"] = "search_budget_exhausted"
            audit["reason"] = "The declared candidate budget stopped the search before a matching recipe was found. This is not proof that no recipe exists."
        else:
            audit["status"] = "no_verified_candidate_in_grid"
            audit["reason"] = "No candidate in this declared grid met the checks. This is not proof that no recipe exists outside the grid."
    audit["selected_ids"] = [formula.id for formula in selected]
    audit["control_parent_id"] = selected[0].id if selected else None
    audit["passing_ids"] = [formula.id for formula in passing] if selected or not control_errors else []
    return {"audit": audit, "policy": policy, "generated": generated, "eligible": eligible,
            "passing": passing if not control_errors else [], "selected": selected,
            "controls": controls, "control_errors": control_errors}


def screen(request, snapshot, *, development, version=None, candidate_budget=None):
    if request.experiment == PROOF_VERSION:
        return screen_proof(request, snapshot, development=development)
    found = run_grid(request, snapshot, version=version, candidate_budget=candidate_budget, development=development)
    return found["selected"], found["controls"], found["audit"]


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
