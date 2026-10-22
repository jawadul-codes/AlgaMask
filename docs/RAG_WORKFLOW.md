# Retrieval-connected workflow — Step 4

The backend can now use the Step 3 local index through `/runs` and `/rag/search`.
The six-agent trace distinguishes real retrieval and grounded explanations from the
remaining demonstration roles. Step 5 is documented in `docs/GROUNDED_GENERATION.md`;
Step 6 handles real formulation calculations and constraints.

## Start the backend

From the repository root, with Step 3's cached model and dev.2 index:

```sh
uv sync --locked --extra dev --extra rag
ALGAMASK_MODE=development uv run --extra rag uvicorn algamask.api:app --host 127.0.0.1 --port 8000
```

The default remains `mock` for compatibility with the existing skeleton. Setting
`ALGAMASK_MODE=development` enables actual candidate retrieval. Change the environment
before starting the server; restart an existing server to apply changes. No model
download happens in the API. Cache the model using the Step 3 build command first.

Optional environment overrides:

| Variable | Default |
|---|---|
| `ALGAMASK_MODE` | `mock` (`development` and `production` also accepted) |
| `ALGAMASK_DATASET_PATH` | Repository `data/candidates/0.1.0-rc.1` |
| `ALGAMASK_INDEX_PATH` | Repository `indexes/reviewed_evidence/0.1.0-dev.2` |

`production` requires a published dataset and compatible non-development index.
It describes retrieval eligibility, not production readiness of the full app.
The current candidate fails that requirement, as intended.

## API

```sh
curl http://127.0.0.1:8000/rag/ready

curl -X POST http://127.0.0.1:8000/rag/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"What relative area was reported for hexanal?","species":"chlorella","chunk_tag":"diagnosis"}'

curl -X POST http://127.0.0.1:8000/runs \
  -H 'Content-Type: application/json' \
  -d '{"algae":"blend","inclusion_pct":5,"serving_g":45,"flavour":"cocoa-spice"}'
```

- `/health` reports process availability, configured mode and lazy retrieval status.
- `/rag/ready` loads and verifies the model/index once per process, then reports
  dataset/index identity. It returns 503 when disabled, missing or incompatible.
- `/rag/search` exposes Step 3's typed filters, scores and source provenance.
- `/runs` uses configured retrieval, stores the result in the existing in-memory
  run store, and exposes it through existing run lookup and HTML report endpoints.

Search runs synchronously in the existing FastAPI thread pool. Model initialization
is protected by a lock. The server still has no durable run storage; restart loses
runs. Persistence remains Step 8.

## Workflow behavior

Single-species runs query that species' diagnosis evidence, then intervention
evidence. Blends query both species separately. Intervention searches include flavour,
algae and requested inclusion in the query but do not impose exact matrix matching:
the current corpus contains qualified related-food evidence rather than trials in
the exact project bar. Every result retains its original matrix/support labels.

The retrieval trace includes each query, its returned evidence, dataset hash, model
identity and index version. Duplicate chunk IDs are merged in the run-level evidence.
If any required search returns no evidence, the remaining four roles are marked
blocked and formulations/controls are empty. A model/index failure returns an explicit
503 without a synthetic fallback or a stored successful run.

Retrieval success only means relevant context was found. A passage explaining a
missing masking trial is still context; it is not positive efficacy evidence. Current
chemistry emits validated source-scoped claims, and demonstration recipe ingredients
carry no evidence citations. The HTML report labels candidate data, mock recipes and
unknown impact values. This avoids implying the real citations support placeholder doses.

The Flutter client still calls its existing preview route. Flutter integration is
Step 7; this step changes the backend's run workflow, not the active Flutter screen.

## Verification

- 73 backend tests passed, including all previous regression cases.
- Real cached MiniLM/FAISS API smoke test with `HF_HUB_OFFLINE=1` passed for all three
  algae choices: 6 passages for spirulina, 6 for chlorella, 9 for the blend.
- Reports rendered; unknown-source search returned `insufficient_evidence`.
- Tests cover blocked downstream roles, no silent fallback, typed API validation,
  stored-run round trips and escaped source content in reports.
