from ..validation import validate_formula


def run(request, formulas):
    return {formula.id: validate_formula(formula, request) for formula in formulas}
