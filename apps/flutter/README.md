# AlgaMask Flutter client

The client submits `/runs`, not the legacy preview endpoint. It displays backend
mode, submitted settings, dataset identity, citations, candidate/control amounts,
nutrition estimates, missing values, screening verdicts and the six-agent trace.
JSON can be copied; the print-ready report opens on the same configured backend.

## Run locally (web)

From the repository root, with the local model/index installed:

```sh
ALGAMASK_MODE=development uv run --extra rag uvicorn algamask.api:app --host 127.0.0.1 --port 8000
```

From `apps/flutter`:

```sh
flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

The backend defaults to mock mode unless explicitly configured. Flutter labels that
mode instead of claiming real evidence. Production formulations remain blocked.
See `docs/LOCAL_RETRIEVAL.md` and `docs/FORMULATION_ENGINE.md` for backend requirements.

Species, inclusion, 40–50 g serving, flavour, exclusions and optional per-serving
protein/calorie/sugar targets are editable. Unknown target inputs block screening;
sugar data and Chlorella energy are incomplete. Allergy exclusions do not imply
free-from certification. Nutrition is estimated, not a measurement of the product.

Requests wait up to 120 seconds with controls disabled. Errors allow manual retry;
there is no automatic duplicate POST. A timed-out server run may still finish.
Runs are currently in memory and report URLs stop working after backend restart.
This is a local web workflow; physical-device networking and native platform
permissions are not validated in this increment. No hosted deployment is configured.

## Verification

```sh
flutter analyze
flutter test
flutter build web
```
