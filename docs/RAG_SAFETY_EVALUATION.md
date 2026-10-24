# RAG safety regression checks

Date: 2026-10-24. Engineering preparation for completion-roadmap Step 4.
Status: draft regression suite passed; independent scientific evaluation pending.

## What was checked

The eleven cases in tests/fixtures/rag_safety_cases.json cover:

- Five qualified-context questions: cinnamon in other foods, reference aroma labels,
  an unlisted compound, the inconsistent recipe denominator, and absent protein-bar
  masking efficacy evidence. Required notes must rank within the top three, preserve
  specific qualifications, and appear in an exactly grounded explanation.
- Four empty-result cases: incompatible species/source, matrix/source, purpose/source
  combinations and a nonexistent source.
- Two unrelated questions, concerning astronomy and infrastructure software.

The six empty-result cases must return no hits and insufficient_evidence. Generation
receives the actual returned context and must block when it is empty. All returned
hits are checked against the requested filters and basic citation completeness.

Related context is not a supported answer to an efficacy question. A note explaining
that no trial exists is useful context, not proof that masking works. No free-form
scientific answering or calibrated confidence claim is introduced by these tests.

## Results and reproducibility

Final report: output/rag/safety-dev-v1-final.json. All 11 cases passed on rc.4/dev.3,
using the cached model with HF_HUB_OFFLINE=1. The report includes query settings,
returned notes, scores, source provenance, rank, generation status and failure codes.
The earlier safety-dev-v1.json is an intermediate run; use the final report.

```sh
cd /Users/mohamaadmazharulislam/AlgaMask
HF_HUB_OFFLINE=1 .venv/bin/python tools/evaluate_rag_safety.py \
  --report output/rag/safety-dev-v1-rerun.json
.venv/bin/python -m pytest -q
```

Choose a new report filename on each run; existing reports cannot be overwritten.
The runner respects configured dataset/index paths but explicitly operates in
development mode. It does not restart servers, change thresholds or modify an index.

Seven evaluator tests verify valid context and detection of wrong species, absent
expected notes, missing caveats, incomplete provenance, unexpected context and invalid
case collections. Full normal suite: 182 passed / 10 opt-in integration checks skipped.
The real-model safety evaluation above runs separately to avoid the previously
documented macOS mixed-native-library test-process conflict.

## Limits and independent review handoff

These questions were written with knowledge of the existing corpus. They are not
blind or held-out; passing them does not establish general accuracy or scientific
safety. Two unrelated queries do not calibrate universal abstention. Cosine similarity
still measures relevance rather than whether a question can be answered safely.
Exact-copy grounding cannot make an incorrect or malicious source note scientifically
valid. Qualified source review remains essential.

Before the Step 4 completion gate, a separate reviewer should record the following
for each new question BEFORE inspecting retrieval results:

| Field | Required reviewer input |
| --- | --- |
| Question ID and text | A new, independently authored question |
| Scope | Species, actual material, matrix and intended claim |
| Expected behavior | Supported context, qualified indirect context or abstention |
| Acceptable sources/notes | Scientifically justified evidence and exclusions |
| Required limitations | Units, denominator, source matrix and applicability |
| Acceptance rule | Required rank/coverage and forbidden conclusions |
| Reviewer | Name, role, date and rationale |

Do not mark reviewer fields complete on their behalf. Preserve their pre-test answers
and evaluate them without changing the questions to fit observed rankings. Separately
review prompt-injection handling and model-assisted generation if those are enabled;
this runner checks the default extractive path, not a live Ollama model.
