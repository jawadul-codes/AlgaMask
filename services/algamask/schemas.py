from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Algae(StrEnum):
    spirulina = "spirulina"
    chlorella = "chlorella"
    blend = "blend"


class RunRequest(BaseModel):
    algae: Algae = Algae.blend
    inclusion_pct: float = Field(default=5, gt=0, le=15)
    serving_g: float = Field(default=45, ge=40, le=50)
    exclusions: list[Literal["peanut", "tree_nut", "sesame", "oats", "coconut"]] = Field(default_factory=list)
    flavour: Literal["cocoa-spice", "vanilla", "citrus"] = "cocoa-spice"


class IngredientAmount(BaseModel):
    ingredient_id: str
    grams: float
    role: str
    chunk_ids: list[str] = Field(default_factory=list)


class Formulation(BaseModel):
    id: str
    name: str
    ingredients: list[IngredientAmount]
    total_g: float
    status: str = "assumed for demo"
    warnings: list[str] = Field(default_factory=list)


class TraceStep(BaseModel):
    agent: str
    state: str
    summary: str
    output: dict
    status: str = "mock"


class RunResult(BaseModel):
    run_id: str
    created_at: str
    mode: Literal["mock"] = "mock"
    version: str = "0.1.0"
    request: RunRequest
    status: Literal["report_ready", "insufficient_data"]
    trace: list[TraceStep]
    sensory_map: list[dict]
    evidence: list[dict]
    formulations: list[Formulation]
    controls: list[Formulation]
    impact: dict
    limitations: list[str]
