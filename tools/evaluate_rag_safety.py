"""Run the draft safety regression suite offline, preserving failures in a report."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services"))
from algamask.runtime import RetrievalRuntime, Settings
from algamask.rag_evaluation import evaluate_cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=ROOT / "tests/fixtures/rag_safety_cases.json")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("Report already exists; choose a new filename")
    runtime = RetrievalRuntime(Settings.from_env().model_copy(update={"mode": "development"}))
    result = evaluate_cases(runtime.get_search(), json.loads(args.suite.read_text()))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({key: result[key] for key in ("suite_version", "case_count", "passed", "index_version")}))
    for row in result["results"]:
        if not row["passed"]:
            print(row["id"], row["errors"])
    return 0 if result["passed"] == result["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
