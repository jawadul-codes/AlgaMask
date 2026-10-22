# Formulation engine — Step 6 progress

## Implemented: nutrition foundation

`estimate_nutrition(formula, snapshot, approved_only=True)` accepts a validated
formulation whose ingredient IDs are **exact dataset ingredient-form IDs**, plus a
loaded dataset snapshot. Unknown IDs raise an error; mock IDs are not translated.
Callers must use the same verified snapshot as the run's retrieval index.

Outputs include composition estimates per serving and per 100 g, protein per
100 kcal, missing ingredient IDs for each nutrient, full selected nutrition records
(including sources, locations, match qualifications and transformations), and warnings.
No intermediate rounding is used. These are literature/database estimates, not
measurements of a manufactured bar.

Only approved rows are used by default. Explicit `approved_only=False` enables
development estimates and labels non-approved records. Missing, non-per-100-g or
ambiguous records do not contribute partial totals: the affected nutrient becomes
unknown. Unknown energy also makes protein per 100 kcal unknown. Zero energy cannot
produce a ratio. Negative or nonfinite inputs fail validation.

Sugar is not available in this schema. Some omega-3 entries are ALA only, so no
total omega-3 estimate is produced. Neither carbohydrate nor ALA is silently
substituted for these missing quantities. Original record qualifications are retained.

## Remaining in Step 6

- Replace mock ingredient IDs and placeholder recipes with exact-form constrained
  candidate generation. Do not silently substitute dried dates for date paste.
- Separate explicit engineering assumptions from source-supported screening bounds;
  the current snack-bar bound does not establish safe protein-bar usage.
- Add feasibility checks for nutrition targets, exclusions and incomplete allergen
  coverage. Missing allergen rows must not imply an allergen-free product.
- Build matched baseline/unmasked controls and expose calculations in the run API,
  independent critic checks and HTML reports.
- Keep measured sensory outcomes unknown until actual panel data exists.

The existing run API still returns demonstration recipes and unknown nutrition.
This increment does not change scientific approvals, publish a release, or make
recipes eligible for production.
