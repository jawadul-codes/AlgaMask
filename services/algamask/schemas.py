from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from .generation import GenerationResult


class Algae(StrEnum):
    spirulina = "spirulina"
    chlorella = "chlorella"
    blend = "blend"


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    algae: Algae = Algae.blend
    inclusion_pct: float = Field(default=5, gt=0, le=15)
    serving_g: float = Field(default=45, ge=40, le=50)
    exclusions: list[Literal["peanut", "tree_nut", "sesame", "oats", "coconut"]] = Field(default_factory=list)
    flavour: Literal["cocoa-spice", "vanilla", "citrus"] = "cocoa-spice"


class AgentInput(BaseModel):
    """Common validated input contract for the structured mock agent roles."""

    request: RunRequest
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    prior_outputs: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Structured agent result; role-specific payload is explicit and traceable."""

    agent: Literal["Profile", "Retrieval", "Chemistry", "Recipe", "Critic", "Impact"]
    state: str
    summary: str
    output: dict[str, Any] = Field(default_factory=dict)
    status: Literal["mock", "assumed", "complete", "blocked"] = "mock"


class IngredientAmount(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    ingredient_id: str
    grams: float = Field(gt=0)
    role: str
    chunk_ids: list[str] = Field(default_factory=list)


class Formulation(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    id: str
    name: str
    ingredients: list[IngredientAmount] = Field(min_length=1)
    total_g: float = Field(gt=0)
    status: str = "assumed for demo"
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mass(self):
        if abs(sum(item.grams for item in self.ingredients) - self.total_g) > 0.001:
            raise ValueError("ingredient masses must sum to total_g")
        ids = [item.ingredient_id for item in self.ingredients]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate ingredient IDs in formulation")
        return self


class TraceStep(BaseModel):
    agent: str
    state: str
    summary: str
    output: dict
    status: str = "mock"


class RunResult(BaseModel):
    run_id: str
    created_at: str
    mode: Literal["mock", "rag_development", "rag"] = "mock"
    retrieval: dict[str, Any] | None = None
    generation: GenerationResult | None = None
    version: str = "0.1.0"
    request: RunRequest
    status: Literal["report_ready", "insufficient_data", "generation_failed"]
    trace: list[TraceStep]
    sensory_map: list[dict]
    evidence: list[dict]
    formulations: list[Formulation]
    controls: list[Formulation]
    impact: dict
    limitations: list[str]
