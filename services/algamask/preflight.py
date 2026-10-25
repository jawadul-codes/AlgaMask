"""Read-only input feasibility; uses the same candidates and checks as execution."""
from math import ceil, floor

from .experiments import PROOF_VERSION, proof_amounts
from .formulation_engine import ACTIVE_SEARCH_VERSION, check_formula, make_formula, run_grid
from .nutrition import estimate_nutrition


def check_inputs(request, snapshot, *, version=None, candidate_budget=None):
    reference_notes = [f"Chlorella nutrition uses {r.ingredient_name}; supplier-label values apply to this reference product only, not every chlorella powder. Manufacturer reports naturally occurring sulfites; allergy safety is not verified."
                       for r in snapshot.records('ingredient_forms')
                       if request.algae.value in {'chlorella', 'blend'} and r.ingredient_form_id == 'IF-CHL-PWD' and r.supplier]
    proof = request.experiment == PROOF_VERSION
    if proof:
        return _proof_inputs(request, snapshot, reference_notes)
    found = run_grid(request, snapshot, version=version or ACTIVE_SEARCH_VERSION,
                     candidate_budget=candidate_budget, development=True)
    audit = found["audit"]
    eligible = found["eligible"]
    passing = found["passing"]
    messages = []
    if not eligible:
        messages = sorted({error for errors in audit["verdicts"].values() for error in errors})
        messages.append('No recipes remain after applying your exclusions. Nutrition targets have not been evaluated.')
        return _result(False, messages, {}, 0, reference_notes + [
            'Review the exclusion requirements. Keep a verified-free-from requirement if you need allergy assurance.'], audit, passing_ids=[])
    nutrition = {f.id: estimate_nutrition(f, snapshot, approved_only=False) for f in eligible}
    estimates = {key: estimate.per_serving for key, estimate in nutrition.items()}
    form_names = {r.ingredient_form_id: r.ingredient_name for r in snapshot.records('ingredient_forms')}
    margins = {}
    prefix = 'Within the checked candidate budget, ' if audit["truncated"] else ''
    for field, nutrient, label, minimum in (
        ('min_protein_g', 'protein_g', 'Protein (g)', True),
        ('max_energy_kcal', 'energy_kcal', 'Energy (kcal)', False),
        ('max_sugar_g', 'sugar_g', 'Sugar (g)', False),
    ):
        values = [e[nutrient] for e in estimates.values() if e[nutrient] is not None]
        target = getattr(request, field)
        margins[field] = {'min': min(values) if values else None,
                          'max': max(values) if values else None,
                          'known_candidates': len(values), 'total_candidates': len(eligible)}
        if target is None:
            continue
        if not values:
            missing_forms = sorted({form for estimate in nutrition.values() for form in estimate.missing[nutrient]})
            missing_names = ', '.join(f'{form_names.get(form, form)} [{form}]' for form in missing_forms)
            messages.append(f'{prefix}{label}: required data is missing. No numeric limit can be verified. '
                            f'Missing composition: {missing_names}. '
                            'Leave this target blank only if it is optional, or add the missing ingredient data.')
        elif minimum and max(values) < target - 1e-8:
            limit = floor(max(values) * 100) / 100
            messages.append(f'{prefix}{label}: requested at least {target:g}; highest available estimate is {max(values):.4f}. '
                            f'Lower the minimum to {limit:.2f} or less, or change the ingredients/inclusion. Other targets still apply.')
        elif not minimum and min(values) > target + 1e-8:
            limit = ceil(min(values) * 100) / 100
            messages.append(f'{prefix}{label}: requested at most {target:g}; lowest available estimate is {min(values):.4f}. '
                            f'Raise the maximum to {limit:.2f} or more, or change the configuration. Other targets still apply.')
    if not passing and not messages:
        messages.append('No single candidate meets all targets together. Adjust the combination of targets; individual ranges do not guarantee a match.')
    if found["control_errors"]:
        messages.append(audit["reason"])
    if audit["truncated"] and not passing:
        messages.append(audit["reason"])
    notes = reference_notes + (['Ingredient preferences omit selected foods from the recipe; supplier cross-contact and allergy safety are not verified.']
              if request.exclusions and request.exclusion_mode == 'ingredient_preference' else [])
    notes.append(audit["scope"] + ' Missing values are never treated as zero.')
    if audit["truncated"] and passing:
        notes.append('Only part of the declared grid was checked because the candidate budget was reached. Margins describe the checked recipes.')
    notes.extend(['Inclusion supports 1–15% in this screen (fixed proof: 2%); serving supports 40–50 g (fixed proof: 45 g). These are software limits, not validated dose limits.',
                  'Passing this check does not establish flavour masking performance. Sensory effects remain unmeasured.'])
    return _result(bool(passing) and not messages, messages, margins, len(passing), notes, audit,
                   passing_ids=audit["passing_ids"])


