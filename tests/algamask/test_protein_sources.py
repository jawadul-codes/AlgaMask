"""Exact reference labels, versioned search, source constraints and compatibility."""
import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from algamask.dataset import load_dataset
from algamask.formulation_engine import (
    ACTIVE_SEARCH_VERSION, PROTEIN_BASE_SEARCH_VERSION, PROTEIN_BASE,
    REFERENCE_WHEY, REFERENCE_PLANT, check_formula, make_formula,
    protein_path, run_grid, screen,
)
from algamask.nutrition import estimate_nutrition
from algamask.preflight import check_inputs
from algamask.publication import verify
from algamask.run_store import RunStore, SubmissionConflict
from algamask.schemas import RunRequest

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / 'data/candidates/0.1.0-rc.6'


@pytest.fixture(scope='module')
def snapshot():
    return load_dataset(NEW / 'reviewed')


def test_frozen_artifacts_and_extraction():
    old = verify(ROOT / 'data/candidates/0.1.0-rc.5')
    assert old['content_hash'] == 'b05a800077d53b3bce3c63bdb527d30bf5b48f5c47e7182a0744f4c1c3f02076'
    new = verify(NEW)
    index = json.loads((ROOT / 'indexes/reviewed_evidence/0.1.0-dev.5/manifest.json').read_text())
    assert index['dataset_hash'] == new['content_hash']
    assert index['development_only'] and not new['runtime_eligible']
    audit = json.loads((ROOT / 'data/extractions/protein_extension_audit_2026-11-07.json').read_text())
    extraction = ROOT / 'data/extractions/myprotein_labels_2026-11-07.json'
    assert hashlib.sha256(extraction.read_bytes()).hexdigest() == audit['extraction_sha256']
    for name, digest in audit['changed_tables'].items():
        assert hashlib.sha256((NEW / f'reviewed/{name}.csv').read_bytes()).hexdigest() == digest


def test_exact_products_not_generic_values(snapshot):
    records = {r.ingredient_form_id: r for r in snapshot.records('ingredient_nutrition')}
    for form, expected in [(REFERENCE_WHEY, (86, 369, 1.7)), (REFERENCE_PLANT, (81, 340, 0))]:
        row = records[form]
        assert (row.protein_g, row.energy_kcal, row.sugar_g) == expected
        assert row.nutrition_source_type == 'supplier_label' and row.value_precision == 'label_rounded'
        assert row.review_status == 'extracted' and row.fdc_id is None
        assert row.iron_mg is None and row.omega3_g is None
    assert records[REFERENCE_WHEY].fibre_g is None
    assert records[REFERENCE_PLANT].fibre_g == 1.5
    assert records['IF-SOY-ISO'].sugar_g is None
    forms = {r.ingredient_form_id: r for r in snapshot.records('ingredient_forms')}
    assert 'soy lecithin' in forms[REFERENCE_WHEY].description
    assert 'fava' in forms[REFERENCE_PLANT].description
    allergens = {(r.ingredient_form_id, r.allergen_id): r.relationship for r in snapshot.records('ingredient_allergens')}
    assert allergens[REFERENCE_WHEY, 'ALG-MILK'] == 'contains'
    assert allergens[REFERENCE_WHEY, 'ALG-SOY'] == 'contains'
    assert allergens[REFERENCE_PLANT, 'ALG-MILK'] == 'may_contain'


