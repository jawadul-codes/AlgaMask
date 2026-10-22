# AlgaMask implementation progress

Updated: 2026-10-22

## Working agreement

Implement one step at a time. Record completed changes, verification, open issues,
and the next action here throughout the work and before any context handoff.
Preserve existing work. Scientific approval must not be inferred from code validation.

## Eight-step sequence

1. **Complete:** finish and validate the backend data model (scope below).
2. Convert extracted research into an approved, versioned dataset.
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

Step 1 is complete. Next is Step 2: review extracted research, resolve missing
provenance/permissions and ingredient coverage, and implement versioned publication.
Begin by reading this log and `docs/BACKEND_DATA_MODEL.md`, then inspect current Git
status. Scientific approval remains outstanding; do not auto-promote extracted rows.
The application still uses mock evidence. Database persistence remains in Step 8.

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
