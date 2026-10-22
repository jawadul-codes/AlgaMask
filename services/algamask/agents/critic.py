from ..validation import validate_formula
from ..generation import critique_explanation


def check_grounding(explanation, evidence, dataset_hash):
    return critique_explanation(explanation, evidence, dataset_hash)


def run(request, formulas):
    return {formula.id: validate_formula(formula, request) for formula in formulas}
