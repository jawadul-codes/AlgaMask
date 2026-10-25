# AlgaMask implementation progress

Updated: 2026-10-25

## Release Step 5: reliability and local verification (2026-10-26, verified with a recorded browser gap)

Windows port reservation no longer lets a second socket take a live listener.
The one-command launcher still runs only on macOS and Linux; Windows uses the
manual steps in the README. The release check can start Flutter when its batch
file is on PATH. Existing retry, backup, grounding, and client-recovery tests
were kept. Details: RELEASE_STEP5_VERIFICATION.md.

- Release check passed: 267 backend tests, 20 ordinary skips, Flutter analyze,
  30 Flutter tests, web build, real rc.5/dev.4 retrieval smoke, and temporary
  backup/restore. Production remains blocked.
- Separate offline retrieval suite: 20 passed.
- No browser tool was available, so the ten live browser scenarios were not
  executed. The services on ports 8000 and 3000 were left running.
- No commit or push.

## Release Step 4: constraint-aware recipe screening (2026-10-25, verified)

The live screen is `protein-base-grid-v2`: dates, flavour, and USDA beverage
whey isolate at 0/10/20% of input mass, with oats as the remainder. Preflight
and execution share that generator. The Critic checks the returned candidates
and controls again. The old nine-recipe policy `exact-form-grid-v1` still runs
for saved jobs that have no policy field, and its chlorella reference numbers
still match. Completed results are not recalculated. `spirulina-proof-v1` is
unchanged. Soy isolate and oat-free recipes stay unavailable. Details and the
measured recipe are in RELEASE_STEP4_RECIPE_SCREENING.md.

- Default spirulina / 5% / 45 g / cocoa-spice: protein 5.211158–9.753953 g,
  energy 149.55975–156.99825 kcal, sugar 7.51284–10.34307 g.
- An 8 g protein minimum, which the old grid cannot meet, returns S25-1-W20:
  9 g whey, 9.7539525 g protein, 155.19825 kcal, 7.52814 g sugar.
- Verification: 264 backend tests passed, 20 opt-in skipped. One pre-existing
  Windows port-reuse launcher test failed and was not changed. Flutter: 30 tests
  passed. No commit or push. Step 5 has not been started.

## Release Step 3: nutrition coverage (2026-10-25, supported coverage verified)

- Adding total sugar with exact USDA food/nutrient identifiers, units and derivations.
  Missing and assumed-zero entries remain unknown, not numeric zero.
- Using the complete manufacturer label for named Algomed chlorella powder as a
  new reference profile; never grafting energy/sugar onto the old laboratory sample.
- Keeping historical frozen candidates and indexes reproducible. New data stays
  extracted, not scientifically approved; estimates are not prototype measurements.
- Activated immutable rc.5/dev.4 (dataset hash
  b05a800077d53b3bce3c63bdb527d30bf5b48f5c47e7182a0744f4c1c3f02076).
  Working tables have the same record values; frozen bytes/hashes are unchanged.
  292 records, 12 sources, 7 algae materials, 19 nutrition rows, 23 evidence notes.
- Added exact per-serving/per-100-g total sugar; 15/19 profiles have supported
  numeric sugar. All algae choices have protein/energy/sugar coverage with vanilla
  and cocoa-spice. Raw orange peel sugar is absent, and coconut oil/salt/soy isolate
  assumed-zero sugar remains unknown. Citrus sugar targets still block explicitly.
  Fibre/iron/total omega-3 are not universally complete. Step 3 does not claim that
  every ingredient/nutrient gap is closed.
- Spreadsheet scientific-data guidance informed exact keys, units, source
  attribution and missing-versus-zero handling; existing CSV generation was retained.
- Chlorella uses a whole named supplier profile (51.9 g protein, 377 kcal,
  0.6 g sugar per 100 g), not values grafted onto laboratory sample A. Manufacturer
  sulfites and supplier/lot limitations are visible. Old sample stays in rc.4.
- Browser reproduced the impossible chlorella/3%/45 g/vanilla/12 g protein/
  426 kcal/zero-sugar inputs: disabled Run, numeric margins (protein max 5.17797 g,
  sugar min 7.508205 g), no missing-energy error. Supported limits 5.17 g/200 kcal/
  10 g produced run be12ec12-ddac-40c3-b1f4-47adbab5c835: S25-1, 5.17797 g protein,
  159.201 kcal, 7.508205 g sugar. Clipboard export, print report, named ingredients
  and persisted report reload were browser-verified. Citrus sugar 10 g blocked
  with missing IF-ORANGE-PEEL identified. Screenshot: output/review/step3-nutrition-report.png.
- Verification: 238 backend tests passed / 20 opt-in skipped; separately 20 real
  offline RAG tests passed across historical/current pairs. All eight golden
  retrieval questions remain rank 1. Thirty Flutter tests passed; analysis clean;
  compiled web build passed. Full development release check (including temporary
  database backup/restore) passed before the final three boundary-only tests.
  Dataset validation: 292 rows / 21 tables / zero errors or warnings.
- Independent USDA audit: five core foods, 36 exact numeric matches; four missing
  ALA values preserved. Deliberately changed protein, changed sugar, wrong basis
  and duplicate record all rejected. Eighteen USDA sugar decisions and the separate
  manufacturer extraction are in output/review/nutrition_step3_sources.json.
- Removed blanket UI claims that sugar/chlorella energy are always missing. Reports
  retain supplier URLs, exact form names and qualifiers. Legacy manifest/header
  compatibility, malformed headers, numeric validity, mixed constraints and dirty
  working-copy preservation have regression coverage. No scientific approval granted.
