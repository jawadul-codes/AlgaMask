# Task-based implementation backlog

The sprint document is treated as a requirements reference. Tasks below have no calendar deadlines.

## Completed skeleton

- Flutter web app with algae, inclusion, serving mass, flavour and exclusion inputs.
- FastAPI health, run, stored run and printable report endpoints.
- Six mock roles, observable trace, three deterministic concepts and B0/A0 controls.
- Ingredient membership, positive mass, exclusion and mass-balance checks.
- Synthetic sensory/evidence cards; unknown impact values; JSON copying and print-to-PDF.
- Eleven CSV templates, request fixtures and API/widget tests.

## Data and provenance

- Curate spirulina and chlorella records, 15–30 compounds, 20–40 ingredients and 20+ approved evidence chunks.
- Add source metadata, review status, licensing notes, nutrition and numeric screening bounds.
- Validate CSV types, joins, duplicate IDs, units and approval provenance.
- Freeze a dataset version with hashes; add a reviewed baseline and control recipe.

## Retrieval and molecular mapping

- Implement PubChem cache and RDKit fingerprints/descriptors with fixed parameters.
- Configure embeddings and FAISS or Chroma; apply metadata filters and diversity reranking.
- Link species → observations → compounds → sensory categories → intervention evidence.
- Implement normalized fusion scoring and reduced confidence for missing modalities.

## Formulation and orchestration

- Replace synthetic ingredient proportions with reviewed concentration bounds and constrained search.
- Add calorie, sugar and complete allergen constraints; validate mechanism citations.
- Add typed role-specific schemas, provider adapter, bounded retry and up to two critique revisions.
- Add explicit state transition checks and degraded fallback traces.
- Persist run records, model/prompt versions, rejected candidates and score breakdowns.
- Connect live progress events to the Flutter trace; current progress is a request-level loading indicator.

## Impact and experiments

- Import reviewed nutrition and calculate density per serving and per 100 kcal.
- Prepare B0/A0/A1 physical prototypes; record blinded trial ratings and methods.
- Calculate descriptive sensory comparisons with sample size, variability and limitations.
- Add report sections for provenance, full trace, assumptions and next experiment.

## Verification and release

- Expand tests for real retrieval, fingerprints, bounds, fallback/revision limits and impact arithmetic.
- Add native Flutter platform projects when target devices are chosen; current runnable target is web.
- Add persistent storage, deployment configuration and an offline saved-run fallback.
- Verify a clean setup, fixed demo scenario and alternative scenario; prepare presentation artifacts.
