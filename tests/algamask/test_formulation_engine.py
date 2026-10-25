from pathlib import Path

import pytest

from algamask.dataset import load_dataset
from algamask.formulation_engine import check_formula, impact, screen
from algamask.schemas import RunRequest


@pytest.fixture(scope="module")
def snapshot():
    return load_dataset(Path(__file__).resolve().parents[2] / "data/candidates/0.1.0-rc.1/reviewed")


@pytest.mark.parametrize("algae", ["spirulina", "chlorella", "blend"])
@pytest.mark.parametrize("flavour", ["cocoa-spice", "vanilla", "citrus"])
@pytest.mark.parametrize("mass,inclusion", [(40, 1), (45, 5), (50, 15)])
def test_grid_constraints_and_controls(snapshot, algae, flavour, mass, inclusion):
    request = RunRequest(algae=algae, flavour=flavour, serving_g=mass, inclusion_pct=inclusion)
    formulas, controls, audit = screen(request, snapshot, development=True)
    assert len(formulas) == 3 and len(controls) == 2
    assert len(audit["verdicts"]) == 9
    assert not audit["production_eligible"]
    assert audit["control_parent_id"] == formulas[0].id
    for formula in formulas + controls:
        assert sum(i.grams for i in formula.ingredients) == pytest.approx(mass)
        assert not check_formula(formula, request, snapshot, baseline=formula.id == "B0", check_grid=formula.id not in {"B0", "A0"})
        assert all(i.ingredient_id.startswith("IF-") and not i.chunk_ids for i in formula.ingredients)
    amounts = [{i.ingredient_id: i.grams for i in f.ingredients} for f in [formulas[0], *controls]]
    assert len({a["IF-DATE-DRIED"] for a in amounts}) == 1
    assert all(key not in amounts[1] for key in ("IF-SPI-PWD", "IF-CHL-PWD"))
    estimates = impact(formulas, controls, snapshot)
    assert estimates["sensory_change_pct"] is None
    assert (estimates["nutrition_change_pct"] is None) == (algae != "spirulina")


@pytest.mark.parametrize("payload,reason", [
    ({"min_protein_g": 50}, "Target not met"),
    ({"max_energy_kcal": 1, "algae": "spirulina"}, "Target not met"),
    ({"max_energy_kcal": 200}, "unknown"),
    ({"max_sugar_g": 10}, "unknown"),
    ({"exclusions": ["oats"]}, "Excluded ingredient"),
    ({"exclusions": ["milk"]}, "coverage unknown"),
    ({"exclusions": ["soy"]}, "coverage unknown"),
    ({"exclusions": ["tree_nut"]}, "coverage unknown"),
])
def test_unsatisfied_or_unknown_constraints(snapshot, payload, reason):
    formulas, controls, audit = screen(RunRequest(**payload), snapshot, development=True)
    assert not formulas and not controls
    assert all(any(reason in error for error in errors) for errors in audit["verdicts"].values())


def test_targets_and_determinism(snapshot):
    request = RunRequest(algae="spirulina", min_protein_g=5, max_energy_kcal=200)
    first = screen(request, snapshot, development=True)
    assert first == screen(request, snapshot, development=True)
    assert first[0]


def test_production_blocked(snapshot):
    formulas, controls, audit = screen(RunRequest(), snapshot, development=False)
    assert not formulas and not controls
    assert "development-only" in audit["reason"]


def test_critic_rejects_altered_species(snapshot):
    request = RunRequest(algae="spirulina")
    formulas, _, _ = screen(request, snapshot, development=True)
    formula = formulas[0].model_copy(deep=True)
    next(i for i in formula.ingredients if i.ingredient_id == "IF-SPI-PWD").ingredient_id = "IF-CHL-PWD"
    assert any("inclusion constraint" in e for e in check_formula(formula, request, snapshot))


def test_critic_rejects_off_grid_proportions(snapshot):
    request = RunRequest(algae="spirulina")
    formulas, _, _ = screen(request, snapshot, development=True)
    formula = formulas[0].model_copy(deep=True)
    next(i for i in formula.ingredients if i.ingredient_id == "IF-DATE-DRIED").grams += 1
    next(i for i in formula.ingredients if i.ingredient_id == "IF-OAT-DRY").grams -= 1
    assert any("Date proportion" in e for e in check_formula(formula, request, snapshot))


@pytest.mark.parametrize('excluded,form_id', [
    ('milk', 'IF-WHEY-PWD'), ('soy', 'IF-SOY-ISO'), ('peanut', 'IF-PEANUT-BUTTER'),
    ('tree_nut', 'IF-ALMOND-BUTTER'), ('sesame', 'IF-TAHINI'), ('coconut', 'IF-COCO-OIL'),
])
def test_preferences_reject_actual_excluded_ingredients(snapshot, excluded, form_id):
    from algamask.formulation_engine import make_formula
    request = RunRequest(algae='spirulina', exclusions=[excluded], exclusion_mode='ingredient_preference')
    formula = make_formula('test', {'IF-SPI-PWD': 2.25, 'IF-OAT-DRY': 41.75, form_id: 1}, 45)
    errors = check_formula(formula, request, snapshot, check_grid=False)
    assert any('Excluded ingredient:' in e and form_id in e for e in errors)
