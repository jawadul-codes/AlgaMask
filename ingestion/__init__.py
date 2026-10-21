"""Load the Day 1 sprint CSVs. Empty cells stay empty."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPRINT = ROOT / "data" / "sprint"

FILES = {
    "algae_vocs": "algae_vocs.csv",
    "maskers": "maskers.csv",
    "nutrition": "nutrition.csv",
    "sources": "sources.csv",
}


def load_scope() -> dict:
    return json.loads((SPRINT / "scope.json").read_text(encoding="utf-8"))


def load_table(name: str) -> list[dict]:
    path = SPRINT / FILES[name]
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_sprint() -> dict:
    tables = {name: load_table(name) for name in FILES}
    return {"scope": load_scope(), **tables}
