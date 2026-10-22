"""Compatibility import for existing ingestion and dictionary tools."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services"))
from algamask.dataset_schema import TABLES, ENUMS, full_cols, prov_cols  # noqa: E402,F401