- Details/reproduction: NUTRITION_COVERAGE.md. Restart backend and Flutter together
  to use defaults; explicit old dataset/index overrides must be updated together.
  Browser tests used an isolated database; an initial readiness-only launch used
  the default database before the override was corrected, with no runs submitted.
  Owned audit services stopped; existing user services left running.
  No commit/push performed.

## Release Step 2: output clarity (2026-10-25, verified)

- Replacing numeric demo sensory risks with unknown/unmeasured values in new runs.
- Adding derived report interpretation: computational outcome, reasons, input-mass
  basis, control roles and citation applicability without upgrading study support
  into proof of recipe masking efficacy. Historical runs receive interpretation
  on read; their stored evidence and measured/estimated values are not rewritten.
- Updating Flutter/HTML reports with context labels, ingredient names/precision,
  visible unknown sugar and suppression of unverified generated claims.
- New mock Critic traces say DEMO_CHECKS_PASSED rather than APPROVED; no implied
  scientific approval. Historical records remain intact and visibly qualified.
- Verified browser run 69804c6a-251c-4969-8eff-efffdda95589 (chlorella/vanilla):
  protein 5.26 g, energy/sugar unknown, background/mismatched-study labels, precise
  ingredient names/grams, control explanations; copied JSON has five null risks.
- Print report and historical report qualification verified in the browser.
  Details: REPORT_OUTPUT_CLARITY.md; screenshot retained in the audit temp folder.
- Flutter analysis clean; 30 Flutter tests passed; compiled web build passed.
  Final backend suite: 213 passed / 10 opt-in skipped; separate real offline RAG
  integration: all 10 passed. Whitespace validation passed. No nutrition dataset,
  evidence records, retrieval ranking or formulation search was expanded.
- Owned audit services stopped; existing user services unchanged. No commit/push.

## Release Step 1: browser workflow audit (2026-10-25, completed within recorded scope)

- Testing the current compiled Flutter UI against real offline development RAG
  using an isolated temporary run database and separate local ports.
- Verified coverage: default run, target edits and invalid inputs, exact blocked
  chlorella example, ingredient preferences/verified exclusions/oats, fixed proof,
  history reopening, HTML report and connection-error recovery.
- Results and evidence recorded in BROWSER_WORKFLOW_AUDIT.md. Four isolated runs
  persisted through restart; blocked previews created no jobs. History filtering,
  report reopening, print-report navigation and JSON copying were browser-verified.
- Fixed New experiment navigation from history, fresh eligibility checks when
  reopening inputs, clipboard-error feedback, and launcher restart socket reuse.
- Final checks: analysis clean, 29 Flutter tests passed, web build and browser
  retest passed; 207 backend tests passed / 10 opt-in ML tests skipped.
- Actual browser width was 689 px; a requested phone viewport override was ignored.
  Automated 390 px form/report tests passed, but real phone-browser testing remains
  a recorded release-test limitation. Step 2 output clarity findings are recorded.
- Owned audit services stopped, audit database/logs/screenshots retained; user
  services unchanged. No dataset changes, commit or push.
- Earlier automated checks are not counted as browser observations.

## Exclusion preferences versus verification (2026-10-25, verified)

- Split the input choice into recipe ingredient preferences and verified-free-from
  requirements. UI explicitly sends the selected mode; historical requests retain
  strict semantics and their submission hashes remain compatible.
- Preferences reject known excluded foods and recorded contains relationships.
  They do not claim supplier cross-contact verification. Strict mode requires
  unavailable supplier verification for all selected groups, including coconut.
- No remaining recipes now yields an exclusion explanation and no nutrition ranges;
  it no longer incorrectly reports missing protein/energy data.
- Saved requests, HTML reports and Flutter reports identify the chosen mode.
- Screenshot configuration (spirulina/5%/50 g/vanilla, protein >=5 g,
  energy <=175 kcal) passes with tree-nut preference; strict mode blocks.
- Verification: 206 backend tests passed / 10 opt-in skipped; separately all 10
  real offline RAG integration tests passed; 27 Flutter tests passed; analysis
  clean and web build successful. Tests cover all six non-oat preferences, actual
  excluded ingredients, absent candidates, mode switching and report labelling.
- Backend and Flutter must be restarted/relaunched to load the changes. Existing
  services and scientific dataset values unchanged; no commit/push made.

## Configuration preflight (2026-10-25, verified)

- Added a read-only feasibility endpoint using the same recipe candidates,
  ingredient data, exclusions and target checks as execution. It reports numeric
  ranges, missing values and conservative adjustment boundaries.
- Flutter checks on input changes, discards stale responses and disables Run while
  checking, blocked or offline. No experiment is submitted by this preview.
- New real-data submissions are checked before a job is created; same-key replay
  keeps its existing recovery semantics. Missing retrieval context also blocks.
- Passing preflight only establishes computational eligibility; it does not
  establish sensory efficacy, global recipe feasibility or laboratory accuracy.
- Exact chlorella/3%/45 g/vanilla/12 g protein/426 kcal/0 g sugar case
  blocks before creating a job: protein maximum 5.01867 g, energy and sugar
  unknown. Suggested protein minimum ceiling is 5.01 g; other targets still apply.
- Tests cover absent evidence, exclusions, fixed controls, old-attempt retry,
  same-key replay, input edits and stale asynchronous results.
- Verification: 193 backend tests passed / 10 opt-in skipped; all 10 real offline
  RAG integration tests passed separately; 26 Flutter tests passed; analysis clean;
  web build succeeded. No new browser-interaction test was performed.
- Added CONFIGURATION_PREFLIGHT.md with semantics and activation instructions.
  Restart backend and rebuild/relaunch Flutter together. Existing services were
  not restarted; no dataset values changed; no commit/push made.

## Client failure recovery (2026-10-25, verified)

