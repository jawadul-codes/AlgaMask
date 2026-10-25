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

Schema 1.1 includes total sugar (not added sugar), calculated with the same exact-form
mass weighting as other nutrients. Legacy schema 1.0 rows load sugar as unknown.
Some omega-3 entries are ALA only, so no total omega-3 estimate is produced. Neither
carbohydrate nor ALA is substituted. See [source coverage](NUTRITION_COVERAGE.md).

## Implemented: experimental screening workflow

With `ALGAMASK_MODE=development`, `/runs` uses the exact dataset snapshot retained
by the verified retrieval index. New runs use `protein-base-grid-v2`: dried dates
at 25/30/35%, flavour ingredients at 1/2/3%, USDA beverage whey-protein powder
isolate at 0/10/20% of input mass, the requested algae inclusion (50:50 for blend),
and rolled oats as the remainder. The 0% whey slice is the previous nine-recipe
grid and keeps those recipe IDs. Cocoa-spice splits its flavour mass equally
between cocoa and cinnamon. Vanilla is extract; citrus is raw orange peel.
These percentages are explicit engineering assumptions, not recommended doses or
food-safety limits. Whey is FDC 173177, a beverage-powder isolate at 58.14 g
protein per 100 g, and it contains milk. Soy isolate is not used because its
sugar value is unknown. No oat-free filler with nutrition is available, so
excluding oats still blocks. No retrieved passage is assigned as dose support.

The search checks serving mass, exact species inclusion, grid membership and
exclusions. Optional per-serving request fields are `min_protein_g`,
`max_energy_kcal` and `max_sugar_g`. A target with missing data cannot pass.
Preflight and execution use the same 27-recipe generator. Candidates meeting
the checks are ranked by estimated protein per serving, with stable ID
tie-breaking; at most three are returned. Failure means no verified candidate
in this declared grid, or that the candidate budget stopped the search. Neither
is proof that the user's goal is impossible outside the grid. The Critic repeats
checks independently of the generator's success result.

`exact-form-grid-v1` remains the nine-recipe oat grid. Jobs saved without a
policy field still run as v1. Completed results are not recalculated.
`spirulina-proof-v1` quantities are unchanged.

Oats/coconut exclusions remove matching ingredient forms. Peanut/tree-nut/sesame/
milk/soy allergy exclusions block screening: the corpus cannot establish complete
free-from coverage, even when no positive allergen relationship is present. This
conservative behavior must not be relaxed by interpreting missing rows as negative
allergen findings. Candidate runs without exclusions still are not allergen-safe
certifications.

The top candidate has matched controls: A0 replaces flavour mass with oats; B0 also
replaces algae mass with oats. Dates and total mass remain constant. Controls do
not have to satisfy candidate nutrition targets. Other candidates do not have
individually matched controls. The reported protein-density percentage change is
only for the top candidate versus B0; missing/zero baseline values yield unknown.

`impact.nutrition` contains estimates and provenance per candidate/control;
`impact.screening` records every checked recipe, the assumptions, search version and control
parent. HTML reports show estimates, missing-data reasons, source qualifications,
review status and screening audit. Sensory change remains unknown and panel size 0.
The default mock mode remains demonstrational and rejects nutrition targets rather
than silently ignoring them. Production formulation is explicitly blocked: this
engineering grid is development-only, even if a future retrieval release exists.

## Remaining for scientifically validated formulations

The bounded whey expansion in `protein-base-grid-v2` is an engineering screen only.
It does not add reviewed protein-bar bounds, supplier-lot measurements, or sensory trials.

- Resolve nutrient and supplier-specific allergen coverage, ingredient processing
  assumptions, product-lot measurements and actual sensory trials.
- Any wider search still needs those reviewed inputs. Production eligibility is
  separate from arithmetic feasibility.

No scientific approvals were changed, no dataset release was published, and no
formulation is claimed production eligible.
