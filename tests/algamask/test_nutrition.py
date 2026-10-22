from pathlib import Path

import pytest

from algamask.dataset import DatasetSnapshot, load_dataset
from algamask.nutrition import calculate_nutrient, estimate_nutrition
from algamask.schemas import Formulation, IngredientAmount


@pytest.fixture(scope="module")
def snapshot():
    return load_dataset(Path(__file__).resolve().parents[2] / "data/candidates/0.1.0-rc.1/reviewed")


def formula(*amounts):
    return Formulation(id="test", name="test", total_g=sum(g for _, g in amounts),
                       ingredients=[IngredientAmount(ingredient_id=i, grams=g, role="test") for i, g in amounts])


def test_exact_values_and_provenance(snapshot):
    result = estimate_nutrition(formula(("IF-SPI-PWD", 5), ("IF-OAT-DRY", 40)), snapshot, approved_only=False)
    assert result.per_serving["protein_g"] == pytest.approx(5 * .5747 + 40 * .1315)
    assert result.per_serving["energy_kcal"] == pytest.approx(166.1)
    assert result.per_100g["energy_kcal"] == pytest.approx(166.1 * 100 / 45)
    assert result.protein_g_per_100_kcal == pytest.approx(result.per_serving["protein_g"] * 100 / 166.1)
    assert {r["nutrition_id"] for r in result.records} == {"NUT-SPI-PWD", "NUT-OAT-DRY"}
    assert all(r["source_id"] and r["source_location"] for r in result.records)
    assert result.per_serving["sugar_g"] is None
    assert result.per_serving["total_omega3_g"] is None


def test_missing_chlorella_energy_not_zero(snapshot):
    result = estimate_nutrition(formula(("IF-CHL-PWD", 5), ("IF-OAT-DRY", 40)), snapshot, approved_only=False)
    assert result.per_serving["energy_kcal"] is None
    assert result.protein_g_per_100_kcal is None
    assert result.missing["energy_kcal"] == ["IF-CHL-PWD"]
    assert result.per_serving["protein_g"] is not None


def test_approval_default_and_missing_record(snapshot):
    assert estimate_nutrition(formula(("IF-SPI-PWD", 45)), snapshot).per_serving["protein_g"] is None
    result = estimate_nutrition(formula(("IF-RICE-PUFF", 45)), snapshot, approved_only=False)
    assert result.records == []
    assert all(value is None for value in result.per_serving.values())


def test_no_implicit_mock_id_mapping(snapshot):
    with pytest.raises(ValueError, match="Unknown ingredient-form"):
        estimate_nutrition(formula(("date_paste", 45)), snapshot, approved_only=False)


def test_ambiguous_records_fail_closed(snapshot):
    tables = {name: snapshot.records(name) for name in snapshot.row_counts}
    tables["ingredient_nutrition"] += (tables["ingredient_nutrition"][0],)
    result = estimate_nutrition(formula(("IF-SPI-PWD", 45)), DatasetSnapshot(tables, []), approved_only=False)
    assert result.per_serving["protein_g"] is None
    assert any("Ambiguous" in warning for warning in result.warnings)


@pytest.mark.parametrize("amounts", [[(-1, 10)], [(1, -1)], [(float("nan"), 1)], [(1, float("inf"))]])
def test_invalid_numbers(amounts):
    with pytest.raises(ValueError):
        calculate_nutrient(amounts)


def test_zero_mass_and_zero_energy(snapshot):
    assert calculate_nutrient([(0, None), (100, 10)]) == 10
    assert calculate_nutrient([]) is None
    result = estimate_nutrition(formula(("IF-SALT", 1)), snapshot, approved_only=False)
    assert result.per_serving["energy_kcal"] == 0
    assert result.protein_g_per_100_kcal is None