def _proof_inputs(request, snapshot, reference_notes):
    structural = request.model_copy(update={"min_protein_g": None, "max_energy_kcal": None, "max_sugar_g": None})
    candidates = [make_formula('A1', proof_amounts('A1'), 45)]
    errors = []
    eligible = []
    for formula in candidates:
        reasons = check_formula(formula, structural, snapshot)
        if not reasons:
            eligible.append(formula)
        errors.extend(reasons)
    for code in ('B0', 'A0'):
        errors.extend(check_formula(make_formula(code, proof_amounts(code), 45), structural,
                                    snapshot, baseline=code == 'B0', check_targets=False))
    messages = sorted(set(errors))
    audit = {"search_version": PROOF_VERSION, "scope": "Fixed engineering comparison; 45 g ingredient input, not verified finished serving. Not approved for physical testing.",
             "truncated": False, "grid_size": 1, "passing_ids": [] if messages or not eligible else ["A1"]}
    if not eligible or messages:
        return _result(False, messages + ['No recipes remain after applying your exclusions. Nutrition targets have not been evaluated.'],
                       {}, 0, reference_notes + ['Review the exclusion requirements. Keep a verified-free-from requirement if you need allergy assurance.'],
                       audit)
    nutrition = {f.id: estimate_nutrition(f, snapshot, approved_only=False) for f in eligible}
    estimates = {key: item.per_serving for key, item in nutrition.items()}
    margins = {}
    for field, nutrient, label, minimum in (
        ('min_protein_g', 'protein_g', 'Protein (g)', True),
        ('max_energy_kcal', 'energy_kcal', 'Energy (kcal)', False),
        ('max_sugar_g', 'sugar_g', 'Sugar (g)', False),
    ):
        values = [e[nutrient] for e in estimates.values() if e[nutrient] is not None]
        margins[field] = {'min': min(values) if values else None, 'max': max(values) if values else None,
                          'known_candidates': len(values), 'total_candidates': len(eligible)}
        target = getattr(request, field)
        if target is None:
            continue
        if not values or (minimum and max(values) < target - 1e-8) or (not minimum and min(values) > target + 1e-8):
            messages.append(f'{label}: the fixed proof recipe does not meet this target.')
    passing = [f for f in eligible if not check_formula(f, request, snapshot)]
    if not passing and not messages:
        messages.append('No single candidate meets all targets together. Adjust the combination of targets; individual ranges do not guarantee a match.')
    notes = reference_notes + ['Inclusion supports 1–15% in this screen (fixed proof: 2%); serving supports 40–50 g (fixed proof: 45 g). These are software limits, not validated dose limits.',
                               'Passing this check does not establish flavour masking performance. Sensory effects remain unmeasured.']
    audit["passing_ids"] = [f.id for f in passing] if not messages else []
    return _result(bool(passing) and not messages, messages, margins, len(passing) if not messages else 0, notes, audit,
                   passing_ids=audit["passing_ids"])


def _result(can_run, messages, margins, candidate_count, notes, audit, passing_ids=None):
    return {'can_run': can_run, 'messages': messages, 'margins': margins,
            'candidate_count': candidate_count, 'notes': notes,
            'search_version': audit['search_version'], 'scope': audit['scope'],
            'enumerated_candidates': audit.get('grid_size') if not audit.get('truncated') else audit.get('candidate_budget'),
            'grid_size': audit.get('grid_size'), 'truncated': audit.get('truncated', False),
            'passing_ids': [] if passing_ids is None else passing_ids}
