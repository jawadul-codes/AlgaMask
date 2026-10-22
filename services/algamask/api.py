import sys
import os
import sqlite3
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import BaseModel, Field

from scoring import placeholder

from .agents.supervisor import run_workflow
from .report import render_report
from .schemas import RunRequest, RunResult
from .runtime import RetrievalRuntime, RetrievalUnavailable, Settings
from .search_schemas import SearchRequest, SearchResult
from .run_store import RunStore

app = FastAPI(title="AlgaMask API", version="0.2.0")
app.state.retrieval_runtime = RetrievalRuntime(Settings.from_env())
app.add_middleware(CORSMiddleware, allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?", allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.state.run_store = RunStore(Path(os.environ.get("ALGAMASK_RUN_DB", ROOT / "var/runs.sqlite3")))


def storage(operation, *args):
    try:
        return operation(*args)
    except (sqlite3.Error, OSError, ValueError) as exc:
        logging.getLogger(__name__).exception("Run storage operation failed")
        raise HTTPException(503, detail={"code": "storage_unavailable", "message": "Run storage is unavailable; no durable success was confirmed."}) from exc


@app.get("/health")
def health(request: Request):
    runtime = request.app.state.retrieval_runtime
    return {"status": "ok", "mode": runtime.settings.mode, "version": "0.2.0", "retrieval": runtime.status}


def configured_search(request: Request):
    try:
        return request.app.state.retrieval_runtime.get_search()
    except RetrievalUnavailable as exc:
        raise HTTPException(503, detail={"code": "retrieval_unavailable", "message": str(exc)}) from exc


@app.get("/rag/ready")
def rag_ready(request: Request):
    search = configured_search(request)
    return {"status": "ready", **{key: search.manifest[key] for key in
                                  ("dataset_version", "dataset_hash", "index_version", "development_only")}}


@app.post("/rag/search", response_model=SearchResult)
def rag_search(query: SearchRequest, request: Request):
    search = configured_search(request)
    try:
        return search.search(query)
    except (ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(503, detail={"code": "retrieval_failed", "message": "Evidence search failed; no mock fallback was used."}) from exc


class Day1Request(BaseModel):
    inclusion_pct: float = Field(default=5, gt=0, le=15)
    exclusions: list[str] = Field(default_factory=list)
    flavour: str = "cocoa-spice"


@app.post("/day1/preview")
def day1_preview(request: Day1Request):
    """Read the local sprint CSVs and return two hard-coded cards."""
    return placeholder(request.inclusion_pct, request.exclusions, request.flavour)


@app.post("/runs", response_model=RunResult)
def create_run(payload: RunRequest, request: Request):
    runtime = request.app.state.retrieval_runtime
    search = None if runtime.settings.mode == "mock" else configured_search(request)
    try:
        result = run_workflow(payload, search, runtime.generation_provider() if search else None)
    except (ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(503, detail={"code": "run_failed", "message": "Run processing failed; no mock fallback was used."}) from exc
    storage(request.app.state.run_store.save, result)
    return result


@app.get("/runs")
def history(request: Request, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    return {"runs": storage(request.app.state.run_store.history, limit, offset), "limit": limit, "offset": offset}


@app.get("/runs/{run_id}", response_model=RunResult)
def get_run(run_id: str, request: Request):
    result = storage(request.app.state.run_store.get, run_id)
    if result is None:
        raise HTTPException(404, "Run not found.")
    return result


@app.get("/runs/{run_id}/report", response_class=HTMLResponse)
def report(run_id: str, request: Request):
    return render_report(get_run(run_id, request))