- Centralized timeout, connection and HTTP error handling for submission, history,
  saved reports, execution details and explicit retries.
- Non-JSON proxy errors and unexpected response envelopes now produce readable
  guidance instead of raw parsing exceptions. Server error internals are not shown.
- Uncertain submissions keep their original idempotency key; no automatic POST
  retries were added. Timeout guidance asks users to check history first.
- Added regression coverage for malformed responses, offline history, timeouts,
  retained submission keys and retry conflicts. Dataset and RAG content unchanged.
- Verification: Flutter analysis clean; all 25 Flutter tests passed (nine new
  regression cases); git diff whitespace validation passed.
- This verifies client recovery contracts with simulated failures, not every
  network environment or end-to-end outage. Backend unchanged; its suite was not
  rerun for this client-only increment. Existing services were not restarted.
- Rebuild/relaunch the Flutter app to pick up the changes. No commit or push made.

## One-command local launcher (2026-10-24, verified)

- Added tools/dev.py: cwd-independent startup, automatic free-port selection,
  reserved loopback sockets, real RAG/storage readiness and matching Flutter API URL.
- Compiles an isolated web build to avoid the prior debug-WebSocket problem.
- Explicit occupied ports fail without stopping their owners. Ctrl+C cleans up only
  launched services; saved runs, logs and existing services remain intact.
- Added seven focused launcher tests and setup/troubleshooting documentation.
- Live launch from apps/flutter (not the repo root) selected 8125/3002 because
  Antigravity's 8124/3001 were occupied. Readiness, compilation, static serving,
  compiled API URL and a real fixed-proof run/report all passed.
- Test run a76a25b5-f045-4dc6-9634-1696647aeef3 is retained in saved history.
- Explicit-port collision returned a clear error. Ctrl+C exited successfully,
  closed only 8125/3002 and left 8124/3001 listening. Logs/build retained under
  var/dev/session-i447tywi. Full suite: 189 passed / 10 opt-in skipped.

## RAG safety regression preparation (2026-10-24, engineering verified)

- Added an eleven-case draft engineering suite: qualified evidence, missing-efficacy
  context, conflicting species/matrix/purpose filters and unrelated questions.
- Added an offline runner that records exact hits, scores, provenance, expected
  ranking, retained qualifications and generation status. Failed cases remain
  visible and return a nonzero exit status; reports cannot be overwritten.
- Added tests of the evaluator itself so wrong filters, missing notes, removed
  caveats, incomplete provenance and unexpected retrieval are not reported as passes.
- No active service, dataset, index or retrieval threshold changed. This supports
  Step 4 preparation; independent reviewer-written evaluations are still required.
- Final offline evaluation: 11/11 pass on rc.4/dev.3. Seven evaluator checks added;
  full normal suite: 182 passed / 10 opt-in skipped. Diff validation passes.
- Results and reviewer handoff: RAG_SAFETY_EVALUATION.md and
  output/rag/safety-dev-v1-final.json. The earlier safety-dev-v1.json is intermediate.

## Fixed proof experiment implementation (2026-10-24, engineering verified)

- Added opt-in spirulina-proof-v1 alongside the unchanged engineering grid.
- Frozen B0/A0/A1 amounts follow FIRST_RELEASE_SCOPE.md: 45 g input, 2% spirulina
  in A0/A1, fixed dates/cocoa and separate cinnamon substitution. No optimization
  or ingredient substitution occurs in this mode.
- Conflicting settings fail validation; exclusions apply to every arm and nutrition
  targets to A1. Unknown required values block output. Production and mock execution
  cannot silently represent this fixed experiment.
- Added Flutter toggle and explicit input-mass/approval warnings. Preserved legacy
  grid submission hashes to avoid breaking same-key retries across this change.
- Scientific review and physical validation remain pending; this is Step 5
  engineering preparation while the Step 2/3 scientific publication gates stay open.
- User requested a health check during the final UI check. Backend remains healthy
  on 8123, rc.4 integrity passes, reviewed tables validate (290 rows; zero issues),
  and 175 backend tests pass (10 opt-in skipped). Separate real-model suite: 10 pass;
  Flutter suite: 16 pass; analysis clean.
- Flutter debug server exited after WebSocket debugger errors; no listener remained
  on 3000. No code/data loss was found. Switching local UI serving to the compiled
  web build to avoid relying on the failed debug-service connection.
- Compiled web build passes and is served on loopback port 3000. Live Flutter run
  68acbb3b-ad97-4b55-a7ab-435df924b29a completed; B0/A0/A1 quantities match the fixed
  table exactly. Screenshot: output/review/fixed-proof-live.png. No scientific
  approval inferred. Recent changes remain local/uncommitted; no automatic push.

## Development dataset/index activation (2026-10-24, completed)

- Updated runtime defaults together to rc.4/dev.3; mock mode remains the default
  unless development mode is explicitly selected. Production review gates remain.
- Found a legacy mock service on port 8000 and no Flutter server on port 3000.
  Preserve that process and its possible in-memory history; start the corrected
  development service on 8123 and connect Flutter on 3000 to that service.
- Running readiness confirms rc.4/dev.3 and development_only=true. Flutter submitted
  a 45 g / 5% spirulina smoke run, displayed corrected claims, opened its printable
  report, and reopened the same saved result through history.
- Run: 7d59dcc1-fd1c-4ab8-84d0-4ac6219c407f. All 161 backend tests and 15 Flutter
  tests pass; Flutter analysis has no issues. Nine opt-in tests were skipped in
  the normal backend suite; their prior separate real-model pass is recorded.
- See DEVELOPMENT_ACTIVATION.md for addresses, launch/rollback instructions and
  the screenshot. This is not approval of a physical recipe or a production release.

