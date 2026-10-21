from datetime import datetime, timezone
from uuid import uuid4

from ..optimizer import build_formula
from ..schemas import AgentOutput, RunRequest, RunResult, TraceStep
from . import chemistry, critic, impact_agent, profile, recipe, retrieve


def run_workflow(request: RunRequest) -> RunResult:
    trace = []

    def record(agent, state, summary, output):
        validated = AgentOutput(agent=agent, state=state, summary=summary, output=output, status="mock")
        trace.append(TraceStep(**validated.model_dump()))

    sensory = profile.run(request)
    record("Profile", "PROFILED", "Prepared five illustrative sensory categories.", {"sensory_map": sensory})
    evidence = retrieve.run(request)
    record("Retrieval", "EVIDENCE_RETRIEVED", "Loaded synthetic evidence cards.", {"chunks": evidence})
    candidates = chemistry.run(request, evidence)
    record("Chemistry", "CANDIDATES_GENERATED", "Selected a placeholder aroma strategy.", candidates)
    formulas = recipe.run(request, candidates)
    record("Recipe", "RECIPES_GENERATED", "Created three mass-balanced demonstration concepts.", {"formulations": [f.model_dump() for f in formulas]})
    verdicts = critic.run(request, formulas)
    approved = [f for f in formulas if not verdicts[f.id]]
    record("Critic", "APPROVED" if approved else "REJECTED", "Checked ingredient library, exclusions and mass balance; scientific review remains pending.", {"verdicts": verdicts, "approved_ids": [f.id for f in approved]})
    impact = impact_agent.run(request, approved)
    record("Impact", "IMPACT_CALCULATED" if approved else "BLOCKED", "Nutrition and sensory measurements are unavailable.", impact)
    controls = [build_formula(request, "B0", None, False), build_formula(request, "A0", None)]
    if any(critic.run(request, controls).values()):
        controls = []
    return RunResult(run_id=str(uuid4()), created_at=datetime.now(timezone.utc).isoformat(), request=request, status="report_ready" if approved else "insufficient_data", trace=trace, sensory_map=sensory, evidence=evidence, formulations=approved, controls=controls, impact=impact, limitations=["Mock run: no live AI, vector retrieval or molecular calculations.", "All recipes, sensory risks and evidence cards are synthetic software fixtures.", "No reviewed nutritional composition or human sensory results are loaded.", "Screening bounds, calorie and sugar constraints, and scientific claim review are future tasks."])
