# AlgaMask dataset and provenance plan

Status: planning baseline  
Purpose: define the scientific, formulation, nutrition, retrieval, and experiment data required for the full application

## 1. Dataset strategy

AlgaMask should not depend on one downloaded “algae flavour dataset.” No single public dataset contains the required chain from algae material, through measured compounds and sensory language, to food-compatible interventions, nutrition, and human response.

The product therefore uses a small, reviewed knowledge base assembled from authoritative databases, source literature, supplier or batch records, and original prototype measurements. Public APIs help with discovery and identifiers. A human reviewer approves the scientific relationships used by the application.

The complete evidence chain is:

```text
algae material / batch
  -> reported compound observation
  -> verified chemical identity and computed molecular features
  -> sensory descriptor relationship
  -> reviewed intervention evidence
  -> allowed food ingredient and screening bounds
  -> nutrition record
  -> generated formulation
  -> B0 / A0 / A1 prototype
  -> blinded sensory observation
  -> impact metric and report
```

No link in this chain may be inferred only because two records share words. Every published relationship needs an explicit evidence type, source, reviewer, and confidence/strength classification.

## 2. Required datasets

| Dataset | Proof target | Runtime purpose | Primary origin |
|---|---:|---|---|
| Algae materials | 2 approved records minimum | Spirulina and chlorella identity, form, processing, inclusion defaults | supplier/batch record plus reviewed composition source |
| Compounds | 15–30 | Chemical identity, descriptors, fingerprints, candidate features | PubChem identity plus reviewed algae literature |
| Algae-compound observations | 30+ observations | Links a material/process to a reported detection or level | peer-reviewed analytical studies |
| Sensory descriptors | 5 required groups; 20+ normalized terms/synonyms | Controlled sensory vocabulary and text embedding input | sensory literature and reviewed project lexicon |
| Compound-sensory links | 30–60 | Explains why a compound is associated with a perceived note | sensory/odor literature with relationship type |
| Ingredients | 20–40 approved forms | Allowed search space, roles, bounds, allergens, warnings | formulation literature, authoritative food-use information, supplier records |
| Ingredient nutrition | 100% coverage for B0/A0/A1 ingredients on required metrics | Per-serving and density calculations | exact supplier label/CoA first, USDA fallback |
| Sources | 10–20 decisive sources minimum | Provenance, licences, links, reviewer notes | DOI/database metadata and source review |
| Evidence chunks | 20–50 approved chunks | Hybrid retrieval for diagnosis and intervention | licensed open text or reviewer-written evidence notes |
| Formulations | B0, A0, three generated variants, selected A1 | Reproducible recipes and score history | application output plus reviewed controls |
| Sensory trials | 5–10 adult participants for the directional proof | Measured human-response modality and impact comparison | original blinded prototype session |

The targets are proof thresholds, not quotas. A smaller record set with direct protein-bar evidence is more useful than a larger weakly related corpus.

## 3. Source policy

### Chemical identity and structure

Use the [PubChem PUG REST API](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) to resolve CID, current PubChem SMILES, InChIKey, molecular formula, molecular weight, XLogP, and related identifiers. Cache the raw response and record retrieval date. Compute the application’s fingerprints and RDKit descriptors locally so their parameters and versions are controlled.

PubChem confirms identity and properties; it does not establish that a compound occurs in a selected algae material or causes its sensory character. Those claims require separate observations and evidence links.

### Nutrition

