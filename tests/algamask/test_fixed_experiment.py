import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from algamask.dataset import load_dataset
from algamask.formulation_engine import check_formula, impact, screen
from algamask.schemas import RunRequest
from algamask.run_store import RunStore


def request(**overrides):
    return RunRequest(**{**dict(experiment="spirulina-proof-v1", algae="spirulina",
                              inclusion_pct=2, serving_g=45, flavour="cocoa-spice"), **overrides})


@pytest.fixture(scope="module")
def snapshot():
    return load_dataset(Path(__file__).resolve().parents[2] / "data/candidates/0.1.0-rc.4/reviewed")


def test_exact_frozen_arms_and_comparison(snapshot):
    candidate, controls, audit = screen(request(), snapshot, development=True)
    assert [f.id for f in controls + candidate] == ["B0", "A0", "A1"]
    expected = {
        "B0": {"IF-OAT-DRY": 30.60, "IF-DATE-DRIED": 13.50, "IF-COCOA-PWD": .90},
        "A0": {"IF-OAT-DRY": 29.70, "IF-DATE-DRIED": 13.50, "IF-COCOA-PWD": .90, "IF-SPI-PWD": .90},
        "A1": {"IF-OAT-DRY": 29.25, "IF-DATE-DRIED": 13.50, "IF-COCOA-PWD": .90, "IF-SPI-PWD": .90, "IF-CINN-PWD": .45},
    }
    for arm in controls + candidate:
        assert {i.ingredient_id: i.grams for i in arm.ingredients} == expected[arm.id]
        assert sum(i.grams for i in arm.ingredients) == pytest.approx(45)
        assert not check_formula(arm, request(), snapshot, baseline=arm.id == "B0")
        assert not any(i.chunk_ids for i in arm.ingredients)
    assert audit["search_version"] == "spirulina-proof-v1"
    assert not audit["production_eligible"]
    assert audit["assumptions"]["finished_mass_g"] is None
    result = impact(candidate, controls, snapshot)
    assert result["sensory_change_pct"] is None
    values = result["nutrition"]
    assert result["nutrition_change_pct"] == pytest.approx(
        (values["A1"]["protein_g_per_100_kcal"] / values["B0"]["protein_g_per_100_kcal"] - 1) * 100)
    assert (candidate, controls, audit) == screen(request(), snapshot, development=True)


@pytest.mark.parametrize("overrides", [dict(algae="blend"), dict(algae="chlorella"),
    dict(inclusion_pct=5), dict(serving_g=50), dict(flavour="vanilla")])
def test_conflicting_settings_rejected(overrides):
    with pytest.raises(ValidationError, match="requires spirulina"):
        request(**overrides)


@pytest.mark.parametrize("overrides", [dict(exclusions=["oats"]), dict(exclusions=["milk"]),
    dict(min_protein_g=50), dict(max_energy_kcal=1), dict(max_sugar_g=5)])
def test_constraints_block_without_substitution(snapshot, overrides):
    candidates, controls, audit = screen(request(**overrides), snapshot, development=True)
    assert not candidates and not controls
    assert audit["status"] == "fixed_experiment_blocked"
    assert any(audit["verdicts"].values())


def test_production_and_mock_blocked(snapshot):
    from algamask.agents.supervisor import run_workflow
    assert screen(request(), snapshot, development=False)[:2] == ([], [])
    with pytest.raises(ValueError, match="mock execution"):
        run_workflow(request())


def test_mutated_mass_balanced_arm_rejected(snapshot):
    candidates, _, _ = screen(request(), snapshot, development=True)
    arm = candidates[0].model_copy(deep=True)
    arm.ingredients[0].grams += .1
    arm.ingredients[-1].grams -= .1
    assert any("Fixed experiment" in e for e in check_formula(arm, request(), snapshot))


def test_legacy_submission_hash_unchanged(tmp_path):
    store = RunStore(tmp_path / "runs.db")
    original = RunRequest()
    legacy = original.model_dump(mode="json", exclude={"experiment", "exclusion_mode"})
    digest = hashlib.sha256(json.dumps(legacy, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    job, _ = store.reserve("old-client-submission", original, {})
    with store.connection() as db:
        assert db.execute("SELECT request_hash FROM jobs WHERE job_id=?", (job["job_id"],)).fetchone()[0] == digest
    assert store.reserve("old-client-submission", original, {})[1] is None
