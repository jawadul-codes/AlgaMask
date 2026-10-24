# First release scope - AlgaMask

Version: 1.0 planning baseline
Prepared: 2026-10-24
Status: engineering scope prepared; scientific and physical-trial sign-off pending.

This document implements Step 1 of PROJECT_COMPLETION_ROADMAP.md. It defines the
first proof experiment, not a published scientific dataset or approved food recipe.
It preserves the original oats, dried dates and cocoa baseline. Historical Day 1
files remain unchanged; use this document for the new completion roadmap.

## Purpose and users

Help the project research team investigate whether spirulina can be included in a
45 g bar while retaining acceptable sensory characteristics and documenting its
estimated nutritional composition. Initial users are the project team and reviewers.
Personal health advice and public consumer recommendations are outside this release.

The first proof covers spirulina powder and a cocoa/cinnamon flavour direction.
Chlorella, blends, citrus, vanilla and additional food matrices remain development
options and are outside the first validation claim. Existing app options are not
disabled by this planning document.

## Fixed engineering comparison

Use 2% spirulina by total ingredient input mass as the first experimental setting:
0.90 g in a 45 g formulation. It is a project screening choice, not an approved
consumption limit. Keep 5% for a later separately reviewed experiment.

The following quantities freeze a reviewable engineering starting point. They are
assumptions to review in Steps 2 and 5, not values established by a cited study.

| Exact dataset ingredient form | B0 baseline (g) | A0 algae control (g) | A1 intervention candidate (g) |
| --- | ---: | ---: | ---: |
| IF-OAT-DRY - dry rolled oats | 30.60 | 29.70 | 29.25 |
| IF-DATE-DRIED - dried dates, not date paste | 13.50 | 13.50 | 13.50 |
| IF-COCOA-PWD - unsweetened cocoa powder | 0.90 | 0.90 | 0.90 |
| IF-SPI-PWD - spirulina powder | 0.00 | 0.90 | 0.90 |
| IF-CINN-PWD - ground cinnamon | 0.00 | 0.00 | 0.45 |
| Total ingredient input | 45.00 | 45.00 | 45.00 |

Dates are fixed at 30%, cocoa at 2%, and A1 cinnamon at 1% of ingredient input
mass. Oats balance each recipe. A0 replaces 0.90 g oats with spirulina; A1 replaces
another 0.45 g oats with cinnamon. Cocoa is present in every arm: A0 means no
additional cinnamon intervention, not an absence of potentially masking ingredients.

These comparisons measure ingredient substitution effects. A1 versus A0 cannot
isolate a pure cinnamon mechanism because the oats amount changes too.

The table specifies 45 g input mass, not a verified 45 g finished serving. Preparation
loss, added water, binding feasibility and finished mass must be recorded during
process development. If the matrix needs water, another binder or another process,
revise all affected recipes under a new scope version before running the comparison.
Do not silently substitute date paste for dried dates.

Supplier, product code, lot, ingredient specifications, processing and storage
instructions remain to be established before physical testing. Selecting these
numbers does not authorize tasting or establish manufacturing feasibility.

## Evidence and RAG boundaries

Retrieve evidence about spirulina sensory characteristics and relevant food-matrix
interventions. Retain source location, ingredient form, units, matrix, review status
and limitations. Label evidence from other products as indirect.

The current candidate is data/candidates/0.1.0-rc.4 and the development index is
indexes/reviewed_evidence/0.1.0-dev.3. Neither is a production release. Required
review coverage includes the five forms above and their source/dependency records.
The recorded approval from Mazharul Islam remains valid as a recorded user decision;
it does not fill missing scientific fields or supply a new trial protocol approval.

Numeric composition, mass balance and nutrition come from structured records and
deterministic calculations. Retrieval similarity is a search score, not a probability
that flavour masking works. Weak or absent evidence must remain explicit.

## Measures and comparisons

| Measure | Comparison and reporting rule |
| --- | --- |
| Primary nutrition measure | Protein g per 100 kcal for A1 versus B0; show both absolute values and percentage change where baseline is positive and both values are known. |
| Supporting nutrition | Protein g and energy kcal per defined serving and per 100 g, with record provenance. These are estimates until supported by finished-product measurements. |
| Primary sensory measure | Overall acceptance for A1 versus A0; report the paired score difference using a reviewed protocol. |
| Supporting sensory | Earthy/muddy, grassy/green, marine/fishy, sulfurous and bitter ratings; record the same scales and conditions for all arms. |
| Process feasibility | Input mass, finished mass, yield, preparation method and deviations; record whether a coherent bar can be prepared. |

The sensory protocol must define scale anchors, sample size, blinding, serving order,
participant criteria and analysis before data collection. Those choices and the
minimum meaningful acceptance difference belong to the scientific reviewer and
Step 6 protocol; no improvement threshold is invented here. Do not report a
percentage improvement from an ordinal liking scale by default.

Unknown nutrition stays unknown. No sensory improvement exists until the relevant
trial is performed. Failure to improve is a valid research outcome and must be
reported. A working app does not require a positive experimental result.

## Permitted statements

Current demonstration: "AlgaMask retrieves source-linked evidence and generates
experimental algae-bar formulations with calculated composition estimates and
documented limitations."

After record review: describe an estimate as calculated from approved source
records, with its version and assumptions. This does not make it a laboratory result.

After physical testing: report the actual observed values, sample size, protocol,
comparison and uncertainty. Describe them as results under the tested conditions.
Do not generalize a small pilot to all consumers or promise improved acceptance.

No claim of diagnosis, treatment, guaranteed health benefit, allergen-free status,
validated shelf life, commercial readiness or proven masking mechanism is supported
by the current project. "Protein bar" is the project matrix name, not an approved
high-protein nutrition claim.

## Implementation gap to resolve in Step 5

Update 2026-10-24: the engineering gap below is now implemented as the explicit
opt-in `spirulina-proof-v1` mode (see FIXED_PROOF_EXPERIMENT.md). The old grid remains
available. Scientific validation and physical-trial approval are still pending.

The existing development generator searches nine points and chooses the top three
by estimated protein. Its controls replace all flavour mass with oats, and cocoa-spice
splits flavour mass equally between cocoa and cinnamon. It does not implement the
fixed comparison table above.

Step 5 must add an explicit versioned experiment configuration with fixed cocoa and
dates across arms, separate cinnamon intervention, matched algae inclusion and the
exact gram totals. Verify the output against this table before claiming that an app
run represents this experiment. Keep current development results labelled according
to their actual recipe/control rules. Production formulation remains blocked until
the reviewed scientific constraints are available.

## Ownership and change control

Project requester: Mazharul Islam. The historical Day 1 scope records Nafiz as its
scope owner; this document does not assign or remove that person's responsibilities.
Scientific reviewer and physical-trial owner: not yet assigned in this document.
No signature or expert approval is asserted.

Any change to serving basis, species, inclusion, ingredient form, gram quantities,
control definition or primary measure requires a new scope version and explanation.
Preserve the prior version and all run snapshots. Scientific revisions are expected
if the proposed starting quantities or process prove unsuitable.

Step 1 preparation is complete. The roadmap's formal signed-scope gate remains open
until the responsible owners review this concrete document. Step 2 evidence review
can proceed against these explicit assumptions without treating them as approved.
