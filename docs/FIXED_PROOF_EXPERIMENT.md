# Fixed B0/A0/A1 experiment

Implemented 2026-10-24. Engineering mode: `spirulina-proof-v1`.
This implements the comparison in FIRST_RELEASE_SCOPE.md, not scientific approval.

## How to use

In Flutter, enable **Fixed B0 / A0 / A1 experiment** before running. The varying
algae, inclusion, serving and flavour controls are hidden; the fixed values are
shown explicitly. Turn it off to return to the existing engineering grid.
Optional nutrition targets and exclusions are preserved in either mode.

API payload:

```json
{
  "experiment": "spirulina-proof-v1",
  "algae": "spirulina",
  "inclusion_pct": 2,
  "serving_g": 45,
  "flavour": "cocoa-spice"
}
```

The API rejects contradictory settings with 422; it does not silently normalize
them. This mode requires real development retrieval. Production and mock mode
cannot return a synthetic successful fixed experiment.

## Quantities and meaning

| Ingredient (g input) | B0 | A0 | A1 |
| --- | ---: | ---: | ---: |
| Dry oats | 30.60 | 29.70 | 29.25 |
| Dried dates | 13.50 | 13.50 | 13.50 |
| Cocoa powder | 0.90 | 0.90 | 0.90 |
| Spirulina powder | 0 | 0.90 | 0.90 |
| Cinnamon powder | 0 | 0 | 0.45 |
| Total | 45 | 45 | 45 |

Each quantity uses its exact dataset form. No date-paste substitution, recipe
optimization or rescaling occurs. Only A1 is a candidate; B0/A0 are controls.
Exclusions apply to all arms. Requested nutrition targets apply to A1 only.
If a target is unmet or needs unknown data, no candidate or controls are returned.

The 45 g is ingredient input mass. Finished yield and serving mass are unverified;
per-serving estimates in this mode refer to 45 g input before processing. Dates
and cocoa remain fixed. A1 versus A0 measures a cinnamon-for-oats substitution,
not an isolated cinnamon mechanism. Sensory outcomes remain unknown.

## Provenance and compatibility

Requests persist the experiment version. Screening audit records the scope document,
input-mass basis, unknown finished mass, control definition and approval status.
Reports retain dataset/index identity, scientific caveats and source-linked estimates.
Existing grid behavior stays unchanged. Old grid submission hashes are preserved
by excluding its default experiment field from canonical submission serialization.
No dataset/index rebuild is required: these are engineering configuration changes,
not new approved evidence records. Saved historical runs are not regenerated.

## Verification

Unit tests check exact masses, fixed ingredients, deterministic output, independent
rejection of altered quantities, conflicting inputs, exclusions, missing nutrition,
production/mock blocking and historical submission hashing. Real-model API tests
cover successful fixed run, persistence, HTML labels and blocked sugar constraints.
Flutter tests verify the toggle's exact submitted payload and retained targets.

Results: 175 backend tests passed (10 opt-in skipped), separate real-model suite
10 passed, Flutter analysis clean, 16 Flutter tests passed and web build succeeded.
Live Flutter run 68acbb3b-ad97-4b55-a7ab-435df924b29a completed with exact B0/A0/A1
amounts. Screenshot: output/review/fixed-proof-live.png.

Scientific recipe approval, supplier documents, preparation instructions and physical
sensory tests remain pending. Do not prepare or taste these recipes based on software
checks alone.
