# First-release nutrition source audit

Completed: 2026-10-24. Outcome: numeric transcription verified; scientific approval
and supplier matching remain pending.

## Evidence checked

Downloaded the April 2018 SR Legacy CSV archive from the
[official USDA download page](https://fdc.nal.usda.gov/download-datasets/).
Archive URL:
https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip

Local complete archive: `data/raw/usda/sr_legacy_verified_download.zip` (ignored by Git).
SHA-256: `b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0`.
This hash records the downloaded bytes; it is not a separately supplied USDA signature.

The independent audit reads food.csv, food_nutrient.csv, nutrient.csv and
food_nutrient_derivation.csv directly from the archive. It does not reuse the
dataset builder's extraction functions or rewrite any scientific record.

## Results

| Ingredient | FDC ID | Protein g/100 g | Energy kcal/100 g | Result |
| --- | --- | ---: | ---: | --- |
| Spirulina, dried | 170495 | 57.47 | 290 | Match |
| Regular/quick dry oats, not fortified | 173904 | 13.15 | 379 | Match |
| Deglet Noor dates | 171726 | 2.45 | 282 | Match |
| Unsweetened dry cocoa powder | 169593 | 19.6 | 228 | Match |
| Ground cinnamon | 171320 | 3.99 | 247 | Match |

All 31 populated values match: protein, energy, carbohydrate, fat, fibre and iron for
each food, plus cinnamon ALA. Units, exact source food descriptions, food IDs and
record publication dates also match. The four other queried ALA values are absent
in this source mapping and correctly remain blank. No missing value was changed
to zero. Cinnamon's 0.011 g/100 g is nutrient 1404 (ALA), not total omega-3.

The archive release is April 2018; food records carry publication date 2019-04-01.
The local `fdc_data_release` column currently stores the latter and the source notes
identify the archive release separately. No conflicting nutrient numbers were found.

The complete audit artifact includes original nutrient rows, nutrient definitions,
derivation metadata, source food records, dataset input hash and audit-script hash:
`output/review/scoped_nutrition_audit.json`.

## Reproduction and verification

Run from the project root after downloading the archive:

```sh
.venv/bin/python tools/audit_scoped_nutrition.py
.venv/bin/python tools/check_nutrition_audit_failures.py
```

The real-source audit passed with no mismatches. Three negative checks also passed:
altered protein, wrong portion basis, and a duplicate local record each cause an
explicit failed audit. Negative checks use temporary copies of input records.

## What is still unresolved

These are generic reference foods, not measurements of purchased ingredients or
finished bars. The dates must match the selected variety/form; oats cover a broad
regular/quick category; supplier identity and product specifications are still absent.
Manufacturing yield, lot variation, allergen declarations, ingredient suitability
and qualified review remain separate tasks. Sugar is not covered by the current
nutrition schema. Passing this audit does not make any row scientifically approved.

No dataset value or approval status changed, so no new candidate or RAG index was
created during this increment. Candidate rc.2 and active rc.1/dev.2 remain as before.