## Corrected dataset RAG build and verification (2026-10-24)

- Built immutable dev.3 against rc.4 using the cached local model: 23 evidence notes.
- All eight existing retrieval questions pass at rank 1. Added nine real-model
  integration checks for corrected claims, API/report/persistence, mismatch
  rejection, production rejection and empty-source retrieval; all pass offline.
- Updated two stale test counts to reflect the audited 290-record/23-note corpus.
- Details and reproducible commands: REVIEWED_RAG_VERIFICATION.md.
- Combined-process opt-in suite hit a native OpenMP conflict loading PyTorch after
  FAISS tests. Keep normal and real-model suites in separate processes; no unsafe
  duplicate-library override was enabled. This limitation is documented.
- Final results: normal suite 161 passed / nine opt-in skipped; separate real-model
  suite nine passed; retrieval evaluation eight of eight; diff validation passes.
- Active defaults remain rc.1/dev.2; no live restart, scientific approval or
  production promotion occurred. Next is the paired development switch and UI check.

## Completion roadmap Step 2 - spirulina analytical audit (2026-10-24)

- Checked original full-text XML for both spirulina analytical papers; source
  URLs, hashes, coverage and limitations are in SPIRULINA_SOURCE_AUDIT.md.
- Corrected sample populations, material forms and manufacturer-reported drying.
- Verified 15 stored profile ranges/counts/identification levels and eight FD
  observations. Added reference-descriptor caveats directly to RAG claims.
- Corrected the outdated geosmin source note and the inference about an unlisted
  compound. Revised records remain extracted, with incremented versions.
- Runtime dataset and RAG index are not switched by this audit.
- Created and verified candidate rc.4: 290 rows in 21 tables; zero structural
  errors/warnings. Supplemental validation and prior rc.3 integrity pass.
- Next engineering action: build a matching development index and run retrieval
  and report regressions before an explicit active dataset/index switch.

## Completion roadmap - Step 1 (2026-10-24)

- Prepared `FIRST_RELEASE_SCOPE.md` for the new ten-step completion roadmap;
  the original eight implementation steps below retain their historical meaning.
- Defined a 45 g input-mass spirulina experiment at 2% inclusion with exact five-form
  B0/A0/A1 compositions, fixed cocoa/dates and a separate cinnamon substitution.
- Quantities are engineering assumptions for scientific review, not approved doses.
- Defined nutrition and sensory comparisons, claim boundaries, process unknowns,
  ownership and version-change rules. No scientific signatures were invented.
- Identified a mismatch with current generator controls: it removes all flavour
  whereas the original proof keeps cocoa. Recorded the required Step 5 alignment;
  runtime, frozen dataset and RAG index have not been changed by this scope work.
- Engineering preparation complete; formal signed-scope gate pending. Next is
  Step 2 source/record review against the five exact ingredient forms.

## Working agreement

### Completion roadmap Step 2 - methods verification (2026-10-24)

- Recovered both primary PDFs; inspected cinnamon methods and ITEPA recipe/sensory
  tables visually. Source hashes and locations are recorded in METHODS_SOURCE_AUDIT.md.
- Added two accurate study-material records; corrected cinnamon and ITEPA joins.
- ITEPA formula totals exceed its 100 g heading in algae arms. Cleared unsupported
  normalized bounds and retained reported labels. Confirmed 20 sensory panelists;
  recorded aroma significance contradiction rather than asserting no sensory effect.
- Revised source/evidence rows retain extracted status and increment versions.
- No active dataset/index switch or production publication. Scientific gate remains open.
- Verification: 290 rows / 21 tables pass structural validation with zero errors and
  warnings; supplemental validation passes. Created and verified candidate rc.3;
  rc.2 integrity still passes. Both remain non-production candidates.

### Completion roadmap Step 2 - first review pass (2026-10-24)

- Audited the five scoped ingredient forms, nutrient provenance, bounds and allergen
  relationships. Logged exact gaps in `SCIENTIFIC_REVIEW_STEP2.md`.
- Checked primary cinnamon journal abstract/licence, USDA documentation and spirulina
  profiling metadata/abstract. ITEPA access failed; no full-method validation claimed.
- Normalized the existing supplemental cinnamon source and one qualified evidence
  note into review inputs; both remain extracted. Material mapping is intentionally
  pending, so the note is not yet eligible for species-filtered retrieval.
- No scientific approval or production publication performed. Step 2 remains open.
- Validation passed: 288 rows / 21 tables, zero errors/warnings; supplemental packet
  15 sources / 25 records, zero errors. Created and verified rc.2 (23 evidence notes,
  11 normalized sources); verified rc.1 integrity. Active rc.1/dev.2 unchanged.
- Next: independently reproduce the five USDA nutrition records, obtain missing
  methods and study-material mapping, then review supplier-specific information.

### Implementation agreement

### Completion roadmap Step 2 - nutrition reproduction (2026-10-24)

- Downloaded the official April 2018 USDA SR Legacy archive and hashed it.
- Added an independent read-only audit for the five scoped foods, comparing food
  identity, basis, record dates, nutrient IDs, units, values and derivation metadata.
- All 31 populated nutrient values match; four absent ALA fields remain blank.
  Cinnamon ALA remains distinct from total omega-3.
- Negative checks reject altered protein, wrong basis and duplicate local records.
- Saved source rows and hashes in `output/review/scoped_nutrition_audit.json`;
  documented results and remaining supplier/reviewer limits in NUTRITION_SOURCE_AUDIT.md.
- No nutrition correction, approval, candidate rebuild or index switch was needed.
- Next: verify full cinnamon methods and study material mapping; recover ITEPA
  methods if available. Supplier/product information still requires team input.

### Standing agreement

