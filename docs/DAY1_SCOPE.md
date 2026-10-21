# Day 1 proof and controls

## Frozen proof

For one 45 g spirulina protein bar, use grounded chemistry and sensory evidence plus constrained formulation concepts to explore whether spirulina can improve protein density while keeping earthy, grassy, marine, sulfurous, and bitter risks visible for physical testing.

Primary metric: protein per 100 kcal. Nutrition improvement remains unknown until recipe calculations use reviewed ingredient records and the prototypes are physically prepared.

## Experiment controls

- **B0:** 45 g baseline bar with no algae: oats, dried dates, and unsweetened cocoa. The existing deterministic demo recipe is a placeholder and is not this frozen physical recipe.
- **A0:** same 45 g baseline matrix with food-grade spirulina at the selected inclusion level; no added masking intervention. This is a control definition; no approved or physically validated recipe is recorded yet.
- **A1:** same spirulina inclusion as A0, with a constrained flavour intervention. This is a concept until the recipe is specified from reviewed ingredient bounds and physically validated.
- Day 1 selectable inclusion levels: 2% and 5%. The 5% value is a project screening choice, not a regulatory or validated safe limit.
- Sensory categories: earthy/muddy, grassy/green, marine/fishy, sulfurous, and bitter.

## Evidence and claim labels

Evidence labels describe where information comes from: `literature-derived`, `database-derived`, `predicted`, or `assumed`.

Claim status labels describe the state of a claim: `measured`, `literature-supported`, `database-derived`, `predicted`, `assumed`, `hypothesis`, or `unknown`. Mock sensory risks and recipes are assumptions; no measured sensory or nutrition improvement is asserted.

## Agent contracts

All roles receive a validated request plus optional evidence and prior outputs (`AgentInput`). Each trace output contains an agent name, state, summary, structured output object, and status (`AgentOutput`). The current workflow uses mock implementations and does not claim live model execution.

## Day 1 validation

Run `python tools/validate_sprint.py` from `AlgaMask/` to check the sample CSV headers, basic values, provenance links, frozen scope and prototype labels, and agent schema examples.

The Flutter Day 1 screen calls `/day1/preview`, which runs the structured mock workflow. Its result view displays the six-role trace, placeholder sensory map, evidence cards, generated recipes, controls, unknown impact values, and limitations. Use the backend and Flutter commands in the project README to view the end-to-end slice.

| Day 1 deliverable | Workspace status |
| --- | --- |
| Product, serving, baseline, inclusion levels, primary metric, proof statement, and B0/A0/A1 definitions frozen | Recorded in `data/sprint/scope.json` and this document |
| Sensory categories and evidence/claim labels | Recorded in `data/sprint/scope.json` |
| CSV sample rows and validation rules | Present in `data/sprint/`; checked by `tools/validate_sprint.py` |
| Agent input/output schemas | `AgentInput` and `AgentOutput` in `services/algamask/schemas.py`; supervisor validates each trace step |
| FastAPI health and run endpoints | `/health`, `/runs`, and `/day1/preview` |
| Flutter Day 1 form and structured result view | Implemented in `apps/flutter/lib/src/algamask/input_screen.dart` |
| Working vertical slice | Backend workflow returns six mock roles and Flutter is wired to render its response; live API/browser execution was not verified in this environment |

This completes the Day 1 software skeleton. It does not complete physical prototyping or scientific validation: the recipes and evidence in the app remain synthetic, and nutrition/sensory impacts remain unknown.
