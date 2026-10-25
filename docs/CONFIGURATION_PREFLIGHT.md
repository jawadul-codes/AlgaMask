# Configuration checks before running

The input screen calls `POST /runs/preflight` after inputs settle for 350 ms.
Every selection and nutrition edit invalidates the previous result immediately.
Run remains disabled during the check, when the check fails, or when the backend
cannot be reached. Responses for older inputs are ignored.

The endpoint does not create a job, run generation, or save an experiment. It uses
the active dataset and the same candidate generation and constraint checks used by
the experiment. If arithmetic passes, it also checks that the workflow's required
retrieval queries have context. Retrieved context does not prove masking efficacy.

## What the ranges mean

Ranges cover recipes for the current species, inclusion, serving and flavour after
structural exclusions. They are estimates from the dataset, not laboratory results
or global feasibility bounds. All requested targets must pass on the same recipe.
Missing nutrients stay unknown. A blank target means the user has chosen not to
require that check; zero sugar is an explicit requirement and blocks with missing data.

Suggested protein maxima are rounded down to two decimals; suggested calorie/sugar
ceilings are rounded up. This avoids suggesting a rounded boundary that itself fails.
The UI also shows the calculated range at four decimals. Other targets still apply.
Input-screen inclusion limits are 1–15% and serving limits 40–50 g. The fixed proof
uses 2% and 45 g. These interface limits do not establish effective or safe doses.

## Reproduced example

Current rc.5: chlorella means the named Algomed powder reference. At 3%, 45 g and
vanilla, ranges are protein 4.57866–5.17797 g, energy 154.017–159.201 kcal,
total sugar 7.508205–10.419345 g. Minimum protein 12 g plus maximum sugar 0 g
blocks with numeric adjustment margins, not missing-data errors. With minimum
protein 5.17 g, maximum energy 200 kcal and maximum sugar 10 g, one candidate passes:
protein 5.17797 g, energy 159.201 kcal, sugar 7.508205 g. These remain estimates.

The following is the preserved historical rc.4 result, not the active data:

Chlorella, 3%, 45 g, vanilla, minimum protein 12 g, maximum energy 426 kcal,
maximum sugar 0 g, on dataset 0.1.0-rc.4:

- Protein range: 4.41936–5.01867 g. Suggested minimum ceiling: 5.01 g.
- Energy and sugar: unknown; no numeric limit can be confirmed.
- Result: blocked before submission. Lowering protein alone does not unblock it.
- With protein 5.01 g and both optional unknown nutrient targets blank, one
  candidate passes the arithmetic. This does not claim zero sugar or known energy.

## API behavior and activation

### Exclusion meaning

The UI defaults to **Omit ingredients (preference)** and sends
`exclusion_mode: ingredient_preference` when exclusions are selected. Known
ingredient identities and recorded `contains` relationships are excluded. Supplier
cross-contact is not evaluated by this preference, and the report says so.

**Require verified free-from** sends `exclusion_mode: verified_free_from`. All
selected groups require supplier verification that the present corpus lacks.
This includes coconut; its absence from the recipe alone cannot verify free-from.
The mode never switches automatically to make a blocked request pass.

Older API requests and saved results without `exclusion_mode` retain strict
`verified_free_from` semantics. The default field is omitted from submission hashes
to preserve recovery keys; explicit ingredient preferences remain distinct requests.

Every current recipe uses oats, so excluding oats blocks both modes. When exclusions
remove all recipes, preflight returns no nutrition margins and states that nutrition
has not been evaluated. It does not mislabel that situation as missing nutrition data.

For spirulina/5%/50 g/vanilla, minimum protein 5 g, maximum energy 175 kcal, and
tree-nut ingredient preference, candidates pass. Their estimates span 5.61415–6.28005 g
protein and 168.935–174.695 kcal. Verified-free-from remains blocked for this input.

New development/production run requests and explicit retries are checked before a
job or attempt is created. Rejected requests return HTTP 422 with
`detail.code = configuration_blocked` and `detail.preflight`. Same-key recovery
returns the existing job/result without rechecking or rerunning it. Historical
insufficient-data reports remain available.

The input screen blocks mock mode and the currently unsupported production recipe
search. Legacy direct mock API calls remain available for software fixtures.
Unexpected execution/generation failures can still occur after a successful check.

Restart the backend and rebuild/relaunch Flutter together to activate this change.
The one-command launcher (`python3 tools/dev.py`) does both; open its printed URL.
Old running instances continue to use their loaded code until restarted.

Verification: backend regression suite, real offline RAG integration, Flutter
analysis/widget tests, and web compilation. See IMPLEMENTATION_PROGRESS.md for counts.