Implement one step at a time. Record completed changes, verification, open issues,
and the next action here throughout the work and before any context handoff.
Preserve existing work. Scientific approval must not be inferred from code validation.

## Eight-step sequence

1. **Complete:** finish and validate the backend data model (scope below).
2. **User approval recorded; data gaps and row promotion pending:** approved, versioned dataset.
3. **Complete for development:** local embeddings, vector index and filtered retrieval.
4. **Complete:** connect real retrieval to the six-agent backend and API.
5. **Complete for constrained evidence explanations:** grounded generation with citations.
6. **Implemented for development screening; scientific/production gates remain:** formulation, nutrition, constraints, and reporting.
7. **Implemented and local-browser verified; native-device verification pending:** connect Flutter to the real run workflow.
8. **Implemented and verified for local development:** history, idempotency, failure recovery, database migration/backup/restore and release checks. Hosted production and scientific gates remain.

## Step 1 scope

Inspect existing schema definitions and validators; implement missing backend data
contracts and relationship validation; preserve compatibility with current data and
the mock API; test valid and invalid data. This step does not approve research or
implement retrieval.

## Work log

- Created this log before implementation.
- Checked repository status: existing planning documents and extraction work are
  uncommitted and will be preserved.

## Resume point

Read `docs/DATASET_PUBLICATION.md` and the candidate's `REVIEW.md` and
`EXTRACTIONS_REVIEW.md`. Mazharul Islam supplied approval in chat; the exact decision
and candidate hashes are recorded in `data/approvals/0.1.0-rc.1.json`. Do not ask for
that approval or name again. The approval does not supply missing scientific data
or verify chemical identities. Per-row promotion and release remain pending those
requirements. Current candidate: `data/candidates/0.1.0-rc.1`; preserve it. Prepare
corrections in input records, then create rc.2. Step 3 now works with the explicit
development candidate. Active index: `indexes/reviewed_evidence/0.1.0-dev.2`.
Read `docs/GROUNDED_GENERATION.md`. Step 5 is complete for exact-note, cited evidence
explanations (extractive by default; local Ollama optional and live-tested).
Step 6 now has exact-form experimental grid search, constraints, sourced nutrition
and reports; see `docs/FORMULATION_ENGINE.md`. Validated production bounds, complete
allergen/nutrition coverage and manufacturing/sensory evidence remain unresolved.
Step 7 Flutter now uses `/runs`; the local browser flow is verified. Step 8 has
SQLite persistence and restart-safe reports. History/filter/reopen/retry UI,
submission keys, durable attempt states, interruption detection, backup/restore and
the local release command are implemented; see `RUN_PERSISTENCE.md`.
Remaining product gates are scientific dataset publication/production formulations
and a deployment/identity design if the app is to leave single-user loopback use.
Real retrieval uses ALGAMASK_MODE=development; default mode
remains mock. Production retrieval still requires a release; no release was created.

## Step 8 work log

### Reliability completion — 2026-10-23

- Implementing history/reopen/filtering in Flutter, persisted submission keys,
  execution states with heartbeat-based interruption detection, explicit retry,
  storage readiness, backup/restore verification and a local release-check command.
- Execution remains in the local API process; no hosted deployment is configured.
  Changes will preserve existing SQLite version-1 records through migration.
- Added SQLite schema 2: submissions, attempt audit records, atomic claim/finish,
  30-second leases renewed every 5 seconds and stale-worker fencing. Retrying a
  prior attempt number is idempotent. Storage readiness and filtered history added.
- Flutter history/filter/reopen/retry implemented. Unresolved submission keys persist
  through local preferences; same-client concurrent submissions share one request.
  Added shared_preferences for device-side recovery; server database enforces keys.
- Added snapshot/restore tooling with exclusive destination creation and integrity /
  record validation. Restored in-flight attempts become interrupted for explicit retry.
- Added `tools/check_release.py` for combined backend/Flutter/data/index/workflow/
  backup checks. Production validation remains fail-closed on missing release gates.
- Combined verification passed: **161 backend tests, 15 Flutter tests**, clean
  Flutter analysis/build, real MiniLM retrieval with ready and insufficient-data
  outcomes, database backup/restore and identical restored reports. Production-mode
  check returned nonzero: current data is not an approved runtime release.
- Live browser verified real submission, saved-history reopening, simulated lease
  interruption recognition, explicit retry to a real report and reopening after
  browser reload. The earlier interrupted attempt remains in the audit records.
- Browser testing exposed a stale list status after retry; corrected the local row
  on report load. Targeted history tests, analysis and web build passed afterward.
- Added shared_preferences 2.5.6 and its resolved dependencies for local pending-key
  recovery. No hosted credentials/accounts or external deployment were configured.
- Screenshot: `var/verification/history-recovery.jpg`; verification-only SQLite file:
  `var/reliability-verification.sqlite3`. Existing user server/database untouched.
- README and persistence guide now describe current behavior, migration and recovery,
  inclusive UTC date filters, retry semantics, data retention and remaining gates.
- All implementation changes are local; no commit or push was requested for this stage.
- Stopped temporary verification servers on 8123/8310 after capturing proof. Retained
  the verification database and screenshot. Final `git diff --check` passed.

### Earlier persistence increment (historical)

- Starting local SQLite persistence with transactional writes, restart-safe reads,
  bounded history and explicit storage errors. No automatic deletion of old runs.
- Will verify the browser workflow against a loopback development server. No
  production exposure or scientific approval changes are included.
- Implemented configurable SQLite run storage, transactional inserts, schema-version
  checks, validated reads and paginated history. Removed silent 100-run eviction.
- Storage errors return explicit 503 responses without a false durable success;
  missing IDs remain 404. Tests use isolated temporary databases, never user history.
