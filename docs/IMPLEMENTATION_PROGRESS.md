# AlgaMask implementation progress

Updated: 2026-10-22

## Working agreement

Implement one step at a time. Record completed changes, verification, open issues,
and the next action here throughout the work and before any context handoff.
Preserve existing work. Scientific approval must not be inferred from code validation.

## Eight-step sequence

1. **Complete:** finish and validate the backend data model (scope below).
2. **Engineering complete; scientific review pending:** approved, versioned dataset.
3. Implement local embeddings, a vector index, and filtered retrieval.
4. Replace mock retrieval in the six-agent backend.
5. Add grounded generation with citations.
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
`EXTRACTIONS_REVIEW.md`. Step 2's tooling and candidate are complete; the approved
release is pending human review and missing ingredient/source data. Current candidate:
`data/candidates/0.1.0-rc.1`. Do not overwrite it or auto-promote records. Prepare
corrections in input records, then create rc.2 after review. Step 3 has not started.

## Step 2 work log

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
