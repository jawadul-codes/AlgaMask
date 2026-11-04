# Codex handoff prompt — AlgaMask release Steps 4 and 5

Copy the prompt below into Codex with the latest AlgaMask checkout open. It covers
the last two steps of the current **five-step engineering release sequence**,
not Steps 4/5 of the older scientific-completion or initial implementation plans.

HANDOFF STATUS: the owner confirms that Step 3 has been pushed to Git. Start from
the latest remote branch containing Step 3: clone it, or update an existing checkout
without discarding local work. Verify that the required candidate/index artifacts,
code and documentation listed below are actually present. This is an owner-reported
push, not an independently verified remote commit in this handoff. Do not transfer
credentials, `.env`, personal run databases or the entire `.venv`. Model caches and
ignored raw source files are separate prerequisites, not automatically in Git.

---

## Your role and requested outcome

You are the software engineer continuing **AlgaMask**, an existing Flutter and
FastAPI application for experimental algae-bar formulation screening. Implement
the remaining engineering work in the current codebase. Do not rebuild the app
from scratch, substitute another framework, or provide only a plan.

Work in this order:

1. **Release Step 4: expand and unify constraint-aware recipe screening.** Improve
   the limited recipe search using explicit, versioned engineering rules and
   traceable ingredient data. Make pre-run feasibility and execution agree.
2. **Release Step 5: fault recovery, end-to-end regression and reproducible local
   release handoff.** Test real workflows and failures, repair demonstrated issues,
   and deliver a reliably runnable local application with truthful release limits.

These are the remaining engineering steps, not a promise that scientific review,
physical testing, food safety approval or hosted production deployment is complete.
The repository has several historical numbered plans. Do not accidentally restart
their older Step 4 RAG wiring or Step 5 grounded generation: those already exist.

First inspect the checkout and confirm understanding. Ask a focused question only
if a missing choice materially changes scope, such as which new ingredient family
may be enabled. Otherwise make conservative engineering decisions, document them,
implement, test, and continue. Never resolve a data gap by guessing a fact.

## Mandatory working rules

- Read applicable `AGENTS.md` files and use any required skills in your environment.
- Inspect Git status first. Preserve any existing local work while obtaining the
  pushed Step 3 baseline. Do not reset, discard, overwrite or commit other people's
  changes.
- **Record progress in Markdown before implementation and after every meaningful
  increment.** Maintain `docs/IMPLEMENTATION_PROGRESS.md`. Create detailed Step 4
  and Step 5 documents linked from it. Before context exhaustion or stopping,
  record completed work, exact verification, unresolved issues and the next action.
- Keep updates understandable to a non-technical owner. Separate observed results
  from assumptions, test fixtures and untested behavior.
- No Git push, PR, deployment, paid service, new external account or scientific
  approval is authorized by this prompt. Ask separately if one is necessary.
- Keep the app local and loopback-only. Never stop an unrelated process to free a
  port. Use an isolated test database and owned processes for destructive/crash tests.
- Do not expose secrets, copy private databases into Git, or weaken release gates.
- Use the current code and compatible APIs where practical. Document and test any
  necessary migration. Do not add dependencies unless their benefit justifies them.

## Phase 0 — verify that you received the correct project state

Resolve the repository root on this computer; do not assume the original owner's
Mac username, absolute paths, running ports, temporary files or cached models exist.

Read, in this order:

1. `README.md`
2. Latest entries in `docs/IMPLEMENTATION_PROGRESS.md`
3. `docs/NUTRITION_COVERAGE.md`
4. `docs/CONFIGURATION_PREFLIGHT.md`
5. `docs/FORMULATION_ENGINE.md`
6. `docs/REPORT_OUTPUT_CLARITY.md`
7. `docs/BROWSER_WORKFLOW_AUDIT.md`
8. `docs/FIXED_PROOF_EXPERIMENT.md` and `docs/FIRST_RELEASE_SCOPE.md`
9. `docs/RUN_PERSISTENCE.md`, `docs/LOCAL_LAUNCHER.md`
10. `docs/LOCAL_RETRIEVAL.md`, `docs/GROUNDED_GENERATION.md` and
    `docs/DATASET_PUBLICATION.md` for the relevant contracts.

