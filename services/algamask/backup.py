"""Consistent SQLite snapshots; restore only into a new destination."""
import sqlite3
from contextlib import closing
from pathlib import Path

from .run_store import RunStore, now_iso
from .schemas import RunRequest, RunResult


def inspect_database(path: Path):
    path = path.resolve(strict=True)
    with closing(sqlite3.connect(f'{path.as_uri()}?mode=ro', uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Database integrity check failed')
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version not in (1, 2):
            raise ValueError('Unsupported backup schema version')
        rows = db.execute('SELECT run_id, payload FROM runs').fetchall()
        for run_id, payload in rows:
            if RunResult.model_validate_json(payload).run_id != run_id:
                raise ValueError('Stored run identity mismatch')
        jobs = 0
        if version == 2:
            for job_id, payload, state in db.execute('SELECT job_id, request_json, state FROM jobs'):
                RunRequest.model_validate_json(payload)
                if state == 'completed' and not db.execute('SELECT 1 FROM runs WHERE run_id=?', (job_id,)).fetchone():
                    raise ValueError('Completed execution is missing its result')
                jobs += 1
        return {'schema_version': version, 'runs': len(rows), 'jobs': jobs}


def snapshot_database(source: Path, destination: Path, *, restore=False):
    source, destination = Path(source).resolve(strict=True), Path(destination).absolute()
    if source == destination.resolve():
        raise ValueError('Source and destination must differ')
    inspect_database(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation guarantees that a user database is never overwritten.
    with destination.open('xb'):
        pass
    destination.chmod(0o600)
    try:
        with closing(sqlite3.connect(f'{source.as_uri()}?mode=ro', uri=True)) as src:
            with closing(sqlite3.connect(destination)) as dst:
                src.backup(dst)
        inspect_database(destination)
        if restore:
            store = RunStore(destination)
            with store.connection() as db:
                stamp = now_iso()
                db.execute("UPDATE attempts SET state='interrupted', error_code='restored_interrupted', ended_at=? WHERE state IN ('queued','running')", (stamp,))
                db.execute("UPDATE jobs SET state='interrupted', error_code='restored_interrupted', updated_at=? WHERE state IN ('queued','running')", (stamp,))
        return inspect_database(destination)
    except Exception:
        destination.unlink(missing_ok=True)  # Only the newly-created unsuccessful copy.
        raise