@pytest.mark.parametrize('algae', ['spirulina', 'chlorella', 'blend'])
@pytest.mark.parametrize('source', ['auto', 'milk', 'plant'])
@pytest.mark.parametrize('flavour', ['vanilla', 'cocoa-spice'])
@pytest.mark.parametrize('mass,inclusion', [(40, 1), (50, 15)])
def test_full_grid_source_mass_nutrients_and_shared_preflight(snapshot, algae, source, flavour, mass, inclusion):
    request = RunRequest(algae=algae, protein_source=source, flavour=flavour,
                         serving_g=mass, inclusion_pct=inclusion,
                         min_protein_g=10, max_energy_kcal=220, max_sugar_g=12)
    found = run_grid(request, snapshot)
    preview = check_inputs(request, snapshot)
    assert len(found['generated']) == len(found['audit']['verdicts']) == 90
    assert len({f.id for f in found['generated']}) == 90
    assert len(found['selected']) == 3 and preview['can_run']
    assert preview['selected_ids'] == [f.id for f in found['selected']]
    assert preview['passing_ids'] == found['audit']['passing_ids']
    paths = [protein_path(f) for f in found['selected']]
    assert paths[:2] == ['milk', 'plant'] if source == 'auto' else set(paths) == {source}
    for formula in found['selected']:
        assert sum(i.grams for i in formula.ingredients) == pytest.approx(request.serving_g)
        assert not check_formula(formula, request, snapshot)
        estimate = estimate_nutrition(formula, snapshot, approved_only=False)
        assert estimate.per_serving['protein_g'] >= 10
        assert estimate.per_serving['energy_kcal'] <= 220
        assert 0 < estimate.per_serving['sugar_g'] <= 12
    selected_powder = {i.ingredient_id: i.grams for i in found['selected'][0].ingredients if i.role == 'protein_base'}
    for control in found['controls']:
        assert {i.ingredient_id: i.grams for i in control.ingredients if i.role == 'protein_base'} == selected_powder
        assert not check_formula(control, request, snapshot, baseline=control.id == 'B0', check_targets=False, check_grid=False)


def test_new_paths_expand_supported_range(snapshot):
    request = RunRequest(algae='chlorella', inclusion_pct=3, serving_g=45, flavour='vanilla')
    old = check_inputs(request, snapshot, version=PROTEIN_BASE_SEARCH_VERSION)
    for source in ('milk', 'plant'):
        preview = check_inputs(request.model_copy(update={'protein_source': source}), snapshot)
        assert preview['margins']['min_protein_g']['max'] > old['margins']['min_protein_g']['max']
    found = run_grid(request, snapshot)
    assert {i.ingredient_id for f in found['generated'] for i in f.ingredients}.isdisjoint({'IF-SOY-ISO'})
    assert sum(protein_path(f) == 'none' for f in found['generated']) == 9
    assert sum(protein_path(f) == 'milk' for f in found['generated']) == 54
    assert sum(protein_path(f) == 'plant' for f in found['generated']) == 27


@pytest.mark.parametrize('exclusions,source,expected', [
    (['milk'], 'auto', 'plant'), (['milk'], 'plant', 'plant'),
    (['soy'], 'auto', 'plant'), (['soy'], 'milk', 'milk'),
    (['milk', 'soy'], 'auto', 'plant'), (['milk'], 'milk', None),
])
def test_actual_ingredient_preferences(snapshot, exclusions, source, expected):
    request = RunRequest(exclusions=exclusions, exclusion_mode='ingredient_preference', protein_source=source)
    found = run_grid(request, snapshot)
    assert bool(found['selected']) == (expected is not None)
    if expected:
        assert protein_path(found['selected'][0]) == expected
        for f in found['selected']:
            ids = {i.ingredient_id for i in f.ingredients}
            assert REFERENCE_WHEY not in ids  # both milk and soy declared
            if 'milk' in exclusions:
                assert PROTEIN_BASE not in ids
    strict = check_inputs(request.model_copy(update={'exclusion_mode': 'verified_free_from'}), snapshot)
    assert not strict['can_run'] and not strict['margins']


@pytest.mark.parametrize('source', ['auto', 'milk', 'plant'])
def test_sugar_zero_and_citrus_unknown_still_block(snapshot, source):
    zero = check_inputs(RunRequest(protein_source=source, max_sugar_g=0), snapshot)
    assert not zero['can_run'] and zero['margins']['max_sugar_g']['min'] > 0
    citrus = check_inputs(RunRequest(protein_source=source, flavour='citrus', max_sugar_g=20), snapshot)
    assert not citrus['can_run'] and citrus['margins']['max_sugar_g']['max'] is None
    assert 'IF-ORANGE-PEEL' in str(citrus['messages'])
    assert check_inputs(RunRequest(protein_source=source, flavour='citrus'), snapshot)['can_run']


