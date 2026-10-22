# AlgaMask implementation progress

Updated: 2026-10-22

## Working agreement

Implement one step at a time. Record completed changes, verification, open issues,
and the next action here throughout the work and before any context handoff.
Preserve existing work. Scientific approval must not be inferred from code validation.

## Eight-step sequence

1. **Complete:** finish and validate the backend data model (scope below).
2. **User approval recorded; data gaps and row promotion pending:** approved, versioned dataset.
3. **Complete for development:** local embeddings, vector index and filtered retrieval.
4. **Complete:** connect real retrieval to the six-agent backend and API.
5. **Complete for constrained evidence explanations:** grounded generation with citations.
6. Complete formulation, nutrition, constraints, and reporting.
7. Connect Flutter to the real run workflow.
8. Add persistence, failure handling, and release verification.

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
explanations (extractive by default; local Ollama optional and live-tested). Next is
Step 6: evidence-driven formulation, nutrition, constraints and reporting. Recipes
remain demonstrations. Real retrieval uses ALGAMASK_MODE=development; default mode
remains mock. Production retrieval still requires a release; no release was created.

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
