import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from algamask.api import app
from algamask.agents.supervisor import run_workflow
from algamask.schemas import RunRequest
from algamask.run_store import RunStore


def test_reopen_retains_exact_run_and_report(tmp_path, monkeypatch):
    path = tmp_path / "runs.sqlite3"
    monkeypatch.setattr(app.state, "run_store", RunStore(path))
    api = TestClient(app)
    response = api.post('/runs', json={})
    assert response.status_code == 200
    run = response.json()
    original_report = api.get(f"/runs/{run['run_id']}/report").text
    monkeypatch.setattr(app.state, "run_store", RunStore(path))
    assert api.get(f"/runs/{run['run_id']}").json() == run
    assert api.get(f"/runs/{run['run_id']}/report").text == original_report
    assert api.get('/runs').json()['runs'][0]['run_id'] == run['run_id']
    assert api.get('/runs?limit=101').status_code == 422
    assert api.get('/runs?offset=-1').status_code == 422


def test_concurrency_and_no_implicit_eviction(tmp_path):
    store = RunStore(tmp_path / "runs.sqlite3")
    results = [run_workflow(RunRequest()) for _ in range(105)]
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(store.save, results))
    assert len(store.history(100)) == 100
    assert len(store.history(100, 100)) == 5
    assert store.get(results[0].run_id) == results[0]
    with pytest.raises(sqlite3.IntegrityError):
        store.save(results[0])
    assert store.get(results[0].run_id) == results[0]
    assert store.get("' OR 1=1 --") is None


def test_storage_failure_is_not_success(tmp_path, monkeypatch):
    monkeypatch.setattr(app.state, "run_store", RunStore(tmp_path))
    api = TestClient(app)
    for method, url in [('post', '/runs'), ('get', '/runs'), ('get', '/runs/id'), ('get', '/runs/id/report')]:
        response = api.request(method, url, json={} if method == 'post' else None)
        assert response.status_code == 503
        assert response.json()['detail']['code'] == 'storage_unavailable'


def test_corrupt_payload_fails_closed(tmp_path, monkeypatch):
    store = RunStore(tmp_path / "runs.sqlite3")
    with store.connection() as db:
        db.execute("INSERT INTO runs VALUES ('bad', 'today', 'report_ready', '{}')")
    monkeypatch.setattr(app.state, "run_store", store)
    assert TestClient(app).get('/runs/bad').status_code == 503
