"""Reproducible dataset review packets and fail-closed release publication."""
import hashlib
import json
import re
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .dataset import SCHEMA_VERSION, load_dataset
from .dataset_schema import TABLES, full_cols

RELEASE_MINIMUMS = {"sources": 10, "algae_materials": 2, "compounds": 15,
                    "ingredient_forms": 20, "evidence_chunks": 20, "retrieval_evaluations": 5}


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extraction_review(packet: dict) -> str:
    lines = ["# Supplemental extraction review", "", "These records are not normalized runtime data. Resolve the listed limitations before import.", "",
             "## Source review", ""]
    for source in packet["sources"]:
        lines += [f"### {source['source_id']}", "", f"{source['title']}", "",
                  f"Source: {source['url']}", "", f"Access: {source['access_level']}", "",
                  f"Permission note: {source['licence_note']}", ""]
    lines += ["## Record decisions needed", ""]
    for record in packet["records"]:
        lines += [f"### {record['record_id']}", "", f"Source: {record['source_id']}; location: {record['source_location']}", "",
                  f"Type: {record['kind']}; matrix: {record['matrix']}", ""]
        lines += [f"- {limitation}" for limitation in record["limitations"]]
        lines.append("")
    return "\n".join(lines)


def audit(directory: Path) -> dict:
    snapshot = load_dataset(directory)
    counts, records, blockers = {}, [], []
    for table in TABLES:
        rows = snapshot.records(table)
        counts[table] = dict(sorted(Counter(getattr(r, "review_status", "metadata") for r in rows).items()))
        for record in rows:
            values = record.model_dump(mode="json")
            status = values.get("review_status")
            missing = [name for name, _, required, _, _ in full_cols(table)
                       if required == "approved" and values.get(name) in (None, "", [])]
            dependencies = []
            for name, kind, _, _, _ in full_cols(table):
                if not kind.startswith(("fk:", "fklist:")) or not values[name]:
                    continue
                target = kind.split(":", 1)[1].split(".")[0]
                ids = values[name] if kind.startswith("fklist:") else [values[name]]
                by_id = {getattr(r, TABLES[target]["pk"]): r for r in snapshot.records(target)}
                dependencies.extend(f"{target}:{key}" for key in ids
                                    if getattr(by_id[key], "review_status", "approved") != "approved")
            records.append({"table": table, "id": values[TABLES[table]["pk"]],
                            "record_version": values.get("record_version"), "review_status": status,
                            "missing_approval_fields": missing, "unapproved_dependencies": dependencies,
                            "record": values})
            if status is not None and status != "approved":
                blockers.append(f"{table}:{values[TABLES[table]['pk']]}: status is {status}")
            if values.get("evidence_status") == "assumed_for_demo":
                blockers.append(f"{table}:{values[TABLES[table]['pk']]}: demo assumption")
            if table == "sources" and values["full_text_stored"] == "true" and values["redistribution_allowed"] != "true":
                blockers.append(f"sources:{values['source_id']}: stored full text lacks redistribution permission")
    for table, minimum in RELEASE_MINIMUMS.items():
        actual = counts[table].get("approved", 0)
        if actual < minimum:
            blockers.append(f"{table}: {actual} approved; minimum {minimum}")
    for tag in ("diagnosis", "intervention"):
        if not any(r.chunk_tag == tag for r in snapshot.records("evidence_chunks", approved_only=True)):
            blockers.append(f"evidence_chunks: no approved {tag} evidence")
    coverage = {}
    for ingredient in snapshot.records("ingredient_forms"):
        key = ingredient.ingredient_form_id
        coverage[key] = {}
        for table in ("ingredient_nutrition", "screening_bounds", "ingredient_allergens"):
            matches = [r for r in snapshot.records(table) if r.ingredient_form_id == key]
            coverage[key][table] = {"total": len(matches), "approved": sum(r.review_status == "approved" for r in matches)}
            if not any(r.review_status == "approved" for r in matches):
                blockers.append(f"ingredient_forms:{key}: lacks approved {table}")
    return {"schema_version": SCHEMA_VERSION, "row_counts": snapshot.row_counts,
            "status_counts": counts, "records": records, "ingredient_coverage": coverage,
            "warnings": [i.model_dump() for i in snapshot.issues],
            "release_blockers": blockers, "publication_ready": not blockers}


def review_markdown(report: dict) -> str:
    lines = ["# Dataset review report", "", "Generated from the copied dataset; validation is not scientific approval.", "",
             f"Publication ready: **{'yes' if report['publication_ready'] else 'no'}**", "",
             "## Table status", "", "| Table | Rows | Approved |", "|---|---:|---:|"]
    for table, count in report["row_counts"].items():
        lines.append(f"| {table} | {count} | {report['status_counts'][table].get('approved', 0)} |")
    lines += ["", "## Ingredient coverage", "", "Counts are candidate records / approved records.", "",
              "| Ingredient | Nutrition | Bounds | Allergens |", "|---|---:|---:|---:|"]
    for key, coverage in report["ingredient_coverage"].items():
        cells = [f"{coverage[t]['total']} / {coverage[t]['approved']}" for t in ("ingredient_nutrition", "screening_bounds", "ingredient_allergens")]
        lines.append(f"| {key} | {' | '.join(cells)} |")
    lines += ["", "## Record review queue", "", "Exact records, source locations and dependency IDs are in `review.json`.", "",
              "| Table / ID | Status | Missing approval fields |", "|---|---|---|"]
    for r in report["records"]:
        if r["review_status"] != "approved":
            lines.append(f"| {r['table']} / {r['id']} | {r['review_status']} | {', '.join(r['missing_approval_fields']) or '—'} |")
    lines += ["", "## Publication blockers", ""] + [f"- {item}" for item in report["release_blockers"]]
    return "\n".join(lines) + "\n"


