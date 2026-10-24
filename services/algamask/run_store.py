"""Local durable run records. Each operation owns its connection and transaction."""
import sqlite3
import json
import hashlib
import time
from datetime import datetime, timezone
from uuid import uuid4
from contextlib import contextmanager
from pathlib import Path

from .schemas import RunRequest, RunResult


class SubmissionConflict(Exception):
    pass


class LeaseLost(Exception):
    pass


def now_iso():
    return datetime.now(timezone.utc).isoformat()


class RunStore:
    lease_seconds = 30
    def __init__(self, path: Path):
        self.path = Path(path)

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version not in (0, 1, 2):
                    raise ValueError("Unsupported run store schema version")
                connection.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)")
                if version < 2:
                    connection.execute("""CREATE TABLE jobs (
                        job_id TEXT PRIMARY KEY, submission_key TEXT UNIQUE NOT NULL,
                        request_hash TEXT NOT NULL, request_json TEXT NOT NULL,
                        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                        state TEXT NOT NULL CHECK(state IN ('queued','running','completed','failed','interrupted')),
                        attempt INTEGER NOT NULL, token TEXT NOT NULL,
                        lease_until REAL NOT NULL, error_code TEXT, context_json TEXT NOT NULL)""")
                    connection.execute("""CREATE TABLE attempts (
                        job_id TEXT NOT NULL REFERENCES jobs(job_id), attempt INTEGER NOT NULL,
                        started_at TEXT NOT NULL, ended_at TEXT, state TEXT NOT NULL,
                        error_code TEXT, context_json TEXT NOT NULL, PRIMARY KEY(job_id, attempt))""")
                    connection.execute("CREATE INDEX jobs_created ON jobs(created_at DESC, job_id DESC)")
                    connection.execute("CREATE INDEX runs_created ON runs(created_at DESC, run_id DESC)")
                    connection.execute("CREATE TABLE store_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                    connection.execute("PRAGMA user_version=2")
                yield connection
        finally:
            connection.close()

    def save(self, result: RunResult):
        with self.connection() as db:
            db.execute("INSERT INTO runs VALUES (?, ?, ?, ?)",
                       (result.run_id, result.created_at, result.status, result.model_dump_json()))

    def get(self, run_id: str) -> RunResult | None:
        with self.connection() as db:
            row = db.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            return None
        result = RunResult.model_validate_json(row[0])
        if result.run_id != run_id:
            raise ValueError("Stored run identity mismatch")
        return result

    def _expire(self, db):
        stamp = now_iso()
        expired = db.execute("SELECT job_id, attempt FROM jobs WHERE state IN ('queued','running') AND lease_until < ?", (time.time(),)).fetchall()
        for job_id, attempt in expired:
            db.execute("UPDATE jobs SET state='interrupted', error_code='execution_interrupted', updated_at=? WHERE job_id=?", (stamp, job_id))
            db.execute("UPDATE attempts SET state='interrupted', error_code='execution_interrupted', ended_at=? WHERE job_id=? AND attempt=?", (stamp, job_id, attempt))

    def _job(self, db, job_id):
        row = db.execute("SELECT job_id, request_json, created_at, updated_at, state, attempt, error_code, context_json FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            return None
        job = dict(zip(('job_id','request','created_at','updated_at','state','attempt','error_code','context'), row))
        job['request'] = RunRequest.model_validate_json(job['request']).model_dump(mode='json')
        job['context'] = json.loads(job['context'])
        job['attempts'] = [dict(zip(('attempt','started_at','ended_at','state','error_code','context'), r))
                           for r in db.execute("SELECT attempt, started_at, ended_at, state, error_code, context_json FROM attempts WHERE job_id=? ORDER BY attempt", (job_id,))]
        for attempt in job['attempts']:
            attempt['context'] = json.loads(attempt['context'])
        return job

    def job(self, job_id):
        with self.connection() as db:
            self._expire(db)
            return self._job(db, job_id)

    def reserve(self, key: str, request: RunRequest, context: dict):
        values = request.model_dump(mode='json')
        # Preserve pre-preset submission hashes and same-key retry semantics.
        if values['experiment'] == 'engineering_grid':
            values.pop('experiment')
        values['exclusions'] = sorted(set(values['exclusions']))
        payload = json.dumps(values, sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self.connection() as db:
            self._expire(db)
            row = db.execute("SELECT job_id, request_hash FROM jobs WHERE submission_key=?", (key,)).fetchone()
            if row:
                if row[1] != digest:
                    raise SubmissionConflict('Submission key already belongs to different inputs.')
                return self._job(db, row[0]), None
            job_id, token, stamp = str(uuid4()), str(uuid4()), now_iso()
            encoded_context = json.dumps(context, sort_keys=True)
            db.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,'queued',1,?,?,NULL,?)",
                       (job_id, key, digest, payload, stamp, stamp, token, time.time() + self.lease_seconds, encoded_context))
            db.execute("INSERT INTO attempts VALUES (?,1,?,NULL,'queued',NULL,?)", (job_id, stamp, encoded_context))
            return self._job(db, job_id), token

    def retry(self, job_id: str, expected_attempt: int, context: dict):
        with self.connection() as db:
            self._expire(db)
            job = self._job(db, job_id)
            if job is None:
                return None, None
            # Retrying the retry request cannot start another attempt, even if it
            # already failed: caller must explicitly name the newer attempt.
            if job['attempt'] != expected_attempt or job['state'] not in ('failed', 'interrupted'):
                return job, None
            attempt, token, stamp = job['attempt'] + 1, str(uuid4()), now_iso()
            encoded_context = json.dumps(context, sort_keys=True)
            db.execute("UPDATE jobs SET state='queued', attempt=?, token=?, lease_until=?, updated_at=?, error_code=NULL, context_json=? WHERE job_id=?",
                       (attempt, token, time.time() + self.lease_seconds, stamp, encoded_context, job_id))
            db.execute("INSERT INTO attempts VALUES (?,?,?,NULL,'queued',NULL,?)", (job_id, attempt, stamp, encoded_context))
            return self._job(db, job_id), token

    def start(self, job_id, token):
        with self.connection() as db:
            self._expire(db)
            changed = db.execute("UPDATE jobs SET state='running', updated_at=? WHERE job_id=? AND token=? AND state='queued'", (now_iso(), job_id, token)).rowcount
            if changed != 1:
                raise LeaseLost('Execution no longer owns this attempt')
            db.execute("UPDATE attempts SET state='running' WHERE job_id=? AND attempt=(SELECT attempt FROM jobs WHERE job_id=?)", (job_id, job_id))

    def heartbeat(self, job_id, token):
        with self.connection() as db:
            changed = db.execute("UPDATE jobs SET lease_until=?, updated_at=? WHERE job_id=? AND token=? AND state='running' AND lease_until>=?",
                                (time.time() + self.lease_seconds, now_iso(), job_id, token, time.time())).rowcount
            if changed != 1:
                raise LeaseLost('Execution lease expired')

    def finish(self, job_id, token, result=None, error_code=None):
        with self.connection() as db:
            self._expire(db)
            row = db.execute("SELECT attempt, request_json FROM jobs WHERE job_id=? AND token=? AND state='running'", (job_id, token)).fetchone()
            if row is None:
                raise LeaseLost('Execution no longer owns this attempt')
            if result is not None:
                if result.run_id != job_id or result.request != RunRequest.model_validate_json(row[1]):
                    raise ValueError('Result identity or request does not match execution')
                db.execute("INSERT INTO runs VALUES (?,?,?,?)", (result.run_id, result.created_at, result.status, result.model_dump_json()))
            state, stamp = ('completed' if result is not None else 'failed'), now_iso()
            db.execute("UPDATE jobs SET state=?, error_code=?, updated_at=? WHERE job_id=?", (state, error_code, stamp, job_id))
            db.execute("UPDATE attempts SET state=?, error_code=?, ended_at=? WHERE job_id=? AND attempt=?", (state, error_code, stamp, job_id, row[0]))

    def history(self, limit: int = 20, offset: int = 0, status=None, algae=None, since=None, until=None):
        if not 1 <= limit <= 100 or offset < 0:
            raise ValueError('Invalid history page')
        clauses, params = [], []
        for column, value, operator in [('status', status, '='), ('algae', algae, '='), ('created_at', since, '>='), ('created_at', until, '<')]:
            if value is not None:
                clauses.append(f'{column} {operator} ?')
                params.append(value)
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        query = """WITH history AS (
            SELECT j.job_id AS run_id, j.created_at,
                CASE WHEN j.state='completed' THEN r.status ELSE j.state END AS status,
                j.state, json_extract(j.request_json, '$.algae') AS algae, j.attempt, j.error_code
            FROM jobs j LEFT JOIN runs r ON r.run_id=j.job_id
            UNION ALL
            SELECT r.run_id, r.created_at, r.status, 'completed',
                json_extract(r.payload, '$.request.algae'), 1, NULL
            FROM runs r WHERE NOT EXISTS (SELECT 1 FROM jobs j WHERE j.job_id=r.run_id)
        ) SELECT * FROM history""" + where + ' ORDER BY created_at DESC, run_id DESC LIMIT ? OFFSET ?'
        with self.connection() as db:
            self._expire(db)
            rows = db.execute(query, (*params, limit, offset)).fetchall()
        return [dict(zip(('run_id','created_at','status','state','algae','attempt','error_code'), row)) for row in rows]

    def ready(self):
        with self.connection() as db:
            if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise ValueError('Database integrity check failed')
            db.execute("INSERT OR REPLACE INTO store_meta VALUES ('readiness', ?)", (now_iso(),))
        return {'status': 'ready', 'schema_version': 2}
