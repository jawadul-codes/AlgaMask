"""Independently compare first-release nutrition with an original USDA CSV archive.

Read-only for dataset inputs. Writes an audit artifact, never approves records.
"""
import argparse
import csv
import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
FOODS = {
    'IF-SPI-PWD': ('170495', 'Seaweed, spirulina, dried'),
    'IF-OAT-DRY': ('173904', 'Cereals, oats, regular and quick, not fortified, dry'),
    'IF-DATE-DRIED': ('171726', 'Dates, deglet noor'),
    'IF-COCOA-PWD': ('169593', 'Cocoa, dry powder, unsweetened'),
    'IF-CINN-PWD': ('171320', 'Spices, cinnamon, ground'),
}
FIELDS = {
    'protein_g': ('1003', 'G'), 'energy_kcal': ('1008', 'KCAL'),
    'carbohydrate_g': ('1005', 'G'), 'fat_g': ('1004', 'G'),
    'fibre_g': ('1079', 'G'), 'iron_mg': ('1089', 'MG'),
    'omega3_g': ('1404', 'G'),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'data/raw/usda/sr_legacy_verified_download.zip')
    parser.add_argument('--dataset', type=Path, default=ROOT / 'data/reviewed')
    parser.add_argument('--output', type=Path, default=ROOT / 'output/review/scoped_nutrition_audit.json')
    args = parser.parse_args()
    dataset_file = args.dataset / 'ingredient_nutrition.csv'
    with dataset_file.open() as handle:
        local_rows = list(csv.DictReader(handle))
    failures, results = [], []
    with ZipFile(args.archive) as archive:
        def rows(name):
            matches = [n for n in archive.namelist() if n.split('/')[-1] == name]
            if len(matches) != 1:
                raise ValueError(f'Expected exactly one {name}: {matches}')
            with archive.open(matches[0]) as handle:
                yield from csv.DictReader(io.TextIOWrapper(handle, encoding='utf-8-sig'))
        foods = {r['fdc_id']: r for r in rows('food.csv')}
        nutrients = {r['id']: r for r in rows('nutrient.csv')}
        derivations = {r['id']: r for r in rows('food_nutrient_derivation.csv')}
        wanted = {v[0] for v in FOODS.values()}
        values = {}
        for row in rows('food_nutrient.csv'):
            if row['fdc_id'] in wanted:
                values.setdefault((row['fdc_id'], row['nutrient_id']), []).append(row)
        for form, (fdc, name) in FOODS.items():
            matches = [r for r in local_rows if r['ingredient_form_id'] == form]
            if len(matches) != 1:
                failures.append(f'{form}: missing/duplicate local record')
                continue
            local, food = matches[0], foods.get(fdc, {})
            metadata_ok = (local['fdc_id'] == fdc and local['basis'] == 'per_100g'
                           and local['fdc_food_type'] == 'SR Legacy'
                           and food.get('data_type') == 'sr_legacy_food'
                           and food.get('description') == name
                           and local['fdc_data_release'] == food.get('publication_date'))
            if not metadata_ok:
                failures.append(f'{form}: food identity/basis/date mismatch')
            checks = []
            for field, (nid, unit) in FIELDS.items():
                found = values.get((fdc, nid), [])
                source = found[0] if len(found) == 1 else {}
                derivation = derivations.get(source.get('derivation_id'), {})
                amount = source.get('amount', '')
                recorded = local[field]
                assumed = 'assumed' in derivation.get('description', '').lower()
                metadata = nutrients.get(nid, {})
                if len(found) > 1:
                    status = 'duplicate_source_values'
                elif recorded:
                    same = bool(amount) and Decimal(recorded) == Decimal(amount)
                    status = 'match' if same and metadata.get('unit_name', '').upper() == unit and not assumed else 'mismatch_or_unsupported'
                elif not amount:
                    status = 'missing_preserved'
                elif assumed:
                    status = 'assumed_value_excluded'
                else:
                    status = 'source_value_not_used'
                if status in ('duplicate_source_values', 'mismatch_or_unsupported'):
                    failures.append(f'{form}.{field}: {status}')
                checks.append({'field': field, 'nutrient_id': nid, 'local_value': recorded,
                               'source_value': amount, 'nutrient': metadata,
                               'source_record': source, 'derivation': derivation, 'status': status})
            results.append({'ingredient_form_id': form, 'nutrition_id': local['nutrition_id'],
                            'food': food, 'metadata_match': metadata_ok, 'checks': checks})
    report = {
        'source_url': 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip',
        'archive_sha256': hashlib.sha256(args.archive.read_bytes()).hexdigest(),
        'dataset_file_sha256': hashlib.sha256(dataset_file.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'results': results, 'failures': failures, 'scientific_approval': False,
        'limitations': ['Generic foods, not supplier lots.',
                        'Nutrient 1404 is ALA only, not total omega-3.',
                        'Blank values are not zero; source_value_not_used needs review.',
                        'Numeric agreement is not approval of ingredient suitability.'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'foods_checked': len(results), 'failures': failures,
                      'statuses': {r['ingredient_form_id']: {c['field']: c['status'] for c in r['checks']} for r in results},
                      'report': str(args.output)}, indent=2))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
