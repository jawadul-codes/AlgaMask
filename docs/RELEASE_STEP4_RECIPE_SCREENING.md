# Release Step 4 — recipe screening

Updated: 2026-10-25. This is an engineering search policy. It is not a reviewed
food-safety limit, a sensory ranking, or proof that no other recipe exists.

## What was limited

`exact-form-grid-v1` builds nine recipes: dried dates at 25/30/35%, flavour
ingredients at 1/2/3%, the requested algae inclusion, and rolled oats as the
remainder. Cocoa-spice splits flavour mass equally between cocoa and cinnamon.
Vanilla is extract. Citrus is raw orange peel. Those nine recipes are the whole
search. A protein target above that grid stays unreachable even if the warning
text is clearer.

Jobs reserved before a policy field existed keep this nine-recipe search when
they run. Their stored results are not recalculated. `spirulina-proof-v1`
quantities are unchanged.

## Active policy: `protein-base-grid-v2`

New development runs use one shared generator for preflight and execution.

| Choice | Rule |
|---|---|
| Dates | 25%, 30%, 35% of input mass. Dried whole dates, not date paste. |
| Flavour | 1%, 2%, 3%. Cocoa-spice, vanilla extract, or raw orange peel, as before. |
| Algae | Requested inclusion. Blend is 50:50 spirulina and the Algomed chlorella reference. |
| Protein base | `IF-WHEY-PWD` at 0%, 10%, or 20% of input mass. 0% keeps the old recipe IDs. |
| Remainder | Rolled oats. Every recipe in this policy still contains oats. |
| Budget | 27 recipes, all enumerated. A smaller budget stops the search and says so. |
| Ranking | Estimated protein per serving, then candidate ID. At most three are returned. |
| Controls | Built only for the top candidate. Flavour mass, then algae mass, is replaced with oats. Whey stays, because it is matrix rather than flavour or algae. Targets do not apply to controls. If a control would break a rule, the run fails instead of returning the candidate. |

These percentages are software levels for screening. They are not validated doses.

### Enabled form, from the frozen rc.5 record

`IF-WHEY-PWD` is USDA SR Legacy FDC 173177, “Beverages, Whey protein powder
isolate”: 58.14 g protein, 359 kcal, and 1.16 g total sugar per 100 g. It is not
a named 80–90% supplier isolate. The allergen row records that it contains milk.
A milk ingredient preference removes those recipes. A verified-free-from milk
requirement still blocks the whole screen, because supplier verification is not
in the dataset.

### Audited and not enabled

- `IF-SOY-ISO`: 88.32 g protein per 100 g, but total sugar is an assumed-zero
  USDA derivation and stays unknown. It is not used to make a sugar target pass.
- `IF-RICE-PUFF`: no nutrition profile. It is not an oat replacement. Excluding
  oats still blocks, with an explicit message.

## Compatibility

- Request hashes do not include the policy name. The same submission key and the
  same inputs still refer to the same job.
- A completed job returns its stored formulations. They are not rerun under v2.
- A job whose saved context has no `search_version` runs as `exact-form-grid-v1`.
- An explicit retry records a new attempt and uses the current policy in that
  attempt’s context. The previous attempt remains stored.
- Reports for `exact-form-grid-v1` still describe nine variations. New runs name
  `protein-base-grid-v2` and the 27-recipe scope.

## Checks that must agree

Preflight and execution use the same candidates, exclusions, bounds and targets.
The Critic checks the returned candidates again. One recipe must meet every
requested target. Separate ranges do not count as a match. Missing nutrition
stays unknown. Suggested protein ceilings still round down; energy and sugar
floors still round up. Mass and grid checks use a tolerance of one millionth of
a gram; target checks use one hundred-millionth of the nutrient unit. Display
rounding is not used for acceptance.

Historical rc.5 / v1 reference, chlorella 3%, 45 g, vanilla, which this policy
must still reproduce when v1 is requested:

- Protein 4.57866–5.17797 g, energy 154.017–159.201 kcal, sugar 7.508205–10.419345 g.
- Minimum protein 5.17 g, maximum energy 200 kcal, maximum sugar 10 g selects
  exactly S25-1.

## Measured on rc.5

Historical v1, chlorella / 3% / 45 g / vanilla, still reproduces:

- Protein 4.57866–5.17797 g, energy 154.017–159.201 kcal, sugar 7.508205–10.419345 g.
- Minimum protein 5.17 g, maximum energy 200 kcal, maximum sugar 10 g selects exactly S25-1: dates 11.25 g, Algomed chlorella 1.35 g, oats 31.95 g, vanilla extract 0.45 g. Protein 5.17797 g, energy 159.201 kcal, sugar 7.508205 g.

Live v2 for that same chlorella input, with no extra target, spans 27 recipes:

- Protein 4.57866–9.22707 g, energy 152.217–159.201 kcal, sugar 7.508205–10.434645 g.

Default spirulina / 5% / 45 g / cocoa-spice under v2:

- Protein 5.211158–9.753953 g, energy 149.55975–156.99825 kcal, sugar 7.51284–10.34307 g.

A minimum of 8 g protein is above the old spirulina grid (its highest estimate was about 5.70 g) and is reachable in v2. The top candidate is S25-1-W20:

- Dried dates 11.25 g, spirulina powder 2.25 g, cocoa powder 0.225 g, cinnamon powder 0.225 g, whey isolate 9 g, rolled oats 22.05 g.
- Protein 9.7539525 g, energy 155.19825 kcal, sugar 7.52814 g per 45 g input.
- Those figures are the mass-weighted rc.5 records, including FDC 173177 for the whey. They are ingredient-input estimates, not a finished bar.

A milk ingredient preference drops the whey recipes and the protein/sugar edges match v1. A verified-free-from milk requirement still blocks the whole screen. Excluding oats still blocks. Citrus with a sugar target still blocks because raw orange peel has no sugar value. Asking for protein above the v1 maximum and sugar only a hair above the v1 minimum fails jointly, even though each limit is possible on its own.

## Verification

- Backend: 264 passed, 20 opt-in RAG tests skipped. One existing launcher test, `test_automatic_selection_skips_busy_port`, did not raise on this Windows machine. The launcher sets `SO_REUSEADDR`, which lets a second bind succeed here. That file was not part of this change.
- The same backend command with `ALGAMASK_MODE=development` left in the shell is not a mock-mode result. The recorded run cleared that variable first.
- Flutter: 30 tests passed.
- rc.1, rc.2 and rc.3, and the Algomed label file, were rewritten to the sealed LF bytes so their recorded hashes match. Record values were not edited. rc.5 and dev.4 were already matching and were not edited.
- No commit and no push.

## Still unsupported

- Soy isolate, because sugar is unknown.
- Any oat-free recipe.
- Citrus plus a sugar target, until raw orange peel has a sourced sugar value.
- Scientific approval, sensory performance, allergy safety, and production use.
