# Corrected dataset RAG verification

Date: 2026-10-24. Status: development-only pair built and tested, not activated.

Subsequent activation completed: see [DEVELOPMENT_ACTIVATION.md](DEVELOPMENT_ACTIVATION.md).
The build-stage account below is retained as verification history.

## Frozen pair

- Dataset: `data/candidates/0.1.0-rc.4`, 290 records and 23 evidence notes.
- Index: `indexes/reviewed_evidence/0.1.0-dev.3`, 23 vectors.
- Dataset content hash: `e999303a8afda5624002ec8ac27994c40b4ae9b9faf59fa72aecd70336c34432`.
- Index content hash: `56ffc86d7255b2b05f927ed25961e176a3e090b5313fea6788b862a0ae26cff4`.
- Same pinned local MiniLM model and source-enriched text preparation as dev.2.
  No external model API, model download or reranker was needed.

Earlier datasets and indexes are preserved. Runtime defaults remain rc.1/dev.2.
This build does not restart the running application or change its configuration.

## Checks

The eight existing draft retrieval evaluations pass, each with the expected note
at rank 1 (MRR 1.0). Results: `output/rag/dev3-rc4-evaluation.json`. These are
development regression questions, not independent evidence of general RAG accuracy.

Nine additional opt-in integration checks pass with the real cached model:

- Source/species-filtered retrieval retains the corrected cinnamon, hexanal,
  geosmin and recipe-denominator caveats.
- Spirulina, chlorella and blended requests complete the API's six-agent flow.
  Extractive generated statements exactly match retrieved claims and cite the
  matching source. Reports retain development warnings, unknown sensory results,
  dataset/index provenance and nutrition source records.
- API persistence returns the same run. Tests use isolated temporary databases,
  not the user's existing run history.
- Production rejects the unapproved candidate. Mixing rc.4 with the old dev.2
  index is rejected. An unknown source filter returns insufficient evidence.

The full suite initially exposed two stale corpus-count expectations from before
the scientific audit. Updated them to 290 records and 23 extracted notes; the
approval safeguards were not weakened.

Final results: normal suite 161 passed and nine opt-in checks skipped; separate
real-model suite nine passed. Whitespace/diff validation also passes.

## Reproduce without downloads

```sh
HF_HUB_OFFLINE=1 .venv/bin/python tools/rag.py evaluate \
  --dataset data/candidates/0.1.0-rc.4 \
  --index indexes/reviewed_evidence/0.1.0-dev.3 --development

.venv/bin/python -m pytest -q

HF_HUB_OFFLINE=1 ALGAMASK_TEST_REVIEWED_RAG=1 .venv/bin/python -m pytest -q \
  tests/algamask/test_reviewed_rag_integration.py
```

Run the two test commands in separate processes on this macOS environment.
Enabling the integration checks across the entire suite caused a native OpenMP
abort when PyTorch loaded after FAISS tests had initialized their runtime. The
standalone integration suite and normal suite are therefore verified separately.
No unsafe duplicate-library override is enabled. The combined-process native
dependency conflict remains a test-environment limitation, not a passed check.

## Next boundary

Switch the development app to this dataset and index together, then smoke-test the
running service and Flutter flow. Old persisted runs retain their original evidence
snapshots. Do not present this as scientific approval or a production release.
Supplier records, qualified review and physical experiments remain unresolved.