Use the exact ingredient label, supplier specification, or certificate of analysis when it represents the actual prototype material. Otherwise use [USDA FoodData Central](https://fdc.nal.usda.gov/api-guide/) and store the FDC ID, food type, description, data release/date, and match rationale. FoodData Central publishes data under CC0, but the project should still cite it.

Never combine nutrient values from different ingredient forms without an explicit transformation. Missing omega-3, iron, or fibre remains null. A label’s rounded value and a laboratory value must not be presented as interchangeable.

### Literature discovery and metadata

Use [Europe PMC](https://dev.europepmc.org/RestfulWebService), [OpenAlex](https://help.openalex.org/api/), and [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/) to discover works and normalize DOI/metadata. Discovery rank is not evidence strength.

Store full text only when its licence permits redistribution. Europe PMC notes that most full text remains copyright-restricted; for restricted works, store bibliographic metadata, an exact source location, and a concise reviewer-written evidence note. Do not copy an abstract or paper section into the retrieval corpus merely because an API exposes it.

### Material, food use, and bounds

Use the exact supplier specification and batch/lot documentation where available. Screening bounds must record the ingredient form, product matrix, basis (`% w/w` or grams per batch), source, evidence type, reviewer, and region/context. Treat food-use or regulatory suitability as market-specific review data, not a global boolean inferred by the model.

### Human sensory data

Trial observations are original project data. Store pseudonymous panelist codes only. Consent records and direct identity stay outside the application dataset. Record protocol version, blinding code, sample order, serving temperature, preparation/storage deviations, and scale anchors with the ratings.

### Sources excluded from production evidence

- Untraceable CSVs, scraped recipe sites, and Kaggle mirrors without primary provenance.
- Vendor marketing claims without a technical source or documented batch fact.
- Search snippets, model-generated summaries, and citation lists that were not checked against the source.
- In-vitro or receptor evidence presented as proof of performance in a protein bar.
- Compound co-occurrence presented as measured concentration or odor activity.

These sources may suggest search terms, but cannot become approved production evidence.

## 4. Data zones and repository layout

```text
data/
  manifests/            source inventory, checksums, retrieval dates, licences
  raw/                  ignored local source/API snapshots; never indexed directly
  staging/              generated normalized candidates and validation reports
  reviewed/             human-reviewed Git-tracked CSV source of truth
  fixtures/             synthetic and golden test inputs, visibly labelled
  dictionaries/         columns, enums, units, status definitions
  published/            generated immutable release manifest only
indexes/
  reviewed_evidence/    generated FAISS index plus manifest/version metadata
```

Large raw downloads, restricted source documents, supplier-confidential records, and personal trial documents must not be committed. Git tracks a manifest and checksum, not prohibited content. Generated databases and indexes are build artifacts; release storage keeps them alongside their manifest.

## 5. Schema changes required before curation

The existing eleven CSV templates are a good start, but they need common provenance fields and several normalized records before real entry begins.

### Common fields on reviewed records

- `record_version`
- `review_status`: `discovered`, `extracted`, `verified`, `approved`, `rejected`, `superseded`
- `reviewer`
- `reviewed_at`
- `source_id`
- `source_location`
- `evidence_status`: database-derived, literature-derived, calculated, AI-predicted, assumed for demo, experimentally measured
- `notes`

Only `approved` rows enter live runtime tables or the vector index.

### Additional required tables

- `algae_materials.csv`: separates a purchasable material/batch from the species concept.
- `ingredient_forms.csv`: separates cocoa powder, extract, oil, paste, and other non-interchangeable forms.
- `screening_bounds.csv`: one bound per ingredient form, matrix, role, region/context, and source.
- `allergens.csv` and `ingredient_allergens.csv`: controlled allergen relationships rather than free text.
- `metric_definitions.csv`: formula, unit, comparator, precision, and allowed evidence statuses.
- `prototype_processes.csv`: batch, mixing, temperature, storage, serving, and deviations for B0/A0/A1.
- `dataset_versions.csv`: published version, content hashes, schema version, reviewer, and release notes.
- `retrieval_evaluations.csv`: question, filters, expected source/chunk family, and reviewer rationale.

Runtime storage should normalize formulation ingredients and agent trace events into tables. The CSV `recipe_json` field can remain an export/import representation, but it should not be the only queryable runtime representation.

### Required controlled vocabularies

- Species/material, ingredient role, sensory modality/category, relationship type, evidence type, evidence strength, review status, evidence-status label, formulation status, confidence band, unit, allergen, and regulatory region.
- Relationship types: `associated_with`, `odor_active`, `taste_active`, `suppresses`, `complements`, and `hypothesized`.
- Evidence types should distinguish direct same-matrix sensory/formulation evidence, related food-matrix evidence, analytical detection, review evidence, in-vitro evidence, database identity, supplier specification, and project measurement.

## 6. Field-level scientific rules

### Algae and compound observations

- Species, strain, material form, process, and batch must remain separate.
- `reported_value` always has a unit and measurement basis.
- Peak area, relative abundance, detection, concentration, odor activity, and sensory attribution are separate concepts.
- A detected compound is not automatically an off-note driver.
- When a study reports only a figure/category, record the qualitative value and do not invent a number.

### Compound identity

- Store CID, SMILES, InChIKey, retrieval date, and identity verification status.
- PubChem values and locally computed RDKit values must have different provenance fields.
- Fingerprints store algorithm, radius, bit length, chirality choice, RDKit version, and molecule-standardization rule.
- Identity conflicts block publication until reviewed.

### Ingredients and screening ranges

- Bounds apply to a named ingredient form and product matrix.
- Use `% w/w` as the normalized formulation basis and keep the reported source unit.
- Hard safety/regulatory maximum and experimental screening range are distinct.
- Allergens are relationships, not a comma-separated warning.
- A binder or matrix ingredient may be allowed by an explicit formulation role without a masking-mechanism claim.

### Nutrition

- Store values per 100 g with the original basis and transformation record.
- Required core fields: protein, energy, carbohydrate, fat, fibre, and iron; omega-3 only when supported.
- Record coverage for each computed formula. If a required nutrient is missing for a material contribution, that result is unknown.
- Do not calculate from a generic ingredient when an exact supplier record is required for the claim.

### Evidence chunks

- One chunk supports one clear claim or tightly related claim set.
- Store exact source location, source ID, related species/compound/ingredient/matrix IDs, evidence type, and reviewer summary.
- Prefer reviewer-written notes of roughly 1–4 sentences. Store verbatim text only when permitted and necessary.
- Diagnosis chunks and intervention chunks need separate tags.
- Every mechanism-like sentence must state whether it is direct evidence, indirect evidence, or hypothesis.

### Trials

- Ratings must use the configured 1–9 scale and anchors.
- One row represents one panelist-sample observation; panelist code is pseudonymous.
- Blinding code resolves to formulation only in a protected trial mapping.
- Do not overwrite observations. Corrections append an amendment/audit event.
- Calculated summaries store sample size, exclusions with reasons, mean, spread, formula version, and created time.

## 7. Review workflow

Every record follows the same controlled flow:

1. `Discover`: record a source candidate and why it may matter.
2. `Extract`: create a candidate row with exact source location and original wording/unit.
3. `Normalize`: resolve controlled IDs, ingredient forms, units, and relationship types.
4. `Verify`: check chemical identity, numerical transcription, source match, and licence.
5. `Scientific review`: confirm that the row supports the intended use and does not overstate causality.
6. `Approve`: reviewer and timestamp are required; the row becomes eligible for publication.
7. `Publish`: validate the complete graph, calculate hashes, create an immutable dataset version, import runtime tables, and build the matching vector index.
8. `Supersede`: corrections create new records/versions; published history remains reproducible.

The extractor and reviewer should be different people for high-impact fields such as compound identity, screening bounds, allergens, regulatory notes, and headline evidence. If only one qualified reviewer is available, record that limitation and require a second review before any external product claim.

## 8. Automated validation gates

Publication fails when any of these checks fail:

- duplicate primary ID or invalid controlled enum;
- orphan foreign key or cyclic/superseded reference used as current;
- missing source, source location, reviewer, review date, or required licence note;
- production row not marked approved;
- invalid CID/SMILES or unresolved identity conflict;
- value without unit/basis or incompatible unit conversion;
- peak area represented as concentration;
- screening minimum greater than maximum;
- allergen relationship missing for an ingredient form;
- nutrition null converted to zero;
- evidence chunk lacking matrix/support classification;
- formulation ingredient missing nutrition/bound/role coverage required for its use;
- indexed chunk set differing from the published approved chunk set;
- dataset or index manifest hash mismatch.

Warnings, which require reviewer acknowledgement but may not block all builds, include indirect evidence, old generic nutrition values, incomplete optional nutrients, missing concentration data, and low modality coverage.

## 9. Dataset versions and reproducibility

Each published version contains:

- semantic dataset version and schema version;
- SHA-256 per reviewed file and a combined content hash;
- row counts by table and review status;
- source/record additions, removals, and supersessions;
- reviewer and publication timestamp;
- molecular feature configuration and RDKit version;
- embedding model name/revision and dimensions;
- FAISS settings and index hash;
- validation report hash;
- code commit that built it.

Every run snapshots the dataset version, index version, prompt version, model/provider, formulation engine version, and deterministic seed. Updating the dataset never changes an old run or report.

This application does not train a custom model in version 1, so a conventional train/validation/test split is unnecessary. Retrieval evaluation uses a separate, reviewer-authored golden query set. Fixed demo scenarios and calculation fixtures remain separate from scientific production rows.

## 10. Acquisition order

Curate in dependency order so no team member enters data that cannot yet be validated:

1. Data dictionary, enums, common provenance fields, and source manifest.
2. Two algae materials and the exact B0/A0 ingredient forms.
3. Source records and 15–30 compound identities.
4. Algae-compound observations and five-category sensory lexicon.
5. Compound-sensory links with evidence classifications.
6. Allowed ingredient forms, roles, allergens, and screening bounds.
7. Nutrition for every B0/A0/candidate ingredient form.
8. Reviewed diagnosis and intervention chunks.
9. Retrieval golden questions and expected evidence families.
10. Published dataset/index version 0.1.
11. Generated formulation records and selected A1.
12. Prototype process records and blinded trial observations.
13. Published measured-impact dataset version 0.2 and final report.

## 11. Dataset proof gates

### Dataset 0.1 — engine-ready

- All minimum record targets are met or an approved exception explains why.
- Every production row is approved and source-linked.
- All B0/A0 and candidate ingredients have roles, bounds, allergens, and required nutrition coverage.
- All compounds resolve and feature generation succeeds offline from cache.
- Every indexed chunk matches the published manifest.
- Golden retrieval questions pass their expected-source thresholds.
- A complete live-mode run can produce three constraint-valid, evidence-linked formulations without synthetic fixtures.

### Dataset 0.2 — impact-ready

- B0, A0, and A1 recipes and process records are immutable.
- Trial protocol and blinding records are complete.
- Valid sensory observations produce the stored summary.
- Nutrition and sensory comparison values reproduce independently.
- Headline X/Y/Z values resolve to stored records and correct status labels.

## 12. Immediate dataset implementation slice

Before collecting records, implement the schema extensions, data dictionary, enum definitions, source manifest, validator, and `validate`/`publish` commands. Then curate only the two algae materials, B0/A0 ingredient forms, and five source records as a pilot. Run the full validation/review/publish loop and correct the process before scaling to the target corpus.
