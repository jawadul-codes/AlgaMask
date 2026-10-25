"""Read-only input feasibility; uses the same candidates and checks as execution."""
from math import ceil, floor

from .formulation_engine import candidate, check_formula, make_formula
from .experiments import PROOF_VERSION, proof_amounts
from .nutrition import estimate_nutrition


def check_inputs(request, snapshot):
    proof = request.experiment == PROOF_VERSION
    candidates = ([make_formula('A1', proof_amounts('A1'), 45)] if proof else
                  [candidate(request, f'S{d}-{f}', d, f) for d in (25, 30, 35) for f in (1, 2, 3)])
    structural = request.model_copy(update=dict(min_protein_g=None, max_energy_kcal=None, max_sugar_g=None))
    errors = []
    eligible = []
    for formula in candidates:
        reasons = check_formula(formula, structural, snapshot)
        if not reasons:
            eligible.append(formula)
        errors.extend(reasons)
    if proof:
        for code in ('B0', 'A0'):
            errors.extend(check_formula(make_formula(code, proof_amounts(code), 45), structural,
                                        snapshot, baseline=code == 'B0', check_targets=False))
    messages = sorted(set(errors)) if not eligible or proof else []
    if not eligible or (proof and messages):
        return {'can_run': False, 'messages': messages + [
                    'No recipes remain after applying your exclusions. Nutrition targets have not been evaluated.'],
                'margins': {}, 'candidate_count': 0,
                'notes': ['Review the exclusion requirements. Keep a verified-free-from requirement if you need allergy assurance.']}
    estimates = {f.id: estimate_nutrition(f, snapshot, approved_only=False).per_serving for f in eligible}
    margins = {}
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
            messages.append(f'{label}: required data is missing. No numeric limit can be verified. '
                            'Leave this target blank only if it is optional, or add the missing ingredient data.')
        elif minimum and max(values) < target - 1e-8:
            limit = floor(max(values) * 100) / 100
            messages.append(f'{label}: requested at least {target:g}; highest available estimate is {max(values):.4f}. '
                            f'Lower the minimum to {limit:.2f} or less, or change the ingredients/inclusion. Other targets still apply.')
        elif not minimum and min(values) > target + 1e-8:
            limit = ceil(min(values) * 100) / 100
            messages.append(f'{label}: requested at most {target:g}; lowest available estimate is {min(values):.4f}. '
                            f'Raise the maximum to {limit:.2f} or more, or change the configuration. Other targets still apply.')
    passing = [f for f in eligible if not check_formula(f, request, snapshot)]
    if not passing and not messages:
        messages.append('No single candidate meets all targets together. Adjust the combination of targets; individual ranges do not guarantee a match.')
    return {'can_run': bool(passing) and not messages, 'messages': messages, 'margins': margins,
            'candidate_count': len(passing),
            'notes': ([ 'Ingredient preferences omit selected foods from the recipe; supplier cross-contact and allergy safety are not verified.']
                      if request.exclusions and request.exclusion_mode == 'ingredient_preference' else []) +
                     ['Ranges describe the current experimental recipes, not every possible recipe. Missing values are never treated as zero.',
                      'Inclusion supports 1–15% in this screen (fixed proof: 2%); serving supports 40–50 g (fixed proof: 45 g). These are software limits, not validated dose limits.',
                      'Passing this check does not establish flavour masking performance. Sensory effects remain unmeasured.']}
