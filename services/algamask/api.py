import sys
import os
import sqlite3
import logging
from datetime import date, datetime, timedelta, timezone
from threading import Event, Thread
from uuid import uuid4
from typing import Annotated, Literal
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

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
from .run_store import RunStore, SubmissionConflict, LeaseLost

app = FastAPI(title="AlgaMask API", version="0.2.0")
app.state.retrieval_runtime = RetrievalRuntime(Settings.from_env())
app.add_middleware(CORSMiddleware, allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?", allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Idempotency-Key"])
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


def execution_context(request):
    return request.app.state.retrieval_runtime.settings.model_dump(mode='json')


def existing_job_response(job, request):
    if job['state'] == 'completed':
        return get_run(job['job_id'], request)
    if job['state'] in ('queued', 'running'):
        return JSONResponse(status_code=202, content={'job': job}, headers={'Retry-After': '3'})
    return JSONResponse(status_code=503, content={'detail': {'code': job['error_code'],
        'message': 'Execution did not complete. Inspect this attempt in history and retry explicitly.', 'job': job}})


def execute(job, token, request):
    if token is None:
        return existing_job_response(job, request)
    store = request.app.state.run_store
    runtime = request.app.state.retrieval_runtime
    job_id = job['job_id']
    stopped = Event()

    def renew():
        while not stopped.wait(5):
            try:
                store.heartbeat(job_id, token)
            except Exception:
                logging.getLogger(__name__).exception('Execution heartbeat failed')
                return

    worker = None
    try:
        storage(store.start, job_id, token)
        worker = Thread(target=renew, daemon=True)
        worker.start()
        payload = RunRequest.model_validate(job['request'])
        search = None if runtime.settings.mode == 'mock' else configured_search(request)
        result = run_workflow(payload, search, runtime.generation_provider() if search else None)
        result = result.model_copy(update={'run_id': job_id, 'created_at': job['created_at']})
        storage(store.finish, job_id, token, result)
        return result
    except LeaseLost:
        return existing_job_response(storage(store.job, job_id), request)
    except Exception as exc:
        logging.getLogger(__name__).exception('Execution failed')
        code = exc.detail.get('code', 'run_failed') if isinstance(exc, HTTPException) and isinstance(exc.detail, dict) else 'run_failed'
        try:
            storage(store.finish, job_id, token, None, code)
        except LeaseLost:
            pass
        return existing_job_response(storage(store.job, job_id), request)
    finally:
        stopped.set()
        if worker is not None:
            worker.join(timeout=6)


@app.post("/runs", response_model=RunResult)
def create_run(payload: RunRequest, request: Request,
               idempotency_key: Annotated[str | None, Header(pattern=r'^[A-Za-z0-9_-]{16,128}$')] = None):
    try:
        job, token = storage(request.app.state.run_store.reserve, idempotency_key or str(uuid4()), payload, execution_context(request))
    except SubmissionConflict as exc:
        raise HTTPException(409, detail={'code': 'submission_conflict', 'message': str(exc)}) from exc
    return execute(job, token, request)


@app.get('/jobs/{job_id}')
def get_job(job_id: str, request: Request):
    job = storage(request.app.state.run_store.job, job_id)
    if job is None:
        raise HTTPException(404, 'Execution not found.')
    return job


class RetryRequest(BaseModel):
    expected_attempt: int = Field(ge=1)


@app.post('/jobs/{job_id}/retry', response_model=RunResult)
def retry_job(job_id: str, payload: RetryRequest, request: Request):
    job, token = storage(request.app.state.run_store.retry, job_id, payload.expected_attempt, execution_context(request))
    if job is None:
        raise HTTPException(404, 'Execution not found.')
    return execute(job, token, request)


@app.get('/storage/ready')
def storage_ready(request: Request):
    return storage(request.app.state.run_store.ready)


@app.get("/runs")
def history(request: Request, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
            status: Literal['queued','running','failed','interrupted','report_ready','insufficient_data','generation_failed'] | None = None,
            algae: Literal['spirulina','chlorella','blend'] | None = None, since: date | None = None, until: date | None = None):
    if since and until and since > until:
        raise HTTPException(422, 'Start date must be before end date.')
    if until == date.max:
        raise HTTPException(422, 'End date is outside supported range.')
    lower = datetime.combine(since, datetime.min.time(), timezone.utc).isoformat() if since else None
    upper = datetime.combine(until + timedelta(days=1), datetime.min.time(), timezone.utc).isoformat() if until else None
    return {"runs": storage(request.app.state.run_store.history, limit, offset, status, algae, lower, upper), "limit": limit, "offset": offset}


@app.get("/runs/{run_id}", response_model=RunResult)
def get_run(run_id: str, request: Request):
    result = storage(request.app.state.run_store.get, run_id)
    if result is None:
        raise HTTPException(404, "Run not found.")
    return result


@app.get("/runs/{run_id}/report", response_class=HTMLResponse)
def report(run_id: str, request: Request):
    return render_report(get_run(run_id, request))
