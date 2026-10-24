# Development activation - rc.4 / dev.3

Completed 2026-10-24. Runtime defaults now select the corrected dataset and matching
index together. The default mode remains mock; this running service explicitly uses
development mode. Approval checks and old immutable snapshots are unchanged.

## Running local services

- Flutter: http://127.0.0.1:3000/
- Corrected API: http://127.0.0.1:8123/
- A pre-existing legacy mock service on 8000 was left untouched to avoid losing
  its possible in-memory results. It is not the backend tested here.

Start the corrected API from the repository root:

```sh
HF_HUB_OFFLINE=1 ALGAMASK_MODE=development .venv/bin/uvicorn \
  algamask.api:app --host 127.0.0.1 --port 8123
```

Start Flutter from apps/flutter:

```sh
flutter run -d web-server --web-hostname 127.0.0.1 --web-port 3000 \
  --dart-define=API_BASE_URL=http://127.0.0.1:8123
```

These local processes must remain running for the URLs to work. No hosted deployment
or credentials were changed. Existing SQLite history was not deleted or rewritten.

Later recovery: Flutter's debug server exited with debugger WebSocket errors. The
current UI uses a compiled build instead. From apps/flutter run
`flutter build web --dart-define=API_BASE_URL=http://127.0.0.1:8123`, then from the
repository root run `.venv/bin/python -m http.server 3000 --bind 127.0.0.1 --directory apps/flutter/build/web`.
Rebuild after UI changes. This loopback static server is for local use, not production
hosting. The backend on 8123 and its SQLite history remain intact.

## Live verification

- `/rag/ready` reports rc.4, dev.3, development_only=true and dataset hash
  e999303a8afda5624002ec8ac27994c40b4ae9b9faf59fa72aecd70336c34432.
- Submitted a real experiment through Flutter: spirulina, 5%, 45 g, cocoa-spice.
  This uses the existing engineering grid, not the proposed frozen 2% experiment.
- Saved run: `7d59dcc1-fd1c-4ab8-84d0-4ac6219c407f`.
- Flutter displays the correct provenance, revised sample/descriptor caveats,
  cinnamon limitations and six-agent trace. The Profile remains illustrative/mock;
  retrieval through impact completes with development warnings.
- The Print-ready report button opens the matching HTML report on port 8123.
- Experiment history lists the run and successfully reopens the same result with
  rc.4/dev.3 provenance. No unsupported sensory result is shown as measured.
- Visual proof: `output/review/rc4-dev3-flutter.png`.
- Backend suite: 161 passed / nine opt-in skipped. Flutter: analysis clean, 15 tests
  passed. Separate real-model integration checks passed in the preceding increment.

## Rollback and remaining work

To roll back development retrieval, stop the corrected API and restart it with both
`ALGAMASK_DATASET_PATH` set to the absolute rc.1 directory and `ALGAMASK_INDEX_PATH`
set to the absolute dev.2 directory. Never mix versions. Saved runs retain their
original evidence snapshots; changing defaults does not regenerate old reports.

The first-release B0/A0/A1 recipe alignment remains separate implementation work.
Supplier-specific records, scientific approval, sensory experiments and production
security/deployment are not completed by this activation.
