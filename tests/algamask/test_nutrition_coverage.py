"""New nutrition references and strict historical compatibility."""
import csv
import hashlib
import json
import shutil
import runpy
from pathlib import Path

import pytest

from algamask.dataset import DatasetValidationError, load_dataset
from algamask.nutrition import estimate_nutrition
from algamask.preflight import check_inputs
from algamask.publication import verify
from algamask.schemas import Formulation, IngredientAmount, RunRequest

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / 'data/candidates/0.1.0-rc.5'


@pytest.fixture(scope='module')
def snapshot():
    return load_dataset(NEW / 'reviewed')


def formula(*amounts):
    return Formulation(id='test', name='test', total_g=sum(g for _, g in amounts),
                       ingredients=[IngredientAmount(ingredient_id=i, grams=g, role='test') for i, g in amounts])


@pytest.mark.parametrize('version', ['0.1.0-rc.1', '0.1.0-rc.2', '0.1.0-rc.3', '0.1.0-rc.4'])
def test_frozen_legacy_reports_still_verify(version):
    path = ROOT / 'data/candidates' / version
    assert verify(path)['schema_version'] == '1.0.0'
    assert all(r.sugar_g is None for r in load_dataset(path / 'reviewed').records('ingredient_nutrition'))


def test_new_schema_and_label_profile(snapshot):
    assert verify(NEW)['schema_version'] == '1.1.0'
    rows = [r for r in snapshot.records('ingredient_nutrition') if r.ingredient_form_id == 'IF-CHL-PWD']
    assert len(rows) == 1
    r = rows[0]
    assert (r.protein_g, r.energy_kcal, r.carbohydrate_g, r.fat_g, r.sugar_g) == (51.9, 377, 9.2, 9.3, .6)
    assert r.fibre_g is None and r.iron_mg is None and r.omega3_g is None
    assert r.fdc_id is None and r.source_id == 'SRC-ALGOMED-POWDER-2026'
    assert r.review_status == 'extracted' and r.value_precision == 'label_rounded'
    f = next(f for f in snapshot.records('ingredient_forms') if f.ingredient_form_id == 'IF-CHL-PWD')
    assert f.material_id == 'MAT-CHL-ALGOMED' and 'reference' in f.ingredient_name


def test_sugar_is_weighted_total_not_added_or_carbohydrate(snapshot):
    n = estimate_nutrition(formula(('IF-CHL-PWD', 1.35), ('IF-OAT-DRY', 31.95),
                                  ('IF-DATE-DRIED', 11.25), ('IF-VAN-EXT', .45)), snapshot, approved_only=False)
    expected = 1.35 * .6 / 100 + 31.95 * .99 / 100 + 11.25 * 63.35 / 100 + .45 * 12.65 / 100
    assert n.per_serving['sugar_g'] == pytest.approx(expected)
    assert n.per_100g['sugar_g'] == pytest.approx(expected * 100 / 45)
    assert n.missing['sugar_g'] == [] and n.per_serving['energy_kcal'] is not None
    assert n.per_serving['sugar_g'] != n.per_serving['carbohydrate_g']
    assert any('named supplier reference' in w for w in n.warnings)
    supplier = next(r for r in n.records if r['ingredient_form_id'] == 'IF-CHL-PWD')
    assert supplier['source_url'] == 'https://algomed.de/products/algomed-chlorella-pulver'
    assert supplier['ingredient_name'] == 'Algomed chlorella powder (reference)'
    assert n.per_serving['total_omega3_g'] is None


@pytest.mark.parametrize('form', ['IF-ORANGE-PEEL', 'IF-SALT', 'IF-COCO-OIL', 'IF-SOY-ISO'])
def test_missing_and_assumed_zero_sugar_stay_unknown(snapshot, form):
    n = estimate_nutrition(formula((form, 1), ('IF-OAT-DRY', 44)), snapshot, approved_only=False)
    assert n.per_serving['sugar_g'] is None
    assert n.missing['sugar_g'] == [form]


