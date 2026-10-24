# AlgaMask project completion roadmap

Updated: 2026-10-24

## Current position

AlgaMask is already a functioning local development application. The Flutter app,
FastAPI backend, six-agent workflow, development RAG, experimental formulation
screening, evidence reports, persistence, retry, backup and automated development
checks are implemented.

The remaining work is mainly scientific approval, physical validation, production
security, deployment and controlled real-world verification. Passing software tests
does not by itself approve the scientific dataset or prove that a formulation is
safe, effective, manufacturable or acceptable to consumers.

## Step 1 - Freeze the first production claim and product scope

Engineering scope prepared on 2026-10-24: see [FIRST_RELEASE_SCOPE.md](FIRST_RELEASE_SCOPE.md)
for the exact proposed B0/A0/A1 quantities, ingredient IDs, measurement rules,
permitted statements and current app mismatch. Owner/scientific sign-off remains
pending; recipe quantities are explicit engineering assumptions for review.

Use one narrow proof path before expanding the system:

- one 45 g algae protein-bar matrix;
- spirulina as the first supported algae;
- one frozen baseline recipe and ingredient-form list;
- B0 baseline, A0 control and one selected candidate formulation;
- clearly defined nutrition, sensory and formulation measurements;
- no diagnosis, treatment or guaranteed health-benefit claims.

### Completion gate

A signed scope document states exactly what the first validated release may and may
not claim. Every team member and scientific reviewer uses the same formulation,
ingredient forms, units and comparison definitions.

## Step 2 - Complete scientific review of the dataset

In progress: the first source audit and normalization pass is recorded in
[SCIENTIFIC_REVIEW_STEP2.md](SCIENTIFIC_REVIEW_STEP2.md). Latest candidate rc.4
contains 290 extracted records, including 23 evidence notes. Nutrition, methods
and spirulina analytical audits are documented. The rc.4/dev.3 development pair
is now active and checked through Flutter (DEVELOPMENT_ACTIVATION.md).
Scientific approval and production eligibility remain pending.

Review the existing candidate dataset instead of rebuilding it from scratch.

1. Confirm source title, authors, year, DOI or stable URL and access information.
2. Check whether stored text may legally be reused; use reviewer-written notes when
   full source text cannot be redistributed.
3. Verify algae species, material form, compound identity and processing details.
4. Check every numeric value, unit, denominator and dry-weight/as-sold basis.
5. Classify evidence as direct, indirect, analytical, review, database, supplier,
   experimental or hypothesis evidence.
6. Confirm that the food matrix is relevant. Evidence from beverages or unrelated
   products must not be presented as direct protein-bar evidence.
7. Complete nutrition, allergen, ingredient-bound and processing records for the
   exact ingredient forms used by the formulation engine.
8. Review each RAG evidence note as a single, accurate and independently usable
   claim with its limitations retained.
9. Mark each eligible row approved, approved with limitations, rejected or needing
   correction. Record reviewer name, review date and reasoning.
10. Create a corrected immutable candidate, expected to be `0.1.0-rc.2`, without
    altering the preserved `0.1.0-rc.1` snapshot.

### Recommended reviewers

- food scientist or food technologist;
- algae or functional-food researcher;
- nutrition specialist;
- sensory-science specialist;
- food-safety or regulatory specialist for market-facing use.

The extractor and reviewer should be different people for high-impact scientific
fields whenever possible.

### Completion gate

Every production-eligible row is source-linked, reviewed and approved. Required
nutrition, allergen, formulation-bound and evidence coverage is complete for the
frozen proof path. Dataset validation passes without relabelling missing information
as approved.

## Step 3 - Publish the approved dataset and production RAG index

1. Run the complete dataset structural and scientific-publication checks.
2. Publish immutable dataset version `0.1.0` with file hashes, schema version,
   reviewer information and release notes.
3. Build a new production FAISS index from approved evidence notes only.
4. Bind the index to the exact dataset hash, embedding model revision, dimensions,
   text-preparation version and artifact hashes.
5. Keep structured nutrition, allergens and numeric limits outside free-text vector
   search so deterministic calculations remain authoritative.
6. Test filters for species, matrix, evidence purpose, source and review status.
7. Confirm that no rejected, provisional or development-only evidence can leak into
   production retrieval.

### Completion gate

Production mode loads the approved dataset and matching index without development
overrides. Every retrieved citation resolves to an approved record in release
`0.1.0`; version or hash mismatches fail explicitly.

## Step 4 - Independently evaluate RAG and grounded explanations

Engineering preparation completed: eleven draft safety regression cases pass on
rc.4/dev.3 (RAG_SAFETY_EVALUATION.md). These are corpus-informed tests, not independent
review. The reviewer-written, predeclared evaluation gate below remains open.

1. Have reviewers write new evaluation questions without seeing retrieval rankings.
2. Include positive diagnosis and intervention questions for the supported species
   and protein-bar matrix.
3. Include negative, irrelevant, ambiguous and insufficient-evidence questions.
4. Define expected evidence families and acceptable indirect evidence in advance.
5. Measure top-result quality, top-three coverage, filter correctness, citation
   resolution and abstention behavior.
6. Review generated explanations for altered numbers, missing qualifications,
   invented citations, excessive claim strength and prompt-injection resistance.
7. Correct the evidence notes, metadata or retrieval configuration when failures are
   scientific rather than merely linguistic.

### Completion gate

All agreed positive questions retrieve acceptable evidence within the required rank,
negative questions return insufficient evidence, and every generated claim is fully
supported by the supplied approved notes.

## Step 5 - Validate the formulation engine scientifically

