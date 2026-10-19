# AlgaMask

AlgaMask is an AI-native formulation assistant that retrieves food and sensory evidence, maps algae molecules to perceived off-notes, and generates constrained masking recipes. Built as a seven-day experimental-decision MVP, it enables higher inclusion rates of nutrient-dense microalgae (spirulina and chlorella) in products like protein bars by outputting mass-balanced, food-grade formulations optimized for both sensory acceptance and nutritional density.

> **Note:** AlgaMask proposes food-grade ingredient combinations and screening ranges based on retrieved evidence. It does not invent novel molecules, claim physical binding without evidence, or represent an untested dose as clinically proven.
> 
> 

## Core Capabilities

* **Multimodal Sensory Mapping:** Fuses molecular structures (Morgan fingerprints and descriptors), chemical observations, sensory text embeddings, and human panel scores using a late-fusion scoring method to map volatile organic compounds (VOCs) to specific off-notes.


* **RAG-Powered Recipe Optimizer:** Uses a hybrid retrieval index (metadata filtering plus vector search) built from reviewed evidence chunks to ensure every proposed ingredient references at least one cited source.


* **Autonomous Agent Workflow:** A deterministic supervisor state machine orchestrates six specific agent roles: Profile, Retrieval, Chemistry, Recipe, Critic, and Impact.


* **Generative Formulation Engine:** Generates candidate recipes by selecting aroma, taste-balancing, and matrix-support strategies while strictly enforcing mass balance, caloric limits, and allergen constraints.


* **Measurable Impact Reporting:** Automatically outputs a data-backed report comparing a baseline bar (B0), an unmasked algae control (A0), and the optimized formulation (A1) across nutritional density and measured sensory changes.



## System Architecture

The project relies on a lightweight, locally runnable stack optimized for a seven-day sprint:

* **Interface:** Flutter application for demonstrating live inputs, molecular-sensory maps, and impact reports.


* **API & Logic:** Python FastAPI serving as the boundary for retrieval, generation, and deterministic safety filters.


* **Data Storage:** Versioned CSV files (algae species, compounds, sensory descriptors, evidence chunks, ingredients, nutrition) and validated JSON.


* **Molecular Features:** PubChem PUG REST and RDKit.


* **Vector Index:** Local FAISS or Chroma index for offline semantic retrieval.



## Project Structure

```text
data/
  raw/
  reviewed/
    algae_species.csv
    compounds.csv
    algae_compound_observations.csv
    sensory_descriptors.csv
    compound_sensory_links.csv
    ingredients.csv
    nutrition.csv
    evidence_chunks.csv
    sources.csv
    formulations.csv
    sensory_trials.csv
fixtures/
  baseline_bar.json
  unmasked_bar.json
  demo_scenarios.json
services/algamask/
  schemas.py
  validation.py
  molecular.py
  embeddings.py
  retrieval.py
  optimizer.py
  nutrition.py
  impact.py
  report.py
  api.py
  agents/
    supervisor.py
    profile.py
    retrieve.py
    chemistry.py
    recipe.py
    critic.py
    impact_agent.py
indexes/
  reviewed_evidence/
tests/algamask/
lib/src/algamask/

```

(Directory structure adapted from the suggested sprint layout.)

## Data Provenance & Safety Constraints

AlgaMask relies on a tightly controlled dataset rather than uncontrolled scraping. Every record published to the MVP index must have a `review_status=approved` flag. The system enforces strict guardrails during generation:

* Only ingredients from the allowed food-grade library are proposed.


* Hard allergen exclusions cannot be overridden by any agent.


* Total recipe mass must perfectly equal the selected batch mass, repaired by deterministic code if necessary.


* The Critic Agent rejects any recipe that includes unsupported mechanistic claims or missing citations.
