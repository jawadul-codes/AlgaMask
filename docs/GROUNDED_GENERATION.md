# Grounded evidence generation — Step 5

The real-retrieval run path now generates a cited evidence explanation, validates
its claims and citation metadata, and includes it in the JSON run and HTML report.

## What generation means in this step

Generation is deliberately constrained to selecting and ordering exact retrieved
evidence notes. Each claim preserves the complete original wording, including units,
negative findings and qualifications. The backend attaches the source title, URL,
location, matrix, support class, evidence/review status and dataset hash itself.

This supports a locally testable grounding contract. It is not unrestricted prose
generation or a general-purpose entailment checker. Source truth and scientific
applicability still depend on the underlying dataset review. Recipe and dose
calculation remain Step 6; the explanation does not supply citations to mock doses.

## Two explicit methods

- `extractive` is the default. It selects up to four diagnosis and four intervention
  notes deterministically. It requires no model server and is labelled `extractive`.
- `ollama` uses a locally installed model to select and reproduce notes. It is labelled
  `model_assisted`. Only loopback HTTP endpoints are supported; proxies and redirects
  are disabled. No model is downloaded automatically.

To enable the installed local model, start Ollama in one terminal:

```sh
ollama serve
```

Then run the backend in another:

```sh
ALGAMASK_MODE=development \
ALGAMASK_GENERATION_PROVIDER=ollama \
ALGAMASK_GENERATION_MODEL=llama3.2:latest \
uv run --extra rag uvicorn algamask.api:app --host 127.0.0.1 --port 8000
```

The default Ollama endpoint is `http://127.0.0.1:11434`; override it with
`ALGAMASK_OLLAMA_URL` for another local port. `ALGAMASK_GENERATION_PROVIDER=extractive`
selects the deterministic method explicitly. Changing configuration requires a server
restart. Mock mode keeps its original fixture workflow and does not invoke generation.

## Output and failure behavior

`RunResult.generation` records method, provider, model/digest, prompt version/hash,
attempt count, validated claims and sanitized failure history. The model digest is
read from the local installation and must remain stable across retries. The prompt
version is `evidence-selection-v1`; temperature is 0 and seed is 42. These parameters
improve reproducibility but do not promise bit-identical model responses.

The generation boundary rejects invented citations, changed text/numbers, omitted
qualifications, duplicate claims, extra fields and omission of an available evidence
family. It permits one correction retry (two attempts total). The Critic independently
rechecks text, section and citation metadata against the retrieved snapshot.

If generation fails, the run is stored with `status=generation_failed`, retained
evidence/error history and blocked downstream steps. No formulations or controls are
returned. A configured model outage never silently switches to extractive mode.
Each local request has a timeout: 5 seconds for model identity, 25 seconds for inference.

HTML reports show the method and model, link claims to evidence entries, escape
source content and preserve qualifications. Current run storage is still in memory;
durability remains Step 8. Flutter remains unchanged until Step 7.

## Verification

- Regression tests cover false citations, changed numbers, stripped caveats, duplicate
  context, absent evidence families, metadata tampering, instruction-injection attempts,
  provider outages, retry recovery and failed-run propagation.
- Live offline-retrieval/local-model API test passed with the installed Llama 3.2.
  Five grounded statements were returned, including the absence of a masking trial
  and the limitation that a tested range is not a regulatory maximum. The first
  response failed schema validation; the correction retry succeeded.
- Tested model digest:
  `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
- The temporary test server used port 11435; it is not a deployed application service.