def build(directory: Path, output: Path, version: str, *, publish: bool = False,
          reviewer: str = "", code_commit: str, supplemental: Path | None = None) -> Path:
    """Freeze a candidate or publish an approved corpus. Never edits input records."""
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?", version):
        raise ValueError("version must be semantic and contain no path components")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", code_commit):
        raise ValueError("code_commit must be a full Git commit hash")
    if publish and not reviewer.strip():
        raise ValueError("publication requires the responsible reviewer's name")
    output.mkdir(parents=True, exist_ok=True)
    destination = output / version
    # Exclusive reservation prevents replacing or racing an existing release.
    reservation = output / f".{version}.lock"
    with reservation.open("x"):
        pass
    temporary = None
    try:
        if destination.exists():
            raise FileExistsError(f"Version already exists: {destination}")
        temporary = Path(tempfile.mkdtemp(prefix=f".{version}-", dir=output))
        copied = temporary / "reviewed"
        copied.mkdir()
        for table in TABLES:
            shutil.copyfile(directory / f"{table}.csv", copied / f"{table}.csv")
        report = audit(copied)
        if publish and not report["publication_ready"]:
            raise ValueError(f"Publication blocked: {len(report['release_blockers'])} unresolved items. Build a candidate review packet first.")
        if supplemental:
            if publish:
                raise ValueError("Supplemental unreviewed extractions belong in candidates, not runtime releases")
            shutil.copyfile(supplemental, temporary / "supplemental_extractions.json")
            packet = json.loads((temporary / "supplemental_extractions.json").read_text())
            (temporary / "EXTRACTIONS_REVIEW.md").write_text(extraction_review(packet), encoding="utf-8")
        (temporary / "review.json").write_bytes(canonical(report))
        (temporary / "REVIEW.md").write_text(review_markdown(report), encoding="utf-8")
        files = {p.relative_to(temporary).as_posix(): digest(p.read_bytes())
                 for p in sorted(temporary.rglob("*")) if p.is_file()}
        manifest = {"format_version": 1, "dataset_version": version, "schema_version": SCHEMA_VERSION,
                    "kind": "release" if publish else "candidate", "runtime_eligible": publish,
                    "reviewer": reviewer.strip() or None, "created_at": datetime.now(timezone.utc).isoformat(),
                    "code_commit": code_commit, "row_counts": report["row_counts"],
                    "builder_hashes": {name: digest(Path(__file__).with_name(name).read_bytes())
                                       for name in ("publication.py", "dataset.py", "dataset_schema.py")},
                    "files": files, "content_hash": digest(canonical(files)),
                    "validation_report_hash": files["review.json"], "index": None}
        (temporary / "manifest.json").write_bytes(canonical(manifest))
        temporary.rename(destination)
        temporary = None
        return destination
    finally:
        if temporary is not None:
            shutil.rmtree(temporary)
        reservation.unlink()


def verify(directory: Path, *, require_release: bool = False) -> dict:
    """Verify bytes and rerun current gates before allowing runtime consumption."""
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("format_version") != 1 or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported manifest or schema version")
    expected = {f"reviewed/{t}.csv" for t in TABLES} | {"review.json", "REVIEW.md"}
    files = manifest["files"]
    if not expected.issubset(files):
        raise ValueError("Manifest omits required files")
    actual_files = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p != directory / "manifest.json"}
    if actual_files != set(files):
        raise ValueError("Unexpected or missing artifact files")
    for name, expected_hash in files.items():
        path = directory / name
        if path.is_symlink() or directory.resolve() not in path.resolve().parents:
            raise ValueError("Artifact path escapes the snapshot")
        if digest(path.read_bytes()) != expected_hash:
            raise ValueError(f"Hash mismatch: {name}")
    if manifest["content_hash"] != digest(canonical(files)) or manifest["validation_report_hash"] != files["review.json"]:
        raise ValueError("Manifest hash mismatch")
    report = audit(directory / "reviewed")
    if report != json.loads((directory / "review.json").read_text()) or report["row_counts"] != manifest["row_counts"]:
        raise ValueError("Review report does not match dataset")
    if require_release and (manifest.get("kind") != "release" or manifest.get("runtime_eligible") is not True or not manifest.get("reviewer") or not report["publication_ready"]):
        raise ValueError("Dataset is not an approved runtime release")
    if require_release and set(files) != expected:
        raise ValueError("Runtime release contains unexpected supplemental files")
    return manifest
