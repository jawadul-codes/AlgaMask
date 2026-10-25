"""Policy expansion, historical grid, and preflight/execution agreement."""
from pathlib import Path

import pytest

from algamask.formulation_engine import (
    ACTIVE_SEARCH_VERSION, LEGACY_SEARCH_VERSION, bound_search_version, check_formula,
    make_formula, run_grid, screen,
)
from algamask.nutrition import estimate_nutrition
from algamask.preflight import check_inputs
from algamask.report_interpretation import interpret
from algamask.schemas import RunRequest, RunResult


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def snapshot():
    from algamask.dataset import load_dataset
    return load_dataset(ROOT / "data/candidates/0.1.0-rc.5/reviewed")


def _request(**overrides):
    values = dict(algae="chlorella", inclusion_pct=3, serving_g=45, flavour="vanilla")
    values.update(overrides)
    return RunRequest(**values)


def test_original_grid_numbers_stay_available(snapshot):
    request = _request()
    preview = check_inputs(request, snapshot, version=LEGACY_SEARCH_VERSION)
    assert preview["search_version"] == LEGACY_SEARCH_VERSION
    assert preview["grid_size"] == 9
    assert preview["margins"]["min_protein_g"]["min"] == pytest.approx(4.57866)
    assert preview["margins"]["min_protein_g"]["max"] == pytest.approx(5.17797)
    assert preview["margins"]["max_energy_kcal"]["min"] == pytest.approx(154.017)
    assert preview["margins"]["max_energy_kcal"]["max"] == pytest.approx(159.201)
    assert preview["margins"]["max_sugar_g"]["min"] == pytest.approx(7.508205)
    assert preview["margins"]["max_sugar_g"]["max"] == pytest.approx(10.419345)
    adjusted = _request(min_protein_g=5.17, max_energy_kcal=200, max_sugar_g=10)
    formulas, _, audit = screen(adjusted, snapshot, development=True, version=LEGACY_SEARCH_VERSION)
    assert audit["passing_ids"] == ["S25-1"]
    assert [formula.id for formula in formulas] == ["S25-1"]
    amounts = {item.ingredient_id: item.grams for item in formulas[0].ingredients}
    assert amounts == pytest.approx({"IF-DATE-DRIED": 11.25, "IF-CHL-PWD": 1.35, "IF-OAT-DRY": 31.95, "IF-VAN-EXT": 0.45})
    nutrition = estimate_nutrition(formulas[0], snapshot, approved_only=False).per_serving
    assert nutrition["protein_g"] == pytest.approx(5.17797)
    assert nutrition["energy_kcal"] == pytest.approx(159.201)
    assert nutrition["sugar_g"] == pytest.approx(7.508205)


def test_whey_recipe_is_outside_the_original_grid(snapshot):
    request = _request(min_protein_g=8, max_energy_kcal=200, max_sugar_g=10)
    assert not screen(request, snapshot, development=True, version=LEGACY_SEARCH_VERSION)[0]
    formulas, controls, audit = screen(request, snapshot, development=True)
    assert audit["search_version"] == ACTIVE_SEARCH_VERSION
    assert formulas[0].id == "S25-1-W20"
    amounts = {item.ingredient_id: item.grams for item in formulas[0].ingredients}
    assert amounts["IF-WHEY-PWD"] == pytest.approx(9)
    assert amounts["IF-OAT-DRY"] == pytest.approx(22.95)
    assert sum(amounts.values()) == pytest.approx(45)
    record = next(row for row in snapshot.records("ingredient_nutrition") if row.ingredient_form_id == "IF-WHEY-PWD")
    assert (record.protein_g, record.energy_kcal, record.sugar_g, record.fdc_id) == (58.14, 359, 1.16, 173177)
    expected = sum(grams * next(row for row in snapshot.records("ingredient_nutrition") if row.ingredient_form_id == form).protein_g / 100
                   for form, grams in amounts.items())
    assert estimate_nutrition(formulas[0], snapshot, approved_only=False).per_serving["protein_g"] == pytest.approx(expected)
    assert expected > 5.17797
    control_amounts = [{item.ingredient_id: item.grams for item in control.ingredients} for control in controls]
    assert control_amounts[0]["IF-WHEY-PWD"] == pytest.approx(9)
    assert "IF-CHL-PWD" not in control_amounts[0]
    assert control_amounts[1]["IF-WHEY-PWD"] == pytest.approx(9)
    assert "milk" in audit["assumptions"]["protein_base_record"]
    preview = check_inputs(request, snapshot)
    assert preview["can_run"] and preview["passing_ids"][:len(formulas)] == [formula.id for formula in formulas]


def test_saved_job_without_policy_keeps_nine_recipes(snapshot):
    version = bound_search_version({})
    formulas, _, audit = screen(_request(algae="spirulina"), snapshot, development=True, version=version)
    assert audit["search_version"] == LEGACY_SEARCH_VERSION
    assert len(audit["verdicts"]) == 9
    assert all("IF-WHEY-PWD" not in {item.ingredient_id for item in formula.ingredients} for formula in formulas)
    with pytest.raises(ValueError, match="Unsupported search policy"):
        bound_search_version({"search_version": "future-grid"})


