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

With `ALGAMASK_MODE=development`, `/runs` now uses the exact dataset snapshot retained
by the verified retrieval index. After grounded explanation succeeds, the Recipe
stage enumerates nine candidates: dried dates at 25/30/35%, flavour ingredients at
1/2/3%, requested algae inclusion (50:50 for blend), and rolled oats as the remainder.
Cocoa-spice splits its flavour mass equally between cocoa and cinnamon. Vanilla is
extract; citrus is raw orange peel. These are **explicit engineering assumptions**,
not recommended doses or evidence-backed manufacturing recipes. Dried dates are
not labelled date paste. No retrieved passage is assigned as dose support.

The search checks serving mass, exact species inclusion, grid membership and
exclusions. Optional per-serving request fields are `min_protein_g`,
`max_energy_kcal` and `max_sugar_g`. A target with missing data cannot pass. Active
rc.5 supports protein/energy/sugar for vanilla and cocoa-spice across all three
algae choices. Citrus sugar remains unknown because the raw-orange-peel record lacks
total sugar. Chlorella refers to the named Algomed supplier-label profile.
Candidates meeting the checks are ranked by estimated protein per serving, with
stable ID tie-breaking; at most three are returned. Failure means **no verified
candidate in this nine-point grid**, not proof that the user's goal is impossible.
The Critic repeats checks independently of the generator's success result.

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
`impact.screening` records all nine verdicts, assumptions, search version and control
parent. HTML reports show estimates, missing-data reasons, source qualifications,
review status and screening audit. Sensory change remains unknown and panel size 0.
The default mock mode remains demonstrational and rejects nutrition targets rather
than silently ignoring them. Production formulation is explicitly blocked: this
engineering grid is development-only, even if a future retrieval release exists.

## Remaining for scientifically validated formulations

- Collect/review applicable protein-bar bounds with a confirmed mass basis and
  material/process context; the existing snack-bar bound is not automatically reused.
- Resolve nutrient and supplier-specific allergen coverage, ingredient processing
  assumptions, product-lot measurements and actual sensory trials.
- Extend the search space and constraint policy using those reviewed inputs, then
  verify production eligibility separately from arithmetic feasibility.

No scientific approvals were changed, no dataset release was published, and no
formulation is claimed production eligible. Flutter integration is a later step.
