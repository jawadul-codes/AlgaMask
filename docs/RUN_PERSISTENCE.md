# Run history, execution recovery and backups

SQLite defaults to `var/runs.sqlite3`; override with `ALGAMASK_RUN_DB`. Keep the same
path across restarts. Schema 1 migrates transactionally to schema 2, preserving all
stored results. The `var/` directory is ignored by Git. Unknown future schemas fail
closed. No automatic deletion or retention expiry is enabled; records remain until
an operator deliberately archives/removes them. A user deletion feature is deferred.

## Submission and execution

`POST /runs` accepts an optional `Idempotency-Key` header (16–128 letters, digits,
underscores or hyphens). Canonical validated inputs are bound to that key; exclusions
are sorted and deduplicated. Concurrent callers with the same key share one job.
Different inputs with an existing key return 409. A missing header creates an
independent submission for backward compatibility.

- 200: completed RunResult, saved atomically with its execution state.
- 202: `{job: ...}` for an existing queued/running execution; no duplicate work.
- 503: failed/interrupted attempt with a safe error code and job details when stored.
- 422: invalid inputs/header; no job created.

An execution moves queued → running → completed or failed. A completed execution
can have a report status of `report_ready`, `insufficient_data` or `generation_failed`;
these are valid workflow outcomes. Unexpected failures are saved separately as failed
executions. Each attempt retains timestamps, error code and runtime configuration.
Result records retain evidence/index/dataset identity. Raw exceptions are server logs,
not client error messages.

A heartbeat renews a 30-second lease every 5 seconds. History/job access and new
claims reconcile expired active jobs as interrupted. Reconciliation is lazy, so an
idle database does not rewrite itself at the expiry instant. A recovered worker whose
lease/token is no longer current cannot save a result. Work executes synchronously
in the API process; there is no separate worker queue. Abrupt shutdown does not
resume computation automatically. Model calls are bounded by the existing provider
timeouts; no new cancellation endpoint is provided.

`POST /jobs/{id}/retry` takes `{"expected_attempt": N}`. Failed/interrupted jobs can
start one new attempt using saved inputs and the current backend configuration.
Replaying the same expected attempt never creates another attempt, even if the first
retry already failed. Completed jobs return their saved result. Earlier attempts
remain in the audit history. Retries can change runtime configuration; the new
attempt records that configuration explicitly.

Flutter stores unresolved submission keys in local preferences, scoped to backend
URL and submitted values. Retrying unchanged inputs after a timeout reuses the key.
Successful responses clear that pending key so a later deliberate experiment can
create a new run. Same-client simultaneous calls share one request. Device preferences
are a convenience, not an authoritative archive: clearing site data, changing browser
origin/device, or independently submitting in another tab can create a new key.
History can recover saved work regardless of that local key cache.

## History and readiness

- `GET /runs?limit=20&offset=0`: stable newest-first ordering, maximum page size 100.
  Optional `status`, `algae`, `since=YYYY-MM-DD`, `until=YYYY-MM-DD`; date endpoints
  are inclusive UTC days. New inserts can shift offset pages; refresh starts at page 1.
- `GET /runs/{id}` and `/runs/{id}/report`: completed JSON and HTML, without rerunning
  models. Legacy schema-1 reports remain accessible and appear as completed history.
- `GET /jobs/{id}`: current execution plus attempts. Legacy results have no job audit.
- `GET /storage/ready`: checks schema, SQLite quick integrity and a committed write.
- `/health`: liveness only. `/rag/ready`: separate model/index readiness.

Flutter's history button opens filtering, pagination, stored reports, execution
details and explicit retry. Refresh checks running/interrupted jobs. Report HTML
uses the current renderer; it is not an immutable archived PDF.

## Backup and restore

SQLite's backup API takes a consistent snapshot, including while the server is
running. Destination files are created exclusively with owner-only permissions;
existing paths are never overwritten. Integrity and stored records are validated.

```sh
uv run python tools/run_database.py backup var/runs.sqlite3 var/backups/runs-2026-10-23.sqlite3
uv run python tools/run_database.py restore var/backups/runs-2026-10-23.sqlite3 var/restored-runs.sqlite3
```

Choose a fresh destination for every operation. To use a restored copy, stop the
backend, set `ALGAMASK_RUN_DB` to that copy, and restart. The original database stays
intact. Any queued/running attempts in the restored copy become interrupted with
`restored_interrupted` so they can be retried explicitly. Copy backups to a separate
protected location for protection against disk loss; no backup scheduler is included.

## Local release verification

```sh
uv run --extra rag --extra dev python tools/check_release.py
uv run --extra rag --extra dev python tools/check_release.py --mode production
```

The development command runs backend tests, Flutter analysis/tests/build, immutable
dataset verification, real offline index/model validation and workflow checks, plus
backup/restore/report comparisons in temporary databases. It honors configured
dataset/index/generation settings and needs the corresponding cached model/runtime.
The production command fails while dataset publication, validated production
formulations and hosted access controls are unavailable. Passing development checks
does not grant scientific approval or deploy anything.

This remains a single-user loopback service. CORS allows local HTTP origins and the
submission-key header; CORS is not authentication. Hosted/multi-user use still needs
an identity/authorization design, TLS, operational monitoring and deployment-specific
configuration. The current task does not introduce an external host or accounts.