Older historical sections may mention missing sugar everywhere or missing
chlorella energy. Those statements describe old datasets; the latest Step 3 notes
supersede them. Inspect actual code/data before relying on any recorded statement.

Confirm that these latest artifacts are present:

- `data/candidates/0.1.0-rc.5/`
- `indexes/reviewed_evidence/0.1.0-dev.4/`, including the vector artifact
- `data/extractions/algomed_chlorella_label_2026-10-25.json`
- `docs/NUTRITION_COVERAGE.md`
- `tests/algamask/test_nutrition_coverage.py`
- `tools/extend_nutrition_dataset.py`

The expected rc.5 dataset content hash is:
`b05a800077d53b3bce3c63bdb527d30bf5b48f5c47e7182a0744f4c1c3f02076`.

Verify the artifacts using the repository's verification tools. Do not replace
missing Step 3 artifacts with fabricated files, a mock index, or relabelled old
versions. If this checkout predates Step 3, explain exactly which files are missing
and request the latest work before implementing changes that depend on it.

Git does not carry `.venv`, the original machine's model cache, or all ignored raw
source files. Install from the lockfile. If the pinned model is absent, use the
documented initial-download path with network access explicitly acknowledged;
ordinary runtime must remain offline and must not silently download or use mock.
Do not use build examples that reuse an existing immutable index version.

## Existing architecture and contracts

### Application and workflow

- Client: Flutter, under `apps/flutter`; run Flutter commands there, where
  `pubspec.yaml` lives, not at the repository root.
- Backend: FastAPI/Pydantic under `services/algamask`.
- Six workflow roles: Profile, Retrieval, Chemistry, Recipe, Critic, Impact.
- Development RAG: local pinned sentence embeddings, FAISS, exact source-scoped
  evidence notes, and a default extractive explanation provider. Optional Ollama
  generation is supported; it is not required for the default working app.
- Structured nutrition, ingredients, allergens and numeric constraints are
  authoritative data, not values the LLM should invent or infer from search scores.
- `Settings` currently defaults to explicit mock mode. The local launcher selects
  development mode. Mock mode must remain visibly synthetic and separate.
- The active development defaults are rc.5/dev.4. Production remains blocked.

### Current dataset and nutrition

- Schema 1.1: 21 tables, 292 records, 12 sources, seven algae materials, 20 ingredient
  forms, 19 nutrition profiles and 23 evidence notes. These are extracted records,
  not row-level scientific approvals.
- Nutrition joins **exact ingredient-form IDs**, not fuzzy names.
- Values are per 100 g; per-input-serving calculation is
  `sum(ingredient_g * nutrient_per_100g / 100)`.
- Unknown, ambiguous or missing required composition produces an unknown total,
  not a partial sum represented as complete. Missing is not zero. Positive-mass
  ingredients determine coverage; do not let absent zero-mass ingredients block it.
- Total sugar is not added sugar and cannot be inferred from carbohydrate.
- Fifteen of 19 profiles have numeric sugar. Raw orange peel is missing sugar;
  coconut oil, salt and soy isolate assumed-zero sugar entries remain unknown.
- Vanilla and cocoa-spice recipes have protein/energy/sugar coverage for spirulina,
  chlorella and blend. Citrus sugar targets currently block explicitly.
- `IF-CHL-PWD` in rc.5 is **Algomed chlorella powder (reference)**, tied to
  `MAT-CHL-ALGOMED` and `SRC-ALGOMED-POWDER-2026`. Its whole rounded manufacturer
  profile per 100 g is protein 51.9 g, energy 377 kcal, carbohydrate 9.2 g, fat 9.3 g,
  sugar 0.6 g. Fibre/iron are not supplied in this profile. The manufacturer reports
  naturally occurring sulfites. This is not a generic chlorella value, a purchased
  lot result, or the old laboratory sample A.
