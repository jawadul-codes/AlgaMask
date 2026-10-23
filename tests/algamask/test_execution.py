import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from fastapi.testclient import TestClient

from algamask.api import app
from algamask.run_store import RunStore, LeaseLost
from algamask.schemas import RunRequest
from algamask.agents.supervisor import run_workflow

KEY = {'Idempotency-Key': 'test-submission-0000001'}


def test_replay_survives_reopen_and_conflict(monkeypatch):
    api = TestClient(app)
    first = api.post('/runs', json={}, headers=KEY)
    monkeypatch.setattr(app.state, 'run_store', RunStore(app.state.run_store.path))
    assert api.post('/runs', json={}, headers=KEY).json() == first.json()
    assert len(api.get('/runs').json()['runs']) == 1
    assert api.post('/runs', json={'inclusion_pct': 2}, headers=KEY).status_code == 409
    assert api.post('/runs', json={}, headers={'Idempotency-Key': 'bad'}).status_code == 422


def test_concurrent_post_executes_once(monkeypatch):
    import algamask.api as module
    entered, release = Event(), Event()
    calls = []
    def slow(*args):
        calls.append(1)
        entered.set()
        assert release.wait(5)
        return run_workflow(*args)
    monkeypatch.setattr(module, 'run_workflow', slow)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(lambda: TestClient(app).post('/runs', json={}, headers=KEY))
        assert entered.wait(5)
        try:
            duplicate = TestClient(app).post('/runs', json={}, headers=KEY)
            assert duplicate.status_code == 202
            assert duplicate.json()['job']['state'] == 'running'
        finally:
            release.set()
        assert first.result().status_code == 200
    assert calls == [1]


def test_failure_and_explicit_retry_are_durable(monkeypatch):
    import algamask.api as module
    def broken(*args):
        raise RuntimeError('private internal detail')
    monkeypatch.setattr(module, 'run_workflow', broken)
    api = TestClient(app)
    failed = api.post('/runs', json={}, headers=KEY)
    assert failed.status_code == 503
    assert 'private internal detail' not in failed.text
    job_id = failed.json()['detail']['job']['job_id']
    assert api.post('/runs', json={}, headers=KEY).json()['detail']['job']['attempt'] == 1
    assert api.post(f'/jobs/{job_id}/retry', json={'expected_attempt': 1}).status_code == 503
    # Replaying the same retry must not start a third attempt.
    assert api.post(f'/jobs/{job_id}/retry', json={'expected_attempt': 1}).json()['detail']['job']['attempt'] == 2
    monkeypatch.setattr(module, 'run_workflow', run_workflow)
    final = api.post(f'/jobs/{job_id}/retry', json={'expected_attempt': 2})
    assert final.status_code == 200 and final.json()['run_id'] == job_id
    job = api.get(f'/jobs/{job_id}').json()
    assert [a['state'] for a in job['attempts']] == ['failed','failed','completed']


def test_expired_lease_cannot_commit_late_result():
    store = app.state.run_store
    job, token = store.reserve('lease-test', RunRequest(), {})
    store.start(job['job_id'], token)
    with store.connection() as db:
        db.execute('UPDATE jobs SET lease_until=0')
    assert store.job(job['job_id'])['state'] == 'interrupted'
    with pytest.raises(LeaseLost):
        store.heartbeat(job['job_id'], token)
    newer, new_token = store.retry(job['job_id'], 1, {})
    store.start(job['job_id'], new_token)
    result = run_workflow(RunRequest()).model_copy(update={'run_id': job['job_id']})
    with pytest.raises(LeaseLost):
        store.finish(job['job_id'], token, result)
    store.finish(job['job_id'], new_token, result)
    assert store.job(job['job_id'])['attempt'] == 2


def test_v1_migration_preserves_records(tmp_path):
    path = tmp_path / 'legacy.db'
    result = run_workflow(RunRequest(algae='chlorella'))
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE runs (run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)')
        db.execute('INSERT INTO runs VALUES (?,?,?,?)', (result.run_id, result.created_at, result.status, result.model_dump_json()))
        db.execute('PRAGMA user_version=1')
    store = RunStore(path)
    assert store.get(result.run_id) == result
    assert store.history(algae='chlorella')[0]['state'] == 'completed'
    assert store.ready()['schema_version'] == 2
    with store.connection() as db:
        db.execute('PRAGMA user_version=999')
    with pytest.raises(ValueError, match='Unsupported'):
        store.ready()


def test_filters_and_readiness():
    api = TestClient(app)
    api.post('/runs', json={'algae':'spirulina'})
    api.post('/runs', json={'algae':'blend','exclusions':['oats']})
    filtered = api.get('/runs?algae=blend&status=insufficient_data').json()['runs']
    assert len(filtered) == 1 and filtered[0]['algae'] == 'blend'
    assert api.get('/runs?since=2000-01-01&until=2001-01-01').json()['runs'] == []
    assert api.get('/runs?since=2026-01-01&until=2000-01-01').status_code == 422
    assert api.get('/runs?status=invalid').status_code == 422
    assert api.get('/storage/ready').json()['status'] == 'ready'
    cors = api.options('/runs', headers={'Origin': 'http://localhost:3000', 'Access-Control-Request-Method':'POST', 'Access-Control-Request-Headers':'idempotency-key,content-type'})
    assert cors.status_code == 200
