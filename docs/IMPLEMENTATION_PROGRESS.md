# AlgaMask implementation progress

Updated: 2026-10-24

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