- Do not combine this label's energy/sugar with the old sample's protein/lipid.
  Old sample A remains in rc.4. No 4/4/9 calorie inference was used to fill it.
- Total omega-3 stays unknown because available fatty-acid entries may be ALA only.
- Schema 1.0 historical CSVs and manifests remain supported with their exact legacy
  header/audit shape. Historical sugar stays unknown.
- Frozen candidates/indexes are immutable and hash-bound. If data changes, produce
  a new candidate and matching index version; do not edit rc.5/dev.4 or rename old
  artifacts to bypass checks. Keep evidence-note rights and source locations intact.

### Existing recipe search

- `engineering_grid` currently enumerates nine combinations: dates 25/30/35%,
  total flavour 1/2/3%, requested algae inclusion, oats as the remainder.
- Spirulina uses `IF-SPI-PWD`; chlorella uses `IF-CHL-PWD`; blend splits algae 50:50.
- Cocoa-spice divides flavour mass equally between cocoa powder and cinnamon
  powder. Vanilla means extract; citrus means raw orange peel, not oil.
- Dates are dried whole dates, not date paste. Do not silently substitute forms.
- All current recipes use oats. Excluding oats currently blocks honestly.
- Candidates are ordered by estimated protein then stable candidate ID, with at
  most three returned. This is not sensory optimization or a global solver.
- Matched A0 replaces flavour with oats; B0 additionally replaces algae with oats.
  These controls are tied to the top candidate. Candidate nutrition targets do not
  apply to controls. An expanded engine may need a different explicit replacement
  policy; it must remain mass-balanced and respect exclusions.
- `spirulina-proof-v1` is a separate frozen comparison: spirulina 2%, 45 g ingredient
  input, cocoa-spice. Preserve exact quantities in `experiments.py`; never optimize,
  scale or silently substitute its B0/A0/A1 recipes under that version name.

### Inputs, exclusions, feasibility and reports

- UI inclusion is 1–15%, serving 40–50 g. The API currently accepts positive inclusion
  up to 15%; inspect and explicitly resolve this UI/API lower-bound distinction if
  you change validation. These ranges are software limits, not safe/effective doses.
- Optional targets: minimum protein, maximum energy, maximum total sugar per serving.
  A blank target differs from explicit zero. Never silently relax a requested target.
- `ingredient_preference` omits actual selected foods and known contains relationships.
  It does not verify cross-contact or allergy safety.
- `verified_free_from` is strict and currently blocks selected groups because
  complete supplier/lot verification is unavailable. Never downgrade it to preference.
- Historical requests lacking `exclusion_mode` retain strict default semantics.
- `/runs/preflight` is read-only and creates no job. Flutter debounces input checks,
  invalidates eligibility immediately, ignores stale responses and disables Run
  while checking, blocked or unavailable.
- New submissions and explicit retries are checked before execution. Same-key
  replay of an existing submission preserves recovery semantics.
- All targets must pass on the **same candidate**. Individually compatible ranges
  do not establish a jointly feasible recipe. Exclusions removing all candidates
  must not be misreported as missing nutrient data.
- Reports distinguish computed outcomes from measurements. New sensory risks are
  null/unmeasured. `recipe_validated=false` is retained for current evidence.
- Background citations are qualified by species/material/matrix and must not become
  proof of the selected dose, masking efficacy, health effects or safe manufacturing.
- Historical stored run values must not be rewritten when rendering updated labels.

### Persistence and recovery

- SQLite default: `var/runs.sqlite3`. Correct override: **`ALGAMASK_RUN_DB`**, not
  `ALGAMASK_RUN_DB_PATH`.
