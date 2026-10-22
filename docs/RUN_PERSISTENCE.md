# Local run persistence

Run results now use SQLite instead of a process-local dictionary. The default file
is `var/runs.sqlite3` under the repository root; override with `ALGAMASK_RUN_DB`.
The database directory is ignored by Git. No existing dataset files are changed.

`POST /runs` returns a result only after its transaction commits. Ready reports,
insufficient-data runs and generation-blocked results are stored with the full
request, trace, evidence, generation metadata, nutrition and dataset/index identity.
Repeated run IDs are rejected rather than overwritten. There is no automatic
100-record eviction. All queries use parameters and each operation closes its own
connection; SQLite serializes concurrent writes with a five-second busy timeout.

- `GET /runs?limit=20&offset=0`: newest-first summaries; limit 1–100, offset >= 0.
- `GET /runs/{id}`: validated stored run, or 404 when absent.
- `GET /runs/{id}/report`: HTML rendered from that stored run, without recomputing
  retrieval or requiring the model to load again.

Storage errors (including corrupt payloads or unsupported schema versions) return
503 with `storage_unavailable`; they are logged server-side without putting filesystem
details in the response. No in-memory fallback claims durable success. Schema version
1 is checked explicitly. Current HTML rendering is used for old records: this is not
an immutable archived PDF or a versioned renderer.

## Operational boundary

This is a **local, single-user development service**, not a hosted release. Bind to
loopback. There is no authentication/authorization, encryption layer, background job
queue, idempotency key, backup scheduler, retention/deletion UI or Flutter history
browser yet. `/health` remains a liveness check, not proof that storage is writable.
Exceptions before a RunResult exists return 503 but are not durable failed-job rows.
A timeout/retry can create separate runs. These are remaining Step 8 tasks, not
capabilities implied by persistence.

Keep the database path stable across restarts. For a simple consistent backup, stop
the service before copying the database and keep the copy outside the repository.
Do not delete the database to resolve errors. Filesystem access to the database
exposes all stored input/output; protect it like other local project data. Old
in-memory runs from processes started before this change cannot be recovered by it.

## Verified

Tests cover reopen/read equality, persisted report equality, more than 100 records,
concurrent writes, duplicate rejection, missing/injection-like IDs, corrupt payloads,
storage failure responses and history pagination validation. A real Flutter browser
run using local MiniLM retrieval generated a report; an allergy-blocked report opened
from Flutter and remained available at the same URL after the verification backend
was stopped and restarted with the same database.
