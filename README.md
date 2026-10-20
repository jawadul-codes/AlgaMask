# AlgaMask

A runnable Flutter + FastAPI skeleton for an algae protein-bar formulation assistant. The current release runs entirely with deterministic mock data and requires no API keys.

Choose spirulina, chlorella or a blend, inclusion percentage, serving mass, exclusions and flavour direction. Submit a run to see six agent roles, a sensory-profile placeholder, three mass-balanced concept recipes, B0/A0 controls, evidence placeholders and a printable report.

## Run locally

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/) and Flutter stable. Flutter web is the configured target. First setup downloads packages; subsequent mock runs need no external services.

From the repository root, start the backend:

```sh
uv sync --extra dev --locked
uv run uvicorn algamask.api:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```sh
cd apps/flutter
flutter pub get
flutter run -d chrome --web-port 3000
```

Alternatively use `flutter run -d web-server --web-port 3000` and open http://localhost:3000 yourself. The app calls `http://127.0.0.1:8000` by default. Override with `--dart-define=API_BASE_URL=http://127.0.0.1:8000` when starting or building Flutter. Use HTTP localhost origins for local development; CORS is restricted to localhost and 127.0.0.1.

API documentation: http://127.0.0.1:8000/docs

## Try it

1. Run the default blend at 5% inclusion and 45 g serving mass.
2. Inspect Profile → Retrieval → Chemistry → Recipe → Critic → Impact in the returned trace.
3. Open A1 to inspect ingredients, then expand evidence and impact sections.
4. Copy the complete run JSON, or open the print-ready report and use Print / Save as PDF.
5. Exclude oats and run again to see the explicit no-feasible-recipe path.

The loading indicator covers the API request. The completed trace is returned together; per-agent streaming is a future integration.

## What is real, and what is mocked?

The HTTP workflow, request validation, IDs, timestamps, mass arithmetic, ingredient exclusions, report rendering and JSON export are functional. Three concepts are generated deterministically from request inputs. The mock base recipe contains oats and date paste, plus selected algae and a flavour ingredient. It is not a validated protein-bar recipe.

Evidence, sensory risk bars and ingredient proportions are **assumed for demo**. There is no live LLM, molecular calculation or vector index. Nutrition and measured sensory improvements are **unknown**, not invented or zero-filled. Screening bounds, calorie/sugar limits and scientific claim validation have not been implemented. The Critic currently checks ingredient membership, exclusions and positive mass/mass balance only.

The report is a print-ready HTML page with browser PDF printing. Copy JSON preserves the full trace and fixture evidence. Runs are kept in memory (up to 100), and disappear on restart or eviction. The skeleton has no authentication and is intended for local use.

## Project map

```text
apps/flutter/             Flutter web application and widget tests
services/algamask/        FastAPI, schemas, mock services and report rendering
  agents/                Six role modules and deterministic supervisor
data/reviewed/           21-table reviewed schema; extracted rows, none approved
data/fixtures/           Reproducible request scenarios
indexes/reviewed_evidence/  Future vector-index integration
tests/algamask/          API, constraint, report and data-boundary tests
docs/TASKS.md            Task-based backlog without timeline commitments
```

Data rules, the extracted rows, and what is still missing are documented in [data/README.md](data/README.md). The next implementation tasks are in [docs/TASKS.md](docs/TASKS.md). The running app still uses synthetic fixtures and does not load `data/reviewed/`.

## Checks

```sh
uv run pytest -q
cd apps/flutter
flutter analyze
flutter test
flutter build web
```

Both dependency lockfiles are checked in. No credentials are required or stored.