- Job states include queued, running, completed, failed and interrupted. Existing
  leases, heartbeat, execution tokens, attempts and retry rules must be preserved.
- Repeated same-key/same-input requests share the existing job/result. Same key with
  different inputs conflicts. Retry uses an explicit expected attempt and does not
  erase prior attempts. Expired execution owners cannot overwrite newer outcomes.
- A completed job can have a non-successful workflow outcome; HTTP success or a
  stored report alone does not establish a valid recipe.
- Backup/restore and historical rendering already exist. Extend and verify them;
  do not replace them with ad hoc file copies or delete the owner's database.

## Files to inspect before changing the implementation

Backend/data:

- `services/algamask/formulation_engine.py`, `preflight.py`, `nutrition.py`
- `services/algamask/schemas.py`, `experiments.py`, `validation.py`
- `services/algamask/agents/supervisor.py`, `agents/recipe.py`, `agents/critic.py`
- `services/algamask/report_interpretation.py`, `report.py`
- `services/algamask/api.py`, `run_store.py`, `backup.py`, `runtime.py`
- `services/algamask/dataset.py`, `dataset_schema.py`, `publication.py`, `rag.py`

Client/tools/tests:

- `apps/flutter/lib/src/algamask/`, particularly input, API client, report and history
- `tools/dev.py`, `check_release.py`, `run_database.py`, `rag.py`
- `tools/extend_nutrition_dataset.py`, `audit_scoped_nutrition.py`,
  `check_nutrition_audit_failures.py`
- `tests/algamask/test_formulation_engine.py`, `test_fixed_experiment.py`,
  `test_nutrition_coverage.py`, `test_rag_workflow.py`, `test_execution.py`,
  `test_run_store.py`, `test_backup.py`, `test_dev_launcher.py`,
  `test_reviewed_rag_integration.py`
- Existing Flutter tests under `apps/flutter/test`.

## Release Step 4 — implementation requirements

### 4.1 Establish the baseline and versioned search policy

Run existing checks before changes and document failures rather than hiding them.
Describe the current limitation: only oats/dates/flavour/algae proportions vary,
so arbitrary high-protein targets are not reachable merely by improving warnings.

Design a bounded, deterministic expanded search policy. Identify enabled exact
forms, ingredient roles, explicit engineering bounds, candidate budget, runtime
limits, ranking, tie-breaking and control construction. Separate source-supported
data from unvalidated recipe assumptions. Do not present assumed engineering bounds
as reviewed food-safety limits.

An appropriate direction is to consider existing exact protein-base forms, with
their source profiles and allergen implications, rather than treating dates/oats
as the only matrix. First audit their actual records. For example, the current
`IF-WHEY-PWD` reference is USDA's beverage whey-protein powder isolate, not a named
80–90% protein supplier isolate; its recorded protein is 58.14 g/100 g. Soy isolate
has unknown sugar under the current policy. Do not substitute typical internet
nutrition values or zero sugar to make a candidate feasible.

Use the smallest defensible ingredient expansion. If ingredient choice requires
owner direction, ask before enabling it. Do not silently add allergens, declare a
vegan preference that does not exist, or claim to meet a newly invented diet rule.
If no supported oat-free matrix exists, preserve an explicit oat-exclusion block;
do not enable an arbitrary replacement just to make the interface pass.

Record the new policy/version in results and persisted execution context. Preserve
the old grid's identity and reproducibility; never change the meaning of an old
stored search version. If changing request defaults or adding policy fields, test
old stored requests and existing idempotency hashes, including pending submissions.
Do not re-execute or reinterpret old recipe quantities as new-policy quantities.

### 4.2 One authoritative feasibility path

Share candidate generation, enabled-form rules, exclusions, bounds and target
evaluation between preflight and execution. Preflight must not simulate a different
search space from the one that actually runs. Remove duplicated hardcoded grid
assumptions where necessary; retain an independently checking Critic/invariant layer
so a generator bug cannot certify its own output.

