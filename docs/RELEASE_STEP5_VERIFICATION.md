# Release Step 5 — verification

Updated: 2026-10-26. This is a local engineering check on one Windows machine.
It does not establish scientific approval, allergy safety, flavour masking, or
production readiness.

## Environment

- Windows 10, PowerShell, repository `G:\AlgaMask`.
- Python environment from `uv sync --locked --extra dev --extra rag`.
- Flutter 3.47.7 was already installed at `C:\Users\Sami\dev\flutter`. The shell
  used for the release check needed that `bin` directory on `PATH`.
- Dataset `data/candidates/0.1.0-rc.5`, content hash
  `b05a800077d53b3bce3c63bdb527d30bf5b48f5c47e7182a0744f4c1c3f02076`.
- Index `indexes/reviewed_evidence/0.1.0-dev.4`.
- `HF_HUB_OFFLINE=1`. The cached MiniLM model loaded. Nothing was downloaded.
- The app already running at `127.0.0.1:8000` and port 3000 was left running.
  Its health check after this work was still `development` / `retrieval: ready`.
  No audit process was left behind.

## What changed

Two defects showed up while checking reliability:

- On Windows, the port reservation used `SO_REUSEADDR`, so a second socket could
  bind a port that was already listening. Reservation on Windows now uses
  exclusive address use. An occupied explicit port still fails without stopping
  the existing listener. The one-command launcher still refuses to start on
  Windows; use the manual PowerShell steps in the README.
- `tools/check_release.py` launched `flutter` by name. On Windows that name is
  a batch file, and Python could not start it. The check now uses the resolved
  program path and says when the program is missing from `PATH`.

The failure, retry, backup, grounding, and client-recovery tests that were
already in the repository were kept. New launcher tests cover a readiness
timeout with no mock fallback, and a non-macOS/Linux launch that stops before
it reserves a port.

## Commands and results

Ordinary backend suite, inside the release check:

- 267 passed, 20 opt-in retrieval tests skipped.

Separate offline retrieval suite:

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:ALGAMASK_TEST_REVIEWED_RAG = "1"
uv run --extra rag python -m pytest -q tests/algamask/test_reviewed_rag_integration.py
```

- 20 passed in 17.61 s.

Release check, with Flutter on `PATH` and `HF_HUB_OFFLINE=1`:

```powershell
uv run --extra rag --extra dev python tools/check_release.py
```

- Backend tests, Flutter analyze, 30 Flutter tests, and `flutter build web` passed.
- Real development retrieval smoke passed for spirulina, blend, and a sugar
  target that must block.
- Temporary database backup and restore matched.
- Result: `status: passed`, `production_eligible: false`, index `0.1.0-dev.4`,
  dataset hash as above.
- `git diff --check` reported no whitespace errors. Git warned that it will
  convert sealed LF snapshots back to CRLF if those files are touched again.
  Those bytes were restored so the recorded hashes match; they were not edited
  as data.

An earlier release-check attempt failed in about 16 seconds with
`[WinError 2] The system cannot find the file specified` because `flutter` was
not startable. That is the defect fixed above. The passing result is from the
run after that fix.

## Browser scenarios

No browser tool is available in this session, and Chrome is not the runtime
used here. The ten live browser scenarios in the Step 5 handoff were not
clicked through. Flutter widget tests cover several of the same screens in a
test harness. That is not a browser pass, and it is not a phone, Safari, or
print pass.

## Still true after this check

- New screening is `protein-base-grid-v2`. Saved jobs without a policy stay on
  the nine-recipe grid. The fixed spirulina proof is unchanged.
- Soy isolate, an oat-free recipe, and citrus plus a sugar target remain blocked.
- Whey recipes contain milk.
- Mock mode stays separate. A missing model or a failed retrieval does not fall
  back to mock.
- Production mode remains blocked.
- Work is local and uncommitted.
