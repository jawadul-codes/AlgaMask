import pytest

from algamask.backup import snapshot_database
from algamask.run_store import RunStore
from algamask.schemas import RunRequest
from algamask.agents.supervisor import run_workflow


def test_backup_restore_keeps_results_and_recovers_active_jobs(tmp_path):
    source, backup, restored = [tmp_path / name for name in ('source.db','backup.db','restored.db')]
    store = RunStore(source)
    result = run_workflow(RunRequest())
    store.save(result)
    job, token = store.reserve('in-progress-key', RunRequest(), {})
    store.start(job['job_id'], token)
    assert snapshot_database(source, backup)['runs'] == 1
    assert snapshot_database(backup, restored, restore=True)['jobs'] == 1
    recovered = RunStore(restored)
    assert recovered.get(result.run_id) == result
    assert recovered.job(job['job_id'])['error_code'] == 'restored_interrupted'
    assert store.job(job['job_id'])['state'] == 'running'
    with pytest.raises(FileExistsError):
        snapshot_database(source, restored)
    with pytest.raises(ValueError):
        snapshot_database(source, source)
    assert recovered.get(result.run_id) == result


def test_invalid_backup_cannot_replace_destination(tmp_path):
    source = tmp_path / 'corrupt.db'
    store = RunStore(source)
    with store.connection() as db:
        db.execute("INSERT INTO runs VALUES ('bad','today','report_ready','{}')")
    destination = tmp_path / 'new.db'
    with pytest.raises(ValueError):
        snapshot_database(source, destination)
    assert not destination.exists()
