"""Validate reviewed CSVs using the same contracts as backend consumers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services"))
from algamask.dataset import DatasetValidationError, load_dataset


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    try:
        snapshot = load_dataset(root / "data" / "reviewed")
        issues = snapshot.issues
        print(f"{sum(snapshot.row_counts.values())} rows in {len(snapshot.row_counts)} tables")
    except DatasetValidationError as exc:
        issues = exc.issues
    for issue in issues:
        print(f"{issue.severity.upper()} [{issue.table} row {issue.row}] {issue.message}")
    errors = sum(i.severity == "error" for i in issues)
    warnings = sum(i.severity == "warning" for i in issues)
    print(f"{errors} error(s), {warnings} warning(s)")
    return int(errors > 0)


if __name__ == "__main__":
    raise SystemExit(main())
