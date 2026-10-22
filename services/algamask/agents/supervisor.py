from datetime import datetime, timezone
from uuid import uuid4

from ..optimizer import build_formula
from ..schemas import AgentOutput, RunRequest, RunResult, TraceStep
from . import chemistry, critic, impact_agent, profile, recipe, retrieve


def run_workflow(request: RunRequest, search=None, generation_provider=None) -> RunResult:
    trace = []

    def record(agent, state, summary, output, status="mock"):
        validated = AgentOutput(agent=agent, state=state, summary=summary, output=output, status=status)
        trace.append(TraceStep(**validated.model_dump()))

    sensory = profile.run(request)
    record("Profile", "PROFILED", "Prepared five illustrative sensory categories.", {"sensory_map": sensory})
    evidence, searches = retrieve.run(request, search)
    metadata = None
    generation = None
    grounding_errors = []
    mode = "mock"
    limitations = ["Mock run: no live AI, vector retrieval or molecular calculations.", "All recipes, sensory risks and evidence cards are synthetic software fixtures.", "No reviewed nutritional composition or human sensory results are loaded.", "Screening bounds, calorie and sugar constraints, and scientific claim review are future tasks."]
    if search is not None:
        metadata = {key: search.manifest[key] for key in ("dataset_version", "dataset_hash", "index_version", "embedding", "development_only")}
        metadata["searches"] = searches
        mode = "rag_development" if metadata["development_only"] else "rag"
        limitations = ["Evidence and cited explanations use local retrieval; sensory profile and recipe generation remain demonstration logic.",
                       "Retrieved passages provide context, not proof that the demonstration formulations work.",
                       "Nutrition, screening constraints and human sensory outcomes are not implemented in this workflow."]
        if metadata["development_only"]:
            limitations.insert(0, "Development candidate data: record-level review and publication checks remain unresolved.")
        complete = all(item["result"]["hits"] for item in searches)
        record("Retrieval", "EVIDENCE_RETRIEVED" if complete else "INSUFFICIENT_EVIDENCE",
               "Searched diagnosis and intervention evidence with source provenance.",
               {"chunks": evidence, **metadata}, "complete" if complete else "blocked")
        if not complete:
            for agent in ("Chemistry", "Recipe", "Critic", "Impact"):
                record(agent, "BLOCKED", "Required retrieval context is missing; downstream generation was skipped.", {}, "blocked")
            return RunResult(run_id=str(uuid4()), created_at=datetime.now(timezone.utc).isoformat(), mode=mode,
                             retrieval=metadata, request=request, status="insufficient_data", trace=trace,
                             sensory_map=sensory, evidence=evidence, formulations=[], controls=[],
                             impact=impact_agent.run(request, []), limitations=limitations)
    else:
        record("Retrieval", "EVIDENCE_RETRIEVED", "Loaded synthetic evidence cards.", {"chunks": evidence})
    if search is not None:
        generation = chemistry.explain(request, evidence, metadata["dataset_hash"], generation_provider)
        grounding_errors = critic.check_grounding(generation, evidence, metadata["dataset_hash"])
        record("Chemistry", "EXPLANATION_GENERATED" if not grounding_errors else "GENERATION_BLOCKED",
               "Selected source-scoped evidence statements and validated their citations.", generation.model_dump(),
               "complete" if not grounding_errors else "blocked")
        if grounding_errors:
            for agent in ("Recipe", "Critic", "Impact"):
                record(agent, "BLOCKED", "Generation failed grounding checks; no downstream result was generated.",
                       {"grounding_errors": grounding_errors} if agent == "Critic" else {}, "blocked")
            return RunResult(run_id=str(uuid4()), created_at=datetime.now(timezone.utc).isoformat(), mode=mode,
                             retrieval=metadata, generation=generation, request=request, status="generation_failed",
                             trace=trace, sensory_map=sensory, evidence=evidence, formulations=[], controls=[],
                             impact=impact_agent.run(request, []), limitations=limitations)
        candidates = {"strategy": request.flavour, "context_chunk_ids": [c.citation.chunk_id for c in generation.claims],
                      "status": "demonstration recipe strategy; evidence summary is separately cited"}
    else:
        candidates = chemistry.run(request, evidence)
        record("Chemistry", "CANDIDATES_GENERATED", "Selected a placeholder aroma strategy.", candidates)
    formulas = recipe.run(request, candidates)
    if search is not None:
        for formula in formulas:
            for ingredient in formula.ingredients:
                ingredient.chunk_ids = []  # Mock recipe logic has not established scientific support.
    record("Recipe", "RECIPES_GENERATED", "Created three mass-balanced demonstration concepts.", {"formulations": [f.model_dump() for f in formulas]})
    verdicts = critic.run(request, formulas)
    approved = [f for f in formulas if not verdicts[f.id]]
    record("Critic", "APPROVED" if approved else "REJECTED", "Checked recipe arithmetic and exclusions; cited explanation checked separately against its evidence snapshot.", {"verdicts": verdicts, "approved_ids": [f.id for f in approved], "grounding_errors": grounding_errors, "grounding_checked": generation is not None}, "complete" if search else "mock")
    impact = impact_agent.run(request, approved)
    record("Impact", "IMPACT_CALCULATED" if approved else "BLOCKED", "Nutrition and sensory measurements are unavailable.", impact)
    controls = [build_formula(request, "B0", None, False), build_formula(request, "A0", None)]
    if any(critic.run(request, controls).values()):
        controls = []
    return RunResult(run_id=str(uuid4()), created_at=datetime.now(timezone.utc).isoformat(), mode=mode, retrieval=metadata, generation=generation, request=request, status="report_ready" if approved else "insufficient_data", trace=trace, sensory_map=sensory, evidence=evidence, formulations=approved, controls=controls, impact=impact, limitations=limitations)