@pytest.mark.parametrize('algae', ['spirulina', 'chlorella', 'blend'])
@pytest.mark.parametrize('flavour', ['vanilla', 'cocoa-spice'])
def test_supported_sugar_targets_have_numeric_ranges(snapshot, algae, flavour):
    args = dict(algae=algae, flavour=flavour, inclusion_pct=3, serving_g=45,
                min_protein_g=5, max_energy_kcal=200, max_sugar_g=10)
    result = check_inputs(RunRequest(**args), snapshot)
    assert result['can_run'] and result['candidate_count'] > 0
    assert all(m['known_candidates'] == 27 for m in result['margins'].values())
    impossible = check_inputs(RunRequest(**{**args, 'max_sugar_g': 0}), snapshot)
    assert not impossible['can_run'] and impossible['candidate_count'] == 0
    assert any('Raise the maximum' in m for m in impossible['messages'])
    if algae != 'spirulina':
        assert any('Algomed' in note for note in result['notes'])


def test_citrus_gap_blocks_only_requested_sugar_target(snapshot):
    assert check_inputs(RunRequest(flavour='citrus'), snapshot)['can_run']
    result = check_inputs(RunRequest(flavour='citrus', max_sugar_g=20), snapshot)
    assert not result['can_run'] and result['margins']['max_sugar_g']['known_candidates'] == 0
    assert any('required data is missing' in m for m in result['messages'])


@pytest.mark.parametrize('value,message', [('-1', 'between 0 and 100'), ('101', 'between 0 and 100'),
                                         ('NaN', 'finite'), ('90', 'exceeds total carbohydrate')])
def test_invalid_sugar_rejected(tmp_path, value, message):
    path = tmp_path / 'reviewed'
    shutil.copytree(NEW / 'reviewed', path)
    target = path / 'ingredient_nutrition.csv'
    with target.open() as handle:
        reader = csv.DictReader(handle)
        fields, records = reader.fieldnames, list(reader)
    records[0]['sugar_g'] = value
    with target.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    with pytest.raises(DatasetValidationError, match=message):
        load_dataset(path)


def test_recorded_source_audit_matches_frozen_data(snapshot):
    audit = json.loads((ROOT / 'output/review/nutrition_step3_sources.json').read_text())
    label = ROOT / 'data/extractions/algomed_chlorella_label_2026-10-25.json'
    assert hashlib.sha256(label.read_bytes()).hexdigest() == audit['label_extraction_sha256']
    assert hashlib.sha256((NEW / 'reviewed/ingredient_nutrition.csv').read_bytes()).hexdigest() == audit['nutrition_csv_sha256']
    records = {r.ingredient_form_id: r for r in snapshot.records('ingredient_nutrition')}
    for item in audit['usda_sugar']:
        r = records[item['ingredient_form_id']]
        assert r.fdc_id == int(item['food']['fdc_id'])
        assert item['nutrient']['id'] == '2000' and item['nutrient']['unit_name'] == 'G'
        if item['decision'] == 'used':
            assert r.sugar_g == float(item['source_record']['amount'])
            assert item['derivation'].get('code') != 'Z'
        else:
            assert r.sugar_g is None


def test_schema_manifest_cannot_mislabel_new_header_as_legacy(tmp_path):
    copied = tmp_path / 'candidate'
    shutil.copytree(NEW, copied)
    path = copied / 'manifest.json'
    value = json.loads(path.read_text())
    value['schema_version'] = '1.0.0'
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='does not match dataset'):
        verify(copied)


def test_legacy_header_exception_does_not_accept_other_missing_columns(tmp_path):
    copied = tmp_path / 'reviewed'
    shutil.copytree(NEW / 'reviewed', copied)
    path = copied / 'ingredient_nutrition.csv'
    with path.open() as handle:
        rows = list(csv.reader(handle))
    position = rows[0].index('iron_mg')
    with path.open('w', newline='') as handle:
        csv.writer(handle).writerows([row[:position] + row[position + 1:] for row in rows])
    with pytest.raises(DatasetValidationError, match='header mismatch'):
        load_dataset(copied)


def test_extension_sync_preserves_dirty_working_copy(tmp_path):
    base = ROOT / 'data/candidates/0.1.0-rc.4'
    target = tmp_path / 'reviewed'
    shutil.copytree(base / 'reviewed', target)
    path = target / 'sources.csv'
    changed = path.read_bytes() + b'\n'
    path.write_bytes(changed)
    sync = runpy.run_path(str(ROOT / 'tools/extend_nutrition_dataset.py'))['sync_working_copy']
    with pytest.raises(ValueError, match='not overwriting'):
        sync(base, NEW / 'reviewed', target)
    assert path.read_bytes() == changed
    assert (target / 'ingredient_nutrition.csv').read_bytes() == (base / 'reviewed/ingredient_nutrition.csv').read_bytes()
