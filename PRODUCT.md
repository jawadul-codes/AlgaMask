# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Food R&D formulators who screen spirulina and chlorella protein-bar recipes on a computer before committing bench time.

## Product Purpose
AlgaMask suggests and screens algae-bar formulations that mask algae off-notes (fishy, grassy) while meeting nutrition and allergen constraints. Success means a formulator leaves with a shortlist of candidate recipes, each backed by cited evidence, ready for bench testing.

## Positioning
- Masking algae off-notes is the core problem: sensory compounds are linked to masking ingredients through reviewed evidence.
- Evidence is cited, never invented: explanations come from a reviewed dataset and evidence index, and their citations are validated.
- Nutrition is computed for the exact ingredient form (for example, powder vs. extract), not generic values.

## Operating Context
Local app: Flutter web front end plus a FastAPI backend, launched with `python tools/dev.py`. Workflow: set inputs and exclusions → preflight check → run screening → read the report (recipes, matched controls, nutrition, cited evidence) → revisit saved runs in history.

## Capabilities and Constraints
- New runs use the 27-recipe `protein-base-grid-v2` screening policy (dates, flavour, 0/10/20% whey isolate); the legacy 9-recipe grid stays for saved jobs.
- Allergen exclusions supported: peanut, tree_nut, sesame, oats, coconut.
- Results are computational experiments; sensory and manufacturing validation are not done, and the dataset is not yet published.

## Evidence on Hand
- Reviewed dataset: `data/reviewed/`, with snapshots in `data/candidates/0.1.0-rc.N` (latest rc.5).
- Evidence index: `indexes/reviewed_evidence/0.1.0-dev.4`.
- Ingredient images: `apps/flutter/assets/ingredients/`.
- No user testimonials, sensory panel results or manufacturing data exist; never fabricate them.

## Product Principles
1. Every claim traces to a reviewed source, or it is not shown.
2. Masking off-notes leads; nutrition and constraints are checks on it.
3. Make it obvious that results are computational, so formulators know what still needs bench testing.
4. Saved runs stay reproducible under the policy they ran with.