- Verification: **153 backend tests passed**; custom-port Flutter web build succeeded.
  Tests cover concurrent inserts, 105 retained runs, duplicate protection, corrupt
  payloads, storage outage handling and reopening/report equality.
- Live in-app browser: Flutter → `/runs` → local MiniLM retrieval → screened candidates
  and nutrition succeeded. Allergy-excluded run displayed insufficient-data reasons.
  Its print-ready button opened the stored report; reloading the same report after a
  backend process restart succeeded. Verification DB: `var/browser-verification.sqlite3`.
- Screenshot: `var/verification/persisted-report.jpg` (ignored local artifact).
- Existing server on port 8000 was not changed. Verification used ports 8123/8310.
- Stopped both temporary verification servers after the restart check; retained the
  verification database and screenshot. `git diff --check` passed. No commit/push.
- Remaining Step 8: Flutter history/reopen UI, idempotency and durable execution-failure
  handling, backup/restore verification, release checks and security/deployment scope.
  No claim of production readiness or completed scientific validation.

## Step 7 work log

- Connecting Flutter to `/runs` with editable species/serving/targets, real evidence,
  nutrition and explicit blocked states. Preserve all local Step 6 changes.
- Replaced legacy two-card preview UI with the full experimental run form and report.
  Added algae/serving controls, optional validated nutrition targets, milk/soy
  exclusions, loading/duplicate-submit protection and retryable failures.
- API client now uses `/runs`, checks the response envelope, waits up to 120 seconds,
  and creates report links from the same configured host. No automatic POST retry.
- Reports expose submitted settings, mock/development/released-evidence mode,
  citations, source links (HTTP/S only), dataset identity, ingredient amounts,
  nutrient estimates/unknowns/provenance, all grid verdicts, trace and limitations.
- JSON copy and print-ready report actions retained. Display explicitly separates
  submitted results from subsequently edited inputs. No recipe is called safe or
  production-approved. Backend data/approval statuses are unchanged.
- Verification: **11 Flutter tests passed**, **149 backend tests passed**,
  `flutter analyze` reported no issues, `flutter build web` succeeded and
  `git diff --check` passed. No dependency upgrades were requested or performed.
- Added API contract/error tests and phone-width widget coverage for ready,
  insufficient-data and generation-failed reports, unknown nutrients, invalid target
  input and retry state. Documented local run commands in `apps/flutter/README.md`.
- Remaining verification: live browser → running backend → displayed report, actual
  clipboard/external-link behavior and physical-device networking. Unit/widget tests
  and compilation do not establish those. No server or browser session was started.
- Step 8 persistence remains unimplemented; report URLs depend on in-memory runs.
  All changes remain local and unpushed, including the preserved Step 6 changes.

## Step 6 work log — in progress

### Integrated development screening increment

- Retained the verified retrieval dataset snapshot for numerical work; no mutable
  reviewed-directory fallback or guessed mapping from mock ingredient IDs.
- Added a deterministic nine-point exact-form grid with explicit engineering
  assumptions, independent Critic checks, stable protein ranking and top-three output.
- Added per-serving protein minimum, calorie maximum and sugar maximum requests.
  Unknown required nutrients fail checks; mock mode cannot silently ignore targets.
- Added conservative milk/soy/peanut/tree-nut/sesame exclusion handling: incomplete
  free-from coverage blocks a candidate. Direct oats/coconut exclusions also checked.
- Added matched B0/A0 controls for the top candidate, nutrition provenance, declared
  comparison basis, per-serving/per-100-g report tables and all grid verdicts.
- Production formulation remains blocked; the single snack-bar bound is not reused
  as a validated protein-bar bound. No dataset rows or approvals were modified.
- Real offline MiniLM/API/report smoke test passed: Spirulina with 5 g protein minimum
  and 200 kcal maximum returned three candidates; blend retained unknown energy;
  a 5 g sugar maximum returned insufficient data with no candidates.
- Development workflow implementation is ready for Flutter integration, not product
  manufacture. Larger optimization spaces and production eligibility require the
  missing reviewed constraints/data documented in `FORMULATION_ENGINE.md`.
- This increment remains local; no commit or push requested/performed.
- Final verification: **149 tests passed**, real local retrieval/API smoke checks
  passed, and `git diff --check` passed.

### Earlier nutrition foundation increment (historical)

- Continuing with a bounded, deterministic engineering search over exact ingredient
  forms, independent mass/inclusion/exclusion/target checks, matched controls and
  API/report nutrition. Search proportions are explicit experimental assumptions,
  not inferred from retrieved passages or promoted to scientific safety bounds.

- Started with the dataset-backed nutrition foundation. Existing recipes still use
  mock ingredient IDs; they must not receive nutrition by guessing ingredient forms.
- Missing Chlorella energy, incomplete allergen coverage and matrix-specific bounds
  prevent claiming fully validated recipes. Preserve the frozen candidate unchanged.
- Current increment: exact-form calculations, missing-value propagation, record-level
  provenance and regression tests. Optimizer/API/report integration follows afterward.
- Implemented `estimate_nutrition` using validated dataset snapshots and exact
  ingredient-form IDs, with per-serving/per-100-g estimates and protein per 100 kcal.
- Defaults to approved records; development use is explicit. Missing/ambiguous
  records fail closed for each nutrient. Full source records and qualifications are
  retained. Sugar and total omega-3 remain unknown; no unsupported substitutions.
- Hardened scalar nutrition arithmetic against negative/nonfinite values and overflow;
  zero-mass entries do not contaminate a nonempty estimate with missing values.
- Verification: **108 tests passed** (10 new regression cases). Documented boundaries
  and remaining work in `docs/FORMULATION_ENGINE.md`. API/report integration and
  constrained recipe generation are **not complete**; Step 6 remains in progress.
