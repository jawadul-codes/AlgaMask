"""Exercise the scoped audit against changed values and duplicate input records.

Requires the downloaded USDA archive; uses temporary copies, not runtime records.
"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with (ROOT / 'data/reviewed/ingredient_nutrition.csv').open() as handle:
        reader = csv.DictReader(handle)
        fields, original = reader.fieldnames, list(reader)
    cases = ('changed_protein', 'changed_sugar', 'wrong_basis', 'duplicate_record')
    with tempfile.TemporaryDirectory(prefix='algamask-nutrition-audit-') as directory:
        work = Path(directory)
        for case in cases:
            rows = [dict(r) for r in original]
            selected = next(r for r in rows if r['ingredient_form_id'] == 'IF-SPI-PWD')
            if case == 'changed_protein':
                selected['protein_g'] = '999'
            elif case == 'changed_sugar':
                selected['sugar_g'] = '0'
            elif case == 'wrong_basis':
                selected['basis'] = 'per_serving'
            else:
                rows.append(dict(selected))
            with (work / 'ingredient_nutrition.csv').open('w') as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools/audit_scoped_nutrition.py'),
                 '--dataset', str(work), '--output', str(work / 'result.json')],
                capture_output=True, text=True,
            )
            if result.returncode != 1 or not (work / 'result.json').exists():
                raise AssertionError(f'{case} did not fail as expected: {result.stdout} {result.stderr}')
            import json
            report = json.loads((work / 'result.json').read_text())
            if not report['failures']:
                raise AssertionError(f'{case} returned no audit findings')
            print(f'PASS: {case} rejected')


if __name__ == '__main__':
    main()
