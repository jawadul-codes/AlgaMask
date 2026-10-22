# Day 2 literature extraction

`day2_sources.json` is the review packet for the 15 selected sources. It contains
25 new structured records from seven papers and links nine sources to their
existing CSV extractions. One paper (ITEPA) occurs in both groups because its
existing extraction was extended. These counts describe coverage, not completed
full-text review of all 15 sources.

Start with the [review guide](../../docs/DAY2_EXTRACTION_REVIEW.md).

## Data contract

- Packet metadata supplies `extracted_at`, `extracted_by`, `record_version` and
  `review_status` for every source and finding. Its `evidence_status` applies to
  the 25 new findings, not the linked pre-existing database rows. Every new
  finding is literature-derived, including
  measurements performed by the paper's authors. None are project measurements.
- Follow `record_id` → `source_id` → source URL/DOI, then `source_location` to
  inspect the exact section, table or page. Page numbers are printed journal
  pages, not PDF viewer indices.
- `data` preserves the original unit, basis, population and ingredient form.
  `null` means unknown. Zero is only used for a reported zero.
- `limitations` applies to the individual record. `access_level` distinguishes
  full-text sections, abstracts, indexed snippets and earlier extractions.
- Source `retrieved_sha256`, where present, identifies the exact PDF inspected.
  PDFs are temporary local research files and are not part of this dataset.
- `coverage=existing_extraction` links to `data/reviewed/sources.csv`; it does not
  claim that those rows were scientifically rechecked in this pass.

Study recipes are kept here because the existing formulation tables describe
project B0/A0/A1 recipes. Likewise, the project's sensory trial tables should not
receive another study's participant data. This JSON packet supports the study
metadata without mixing those meanings or changing the running application.

## Validation and publication

Run `uv run python tools/validate_extractions.py` from the repository root.
It checks IDs, source links, DOI consistency, provenance fields, measurement
units/bases, recipe completeness and 100 g totals for complete recipes.
It cannot establish that a scientific claim is true or that a licence permits
a particular downstream use.

The existing dataset check remains `uv run python tools/validate.py`.
Neither command approves records. This packet has `review_status=extracted`
and `runtime_eligible=false`, consistent with the existing repository contract.
Resolve the listed issues, record the reviewer and decision, and map accepted
claims into the appropriate reviewed tables before publishing a dataset version
or building the approved retrieval index. Do not mark an entire paper approved
just because one finding has been checked.