Compute margins from the eligible policy candidates using exact nutrient values.
Preserve joint-target checks, missing-data handling and conservative rounding:
suggested protein ceilings round down; maximum energy/sugar adjustments round up.
Changing inputs invalidates any previous result. No invalid or infeasible new
submission should create a job, invoke generation unnecessarily or produce a
success-looking formulation.

Distinguish: invalid input, unavailable source coverage, unsupported exclusions,
no candidate within the declared policy, retrieval unavailable, generation failed,
and valid computational candidates. Search-budget exhaustion or a bounded-grid miss
is not a mathematical proof that no recipe exists anywhere.

### 4.3 Valid formulations, controls and ranking

Every returned candidate must have finite nonnegative quantities, exact input-mass
balance, exact algae inclusion/species split, supported ingredient forms, valid
policy bounds, preserved exclusions and all requested nutrition limits satisfied.
Recalculate independently before returning it. Numerical tolerance must be explicit
and consistent; do not rely on rounded display values for acceptance.

Return a small, stable, duplicate-free selection. Document the ranking; retain the
existing protein-first policy unless a justified transparent change is made. Do
not label higher semantic similarity as better taste or masking performance.

Controls must remain mass-balanced, excluded-food-aware and traceable to the top
candidate. Document what is replaced and by what. If suitable controls cannot be
constructed under a policy, fail explicitly rather than silently violate a rule.
Keep `spirulina-proof-v1` exactly unchanged.

### 4.4 End-to-end presentation and Step 4 tests

Update Flutter, HTML, JSON and report interpretation together: policy name/version,
actual search scope, ingredient names, source qualifications, margins, control basis
and no-result reasons. Replace obsolete statements such as “nine candidates” only
for new policies; historical reports must retain their actual scope.

Add regression coverage for all species/flavours, boundary inputs, exclusions in
both modes, missing nutrition, ambiguous records, deterministic ordering, mass
balance, feasible and jointly infeasible constraints, budget/runtime limits,
preflight/execution parity, controls, immutable fixed proof, old run rendering and
submission-key compatibility. Add source audit tests if enabling additional forms.

Demonstrate at least one appropriately supported newly enabled recipe configuration
that the old grid could not generate, and prove its numbers from the actual records.
If new source evidence is essential, obtain and cite primary sources, preserve
units/derivations/rights, and version the dataset and index together. Never call an
unsupported extension complete simply because a UI selection was added.

**Step 4 gate:** tested policy-backed expansion, matching preflight/execution,
independent invariant checking, truthful outputs, preserved historical/fixed-proof
behavior and a documented supported-input matrix. Update Markdown before Step 5.

## Release Step 5 — reliability and release verification

### 5.1 Deterministic automated fault tests

Inspect existing tests and add missing coverage rather than reproducing them under
new names. Cover the following with isolated temporary databases and controlled
providers; do not force failures in the owner's active service:

- Backend unavailable, startup readiness failure, wrong API origin/port, timeout,
  malformed/non-JSON proxy responses and recovery with inputs preserved.
- Missing cached model, missing/mismatched/tampered dataset or index, no evidence,
  and provider failure. No silent mock fallback.
- Grounding/schema failure: safe failed outcome, no unsupported success claims,
  citation/injection safeguards retained, no invented numeric data.
- Duplicate submission, concurrent same-key requests, same-key/different-input
  conflict, timeout followed by replay, and exactly one completed result where
  required. An uncertain request must not be retried under a fresh key silently.
- Controlled mid-execution interruption, lease expiry, restart reconciliation,
  stale-owner write rejection and explicit retry preserving previous attempts.
  Do not make tests depend on unexplained long sleeps; use controlled clocks or
  deterministic synchronization where appropriate.
- Failed-attempt inspection, history refresh/filter/pagination, persisted results
  after restart and consistent JSON/HTML/Flutter outcomes.
