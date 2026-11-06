"""Append exact reference products to verified rc.5; never rewrite frozen artifacts."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from extend_nutrition_dataset import ROOT, read_table, write_table
from algamask.dataset import load_dataset
from algamask.publication import canonical, verify

BASE_HASH = 'b05a800077d53b3bce3c63bdb527d30bf5b48f5c47e7182a0744f4c1c3f02076'


def extend(output, audit_path, sync=False):
    base = ROOT / 'data/candidates/0.1.0-rc.5'
    manifest = verify(base)
    if manifest['content_hash'] != BASE_HASH:
        raise ValueError('Unexpected base dataset')
    label_path = ROOT / 'data/extractions/myprotein_labels_2026-11-07.json'
    label = json.loads(label_path.read_text())
    if label['scientific_approval'] is not False:
        raise ValueError('Reference extraction must not imply approval')
    tables = {name: read_table(base / 'reviewed', name) for name in
              ('sources', 'ingredient_forms', 'ingredient_nutrition', 'ingredient_allergens')}
    if sync:
        for path in (base / 'reviewed').glob('*.csv'):
            if read_table(ROOT / 'data/reviewed', path.stem) != read_table(base / 'reviewed', path.stem):
                raise ValueError(f'Working table differs from base: {path.name}')
    for product in label['products']:
        if product['basis'] != 'per_100g':
            raise ValueError('Unexpected label basis')
        notes = label['limitations'] + ' ' + product['notes']
        provenance = dict(record_version='1', review_status='extracted', evidence_status='database_derived',
                          source_id=product['source_id'], source_location=product['source_location'], notes=notes)
        tables['sources'].append(dict(source_id=product['source_id'], source_type='supplier_spec',
            title=product['name'] + ': manufacturer label', authors=product['supplier'], year='2026',
            url=product['url'], discovered_via='manual', retrieved_at=label['retrieved_at'],
            licence=label['rights'], redistribution_allowed='false', full_text_stored='false',
            why_it_matters='Exact product nutrition and ingredient/allergen declaration.',
            **{k: v for k, v in provenance.items() if k not in ('source_id', 'source_location')}))
        tables['ingredient_forms'].append(dict(ingredient_form_id=product['ingredient_form_id'],
            ingredient_name=product['name'], form_type='isolate', ingredient_role='protein_base',
            supplier=product['supplier'], product_code=product['product_code'],
            description=product['ingredients'] + ' ' + product['allergen_statement'], **provenance))
        tables['ingredient_nutrition'].append(dict(nutrition_id='NUT-' + product['ingredient_form_id'][3:],
            ingredient_form_id=product['ingredient_form_id'], basis=product['basis'], **product['values'],
            nutrition_source_type='supplier_label', value_precision='label_rounded',
            match_rationale='Exact named unflavoured product and market; entire profile from one label.',
            transformation_record='Per-100 g declared values transcribed without conversion. Undeclared values blank.',
            **provenance))
        for allergen, relationship in product['allergens'].items():
            tables['ingredient_allergens'].append(dict(
                ingredient_allergen_id='IA-' + product['ingredient_form_id'][3:] + '-' + allergen[4:],
                ingredient_form_id=product['ingredient_form_id'], allergen_id=allergen,
                relationship=relationship, **{**provenance, 'notes': product['allergen_statement'] + ' ' + notes}))
    output.mkdir(parents=True, exist_ok=False)
    for path in (base / 'reviewed').glob('*.csv'):
        shutil.copyfile(path, output / path.name)
    for name, rows in tables.items():
        write_table(output, name, rows)
    snapshot = load_dataset(output)
    audit = dict(base_dataset_hash=BASE_HASH, scientific_approval=False,
                 extraction_sha256=hashlib.sha256(label_path.read_bytes()).hexdigest(),
                 extraction=label, row_counts=snapshot.row_counts,
                 changed_tables={name: hashlib.sha256((output / f'{name}.csv').read_bytes()).hexdigest() for name in tables})
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open('xb') as handle:
        handle.write(canonical(audit))
    if sync:
        for name in tables:
            target = ROOT / f'data/reviewed/{name}.csv'
            content = (output / f'{name}.csv').read_bytes()
            # Frozen artifacts retain canonical bytes; working CSVs retain
            # their existing newline convention to avoid unrelated diffs.
            if b'\r\n' not in target.read_bytes():
                content = content.replace(b'\r\n', b'\n')
            target.write_bytes(content)
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--sync-working-copy', action='store_true')
    args = parser.parse_args()
    result = extend(args.output, args.audit, args.sync_working_copy)
    print(f"Staged {sum(result['row_counts'].values())} records; development only")
