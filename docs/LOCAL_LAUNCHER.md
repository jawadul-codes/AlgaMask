# One-command local launcher

Use `python3 tools/dev.py` from the repository root, or pass the absolute script path
from any directory. It always resolves the backend and Flutter directories from the
script location; it does not depend on the terminal's current directory.

## Prerequisites

- macOS or Linux with Python 3.11+ and Flutter available on PATH.
- Repository virtual environment installed using
  `uv sync --locked --extra dev --extra rag` from the repository root.
- Matching dataset/index files and the cached embedding model as documented in
  LOCAL_RETRIEVAL.md. No implicit model download or mock fallback occurs.
- Flutter's ordinary build dependencies must be installed. The build may perform
  standard Flutter package resolution if needed.

## Behavior

The default backend preference is 8124; the web preference is 3001. If occupied,
the launcher tries up to 29 subsequent ports. Both sockets remain reserved during
startup; the backend inherits its bound socket, and the web server adopts its socket.
The selected backend URL is compiled into an isolated Flutter build so the two always
agree. Existing servers and their processes are never terminated by port number.

Explicit `--api-port` and `--web-port` require those exact ports. If occupied, startup
fails immediately with a useful message. The launcher uses loopback only and is not
production hosting. It forces development retrieval and default extractive generation.
Existing dataset/index/database environment overrides are respected; relative paths
are resolved from the repository root.

Backend RAG and database readiness are required before building the UI. A backend
failure stops the UI instead of leaving a page pretending to have a working API.
Ctrl+C or SIGTERM shuts down only this launcher's child process groups and web server.
Saved runs are not deleted. Unrelated services remain running.

## Troubleshooting

- Missing `.venv`: run the dependency-install command above.
- Missing Flutter: fix this terminal's PATH to point to the installed SDK.
- Port conflict: omit the explicit flags to let the launcher choose free ports, or
  choose different explicit ports. Do not kill unknown processes.
- Missing/incompatible RAG files or uncached model: inspect `backend.log` and follow
  LOCAL_RETRIEVAL.md. Readiness has a bounded timeout; it never falls back to mock.
- Flutter build failure: inspect `flutter-build.log` in the printed session folder.
- Code changes: stop and rerun. This is a compiled local UI, not hot reload.
- Old bookmarks: open the exact URL printed by the current launch.

Logs and compiled builds stay in ignored `var/dev/session-*` folders for diagnosis.
No automatic cleanup deletes earlier sessions. They can consume disk space over time.
Only the compiled web directory is served, not the repository or backend log directory.

## Verification (2026-10-24)

Seven launcher tests pass; full backend suite: 189 passed, 10 opt-in tests skipped.
A live launch from apps/flutter chose 8125/3002 around occupied 8124/3001, verified
RAG/storage, compiled and served Flutter with the correct API URL, and completed
fixed-proof run a76a25b5-f045-4dc6-9634-1696647aeef3 with a rendered report.
An explicit occupied-port request failed cleanly. Ctrl+C closed both owned ports
while the pre-existing servers remained listening. No user server was restarted.