- Backup/restore into temporary destinations, malformed/future-schema databases,
  incomplete restores and refusal to overwrite an existing destination. Never
  restore over the owner's active database.
- Launcher occupied-port handling, matching client/API URL, readiness timeout,
  owned-child cleanup and immediate restart. Do not kill unknown listeners.

Any reliability fix must preserve prior attempt history, dataset/index provenance
and explicit error semantics. Never expose stack traces or secrets to the UI.

### 5.2 Real-browser acceptance checks

Build the actual Flutter web client, start real offline development RAG and use an
isolated database via `ALGAMASK_RUN_DB`. Use browser tools available in your Codex
environment; record if browser access is unavailable. Backend tests or page-source
inspection do not count as actual browser interaction.

Use unused ports or let `tools/dev.py` choose. Keep the owner's service untouched.
Test and record actual browser, viewport, dataset/index pair and run IDs:

1. Default supported run through the six-agent trace and report.
2. New Step 4 supported configuration, with actual source-backed numeric outputs.
3. Impossible protein/zero-sugar constraints: disabled Run and correct margins.
4. Citrus with an explicit sugar target: missing raw-peel sugar blocks unless a
   genuinely supported, versioned source update has resolved that exact gap.
5. Preference versus strict-free-from exclusions, and actual excluded ingredients.
6. Fixed proof: unchanged B0/A0/A1 quantities and restrictions.
7. Rapid input edits and stale response protection.
8. History reopen, filters, new-experiment navigation, printable report and JSON
   copy; verify clipboard completion before reading it.
9. Backend outage/recovery, plus a controlled failed/interrupted attempt and
   explicit retry through the UI where supported.
10. Restart and reopen the saved report without recomputing its old formulation.

Check desktop and narrow layout. Record the **actual** viewport; a requested mobile
override that did not take effect is not a phone-browser pass. Do not claim Safari,
Chrome, mobile hardware or physical printing was tested unless actually tested.
Save meaningful screenshots and keep them distinct from generated mocks.

### 5.3 Reproducible verification commands

Run from repository root unless a different directory is shown. Inspect tool help
before using commands whose interface may have changed in your checkout.

```sh
uv sync --locked --extra dev --extra rag
.venv/bin/python tools/validate.py
.venv/bin/python -m pytest -q

# Separate process for real ML integration: avoids known FAISS/PyTorch OpenMP issues.
HF_HUB_OFFLINE=1 ALGAMASK_TEST_REVIEWED_RAG=1 \
  .venv/bin/python -m pytest -q tests/algamask/test_reviewed_rag_integration.py

# From apps/flutter:
flutter pub get
flutter analyze
flutter test
flutter build web

# Back at repository root:
HF_HUB_OFFLINE=1 .venv/bin/python tools/check_release.py
git diff --check
```

On platforms without `.venv/bin/python`, use the matching environment executable.
The current launcher supports macOS/Linux; do not claim Windows support without
implementing and testing it. Flutter builds are platform/browser artifacts, not
proof of a release on every device.

For an isolated local test launch on macOS/Linux:

```sh
ALGAMASK_RUN_DB="$PWD/var/step5-audit/runs.sqlite3" \
  .venv/bin/python tools/dev.py --api-port 8125 --web-port 3002
```

Choose other ports if those are occupied. Use a fresh audit DB path if this one
already contains data needed by somebody else. Never delete it to force a clean
test. The launcher selects development/extractive mode and prints the actual URL.
Explicit old `ALGAMASK_DATASET_PATH`/`ALGAMASK_INDEX_PATH` environment overrides can
pin an old pair; inspect and correct them together for the test environment only.

If raw-source audits are rerun, obtain the original USDA archive from the documented
official source and verify its hash. It may not exist on this machine. Do not
silently skip source audits while reporting them as passed. Do not rerun the old
full extractor or the historical Step 3 migration over current reviewed tables.