def test_critic_rejects_mixed_powders_wrong_source_and_off_grid(snapshot):
    request = RunRequest(algae='spirulina', protein_source='plant')
    amounts = {'IF-SPI-PWD': 2.25, 'IF-DATE-DRIED': 11.25, 'IF-COCOA-PWD': .225,
               'IF-CINN-PWD': .225, REFERENCE_WHEY: 4.5, REFERENCE_PLANT: 4.5, 'IF-OAT-DRY': 22.05}
    errors = check_formula(make_formula('tampered', amounts, 45), request, snapshot)
    assert 'Only one protein powder is allowed per recipe.' in errors
    assert 'Protein powder does not match the requested source.' in errors
    amounts.pop(REFERENCE_WHEY)
    amounts[REFERENCE_PLANT] = 8
    amounts['IF-OAT-DRY'] = 23.05
    assert any('Protein-base proportion' in e for e in check_formula(make_formula('off', amounts, 45), request, snapshot))


def test_joint_guidance_actually_passes(snapshot):
    request = RunRequest(algae='chlorella', inclusion_pct=3, flavour='vanilla',
                         protein_source='plant', min_protein_g=12, max_energy_kcal=170, max_sugar_g=0)
    preview = check_inputs(request, snapshot)
    limit = preview['margins']['max_sugar_g']['suggested_limit']
    assert limit is not None and limit > 0
    adjusted = request.model_copy(update={'max_sugar_g': limit})
    assert check_inputs(adjusted, snapshot)['can_run']
    assert screen(adjusted, snapshot, development=True)[0]


@pytest.mark.parametrize('nutrient,target', [('sugar_g', 'max_sugar_g'), ('energy_kcal', 'max_energy_kcal'), ('protein_g', 'min_protein_g')])
def test_missing_product_nutrition_is_not_zero(snapshot, nutrient, target):
    from copy import deepcopy
    broken = deepcopy(snapshot)
    row = next(r for r in broken.records('ingredient_nutrition') if r.ingredient_form_id == REFERENCE_PLANT)
    object.__setattr__(row, nutrient, None)  # Deliberately corrupt only this test copy.
    request = RunRequest(protein_source='plant', **{target: 20})
    preview = check_inputs(request, broken)
    assert not preview['can_run'] and preview['margins'][target]['max'] is None
    assert not screen(request, broken, development=True)[0]


def test_controls_do_not_replace_failing_candidates(snapshot):
    request = RunRequest(algae='spirulina', protein_source='milk', min_protein_g=15)
    found = run_grid(request, snapshot)
    assert found['selected']
    # Algae removal lowers protein below the candidate minimum in B0.
    assert any('min_protein_g' in error for error in check_formula(
        found['controls'][0], request, snapshot, baseline=True, check_grid=False))
    assert not check_formula(found['controls'][0], request, snapshot, baseline=True,
                             check_grid=False, check_targets=False)
    impossible = request.model_copy(update={'min_protein_g': 50})
    assert not check_inputs(impossible, snapshot)['can_run']
    formulas, controls, _ = screen(impossible, snapshot, development=True)
    assert not formulas and not controls


def test_legacy_submission_hash_and_explicit_source_conflict(tmp_path):
    store = RunStore(tmp_path / 'runs.db')
    request = RunRequest()
    job, _ = store.reserve('legacy-auto-key', request, {'search_version': PROTEIN_BASE_SEARCH_VERSION})
    values = request.model_dump(mode='json')
    for key in ('experiment', 'exclusion_mode', 'protein_source'):
        values.pop(key)
    old_payload = json.dumps(values, sort_keys=True, separators=(',', ':'))
    with store.connection() as db:
        db.execute('UPDATE jobs SET request_hash=?, request_json=? WHERE job_id=?',
                   (hashlib.sha256(old_payload.encode()).hexdigest(), old_payload, job['job_id']))
    replay, token = store.reserve('legacy-auto-key', RunRequest(protein_source='auto'), {'search_version': ACTIVE_SEARCH_VERSION})
    assert token is None and replay['job_id'] == job['job_id']
    assert replay['context']['search_version'] == PROTEIN_BASE_SEARCH_VERSION
    with pytest.raises(SubmissionConflict):
        store.reserve('legacy-auto-key', RunRequest(protein_source='plant'), {})


def test_api_validation_and_mock_source_rejection():
    from algamask.api import app
    client = TestClient(app)
    assert client.post('/runs', json={'protein_source': 'soy'}).status_code == 422
    assert client.post('/runs', json={'protein_source': 'plant'}).status_code == 422
    assert client.post('/runs', json={'experiment': 'spirulina-proof-v1', 'algae': 'spirulina',
                                    'inclusion_pct': 2, 'protein_source': 'milk'}).status_code == 422