- Changes are local, not committed or pushed. Resume with exact-form recipe
  generation and independent constraints, then wire nutrition into API/report output.

## Step 5 work log

- Added strict generation contracts, exact-note grounding checks, source/dataset-bound
  citations, a versioned prompt and prompt hash, and one bounded correction retry.
- Default extractive generation works without a model server. Optional local Ollama
  generation selects/reproduces supported notes; it cannot introduce free-form claims
  or doses. Methods are labelled separately in every generation result.
- Found installed Ollama/Llama 3.2; started a temporary server on loopback port 11435
  for live verification. No model was downloaded and no hosted provider was contacted.
- Connected generated explanations to Chemistry and independent metadata/text checks
  to Critic. Invalid generation blocks recipe/impact work and is stored as a failed run.
- HTML reports include cited explanations with links to retrieved notes, provider,
  method, model, original matrix, support class and review status.
- Real-model API test passed with five grounded claims. First response failed schema
  validation; the one correction retry succeeded. Model digest:
  `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
- Added tests for invented IDs, altered numbers, removed qualifications, missing
  evidence families, metadata tampering, injection attempts and provider outages.
- Git handoff completed: implementation commit `46a27c4` was pushed successfully to
  `origin/main` without force. This log records the verified push result.
- Final verification: **98 tests passed** and `git diff --check` passed. Added local
  transport/model-identity tests and an API test proving failed generations remain
  inspectable without returning mock formulations.
- Added `docs/GROUNDED_GENERATION.md` with exact scope, configuration, output and
  failure contracts. Free-form claims and new recipe/dose facts are intentionally
  outside this step's exact-note grounding contract.
- Stopped the temporary Ollama server started for verification on port 11435.
- Fetched origin/main before committing: local and remote were aligned at 66a0880;
  Step 4 was already committed/pushed. Only this step's changes need publishing.

## Step 4 work log

- Added explicit mock/development/production retrieval settings and a lazy, locked
  offline model/index loader. Native retrieval libraries remain optional in mock mode.
- Moved search request/response contracts into a dependency-light module; retained
  compatibility imports from `rag.py`.
- Connected species-specific diagnosis searches and a flavour/inclusion intervention
  search to the Retrieval agent. Blend runs query both species separately.
- Recorded per-query evidence, candidate status, dataset hash, embedding identity and
  index version in run/trace output. Missing required evidence blocks all later roles.
- Added `/rag/search` and `/rag/ready`; `/health` reports configured mode/readiness.
  Retrieval failures return 503, with no automatic mock fallback or saved success.
- Kept other agent roles explicitly demonstrational. Chemistry records context IDs,
  not support claims; placeholder recipes have no scientific citations in real mode.
- Updated HTML reports to show real evidence provenance, retrieval mode and trace,
  while labelling demonstration recipes and unknown nutrition/sensory outcomes.
- Verification: **73 tests passed**. Real-model offline API smoke checks passed for
  spirulina/chlorella/blend with **6/6/9 passages** and successful report rendering.
  Unknown-source query returned insufficient evidence.
- Added `docs/RAG_WORKFLOW.md` with start commands and exact integration boundaries.
  Flutter still uses its previous preview route; connection is planned for Step 7.
- Existing approval files remain untouched. No commit, push or server restart was
  performed. Changes are local.

## Step 3 work log

- User requested the next step. Scope: pinned local embedding provider, versioned
  FAISS index, metadata-filtered search, explicit empty results and evaluation.
- Inspected existing stubs, eight evaluation questions, dependency configuration
  and API. The existing mock workflow remains for Step 4 integration.
- Checking runtime/package compatibility before choosing the embedding runtime.
- Installed the optional locked `rag` dependencies: sentence-transformers 6.2.0
  and faiss-cpu 1.15.1. Existing Python 3.14 is supported; no runtime change needed.
- Pinned MiniLM model revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Added local CPU embeddings, normalized FAISS cosine indexing, provenance-preserving
  metadata, pre-ranking filters and strict dataset/model/index compatibility checks.
- Added build/search/evaluation CLI. Model loading is offline by default; initial
  download requires an explicit flag. Live build/evaluation and regression tests next.
- First real embedding run crashed in native CPU execution; retry with one OpenMP
  thread and tokenizer parallelism disabled succeeded. Added these default settings
  before native-library imports. Package availability alone did not prove runtime stability.
- Built `indexes/reviewed_evidence/0.1.0-dev.1` from all 22 candidate chunks with the
  real MiniLM model. Cached model weights are local; no API key is required.
- Regression suite: **63 passed**. Draft retrieval quality evaluation is next.
- Vector-only evaluation: **7/8 rank-one checks**, MRR 0.892857. EV-02 (highest
  FD factors) retrieved the expected chunk at rank 7.
- Tested pinned local cross-encoder reranking. Float32 produced NaNs on this
  machine; float64 worked, but quality remained 7/8 with EV-02 at rank 8. Kept
  reranking opt-in rather than making a non-improving experiment the default.
- Resumed after interruption. Testing source-title/location enrichment in indexed
  text as version 2. Original evaluation artifacts and index remain preserved.
- Source enrichment succeeded: active dev.2 returns the expected chunk at rank 1
  for **all 8 draft questions**, MRR **1.0**. No claims or evaluation questions changed.
- Offline smoke check with `HF_HUB_OFFLINE=1`: unrelated orbital-mechanics query
  returned `insufficient_evidence` with no hits. Report saved under `output/rag/`.
- Final regression run: **65 tests passed**. No model downloads are needed for
  these tests; a test-only deterministic provider exercises index invariants.
- Added `docs/LOCAL_RETRIEVAL.md`, reproduction commands, evaluation caveats,
  model/runtime details and the explicit Step 4 integration boundary.
- These eight questions are development checks, not held-out scientific validation.
  Candidate review status remains visible. Current app workflow still uses mock data.
- Final data validation: **286 records, zero errors/warnings**; candidate integrity
  verification and `git diff --check` passed. Changes remain local, uncommitted.

## Step 2 work log

### Approval received — 2026-10-22

- User instructed “approve them” and supplied reviewer name **Mazharul Islam**.
- Recorded that approval for the 286 candidate records in a separate decision file,
  tied to the candidate content hash and review-report hash. This preserves rc.1.
- Row statuses have not been promoted: chemical identities still say
  `pubchem_matched`, not `verified`; dependent approval and ingredient coverage
  checks still apply. Approval alone must not invent those facts.
- Inspection of the candidate review queue found no missing approval-required
  fields besides reviewer/date. The outstanding issues are semantic verification,
  dependencies, demo assumptions and incomplete ingredient coverage, rather than
  additional blank required cells.
- Release remains unpublished. This is a recorded user approval, not a claim that
  the assistant performed independent scientific verification.
- Verified the candidate is unchanged, the approval JSON is valid and contains the
  requested name/scope, and `git diff --check` passes.

- Rechecked repository status: clean at the start of Step 2; Step 1 files are present.
- Read the progress log, dataset plan and supplemental extraction records.
- Existing dataset plan requires human scientific approval. Supplemental extraction
  records include unresolved units, permissions and incomplete methods; these must
  remain review candidates until resolved.
- Implemented dataset audits with per-record missing approval fields, dependency
  lists, ingredient coverage, and publication blockers.
- Added candidate/publication/verification commands, content hashes, immutable
  version paths, concurrent-build reservations and cleanup of failed builds.
- Production publication requires approved records and minimum corpus coverage;
  supplemental extractions remain candidate-only. Regression tests are pending.
- Created and verified `data/candidates/0.1.0-rc.1`, preserving 286 records in 21
  tables and the separate 15-source/25-record extraction packet. The candidate
  includes human-readable review reports, machine-readable records and SHA-256 hashes.
- Added `docs/DATASET_PUBLICATION.md` with commands, review order and known limits.
- All 286 current records remain extracted; no scientific approval was invented.
  There are 19 nutrition rows, one screening bound and five allergen relationships
  for 20 forms. These coverage gaps and per-record dependencies are in the packet.
- Initial publication tests: 46 total tests passed. Final supplemental and
  approval-bypass checks added; final verification pending below.

### Step 2 verification and remaining gate

- Final backend suite: **48 passed**, with the existing Starlette deprecation warning.
- Reviewed dataset: **286 records / 21 tables / zero validation errors or warnings**.
- Supplemental extraction validation and sprint validation: **passed**.
- Candidate integrity verification and `git diff --check`: **passed**.
- Tests prove deterministic content hashes, rejection of unapproved publication,
  no overwrite, failed-build cleanup, path validation, tamper detection, supplemental
  preservation and successful publication of a synthetic approved test corpus.
- Current production release: **not published**. A human scientific reviewer must
  resolve the review queue and missing coverage before the approved-release gate passes.
- Changes remain local; no commit or push performed. Step 2 is not scientifically
  complete merely because its publication tooling is ready.

### Inspection findings

- No repository `AGENTS.md` was found in the repository file search.
- The schema covers 21 tables but backend consumers have no typed dataset loader.
- List relationships do not enforce approved dependencies; floats accept NaN and
  infinity; several range and cross-record consistency checks are absent.
- Schema generation currently overwrites reviewed tables and the source manifest.
- Moved the canonical schema into the backend package and retained the tooling
  import path through a compatibility module. No CSV data or review statuses changed.

### Implemented, verification pending

- Added generated Pydantic record models for every table, preserving the canonical
  schema and approval-only requirements. Empty values become `None`.
- Added a reusable dataset loader with structured errors, complete-file validation,
  duplicate/orphan checks, approved dependency checks (including lists), finite
  numbers, numeric ranges, ingredient-bound matching, and approved recipe mass checks.
- Preserved existing scientific checks and added retrieval evaluation reference checks.
- Made template generation preserve existing reviewed files and source manifests.
- Added finite-number, positive-mass, unique-ingredient and mass-balance API contracts.
- Next: wire the validation CLI, run baseline and regression tests, document usage.

### Verification progress

- Initial checks: all 18 existing tests passed; 286 records passed basic validation.
- Added regression checks for nonfinite/negative values, orphans, duplicate IDs,
  malformed rows, approval dependencies, cycles, unknown values, safe template
  generation and API mass contracts.
- Expanded JSON validation exposed three plain-text `recipe_json` values. Encoded
  the descriptions as JSON, incremented record versions to 2, and corrected the
  generator. No scientific values or review statuses changed.
- Added `docs/BACKEND_DATA_MODEL.md` describing the contracts and their boundaries.
- Final verification completed successfully (see below).

### Final verification and handoff

- `uv run pytest -q`: **37 passed** (18 existing tests plus 19 new cases).
- `uv run python tools/validate.py`: **286 rows, 21 tables, zero errors/warnings**.
- `uv run python tools/validate_extractions.py`: **15 sources, 25 records, zero errors**.
- `uv run python tools/validate_sprint.py`: **passed**.
- `git diff --check`: **passed**.
- Existing dependency warning: Starlette reports its httpx TestClient integration
  as deprecated; this did not fail any tests.
- No RAG, publication, scientific approval, database persistence or Flutter changes
  were included in Step 1. Changes are local and have not been committed or pushed.
- No dependencies were added. Existing uncommitted planning/extraction work remains.