Engineering preparation: the opt-in fixed B0/A0/A1 comparison is implemented and
tested (FIXED_PROOF_EXPERIMENT.md). This does not complete scientific validation
or bypass the pending Step 2/3 approval and publication gates.

1. Confirm exact supplier ingredient forms and specifications.
2. Replace development search bounds with reviewed ingredient, processing and
   product-matrix limits.
3. Complete deterministic nutrition data for every enabled ingredient and required
   nutrient; unknown values must remain unknown.
4. Complete allergen and cross-contact information for every enabled ingredient.
5. Review mass balance, serving-size calculations, inclusion percentages and units.
6. Confirm that B0, A0 and the candidate differ only in the intended variables.
7. Review candidate scoring and ensure semantic similarity is never treated as proof
   of sensory effectiveness.
8. Test feasible, infeasible, allergy-excluded and missing-data scenarios.

### Completion gate

The fixed proof scenario reproducibly generates distinct, mass-balanced candidates
that satisfy every reviewed hard constraint. Unsupported inputs produce explicit
blocked or insufficient-data results rather than guessed formulations.

## Step 6 - Produce and test physical prototypes

Software and RAG cannot replace this stage.

1. Prepare the approved B0 baseline, A0 control and selected candidate using exact
   batch instructions and ingredient lots.
2. Record preparation method, equipment, temperature, timing, storage and deviations.
3. Assign blinded sample codes and randomize serving order.
4. Use a reviewed sensory protocol with defined scales and anchors.
5. Record appearance, aroma, flavour, bitterness, earthiness, texture, aftertaste and
   overall acceptance as appropriate to the agreed scope.
6. Store pseudonymous panelist identifiers only; keep consent and direct identity
   outside the application dataset.
7. Record exclusions, incomplete sessions and protocol deviations.
8. Analyze the candidate against the declared B0 and A0 comparison bases.

### Completion gate

At least one protocol-compliant physical comparison has complete, reviewable raw
records and calculated results. The application does not claim measured improvement
unless the required measurements and comparison bases are present.

## Step 7 - Add measured results to the application

1. Validate and import trial observations as a new immutable dataset version.
2. Label measured values as `experimentally_measured`; keep predictions, literature
   values and calculations visibly separate.
3. Add trial-entry and review interfaces if manual entry will continue.
4. Display sample sizes, protocol version, uncertainty and limitations beside results.
5. Update reports to compare B0, A0 and the candidate without overstating causality.
6. Rebuild the matching index only if approved retrieval evidence changed.
7. Preserve old run snapshots so a new dataset never rewrites earlier reports.

### Completion gate

The application can reproduce the approved trial summary from stored observations,
and every displayed outcome retains its evidence-status label, dataset version and
comparison basis.

## Step 8 - Complete production security and privacy

1. Decide whether the product is single-user, team-only or public.
2. Add authentication, authorization and role separation for users, reviewers and
   administrators.
3. Define what personal data may be collected and minimize it.
4. Add consent, retention, deletion and data-export behavior where applicable.
5. Protect secrets and production configuration outside source control.
6. Add request limits, input-size limits, secure headers and controlled file handling.
7. Perform dependency, API, database and threat-model reviews.
8. Log security-relevant events without storing sensitive questionnaire content in
   unsafe logs.

### Completion gate

An independent security review finds no unresolved critical issues. Access rules,
privacy behavior, retention and recovery are documented and verified.

## Step 9 - Deploy and operate the production system

1. Select the production hosting, database and backup architecture.
2. Package the backend with pinned dependencies and controlled migrations.
3. Configure HTTPS, domains, environment separation and secure secrets.
4. Add health checks, structured logs, metrics, alerting and error tracking.
5. Automate tested database backups and restoration drills.
6. Add continuous integration gates for backend tests, Flutter checks, dataset
   validation, index integrity, migrations and deployment smoke tests.
7. Verify the Flutter app on supported browsers and real mobile devices.
8. Write rollback, incident-response and dataset-recall procedures.

### Completion gate

A staging deployment passes the complete user journey, failure recovery, backup
restore, monitoring and rollback checks using the approved dataset and index.

## Step 10 - Run a controlled pilot and release

1. Select trained pilot users and define what they are allowed to do.
2. Provide visible limitations and require acknowledgment where appropriate.
3. Monitor retrieval failures, blocked formulations, calculation errors, usability
   problems and unsafe interpretation.
4. Review every serious issue before expanding access.
5. Freeze the release's code commit, dataset, index, prompt, model, formulation-engine
   version and operating configuration.
6. Obtain final scientific, security and product release sign-off.
7. Publish release notes and known limitations.

### Completion gate

The released system is traceable from user report to code, dataset, RAG index,
scientific review and physical-validation records. The team can suspend or roll back
the release without losing audit history.

## Immediate next action

Begin Step 1 and Step 2, not additional application features. Freeze the exact first
protein-bar proof path, assign qualified reviewers, and work through the current
candidate review queue. Engineering should support corrections and validation while
protecting the existing immutable candidate and development index.

## Definition of complete

AlgaMask is complete for its first production scope only when:

- the permitted claim and product scope are frozen;
- every runtime scientific row is approved and source-linked;
- production RAG uses only the matching approved dataset and index;
- retrieval and grounded explanations pass independent evaluation;
- formulations use reviewed bounds, nutrition and allergen data;
- physical B0/A0/candidate testing is complete;
- measured claims are reproducible and correctly labelled;
- security, privacy, deployment, backup and recovery checks pass;
- real-device and full user-journey tests pass;
- scientific, security and product owners sign off on the same frozen release.
