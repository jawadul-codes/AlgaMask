"""Validate the literature extraction packet without publishing it to runtime.

Run: uv run python tools/validate_extractions.py
Checks provenance and data consistency, not scientific truth or approval.
"""

import argparse
import csv
import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data/extractions/day2_sources.json"
KINDS = {"material", "recipe", "process", "sensory_design", "finding",
         "quality_issue", "formulation_rule", "measurement", "study_design", "dataset_link"}


def validate(packet: dict, reviewed: Path = ROOT / "data/reviewed") -> list[str]:
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def number(value):
        return type(value) in (int, float) and math.isfinite(value)

    check(packet.get("schema_version") == 1, "Unsupported schema version")
    check(type(packet.get("record_version")) is int and packet["record_version"] > 0,
          "Invalid record version")
    check(packet.get("evidence_status") == "literature_derived", "Invalid evidence status")
    check(packet.get("review_status") == "extracted", "Packet must remain extracted")
    check(packet.get("runtime_eligible") is False, "Extraction packet is not a runtime release")
    check(nonempty(packet.get("extracted_by")), "Missing extractor")
    try:
        date.fromisoformat(packet.get("extracted_at", ""))
    except (ValueError, TypeError):
        errors.append("Invalid extraction date")

    with (reviewed / "sources.csv").open(newline="", encoding="utf-8") as handle:
        existing = {r["source_id"]: r for r in csv.DictReader(handle)}

    sources = packet.get("sources", [])
    records = packet.get("records", [])
    source_ids = [s.get("source_id") for s in sources]
    record_ids = [r.get("record_id") for r in records]
    for name, identifiers in (("source", source_ids), ("record", record_ids)):
        check(all(nonempty(i) for i in identifiers), f"Missing {name} ID")
        check(len(identifiers) == len(set(identifiers)), f"Duplicate {name} ID")
    selections = [s.get("selection_number") for s in sources]
    check(sorted(selections) == list(range(1, 16)), "Expected the original 15 selected sources")
    dois = [s.get("doi") for s in sources if s.get("doi")]
    check(len(dois) == len(set(dois)), "Duplicate DOI")
    by_source = {s["source_id"]: s for s in sources}
    counts = Counter(r.get("source_id") for r in records)
    for source in sources:
        sid = source.get("source_id")
        for field in ("title", "url", "licence_note", "access_level"):
            check(nonempty(source.get(field)), f"{sid}: missing {field}")
        check(urlparse(source.get("url", "")).scheme == "https", f"{sid}: invalid URL")
        check(source.get("coverage") in {"existing_extraction", "new_extraction", "extended_extraction"},
              f"{sid}: invalid coverage")
        linked = source.get("existing_source_id")
        if source.get("coverage") in {"existing_extraction", "extended_extraction"}:
            check(linked in existing, f"{sid}: missing existing source link")
            if linked in existing:
                check((source.get("doi") or "") == existing[linked]["doi"], f"{sid}: DOI mismatch")
        if source.get("coverage") != "existing_extraction":
            check(counts[sid] > 0, f"{sid}: new source has no extracted records")
        if "retrieved_sha256" in source:
            check(bool(re.fullmatch(r"[0-9a-f]{64}", source["retrieved_sha256"])), f"{sid}: invalid hash")

    for record in records:
        rid = record.get("record_id")
        check(record.get("source_id") in by_source, f"{rid}: unknown source")
        for field in ("source_location", "matrix"):
            check(nonempty(record.get(field)), f"{rid}: missing {field}")
        check(record.get("kind") in KINDS, f"{rid}: invalid kind")
        check(bool(record.get("limitations")) and all(nonempty(v) for v in record["limitations"]),
              f"{rid}: missing limitations")
        data = record.get("data", {})
        check(isinstance(data, dict) and bool(data), f"{rid}: empty data")
        if not isinstance(data, dict):
            continue
        if record.get("kind") == "measurement":
            for field in ("metric", "unit", "basis"):
                check(nonempty(data.get(field)), f"{rid}: missing measurement {field}")
        if record.get("kind") == "recipe":
            check(nonempty(data.get("basis")), f"{rid}: missing recipe basis")
            check(type(data.get("complete")) is bool, f"{rid}: missing recipe completeness")
            ingredients = data.get("ingredients", [])
            check(bool(ingredients), f"{rid}: missing ingredients")
            names = [i.get("name") for i in ingredients]
            check(all(nonempty(n) for n in names) and len(names) == len(set(names)),
                  f"{rid}: missing or duplicate ingredient")
            amounts = [i.get("amount") for i in ingredients]
            valid = all(number(a) and a >= 0 for a in amounts)
            check(valid, f"{rid}: invalid ingredient amount")
            if valid and data.get("complete"):
                check(abs(sum(amounts) - 100) < 0.01, f"{rid}: complete recipe does not sum to 100")
        if "parent_record_id" in data:
            check(data["parent_record_id"] in record_ids, f"{rid}: missing parent recipe")

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT)
    args = parser.parse_args()
    try:
        packet = json.loads(args.path.read_text(encoding="utf-8"))
        errors = validate(packet)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(f"Invalid extraction packet: {exc}")
        return 1
    for error in errors:
        print(f"ERROR: {error}")
    print(f"{len(packet['sources'])} sources; {len(packet['records'])} new records; {len(errors)} errors")
    print("Review status: extracted. Scientific approval and runtime publication are separate.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
