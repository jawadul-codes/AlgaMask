import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scoring import placeholder

from .agents.supervisor import run_workflow
from .report import render_report
from .schemas import RunRequest, RunResult

app = FastAPI(title="AlgaMask mock API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?", allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
# Deliberately local and ephemeral. Replace with persistence before real trials.
runs: dict[str, RunResult] = {}


class Day1Request(BaseModel):
    inclusion_pct: float = Field(default=5, gt=0, le=15)
    exclusions: list[str] = Field(default_factory=list)
    flavour: str = "cocoa"


@app.get("/health")
def health():
    return {"status": "ok", "mode": "mock", "version": "0.1.0"}


@app.post("/day1/preview")
def day1_preview(request: Day1Request):
    return placeholder(request.inclusion_pct, request.exclusions, request.flavour)


@app.post("/runs", response_model=RunResult)
def create_run(request: RunRequest):
    result = run_workflow(request)
    if len(runs) >= 100:
        del runs[next(iter(runs))]
    runs[result.run_id] = result
    return result


@app.get("/runs/{run_id}", response_model=RunResult)
def get_run(run_id: str):
    if run_id not in runs:
        raise HTTPException(404, "Run not found. Local runs are cleared on restart.")
    return runs[run_id]


@app.get("/runs/{run_id}/report", response_class=HTMLResponse)
def report(run_id: str):
    return render_report(get_run(run_id))
