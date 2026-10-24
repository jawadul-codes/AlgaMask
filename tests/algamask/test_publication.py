import csv
import json
from pathlib import Path

import pytest

from algamask.dataset_schema import TABLES, full_cols
from algamask.publication import audit, build, verify

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "a" * 40


def test_candidate_is_reproducible_and_not_runtime(tmp_path):
    a = build(ROOT / "data/reviewed", tmp_path / "a", "0.1.0-rc.1", code_commit=COMMIT)
    b = build(ROOT / "data/reviewed", tmp_path / "b", "0.1.0-rc.1", code_commit=COMMIT)
    first, second = verify(a), verify(b)
    assert first["content_hash"] == second["content_hash"]
    assert first["runtime_eligible"] is False
    with pytest.raises(ValueError, match="approved runtime"):
        verify(a, require_release=True)
    with pytest.raises(FileExistsError):
        build(ROOT / "data/reviewed", tmp_path / "a", "0.1.0-rc.1", code_commit=COMMIT)
    assert verify(a) == first


def test_publish_rejects_current_corpus_without_leaving_partial_release(tmp_path):
    with pytest.raises(ValueError, match="Publication blocked"):
        build(ROOT / "data/reviewed", tmp_path, "0.1.0", publish=True, reviewer="Test reviewer", code_commit=COMMIT)
    assert list(tmp_path.iterdir()) == []


def test_mutation_and_manifest_tampering_detected(tmp_path):
    path = build(ROOT / "data/reviewed", tmp_path, "0.1.0", code_commit=COMMIT)
    target = path / "reviewed/sources.csv"
    target.write_bytes(target.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Hash mismatch"):
        verify(path)


@pytest.mark.parametrize("version", ["../bad", "/tmp/bad", "1", "01.0.0"])
def test_invalid_version(tmp_path, version):
    with pytest.raises(ValueError, match="semantic"):
        build(ROOT / "data/reviewed", tmp_path, version, code_commit=COMMIT)


def test_audit_contains_actionable_review_items():
    report = audit(ROOT / "data/reviewed")
    assert not report["publication_ready"]
    assert report["status_counts"]["evidence_chunks"] == {"extracted": 23}
    chunk = next(r for r in report["records"] if r["table"] == "evidence_chunks")
    assert "reviewer" in chunk["missing_approval_fields"]
    assert chunk["unapproved_dependencies"]
    assert report["ingredient_coverage"]


def test_supplemental_packet_is_preserved_and_reviewable(tmp_path):
    source = ROOT / "data/extractions/day2_sources.json"
    path = build(ROOT / "data/reviewed", tmp_path, "0.1.0", code_commit=COMMIT, supplemental=source)
    assert (path / "supplemental_extractions.json").read_bytes() == source.read_bytes()
    report = (path / "EXTRACTIONS_REVIEW.md").read_text()
    assert "EXT-NEROLI-DOSE" in report
    assert "Volume cannot become mass percent without density" in report
    assert verify(path)["kind"] == "candidate"


def test_changing_candidate_label_does_not_bypass_approval(tmp_path):
    path = build(ROOT / "data/reviewed", tmp_path, "0.1.0", code_commit=COMMIT)
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(kind="release", runtime_eligible=True, reviewer="Fake label")
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="approved runtime"):
        verify(path, require_release=True)


def test_approved_release_path(tmp_path, monkeypatch):
    # Synthetic two-chunk corpus tests publication, not scientific approval.
    monkeypatch.setattr("algamask.publication.RELEASE_MINIMUMS", {"sources": 1, "evidence_chunks": 2})
    inputs = tmp_path / "input"
    inputs.mkdir()
    common = {"record_version": "1", "review_status": "approved", "reviewer": "Synthetic test",
              "reviewed_at": "2026-10-22T00:00:00Z", "evidence_status": "literature_derived"}
    for table in TABLES:
        with (inputs / f"{table}.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[c[0] for c in full_cols(table)])
            writer.writeheader()
            if table == "sources":
                writer.writerow({**common, "source_id": "S", "source_type": "project_data", "title": "Synthetic source",
                                 "retrieved_at": "2026-10-22", "licence": "Synthetic fixture", "redistribution_allowed": "true", "full_text_stored": "false"})
            if table == "evidence_chunks":
                for tag in ("diagnosis", "intervention"):
                    writer.writerow({**common, "chunk_id": tag, "chunk_tag": tag, "claim_summary": "Synthetic fixture",
                                     "support_class": "indirect", "evidence_type": "related_food_matrix", "matrix": "test",
                                     "source_id": "S", "source_location": "test", "verbatim_permitted": "false"})
    output = build(inputs, tmp_path / "output", "1.0.0", publish=True, reviewer="Synthetic test", code_commit=COMMIT)
    assert verify(output, require_release=True)["runtime_eligible"]
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["row_counts"]["sources"] = 999
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="does not match"):
        verify(output)
