# Dataset review and publication

Step 2 introduces a reproducible candidate packet and an approved-release build.
It does not assign scientific approval automatically.

## Current candidate

`data/candidates/0.1.0-rc.1` freezes the current 286 records across 21 tables plus
the supplemental packet of 15 selected sources and 25 extractions. The two source
sets overlap; do not add their counts. Supplemental records are not yet normalized
into the runtime tables.

Read `REVIEW.md` for table counts, ingredient coverage and the review queue.
`review.json` contains every exact record, missing approval fields and unapproved
dependencies. `EXTRACTIONS_REVIEW.md` lists source access/permission notes and each
supplemental record's unresolved limitations. Original extractions are preserved.

## Commands

```sh
uv run python tools/publish_dataset.py candidate 0.1.0-rc.1 --extractions data/extractions/day2_sources.json
uv run python tools/publish_dataset.py verify data/candidates/0.1.0-rc.1
```

Existing versions cannot be overwritten. Make corrections in the review inputs,
increment corrected record versions, then build a new candidate version.

Once the records have actually been reviewed and approved:

```sh
uv run python tools/publish_dataset.py publish 0.1.0 --reviewer 'Actual reviewer name'
uv run python tools/publish_dataset.py verify data/published/0.1.0 --require-release
```

The reviewer argument identifies responsibility for publication; it does not approve
rows. Each scientific row must already have approved status, reviewer, date and
required provenance. The publisher validates the full copied dataset. It rejects
unapproved rows, demo assumptions, insufficient approved corpus counts, missing
ingredient coverage, and absent diagnosis/intervention evidence. For a smaller
release scope, prepare a separate complete input directory with reviewed dependency
closure; do not relabel unwanted records as approved to get past the gates.

## Reproducibility

Every artifact has per-file SHA-256 hashes, a combined content hash, validation report
hash, schema version, row counts, build time and Git commit. Builder file hashes
capture local implementation changes even before commit. The combined hash excludes
the timestamp-bearing manifest, so identical content produces the same content hash.
Verification rechecks bytes and re-runs dataset gates. These checks detect corruption;
they are not a digital signature or proof of who reviewed the science.

Builds reserve the version name exclusively and rename a validated temporary directory
into place. Failed builds remove only their own temporary directory. An interrupted
process may leave a lock or temporary directory; inspect it before manual cleanup.
Published artifacts are immutable by the tool, not protected from manual file edits.

The release manifest is the publication registry. The reviewed `dataset_versions.csv`
is retained as input metadata; the publisher does not modify its own input or create
a self-referential content hash. Runtime code must use `verify(require_release=True)`.
Embedding/index metadata remains absent until Step 3 creates a separately hashed
index linked to this dataset content hash.

## Review order and current decisions

1. Resolve source metadata, access and permission notes first. Existing source flags
   and licence statements have not been newly verified by this engineering pass.
2. Verify chemical identities and material/process mappings, then their dependent
   observations, sensory relationships and evidence notes.
3. Complete ingredient-form nutrition, bounds and allergen coverage. Current data
   contain 19 nutrition rows, one bound and five allergen relationships for 20 forms.
   Missing allergen data must not be interpreted as allergen-free.
4. Resolve supplemental extraction limits before normalization: dry-weight versus
   as-sold nutrition, unspecified inclusion bases, microlitres versus mass, incomplete
   recipes, and evidence from matrices other than the project's protein bar.
5. Review evidence chunks and golden questions, then publish only after the graph
   and coverage gates pass.

A human scientific reviewer is required by the agreed dataset plan. Step 2's final
approved-release gate remains pending until those decisions are supplied. The
engineering tests and candidate freeze do not satisfy that gate.
