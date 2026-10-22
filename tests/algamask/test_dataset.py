import csv
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from algamask.dataset import RECORD_MODELS, DatasetValidationError, load_dataset
from algamask.dataset_schema import TABLES, full_cols
from algamask.schemas import Formulation, IngredientAmount, RunRequest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def dataset(tmp_path):
    directory = tmp_path / "reviewed"
    shutil.copytree(ROOT / "data/reviewed", directory)
    return directory


def change(directory, table, mutate):
    path = directory / f"{table}.csv"
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        columns, rows = reader.fieldnames, list(reader)
    mutate(rows)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def test_current_corpus_and_unknown_values():
    snapshot = load_dataset(ROOT / "data/reviewed")
    assert set(snapshot.row_counts) == set(TABLES)
    assert sum(snapshot.row_counts.values()) == 286
    assert snapshot.records("evidence_chunks", approved_only=True) == ()
    record = RECORD_MODELS["ingredient_nutrition"].model_validate({
        "nutrition_id": "N", "ingredient_form_id": "I", "record_version": "1",
        "review_status": "extracted", "protein_g": "", "fat_g": "0",
    })
    assert record.protein_g is None
    assert record.fat_g == 0
    assert all(model.model_json_schema()["properties"] for model in RECORD_MODELS.values())


@pytest.mark.parametrize("table,field,value,message", [
    ("ingredient_nutrition", "protein_g", "NaN", "finite"),
    ("ingredient_nutrition", "energy_kcal", "inf", "finite"),
    ("ingredient_nutrition", "protein_g", "-1", "between 0 and 100"),
    ("ingredient_nutrition", "basis", "per_serving", "per_100g"),
    ("compounds", "record_version", "0", "positive"),
    ("compounds", "record_version", "1.2", "invalid literal"),
    ("evidence_chunks", "related_compound_ids", "missing", "orphan"),
    ("evidence_chunks", "verbatim_text", "unlicensed text", "permission"),
    ("screening_bounds", "max_pct_ww", "101", "between 0 and 100"),
    ("retrieval_evaluations", "filters", "[]", "JSON object"),
    ("retrieval_evaluations", "expected_chunk_ids", "missing", "orphan"),
])
def test_rejects_invalid_records(dataset, table, field, value, message):
    change(dataset, table, lambda rows: rows[0].update({field: value}))
    with pytest.raises(DatasetValidationError, match=message):
        load_dataset(dataset)


def test_duplicate_and_missing_files(dataset):
    change(dataset, "sources", lambda rows: rows.append(rows[0].copy()))
    (dataset / "compounds.csv").unlink()
    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(dataset)
    assert any("duplicate primary key" in i.message for i in caught.value.issues)
    assert any(i.table == "compounds" for i in caught.value.issues)


def test_approved_list_references_require_approval(dataset):
    def approve(rows):
        rows[0].update(review_status="approved", reviewer="test reviewer", reviewed_at="2026-10-22T00:00:00Z")
    change(dataset, "evidence_chunks", approve)
    with pytest.raises(DatasetValidationError, match="related_.*non-approved"):
        load_dataset(dataset)


def test_approval_cannot_bypass_required_fields_with_whitespace():
    with pytest.raises(ValidationError, match="required for approved"):
        RECORD_MODELS["sources"].model_validate({"source_id": "S", "record_version": 1, "review_status": " approved "})


def test_cycles(dataset):
    change(dataset, "formulations", lambda rows: rows[0].update(parent_formulation_id=rows[0]["formulation_id"]))
    with pytest.raises(DatasetValidationError, match="cycle"):
        load_dataset(dataset)


def test_malformed_csv_row(dataset):
    with (dataset / "sources.csv").open("a") as handle:
        handle.write("too,few,columns\n")
    with pytest.raises(DatasetValidationError, match="number of columns"):
        load_dataset(dataset)


def test_template_generator_preserves_existing_data(tmp_path):
    # Execute the generator in an isolated project, never against the user's data.
    (tmp_path / "tools").mkdir()
    shutil.copy(ROOT / "tools/build_schema.py", tmp_path / "tools/build_schema.py")
    shutil.copy(ROOT / "services/algamask/dataset_schema.py", tmp_path / "tools/schema.py")
    for relative in ("data/reviewed/sources.csv", "data/manifests/source_manifest.csv"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("preserve me\n")
    subprocess.run([sys.executable, str(tmp_path / "tools/build_schema.py")], check=True, capture_output=True)
    for relative in ("data/reviewed/sources.csv", "data/manifests/source_manifest.csv"):
        assert (tmp_path / relative).read_text() == "preserve me\n"
    with (tmp_path / "data/reviewed/compounds.csv").open() as handle:
        assert next(csv.reader(handle)) == [c[0] for c in full_cols("compounds")]


def test_api_mass_and_request_contracts():
    with pytest.raises(ValidationError):
        RunRequest(serving_g=float("nan"))
    with pytest.raises(ValidationError):
        RunRequest(unknown_option=True)
    with pytest.raises(ValidationError):
        IngredientAmount(ingredient_id="x", grams=-1, role="binder")
    ingredient = IngredientAmount(ingredient_id="x", grams=10, role="binder")
    with pytest.raises(ValidationError, match="sum"):
        Formulation(id="x", name="x", ingredients=[ingredient], total_g=20)
    with pytest.raises(ValidationError, match="duplicate"):
        Formulation(id="x", name="x", ingredients=[ingredient, ingredient], total_g=20)
