"""Verify the local application or fail closed on production eligibility."""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['development', 'production'], default='development')
    args = parser.parse_args()
    from algamask.runtime import Settings, RetrievalRuntime
    from algamask.publication import verify
    from algamask.run_store import RunStore
    from algamask.backup import snapshot_database
    from algamask.agents.supervisor import run_workflow
    from algamask.schemas import RunRequest
    from algamask.report import render_report
    try:
        settings = Settings.from_env().model_copy(update={'mode': args.mode})
        verify(settings.dataset_path, require_release=args.mode == 'production')
        if args.mode == 'production':
            raise ValueError('Production formulation bounds/process and hosted access controls are not implemented. Production release blocked.')
        for command, directory in [
            ([sys.executable, '-m', 'pytest', '-q'], ROOT),
            (['flutter', 'analyze'], ROOT / 'apps/flutter'),
            (['flutter', 'test'], ROOT / 'apps/flutter'),
            (['flutter', 'build', 'web'], ROOT / 'apps/flutter'),
        ]:
            argv = list(command)
            if argv[0] != sys.executable:
                resolved = shutil.which(argv[0])
                if resolved is None:
                    raise RuntimeError(f"{argv[0]} was not found on PATH. Install it and open a terminal that can run `{argv[0]}`.")
                argv[0] = resolved
            subprocess.run(argv, cwd=directory, check=True)
        runtime = RetrievalRuntime(settings)
        search = runtime.get_search()
        with tempfile.TemporaryDirectory(prefix='algamask-release-') as temporary:
            folder = Path(temporary)
            store = RunStore(folder / 'runs.db')
            store.ready()
            for payload in (RunRequest(algae='spirulina'), RunRequest(algae='blend'), RunRequest(max_sugar_g=5)):
                result = run_workflow(payload, search, runtime.generation_provider())
                expected = 'insufficient_data' if payload.max_sugar_g is not None else 'report_ready'
                if result.status != expected or not result.generation or result.generation.status != 'complete':
                    raise ValueError('Real retrieval workflow did not satisfy smoke checks')
                store.save(result)
            snapshot_database(folder / 'runs.db', folder / 'backup.db')
            snapshot_database(folder / 'backup.db', folder / 'restored.db', restore=True)
            restored = RunStore(folder / 'restored.db')
            for row in store.history():
                original, recovered = store.get(row['run_id']), restored.get(row['run_id'])
                if original != recovered or render_report(original) != render_report(recovered):
                    raise ValueError('Restored report differs')
        print(json.dumps({'status': 'passed', 'scope': 'local development', 'dataset_hash': search.manifest['dataset_hash'],
                          'index_version': search.manifest['index_version'], 'production_eligible': False}, indent=2))
        return 0
    except Exception as exc:
        print(f'Release verification failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
