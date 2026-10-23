"""Back up a run database or restore into a new path; never overwrite."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services'))
from algamask.backup import snapshot_database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['backup', 'restore'])
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        result = snapshot_database(args.source, args.destination, restore=args.command == 'restore')
        print(json.dumps({'destination': str(args.destination), **result}, indent=2))
        return 0
    except Exception as exc:
        print(f'Database operation failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