def test_milk_preference_removes_whey_and_matches_original_ranges(snapshot):
    preferred = _request(exclusions=["milk"], exclusion_mode="ingredient_preference")
    current = check_inputs(preferred, snapshot)
    original = check_inputs(_request(), snapshot, version=LEGACY_SEARCH_VERSION)
    assert current["grid_size"] == 27
    assert current["margins"]["min_protein_g"]["total_candidates"] == 9
    assert current["margins"]["min_protein_g"]["max"] == pytest.approx(original["margins"]["min_protein_g"]["max"])
    assert current["margins"]["max_sugar_g"]["min"] == pytest.approx(original["margins"]["max_sugar_g"]["min"])
    assert all("IF-WHEY-PWD" not in formula_id for formula_id in current["passing_ids"])
    strict = check_inputs(_request(exclusions=["milk"]), snapshot)
    assert not strict["can_run"] and strict["margins"] == {}
    assert any("free-from coverage unknown" in message for message in strict["messages"])


def test_oat_exclusion_stays_blocked(snapshot):
    preview = check_inputs(_request(exclusions=["oats"], exclusion_mode="ingredient_preference"), snapshot)
    assert not preview["can_run"] and preview["margins"] == {}
    assert any("no oat-free recipe" in message for message in preview["messages"])


@pytest.mark.parametrize("algae", ["spirulina", "chlorella", "blend"])
@pytest.mark.parametrize("flavour", ["cocoa-spice", "vanilla", "citrus"])
@pytest.mark.parametrize("mass,inclusion", [(40, 1), (50, 15)])
def test_preflight_matches_execution(snapshot, algae, flavour, mass, inclusion):
    request = RunRequest(algae=algae, flavour=flavour, serving_g=mass, inclusion_pct=inclusion)
    preview = check_inputs(request, snapshot)
    formulas, _, audit = screen(request, snapshot, development=True)
    assert preview["can_run"] == bool(formulas)
    assert preview["search_version"] == audit["search_version"]
    assert preview["passing_ids"][:3] == [formula.id for formula in formulas]
    for formula in formulas:
        assert not check_formula(formula, request, snapshot, version=audit["search_version"])
        assert sum(item.grams for item in formula.ingredients) == pytest.approx(mass)
        assert len({item.ingredient_id for item in formula.ingredients}) == len(formula.ingredients)


def test_joint_targets_are_not_satisfied_by_separate_ranges(snapshot):
    base = RunRequest(algae="spirulina", inclusion_pct=5, serving_g=45, flavour="cocoa-spice")
    original = check_inputs(base, snapshot, version=LEGACY_SEARCH_VERSION)
    current = check_inputs(base, snapshot)
    protein_floor = original["margins"]["min_protein_g"]["max"] + 0.2
    sugar_cap = original["margins"]["max_sugar_g"]["min"] + 0.001
    request = base.model_copy(update={"min_protein_g": protein_floor, "max_sugar_g": sugar_cap})
    preview = check_inputs(request, snapshot)
    assert current["margins"]["min_protein_g"]["max"] >= protein_floor
    assert current["margins"]["max_sugar_g"]["min"] <= sugar_cap
    assert not preview["can_run"]
    assert any("all targets together" in message for message in preview["messages"])
    assert not screen(request, snapshot, development=True)[0]


def test_budget_stop_is_not_reported_as_global_impossibility(snapshot):
    request = _request(algae="spirulina", flavour="cocoa-spice", inclusion_pct=5, min_protein_g=8)
    assert screen(request, snapshot, development=True)[0]
    formulas, _, audit = screen(request, snapshot, development=True, candidate_budget=1)
    assert not formulas
    assert audit["truncated"] and audit["status"] == "search_budget_exhausted"
    assert "not proof" in audit["reason"]
    preview = check_inputs(request, snapshot, candidate_budget=1)
    assert not preview["can_run"]
    assert any("not proof" in message for message in preview["messages"])
    assert preview["passing_ids"] == []


def test_whey_proportion_is_checked_independently(snapshot):
    request = RunRequest(algae="spirulina")
    formula = make_formula("off", {"IF-SPI-PWD": 2.25, "IF-DATE-DRIED": 11.25, "IF-COCOA-PWD": 0.225,
                                   "IF-CINN-PWD": 0.225, "IF-WHEY-PWD": 8, "IF-OAT-DRY": 23.05}, 45)
    assert any("Protein-base proportion" in error for error in check_formula(formula, request, snapshot))


def test_historical_report_keeps_nine_recipe_wording():
    result = RunResult(
        run_id="historical", created_at="2026-10-25T00:00:00+00:00", mode="rag_development",
        request=RunRequest(algae="spirulina"), status="report_ready", trace=[], sensory_map=[], evidence=[],
        formulations=[make_formula("S25-1", {"IF-SPI-PWD": 2.25, "IF-OAT-DRY": 42.75}, 45)], controls=[],
        impact={"nutrition": {"S25-1": {"per_serving": {"protein_g": 5, "energy_kcal": 150, "sugar_g": 8}}},
                "screening": {"search_version": "exact-form-grid-v1", "scope": "Nine-point engineering grid only"}},
        limitations=[])
    text = interpret(result)
    assert "nine recipe variations" in text["reason"]
    assert "whey" not in text["reason"]
    current = result.model_copy(update={"impact": {**result.impact, "screening": {"search_version": "protein-base-grid-v2"}}})
    assert "protein-base grid" in interpret(current)["reason"]
    assert "Whey protein powder isolate" in interpret(current)["ingredient_names"]["IF-WHEY-PWD"]
