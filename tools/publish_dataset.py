"""Build immutable review candidates, publish approved datasets, or verify artifacts."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services"))
from algamask.publication import build, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("candidate", "publish"):
        command = commands.add_parser(name)
        command.add_argument("version")
        command.add_argument("--input", type=Path, default=ROOT / "data/reviewed")
        command.add_argument("--output", type=Path, default=ROOT / "data" / ("published" if name == "publish" else "candidates"))
        command.add_argument("--reviewer", default="")
        if name == "candidate":
            command.add_argument("--extractions", type=Path)
    check = commands.add_parser("verify")
    check.add_argument("directory", type=Path)
    check.add_argument("--require-release", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "verify":
            manifest = verify(args.directory, require_release=args.require_release)
            print(f"Verified {manifest['kind']} {manifest['dataset_version']}; runtime eligible: {manifest['runtime_eligible']}")
            return 0
        supplemental = getattr(args, "extractions", None)
        if supplemental:
            import json
            from validate_extractions import validate
            errors = validate(json.loads(supplemental.read_text()), args.input)
            if errors:
                raise ValueError("Supplemental extraction errors: " + "; ".join(errors))
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        path = build(args.input, args.output, args.version, publish=args.command == "publish",
                     reviewer=args.reviewer, code_commit=commit, supplemental=supplemental)
        verify(path, require_release=args.command == "publish")
        print(f"Created {path}")
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