### 5.4 Final release gate and deliverables

Re-run the release check after the last code changes. Re-run affected integration
tests after any fix; do not quote pre-fix results as final evidence. A skipped test
is not a pass. If a model, browser or source archive is unavailable, identify the
exact unverified gate and what is needed to complete it.

Deliver:

- Working Step 4/5 changes in the existing app, with no unrelated redesign.
- `docs/RELEASE_STEP4_RECIPE_SCREENING.md`: policy/version, enabled exact forms,
  engineering assumptions, constraints, ranking, controls, compatibility, scenarios,
  numeric evidence and remaining unsupported inputs.
- `docs/RELEASE_STEP5_VERIFICATION.md`: environment, exact commands/results, failure
  cases, browser evidence/run IDs, persistence/restore evidence, defects fixed,
  remaining limitations and local acceptance decision.
- Updated `docs/IMPLEMENTATION_PROGRESS.md`, README and affected setup/report/API
  docs. Keep historical facts labelled rather than silently rewriting them.
- Any new immutable dataset/index artifacts and source audits genuinely required
  by the change, with manifest verification and no claimed scientific approval.
- One clear setup/start procedure for a fresh computer, including model download
  prerequisites, Flutter project directory, port behavior, database location,
  restart behavior and how to recognize mock versus real-data mode.
- Final concise handoff: what changed, exact tests, supported and blocked cases,
  how to run, unresolved items, and whether work is local/uncommitted. Stop owned
  audit services, preserve logs/results, and leave the owner's service intact.

**Step 5 gate:** all agreed local engineering scenarios pass, failure states recover
truthfully, data survives restart/restore, and documented startup is reproducible.
Do not declare “no possible errors,” universal ingredient coverage, scientific
validation, allergy safety, masking efficacy or production readiness. Completing
these two engineering steps is not permission to bypass the remaining scientific,
physical-trial, regulatory, security or deployment work.

## Known Step 3 regression examples and baseline results

Use these as frozen **rc.5 / original-grid** regression references. An expanded
policy may legitimately have different ranges; report its version and do not
overwrite these historical expected results with new-policy numbers.

Chlorella / 3% / 45 g input / vanilla, original nine-point grid:

- Protein range: 4.57866–5.17797 g.
- Energy range: 154.017–159.201 kcal.
- Total sugar range: 7.508205–10.419345 g.
- Minimum protein 12 g + maximum energy 426 kcal + maximum sugar 0 g blocks before
  submission. Protein and sugar are the failures, not absent energy/sugar data.
- Minimum protein 5.17 g + maximum energy 200 kcal + maximum sugar 10 g returns
  exactly S25-1: dates 11.25 g, Algomed reference chlorella 1.35 g, oats 31.95 g,
  vanilla extract 0.45 g. Protein 5.17797 g, energy 159.201 kcal, sugar 7.508205 g.
- These are ingredient-input composition estimates, not finished-product results.

Recorded Step 3 checks on the original machine:

- 238 backend tests passed; 20 opt-in tests skipped in the ordinary run.
- Separately, 20 real offline RAG tests passed across historical/current pairs.
- 30 Flutter tests passed; analysis and web build passed.
- All eight golden retrieval questions had their first relevant result at rank 1.
- Dataset validation: 292 records / 21 tables / zero errors or warnings.
- Full local development release check, including temporary backup/restore, passed
  before three final boundary-only tests were added; the final backend suite passed.
- Independent USDA audit: five core foods, 36 numeric matches, four missing ALA
  values preserved. Changed protein, changed sugar, wrong basis and duplicate
  record negative checks all rejected. Other audit scopes are separately documented.
- Browser report screenshot: `output/review/step3-nutrition-report.png`.

These are historical handoff evidence, not your new checkout's test results. Verify
your baseline, then implement Step 4 and Step 5 sequentially, logging as you go.
