"""Local durable run records. Each operation owns its connection and transaction."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .schemas import RunResult


class RunStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            with connection:
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version not in (0, 1):
                    raise ValueError("Unsupported run store schema version")
                connection.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)")
                connection.execute("PRAGMA user_version=1")
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

    def history(self, limit: int = 20, offset: int = 0):
        with self.connection() as db:
            rows = db.execute("SELECT run_id, created_at, status FROM runs ORDER BY created_at DESC, run_id DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return [dict(zip(("run_id", "created_at", "status"), row)) for row in rows]
