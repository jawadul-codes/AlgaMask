# Backend data model

Step 1 implementation, 2026-10-22. Schema contract version: `1.0.0`.

## Canonical contracts

`services/algamask/dataset_schema.py` defines all 21 scientific tables, their
columns, controlled vocabularies, relationships, and approval requirements.
`tools/schema.py` retains compatibility for existing ingestion scripts.
`services/algamask/dataset.py` generates Pydantic record classes from that same
definition; table definitions and runtime types cannot drift independently.

CSV remains the review/import format. This step introduces a validated in-memory
snapshot; database persistence and dataset publication belong to later steps.

## Loading

```python
from pathlib import Path
from algamask.dataset import load_dataset, DatasetValidationError

snapshot = load_dataset(Path("data/reviewed"))
chunks = snapshot.records("evidence_chunks", approved_only=True)
counts = snapshot.row_counts
```

All files must be present, even when a table contains only a header. Loading checks
the entire dataset and raises `DatasetValidationError` with structured `issues`
on any error. It never returns a partially valid dataset. Row numbers refer to CSV
records, including the header as row 1. Warnings remain in `snapshot.issues`.

Records are frozen Pydantic models. Empty optional cells become `None`; zero remains
zero. Semicolon-separated foreign-key lists become tuples. Dates and timestamps
become Python date/datetime values. Use `model_dump(mode="json")` for JSON output.
Record JSON schemas are available through `RECORD_MODELS[table].model_json_schema()`.

## Validation boundaries

- Exact headers, row widths, required fields, controlled vocabularies and types.
- Unique primary keys, valid references, and approved dependencies for approved rows.
- Finite numeric values, positive versions/masses and sensible percentage ranges.
- Observation units/bases, verified chemical identity for approved compounds,
  verbatim permission, and evidence support classification.
- Per-100-g nutrition with unknown values preserved; ingredient-bound identity.
- Approved formulation lines, required ingredient coverage, and mass balance.
- Retrieval evaluation references, JSON fields, and cyclic parent/amendment links.

These are structural checks. Passing them is not scientific approval. Current
records remain extracted, so approved-only evidence is empty. Step 2 must resolve
source review, provenance and publication; Step 3 implements retrieval. A snapshot
is not an immutable published release and carries no content/index hash yet.

The existing mock API additionally rejects nonfinite inputs, unknown run options,
nonpositive ingredient masses, repeated ingredients and inconsistent total mass.
It still uses its existing mock evidence and workflow.

## Commands

```sh
uv run python tools/validate.py
uv run pytest -q
```

`tools/build_schema.py` now creates only missing reviewed tables and manifests.
It regenerates dictionaries but preserves existing data, including mismatched
headers: a schema migration must be deliberate and followed by validation.

The three draft formulation descriptions were encoded as JSON objects in
`recipe_json`; their record versions increased to 2. Their values and scientific
status are unchanged. The extraction generator now emits that corrected format.
