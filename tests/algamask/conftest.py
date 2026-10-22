import pytest


@pytest.fixture(autouse=True)
def isolated_run_store(tmp_path, monkeypatch):
    from algamask.api import app
    from algamask.run_store import RunStore
    monkeypatch.setattr(app.state, "run_store", RunStore(tmp_path / "runs.sqlite3"))
