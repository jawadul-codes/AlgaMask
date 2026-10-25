# AlgaMask

### Quick Start
```sh
python3 tools/dev.py
```

AlgaMask is a local Flutter + FastAPI application for experimental algae-bar
formulation screening. It supports source-grounded evidence explanations, exact-form
nutrition estimates, constraint checks, matched controls, reports and saved history.
Current formulations are computational experiments; manufacturing/sensory validation
and scientific dataset publication remain incomplete.

## Start locally

### One-command launch (macOS/Linux)

After the dependencies and local RAG model are installed, run this from any terminal
(including Antigravity):

```sh
python3 /AlgaMask/tools/dev.py
```

On another computer, replace the path with your checkout location. From the repository
root, the shorter command is `python3 tools/dev.py`.

The launcher finds available loopback ports, checks the backend's real RAG and storage,
builds Flutter with the matching API URL, and prints the app URL. It does not use the
Flutter browser debugger or stop existing servers. Keep the terminal open; Ctrl+C
stops only the services it started. Restart the launcher after code changes.

To require specific ports instead of automatic selection:

```sh
python3 tools/dev.py --api-port 8124 --web-port 3001
```

An occupied explicit port produces an error without killing its owner. Logs and each
isolated compiled build are retained under `var/dev/session-*` (ignored by Git).
See [local launcher](docs/LOCAL_LAUNCHER.md) for setup and troubleshooting.

### Manual launch / initial setup

Requirements: Python 3.11+, uv and Flutter. Install dependencies:

```sh
uv sync --extra dev --extra rag --locked
```

For the real local evidence workflow, configure the cached model/index described in
[Local retrieval](docs/LOCAL_RETRIEVAL.md), then start:

```sh
ALGAMASK_MODE=development uv run --extra rag uvicorn algamask.api:app --host 127.0.0.1 --port 8000
```

Omitting `ALGAMASK_MODE` selects the explicit mock workflow. No hosted API key is
needed for default extractive explanations. Optional local Ollama generation is
documented in [Grounded generation](docs/GROUNDED_GENERATION.md).

In another terminal:

```sh
cd apps/flutter
flutter pub get
flutter run -d chrome --web-port 3000 --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

Use loopback for this single-user development service. API docs are available at
http://127.0.0.1:8000/docs. Hosted access controls are not configured.

## Use the app

Choose algae, serving size, inclusion, flavour, exclusions and optional nutrition
targets, then run an experiment. Inspect candidates, controls, cited evidence,
estimated nutrition and screening reasons. The report records the dataset/index
used. Missing nutrient values stay unknown and block any target needing them.

Use the history icon to filter/reopen saved results or inspect failed/interrupted
attempts. An explicit retry preserves earlier attempts. Submission keys protect
same-input network retries; completed reports survive backend restarts. Copy JSON
or open the printable HTML report. See [Run persistence](docs/RUN_PERSISTENCE.md)
for exact retry, retention, migration, backup and restore behavior.

Evidence retrieval and numeric calculations use the versioned dataset. Sensory
profiles remain illustrative; the engineering search grid is not a validated recipe
space. Full allergen coverage, ingredient/process bounds, nutrient gaps and panel
results remain open. See [Formulation engine](docs/FORMULATION_ENGINE.md).

## Verify

```sh
uv run --extra rag --extra dev python tools/check_release.py
```

This checks backend tests, Flutter analysis/tests/build, dataset/index integrity,
real retrieval workflows and database backup/restore. Add `--mode production` to
check production gates; the current candidate correctly fails that check.

## Project map

- `apps/flutter/`: local web client and tests.
- `services/algamask/`: API, six-agent workflow, retrieval, generation, screening and storage.
- `data/candidates/`: immutable data snapshots; current candidate is `0.1.0-rc.5`.
- `indexes/reviewed_evidence/`: local embedding index, currently `0.1.0-dev.4`.
- `tools/`: dataset/index operations, database recovery and release verification.
- `var/`: ignored local databases and verification artifacts.
- [Implementation progress](docs/IMPLEMENTATION_PROGRESS.md): completed work and remaining gates.

No deployment or scientific publication is implied by a successful local run.

Total-sugar and chlorella-energy estimates are now available for vanilla and
cocoa-spice recipes. Chlorella uses the explicitly named Algomed powder label,
not a generic species composition. Citrus sugar still lacks a supported raw-peel
value and blocks requested sugar targets. See [nutrition coverage](docs/NUTRITION_COVERAGE.md).
