"""Build a new nutrition staging snapshot; never modify frozen historical data.

Sugar is USDA nutrient 2000 (total, not added). Retain source derivations and
exclude assumed/unsubstantiated zeros. Replace the complete chlorella reference,
never mix the supplier label with the previous laboratory-method profile.
"""
import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services"))
from algamask.dataset import load_dataset
from algamask.dataset_schema import full_cols
from algamask.publication import canonical, verify

ARCHIVE_SHA256 = "b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0"
ARCHIVE_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip"


def read_table(directory, table):
    with (directory / f"{table}.csv").open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_table(directory, table, records):
    with (directory / f"{table}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[c[0] for c in full_cols(table)])
        writer.writeheader()
        writer.writerows(records)


def sync_working_copy(base, staged, target):
    """Mechanical generated-table update; refuse unrelated local edits."""
    sources = sorted((base / 'reviewed').glob('*.csv'))
    for source in sources:
        if (target / source.name).read_bytes() != source.read_bytes():
            raise ValueError(f'Working CSV differs from the base; not overwriting: {source.name}')
    load_dataset(staged)
    for source in sources:
        shutil.copyfile(staged / source.name, target / source.name)


def source_sugar(archive_path, wanted):
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("USDA source archive hash mismatch")
    with ZipFile(archive_path) as archive:
        def rows(name):
            paths = [p for p in archive.namelist() if p.split('/')[-1] == name]
            if len(paths) != 1:
                raise ValueError(f"Expected exactly one {name}")
            with archive.open(paths[0]) as handle:
                yield from csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig"))
        foods = {r['fdc_id']: r for r in rows('food.csv') if r['fdc_id'] in wanted}
        nutrients = {r['id']: r for r in rows('nutrient.csv')}
        if nutrients['2000']['name'] != 'Sugars, Total' or nutrients['2000']['unit_name'] != 'G':
            raise ValueError("Unexpected USDA total-sugar identity/unit")
        derivations = {r['id']: r for r in rows('food_nutrient_derivation.csv')}
        buckets = {fdc: [] for fdc in wanted}
        for row in rows('food_nutrient.csv'):
            if row['fdc_id'] in wanted and row['nutrient_id'] == '2000':
                buckets[row['fdc_id']].append(row)
    results = {}
    for fdc, matches in buckets.items():
        if fdc not in foods or len(matches) > 1:
            raise ValueError(f"Missing food or duplicate sugar records: {fdc}")
        row = matches[0] if matches else {}
        derivation = derivations.get(row.get('derivation_id'), {})
        amount = row.get('amount', '')
        assumed = derivation.get('code') == 'Z' or 'assumed zero' in derivation.get('description', '').lower()
        unsupported_zero = amount != '' and Decimal(amount) == 0 and not derivation and row.get('data_points') in ('', '0')
        usable = amount != '' and not assumed and not unsupported_zero
        if usable and (not Decimal(amount).is_finite() or not 0 <= Decimal(amount) <= 100):
            raise ValueError(f"Invalid sugar value: {fdc}")
        results[fdc] = dict(food=foods[fdc], nutrient=nutrients['2000'], source_record=row,
                            derivation=derivation, value=amount if usable else '',
                            decision='used' if usable else 'unknown_preserved')
    return results


def extend(base, output, archive_path, label_path, audit_path):
    manifest = verify(base)
    load_dataset(base / 'reviewed')
    label = json.loads(label_path.read_text())
    if label['basis'] != 'per_100g' or label['scientific_approval'] is not False:
        raise ValueError('Unexpected supplier extraction basis/approval')
    nutrition = read_table(base / 'reviewed', 'ingredient_nutrition')
    sugar = source_sugar(archive_path, {r['fdc_id'] for r in nutrition if r['fdc_id']})
    audit_rows = []
    for row in nutrition:
        row['sugar_g'] = ''
        if not row['fdc_id']:
            continue
        found = sugar[row['fdc_id']]
        if row['fdc_food_type'] != 'SR Legacy' or row['basis'] != 'per_100g' or row['fdc_data_release'] != found['food']['publication_date']:
            raise ValueError(f"Source identity/date/basis mismatch: {row['nutrition_id']}")
        row['sugar_g'] = found['value']
        row['record_version'] = str(int(row['record_version']) + 1)
        row['source_location'] += '; total sugar: nutrient 2000 (g per 100 g)'
        row['notes'] += ' Total sugar derivation: ' + (found['derivation'].get('code') or 'not supplied') + '. '
        row['notes'] += 'Source absence or assumed/unsubstantiated zero remains blank.'
        audit_rows.append(dict(ingredient_form_id=row['ingredient_form_id'], nutrition_id=row['nutrition_id'], **found))
    matches = [r for r in nutrition if r['ingredient_form_id'] == 'IF-CHL-PWD']
    if len(matches) != 1:
        raise ValueError('Expected exactly one chlorella profile')
    chl = matches[0]
    old_profile = dict(chl)
    for field in ('protein_g', 'energy_kcal', 'carbohydrate_g', 'fat_g', 'sugar_g', 'fibre_g', 'iron_mg', 'omega3_g', 'fdc_id', 'fdc_food_type', 'fdc_data_release'):
        chl[field] = ''
    chl.update(label['values'])
    chl.update(nutrition_id='NUT-CHL-ALGOMED-LABEL', nutrition_source_type='supplier_label',
               value_precision='label_rounded', source_id=label['source_id'],
               source_location=label['source_location'], evidence_status='database_derived',
               review_status='extracted', reviewer='', reviewed_at='',
               record_version=str(int(old_profile['record_version']) + 1),
               match_rationale=label['limitations'], transformation_record='Complete supplier-label reference replaces the old laboratory profile. No Atwater estimate, no combined-source nutrient profile.',
               notes='PENDING HUMAN REVIEW. ' + label['limitations'])
    # Reserve a new staging directory only after source checks; never overwrite.
    output.mkdir(parents=True, exist_ok=False)
    for source in (base / 'reviewed').glob('*.csv'):
        shutil.copyfile(source, output / source.name)
    write_table(output, 'ingredient_nutrition', nutrition)
    sources = read_table(output, 'sources')
    sources.append(dict(source_id=label['source_id'], source_type='supplier_spec',
                        title='Algomed Chlorella Pulver: manufacturer nutrition label',
                        authors=label['supplier'], year='2026', url=label['url'],
                        discovered_via='manual', retrieved_at=label['retrieved_at'],
                        licence=label['rights'], redistribution_allowed='false', full_text_stored='false',
                        why_it_matters='Complete reference-product nutrition profile, not generic species composition.',
                        record_version='1', review_status='extracted', evidence_status='database_derived',
                        notes=label['limitations']))
    write_table(output, 'sources', sources)
    materials = read_table(output, 'algae_materials')
    materials.append(dict(material_id='MAT-CHL-ALGOMED', species_material='chlorella',
                          species_name='Chlorella vulgaris', material_form='powder',
                          processing='Commercial powder; supplier describes phototrophic glass-tube cultivation.',
                          supplier=label['supplier'], composition_source_id=label['source_id'],
                          record_version='1', review_status='extracted', source_id=label['source_id'],
                          source_location=label['source_location'], evidence_status='database_derived',
                          notes=label['limitations']))
    write_table(output, 'algae_materials', materials)
    forms = read_table(output, 'ingredient_forms')
    for form in forms:
        if form['ingredient_form_id'] == 'IF-CHL-PWD':
            form.update(ingredient_name='Algomed chlorella powder (reference)',
                        supplier=label['supplier'], product_code=label['product'], material_id='MAT-CHL-ALGOMED',
                        description=label['limitations'], source_id=label['source_id'],
                        source_location=label['source_location'], evidence_status='database_derived',
                        record_version=str(int(form['record_version']) + 1), notes=label['limitations'])
    write_table(output, 'ingredient_forms', forms)
    snapshot = load_dataset(output)
    audit = dict(base_dataset_hash=manifest['content_hash'], schema_version='1.1.0',
                 archive_url=ARCHIVE_URL, archive_sha256=ARCHIVE_SHA256,
                 label_extraction_sha256=hashlib.sha256(label_path.read_bytes()).hexdigest(),
                 supplier_extraction=label, previous_chlorella_profile=old_profile,
                 usda_sugar=audit_rows, scientific_approval=False,
                 row_counts=snapshot.row_counts,
                 nutrition_csv_sha256=hashlib.sha256((output / 'ingredient_nutrition.csv').read_bytes()).hexdigest())
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open('xb') as handle:
        handle.write(canonical(audit))
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=ROOT / 'data/candidates/0.1.0-rc.4')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--archive', type=Path, default=ROOT / 'data/raw/usda/sr_legacy_verified_download.zip')
    parser.add_argument('--label', type=Path, default=ROOT / 'data/extractions/algomed_chlorella_label_2026-10-25.json')
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--sync-working-copy', action='store_true', help='Update data/reviewed only if every current CSV still matches the base')
    args = parser.parse_args()
    result = extend(args.base, args.output, args.archive, args.label, args.audit)
    if args.sync_working_copy:
        sync_working_copy(args.base, args.output, ROOT / 'data/reviewed')
    print(f"Staged {sum(result['row_counts'].values())} records; scientific approval unchanged")
