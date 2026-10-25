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
    experiment: Literal["engineering_grid", "spirulina-proof-v1"] = "engineering_grid"
    algae: Algae = Algae.blend
    inclusion_pct: float = Field(default=5, gt=0, le=15)
    serving_g: float = Field(default=45, ge=40, le=50)
    exclusions: list[Literal["peanut", "tree_nut", "sesame", "oats", "coconut", "milk", "soy"]] = Field(default_factory=list)
    # Preserve historical requests as strict requirements; the UI explicitly opts
    # into recipe preferences. Never silently downgrade a saved allergy request.
    exclusion_mode: Literal['ingredient_preference', 'verified_free_from'] = 'verified_free_from'
    flavour: Literal["cocoa-spice", "vanilla", "citrus"] = "cocoa-spice"
    min_protein_g: float | None = Field(default=None, ge=0, le=50)
    max_energy_kcal: float | None = Field(default=None, gt=0, le=1000)
    max_sugar_g: float | None = Field(default=None, ge=0, le=50)

    @model_validator(mode="after")
    def fixed_experiment_settings(self):
        if self.experiment == "spirulina-proof-v1" and (
            self.algae != Algae.spirulina or self.inclusion_pct != 2
            or self.serving_g != 45 or self.flavour != "cocoa-spice"
        ):
            raise ValueError("spirulina-proof-v1 requires spirulina, 2% inclusion, 45 g input mass and cocoa-spice")
        return self


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
