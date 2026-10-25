# Release Step 2 — report output clarity

Date: 2026-10-25. Implemented and verified within the scope below.

## What a result establishes

Reports distinguish computational candidates, synthetic demonstrations, no candidate
and a failed evidence explanation. A report existing does not itself mean a recipe
passed checks. Blocking reasons are visible near the outcome when available.

Candidates are ordered by estimated protein within the declared nine-point search.
The fixed proof uses its frozen quantities. No ranking is described as sensory
optimization. B0/A0 are labelled comparison controls; nutrition limits apply to
candidates and controls may exceed them. The actual comparison basis remains in
the detailed screening record.

Nutrition uses the ingredient input mass. Finished yield and measured product
nutrition are not established. Unknown selected protein/energy/sugar are called out
at the top, and unknown sugar is never displayed as zero. Ingredient names are
shown for the exact forms in the current recipe engine, with four decimal places
for ingredient grams. Raw JSON retains calculation precision and form IDs.

## Evidence applicability

Every current source statement receives one conservative label:

- Species background: diagnosis context includes all requested species.
- Related-study background: broader context, including other species/materials.
- Hypothesis or evidence limitation: source support metadata is hypothesis-level.

The label is derived from the retrieved metadata, not a model judgement. Notes
identify the study material, absent/mismatched species coverage and missing
validation for the selected flavour, inclusion and masking effect. Even a source
statement labelled direct is never promoted into validation of this recipe.

The current corpus and engineering recipe engine do not establish masking efficacy
for a selected recipe. This release therefore reports recipe_validated=false.
If future physical trial evidence is added, its applicability needs an explicit
validated contract rather than a keyword-based upgrade.

Generated claims are displayed as cited explanations only when generation is
complete and the run has not failed grounding. Failed runs may still show their
retrieved source notes as background, with the failed outcome clearly visible.

## Sensory data and historical records

New runs retain possible sensory category names but set relative_risk=null and
status=unmeasured. Fixed demo numbers no longer enter new run records. There is no
computed risk score or predicted percentage improvement.

Older saved JSON is preserved. Reading an old run derives report interpretation
without changing stored values. If historical numeric demo risks exist, the report
explicitly labels them illustrative. Flutter and print reports consume/display the
same interpretation; unsupported older responses receive conservative UI fallbacks.

## Verification

Tests cover unknown sensory risks, old-record preservation, species/material
mismatch, direct-source support without recipe proof, hidden failed-generation
claims, HTML escaping, control labels, ingredient precision and Flutter rendering.
Browser and final test results are recorded in IMPLEMENTATION_PROGRESS.md.

Browser verification used the isolated Step 1 database with API 8125 and web 3002,
build/log folder var/dev/session-70o2jh2h. Chlorella/5%/45 g/vanilla without optional
nutrition targets produced run 69804c6a-251c-4969-8eff-efffdda95589. The UI showed
5.26 g estimated protein, unknown energy and sugar, control roles, precise ingredient
grams, and the species mismatch on spirulina/cinnamon context. Copied JSON confirmed
five null relative_risk values and recipe_validated=false. The HTML report showed
the same distinctions. Historical print report 0af9f425-31d3-4582-9667-ce4fe4ceee99
showed the historical-demo-score qualification and unknown sugar.

Screenshot: /tmp/algamask-browser-audit.A7gUpB/step2-report.png. The file is temporary;
this record preserves its substantive observations. Owned audit services were
stopped after verification; the user's existing services were not stopped.

Automated checks cover failure rendering and old-record preservation. No intentional
model failure was generated through the live browser for this step.

This step changes interpretation and display. Sugar/energy data completion belongs
to Step 3; recipe expansion belongs to Step 4.
