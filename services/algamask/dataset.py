"""Typed CSV boundary and relational validation for the scientific dataset.

Draft records may omit approval-only fields. Loading never grants approval.
Consumers receive a snapshot only after the entire dataset passes validation.
"""
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model, model_validator

from .dataset_schema import ENUMS, TABLES, full_cols

SCHEMA_VERSION = "1.1.0"
SUPPORTED_SCHEMA_VERSIONS = {"1.0.0", SCHEMA_VERSION}


def dataset_schema_version(directory: Path) -> str:
    """The only legacy shape is the exact 1.0 nutrition header without sugar."""
    with (directory / "ingredient_nutrition.csv").open(newline="", encoding="utf-8-sig") as handle:
        header = next(csv.reader(handle))
    current = [column[0] for column in full_cols("ingredient_nutrition")]
    return "1.0.0" if header == [name for name in current if name != "sugar_g"] else SCHEMA_VERSION


class DatasetRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    table: ClassVar[str]

    @model_validator(mode="before")
    @classmethod
    def normalize_csv(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        result = dict(value)
        status = result.get("review_status")
        if isinstance(status, str):
            result["review_status"] = status.strip()
        for name, kind, required, _, _ in full_cols(cls.table):
            item = result.get(name)
            if isinstance(item, str):
                item = item.strip()
                if kind.startswith("fklist:"):
                    item = tuple(part.strip() for part in item.split(";") if part.strip())
                elif not item:
                    item = None
            if required == "always" and (item is None or item == ()):
                raise ValueError(f"{name} is required")
            if result.get("review_status") == "approved" and required == "approved" and item is None:
                raise ValueError(f"{name} is required for approved rows")
            if item is not None:
                if kind == "int" and isinstance(item, str):
                    item = int(item)  # reject decimal strings rather than silently coercing
                if kind == "date" and isinstance(item, str):
                    item = date.fromisoformat(item)
                if kind == "datetime" and isinstance(item, str):
                    item = datetime.fromisoformat(item)
                if kind in {"int", "float"} and isinstance(item, bool):
                    raise ValueError(f"{name} cannot be a boolean")
            result[name] = item
        return result


def _record_model(table: str) -> type[DatasetRecord]:
    fields = {}
    for name, kind, required, _, description in full_cols(table):
        if kind.startswith("enum:"):
            annotation = Literal[tuple(v for v, _ in ENUMS[kind[5:]])]
        elif kind.startswith("fklist:"):
            annotation = tuple[str, ...]
        else:
            annotation = {"int": int, "float": float, "date": date, "datetime": datetime}.get(kind, str)
        if required != "always":
            annotation = annotation | None
        fields[name] = (annotation, Field(default=... if required == "always" else None, description=description))
    model = create_model("".join(word.title() for word in table.split("_")) + "Record", __base__=DatasetRecord, **fields)
    model.table = table
    return model


RECORD_MODELS = {table: _record_model(table) for table in TABLES}


class ValidationIssue(BaseModel):
    table: str
    row: int | None = None
    message: str
    severity: Literal["error", "warning"] = "error"


class DatasetValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        super().__init__("; ".join(f"{i.table}:{i.row}: {i.message}" for i in issues))


class DatasetSnapshot:
    def __init__(self, tables: dict[str, tuple[DatasetRecord, ...]], issues: list[ValidationIssue]):
        self._tables = tables
        self.issues = tuple(issues)

    def records(self, table: str, *, approved_only: bool = False) -> tuple[DatasetRecord, ...]:
        records = self._tables[table]
        if approved_only:
            return tuple(r for r in records if getattr(r, "review_status", None) == "approved")
        return records

    @property
    def row_counts(self) -> dict[str, int]:
        return {table: len(rows) for table, rows in self._tables.items()}


def load_dataset(directory: Path | str) -> DatasetSnapshot:
    """Load a directory containing the 21 reviewed CSV files; fail closed on errors."""
    directory = Path(directory)
    issues: list[ValidationIssue] = []
    parsed = {}

    def issue(table, row, message, severity="error"):
        issues.append(ValidationIssue(table=table, row=row, message=message, severity=severity))

    for table in TABLES:
        parsed[table] = []
        try:
            with (directory / f"{table}.csv").open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                expected = [column[0] for column in full_cols(table)]
                legacy = table == "ingredient_nutrition" and reader.fieldnames == [n for n in expected if n != "sugar_g"]
                if reader.fieldnames != expected and not legacy:
                    issue(table, None, "header mismatch")
                    continue
                for number, row in enumerate(reader, 2):
                    if None in row or any(value is None for value in row.values()):
                        issue(table, number, "row has an incorrect number of columns")
                        continue
                    try:
                        record = RECORD_MODELS[table].model_validate(row)
                        parsed[table].append((number, record))
                    except ValidationError as exc:
                        for error in exc.errors():
                            issue(table, number, f"{'.'.join(map(str, error['loc']))}: {error['msg']}")
        except (OSError, UnicodeError, csv.Error) as exc:
            issue(table, None, str(exc))

    lookup = {table: {getattr(record, TABLES[table]["pk"]): record for _, record in rows} for table, rows in parsed.items()}
    for table, rows in parsed.items():
        seen = set()
        for number, record in rows:
            r = record.model_dump()
            pk = r[TABLES[table]["pk"]]
            approved = r.get("review_status") == "approved"
            fail = lambda message: issue(table, number, message)
            if pk in seen:
                fail(f"duplicate primary key {pk}")
            seen.add(pk)
            for name, kind, _, _, _ in full_cols(table):
                value = r[name]
                if value is None:
                    continue
                if kind.startswith(("fk:", "fklist:")):
                    target = kind.split(":", 1)[1].split(".")[0]
                    ids = value if kind.startswith("fklist:") else (value,)
                    if len(ids) != len(set(ids)):
                        fail(f"{name} contains duplicate references")
                    for key in ids:
                        other = lookup[target].get(key)
                        if other is None:
                            fail(f"{name}: orphan reference {target}:{key}")
                        elif approved and hasattr(other, "review_status") and other.review_status != "approved":
                            fail(f"{name}: approved row references non-approved {target}:{key}")
                if name == "record_version" and value < 1:
                    fail("record_version must be positive")
                if name in {"min_pct_ww", "max_pct_ww", "amount_pct_ww", "inclusion_default_pct_ww"} and not 0 <= value <= 100:
                    fail(f"{name} must be between 0 and 100")
                if name in {"protein_g", "carbohydrate_g", "fat_g", "fibre_g", "omega3_g", "sugar_g"} and not 0 <= value <= 100:
                    fail(f"{name} must be between 0 and 100 per 100 g")
                if name in {"energy_kcal", "iron_mg", "reported_value", "odor_threshold_value", "spread", "exclusions_count"} and value < 0:
                    fail(f"{name} must be nonnegative")
                if name in {"serving_size_g", "amount_g_per_batch", "batch_size_g", "molecular_weight", "pubchem_cid", "fingerprint_bits", "sample_size", "sample_order", "min_rank", "embedding_dims"} and value <= 0:
                    fail(f"{name} must be positive")
            if table == "screening_bounds" and r["min_pct_ww"] is not None and r["max_pct_ww"] is not None and r["min_pct_ww"] > r["max_pct_ww"]:
                fail("min_pct_ww exceeds max_pct_ww")
            if table == "algae_compound_observations":
                if r["reported_value"] is not None and (not r["reported_unit"] or not r["measurement_basis"]):
                    fail("reported_value needs reported_unit and measurement_basis")
                if r["observation_type"] == "qualitative" and r["reported_value"] is not None:
                    fail("qualitative observation must not have a numeric value")
                if r["observation_type"] == "peak_area" and r["reported_unit"] not in {None, "peak_area", "relative_percent"}:
                    fail("peak area must not carry a concentration unit")
                if r["observation_type"] == "concentration" and r["reported_unit"] not in {None, "ug_per_g", "ng_per_g", "mg_per_kg", "ppm", "ppb", "mg_per_100g", "g_per_100g", "pct_ww"}:
                    fail("concentration needs a concentration unit")
            if table == "evidence_chunks":
                if r["support_class"] == "direct" and r["evidence_type"] == "in_vitro":
                    fail("in-vitro evidence cannot be classed direct")
                if r["verbatim_text"] and r["verbatim_permitted"] != "true":
                    fail("verbatim_text stored without permission")
            if table == "compounds":
                if r["identity_verification_status"] == "conflict":
                    fail("identity conflict blocks publication")
                if approved and r["identity_verification_status"] != "verified":
                    fail("approved compound requires verified identity")
            if table == "ingredient_nutrition":
                if r["sugar_g"] is not None and r["carbohydrate_g"] is not None and r["sugar_g"] > r["carbohydrate_g"]:
                    fail("total sugar exceeds total carbohydrate")
                if r["basis"] not in {None, "per_100g"}:
                    fail("nutrition basis must be per_100g")
                if approved:
                    for name in ("protein_g", "energy_kcal", "carbohydrate_g", "fat_g", "fibre_g", "iron_mg"):
                        if r[name] is None:
                            issue(table, number, f"{name} is unknown", "warning")
            if table == "sensory_trials":
                if not 1 <= r["rating_1_9"] <= 9:
                    fail("rating outside 1-9")
                if r["amends_observation_id"] and not r["amendment_reason"]:
                    fail("amendment requires a reason")
            if table == "formulation_ingredients":
                bound = lookup["screening_bounds"].get(r["bound_id"])
                if bound and bound.ingredient_form_id != r["ingredient_form_id"]:
                    fail("bound belongs to a different ingredient form")
                if approved:
                    for target in ("screening_bounds", "ingredient_nutrition", "ingredient_allergens"):
                        if not any(x.ingredient_form_id == r["ingredient_form_id"] and x.review_status == "approved" for _, x in parsed[target]):
                            fail(f"ingredient lacks approved {target} coverage")
            if table == "retrieval_evaluations":
                for field, target in (("expected_source_ids", "sources"), ("expected_chunk_ids", "evidence_chunks")):
                    for key in (r[field] or "").split(";"):
                        key = key.strip()
                        if key and key not in lookup[target]:
                            fail(f"{field}: orphan reference {key}")
                        elif key and approved and lookup[target][key].review_status != "approved":
                            fail(f"{field}: expected record is not approved: {key}")
            for field in {"retrieval_evaluations": ("filters",), "dataset_versions": ("row_counts",), "formulations": ("recipe_json",)}.get(table, ()):
                if r[field]:
                    try:
                        decoded = json.loads(r[field])
                        if field != "recipe_json" and not isinstance(decoded, dict):
                            fail(f"{field} must be a JSON object")
                        if field == "row_counts" and isinstance(decoded, dict) and any(type(v) is not int or v < 0 for v in decoded.values()):
                            fail("row_counts must contain nonnegative integer counts")
                    except (ValueError, TypeError):
                        fail(f"{field} must contain valid JSON")

    # Single-parent relationships must terminate rather than form cycles.
    for table, field in (("sensory_descriptors", "synonym_of"), ("formulations", "parent_formulation_id"), ("sensory_trials", "amends_observation_id")):
        for number, record in parsed[table]:
            visited = {getattr(record, TABLES[table]["pk"])}
            parent = getattr(record, field)
            while parent in lookup[table]:
                if parent in visited:
                    issue(table, number, f"{field} contains a cycle")
                    break
                visited.add(parent)
                parent = getattr(lookup[table][parent], field)

    # An approved recipe must be complete and mass-balanced.
    for number, formula in parsed["formulations"]:
        if formula.review_status != "approved":
            continue
        lines = [r for _, r in parsed["formulation_ingredients"] if r.formulation_id == formula.formulation_id]
        if not lines or any(r.review_status != "approved" or r.amount_pct_ww is None for r in lines):
            issue("formulations", number, "approved formulation needs approved ingredient lines with percentages")
        elif abs(sum(r.amount_pct_ww for r in lines) - 100) > 0.001:
            issue("formulations", number, "ingredient percentages must sum to 100")
    if any(i.severity == "error" for i in issues):
        raise DatasetValidationError(issues)
    return DatasetSnapshot({t: tuple(r for _, r in rows) for t, rows in parsed.items()}, issues)
