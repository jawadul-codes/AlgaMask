# Local evidence retrieval — Step 3

Implemented and tested on 2026-10-22. Active development index:
`indexes/reviewed_evidence/0.1.0-dev.2`.

## What works

The 22 evidence notes in candidate `0.1.0-rc.1` are embedded locally with a pinned
MiniLM model and stored in a normalized FAISS inner-product index (cosine similarity).
Search returns source IDs, titles, links, exact locations, scientific evidence labels,
record review status, dataset hash and index version. It does not generate answers.

Filters are applied before ranking: diagnosis/intervention tag, species, exact matrix
(case-insensitive) and source IDs. Species comes from linked material records, not
guessed from wording. A species filter excludes notes without a material mapping.
Empty eligible sets or no matches above the requested cosine threshold return
`insufficient_evidence`. The default threshold 0.2 is a development heuristic, not a
scientific confidence level or a calibrated guarantee of answerability.

Indexed text includes the claim, source title, source location, matrix and mapped
species. It does not contain evaluation questions or expected answers. Version 2
adds source context; version 1 artifacts are preserved as an experiment, but the
current loader rejects their older text-preparation version.

## Reproduce locally

```sh
uv sync --locked --extra dev --extra rag

# Initial download only; choose a NEW version if the output already exists.
uv run --extra rag python tools/rag.py build \
  --dataset data/candidates/0.1.0-rc.1 --development \
  --version 0.1.0-dev.3 --download-model

# Existing dev.2 works offline after the initial model download.
uv run --extra rag python tools/rag.py search \
  --dataset data/candidates/0.1.0-rc.1 \
  --index indexes/reviewed_evidence/0.1.0-dev.2 --development \
  --query 'What relative area did the chlorella culture paper report for hexanal?' \
  --tag diagnosis --species chlorella

uv run --extra rag python tools/rag.py evaluate \
  --dataset data/candidates/0.1.0-rc.1 \
  --index indexes/reviewed_evidence/0.1.0-dev.2 --development

uv run --extra rag --extra dev pytest -q
```

Model weights stay in the standard local Hugging Face cache, outside the repository.
No embedding API key is required. Downloads are disabled unless `--download-model`
is supplied. `HF_HUB_OFFLINE=1` can additionally enforce offline Hub behavior.

## Version and review checks

The index manifest binds model name/revision/dimensions, text-preparation version,
dataset content hash, dataset version, vector count, metric and file hashes.
Loading checks hashes, metadata against the frozen dataset, normalized vectors,
model compatibility and candidate/release eligibility. Existing index versions and
evaluation output files cannot be overwritten by the commands.

`--development` is required for this candidate. It is displayed as
`development_only: true` in responses. Production uses the default path and requires
an approved dataset release; it cannot load this candidate index. Mazharul Islam's
recorded approval remains preserved separately; the unresolved per-row data checks
from Step 2 are not bypassed by retrieval.

## Evaluation results

| Experiment | Expected chunk at rank 1 | Mean reciprocal rank |
|---|---:|---:|
| Initial claim/matrix/species vectors | 7 / 8 | 0.892857 |
| Initial vectors with optional cross-encoder | 7 / 8 | 0.890625 |
| Source-enriched vectors (active dev.2) | 8 / 8 | 1.0 |

Reports are stored in `output/rag/`. The eight questions are draft development
questions used while improving retrieval; these scores are not a held-out quality
estimate. Additional independently reviewed questions are still needed for release.
An unrelated orbital-mechanics query returned no evidence with Hub offline mode.
Regression tests cover filters, provenance, no-result behavior, tampering, model and
dataset mismatches, candidate rejection, invalid vectors and optional reranking.

## Runtime choices and optional reranking

Dependencies are locked in `uv.lock`; the `rag` extra pins sentence-transformers
6.2.0 and faiss-cpu 1.15.1. The embedding model is
`sentence-transformers/all-MiniLM-L6-v2`, revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, with 384 dimensions on CPU.
One OpenMP thread and disabled tokenizer parallelism are the defaults because the
initial native execution crashed on this macOS machine with competing thread pools.

`--rerank` enables an experimental local cross-encoder. Its identity and separate
rerank scores appear in results; cosine scores and evidence strength remain separate.
Initial use needs `--download-model` to cache its weights. The tested revision is
`233902d25c440f23af6f7d6e94d2946bac0bee0a` of
`cross-encoder/ms-marco-MiniLM-L6-v2`. Float64 CPU execution avoids observed NaNs in
float32 on this runtime. It is optional because the initial evaluation did not improve.

Model references: [embedding model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2),
[reranker model card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2),
[Sentence Transformers API](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).

## Next boundary

Step 4 connects `EvidenceSearch` to the Retrieval agent and API workflow. Current
`/runs` remains the existing mock workflow; Step 3 alone does not make app answers
or formulations grounded in this evidence. Grounded generation belongs to Step 5.
