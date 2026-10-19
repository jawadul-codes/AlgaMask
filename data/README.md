# Data contract

`reviewed/` contains header-only CSV templates from the project brief. No scientific records have been reviewed or approved yet. Blank numeric cells mean unknown, never zero. Join records by IDs; preserve units, provenance, ingredient form and review status.

Synthetic runtime data lives in `services/algamask/fixtures.py` and is never passed off as reviewed data. The future index must load only approved chunks with valid source references. CSV ingestion, cross-table validation and publication are pending tasks.

`fixtures/demo_scenarios.json` supplies reproducible requests. Baseline and unmasked controls are generated from the same request by `optimizer.build_formula`, keeping serving size and algae inclusion consistent.
