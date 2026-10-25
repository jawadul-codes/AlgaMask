from html import escape

from .schemas import RunResult
from .report_interpretation import interpret


def render_report(result: RunResult) -> str:
    interpretation = interpret(result)
    ingredient_names = interpretation['ingredient_names']
    controls = {f.id for f in result.controls}
    rows = "".join(f"<tr><td>{escape(f.id)} ({'comparison control' if f.id in controls else 'candidate'})</td><td>{escape(f.name)}</td><td>{f.total_g:g} g</td><td>{escape(', '.join(f'{ingredient_names.get(i.ingredient_id, i.ingredient_id)} [{i.ingredient_id}]: {i.grams:g} g' for i in f.ingredients))}</td></tr>" for f in result.controls + result.formulations)
    reasons = ''.join(f'<li>{escape(reason)}</li>' for reason in interpretation['blocking_reasons'])
    outcome = (f"<h2>{escape(interpretation['title'])}</h2><p>{escape(interpretation['reason'])}</p><ul>{reasons}</ul>"
               f"<p>{escape(interpretation['sensory'])}</p><p>{escape(interpretation['mass_basis'])}</p>"
               f"<p>{escape(interpretation['nutrition_notice'])}</p>")
    limitations = "".join(f"<li>{escape(text)}</li>" for text in result.limitations)
    label = {"mock": "MOCK • Assumed for demo", "rag_development": "LOCAL RETRIEVAL • Development data • Experimental screening",
             "rag": "LOCAL RETRIEVAL • Production formulation unavailable"}[result.mode]
    evidence = "".join(
        f"<li id=\"evidence-{escape(item['chunk_id'])}\"><strong>{escape(item['chunk_id'])}</strong> — {escape(item.get('claim_summary', item.get('text', '')))}"
        f"<br>Applicability: {escape(interpretation['evidence'][item['chunk_id']]['label'])}. Recipe masking validation is not established."
        f"<br>Source: {escape(item['source_id'])}; {escape(item.get('source_title', item.get('title', '')))}"
        f"<br>Location: {escape(item.get('source_location', 'demo'))}; review: {escape(item.get('review_status', 'mock'))}</li>"
        for item in result.evidence)
    trace = "".join(f"<li>{escape(step.agent)}: {escape(step.state)} ({escape(step.status)})</li>" for step in result.trace)
    provenance = ""
    if result.retrieval:
        provenance = f"<p>Dataset: {escape(result.retrieval['dataset_version'])}; index: {escape(result.retrieval['index_version'])}</p>"
    if result.request.exclusions:
        exclusion_label = ('Ingredient preferences (allergy safety not verified)' if
                           result.request.exclusion_mode == 'ingredient_preference' else 'Verified-free-from requirements')
        provenance += f"<p>{exclusion_label}: {escape(', '.join(result.request.exclusions))}</p>"
    if result.request.experiment == "spirulina-proof-v1":
        provenance += "<p>Experiment: spirulina-proof-v1. 45 g ingredient input, not verified finished serving. Nutrition per serving refers to this input mass. Scientific and physical-trial approval pending.</p>"
    explanation = ""
    if result.generation and result.generation.status == 'complete' and result.status != 'generation_failed':
        generated = result.generation
        claims = "".join(f"<li>{escape(c.text)} <a href=\"#evidence-{escape(c.citation.chunk_id)}\">[{escape(c.citation.chunk_id)}]</a>"
                         f"<br>{escape(interpretation['evidence'].get(c.citation.chunk_id, {}).get('label', 'Background context; recipe applicability unverified'))}"
                         f"<br>{escape(' '.join(interpretation['evidence'].get(c.citation.chunk_id, {}).get('notes', [])))}"
                         f"<br>Matrix: {escape(c.citation.matrix)}; source statement support: {escape(c.citation.support_class)}; review: {escape(c.citation.review_status)}</li>"
                         for c in generated.claims)
        explanation = (f"<h2>Evidence context and limits</h2><p>Method: {escape(generated.method)}; "
                       f"provider: {escape(generated.provider)}; model: {escape(generated.model or 'none')}; "
                       f"status: {escape(generated.status)}</p><p>{escape(generated.limitation)}</p><ul>{claims}</ul>")
    nutrition = ""
    def number(value):
        return "unknown" if value is None else f"{value:.3f}"
    for code, estimate in result.impact.get("nutrition", {}).items():
        nutrient_rows = "".join(f"<tr><td>{escape(key)}</td><td>{number(value)}</td><td>{number(estimate['per_100g'][key])}</td>"
                                f"<td>{escape(', '.join(estimate['missing'][key]))}</td></tr>"
                                for key, value in estimate["per_serving"].items())
        sources = "".join(f"<li>{escape(r['nutrition_id'])}: {escape(r['source_id'] or '')}; {escape(r['source_location'] or '')}"
                          f" — {escape(r['match_rationale'] or '')}; {escape(r['transformation_record'] or '')}; review: {escape(r['review_status'])}</li>"
                          for r in estimate["records"])
        warnings = "".join(f"<li>{escape(w)}</li>" for w in estimate["warnings"])
        nutrition += (f"<h3>{escape(code)} — estimated composition</h3><table><tr><th>Nutrient / unit</th><th>Per serving</th><th>Per 100 g</th><th>Missing forms</th></tr>{nutrient_rows}</table>"
                      f"<p>Protein g per 100 kcal: {number(estimate['protein_g_per_100_kcal'])}</p><ul>{warnings}</ul><ul>{sources}</ul>")
    screening = result.impact.get("screening")
    screening_html = ""
    if screening:
        from json import dumps
        screening_html = f"<h2>Screening assumptions and checks</h2><pre>{escape(dumps(screening, indent=2))}</pre>"
    heading = "Demonstration formulations" if result.mode == "mock" else "Experimental formulations — not production eligible"
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>AlgaMask concept report</title>
<style>body{{font:16px system-ui;max-width:900px;margin:48px auto;padding:24px;color:#183c32}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}li{{margin-bottom:12px}}@media print{{button{{display:none}}}}</style>
<h1>AlgaMask concept report</h1><p>{label} • {escape(result.status)}</p><p>Run {escape(result.run_id)}</p>{outcome}
<p>{escape(result.request.algae.value)} · {result.request.inclusion_pct:g}% inclusion · {result.request.serving_g:g} g serving</p>
{provenance}<h2>Workflow trace</h2><ol>{trace}</ol>{explanation}
<h2>{heading}</h2><p>{escape(interpretation['controls'])}</p><p>{'No formulations were returned for this run.' if not rows else 'Amounts below retain calculation precision.'}</p><table><tr><th>Code</th><th>Concept</th><th>Mass</th><th>Ingredients</th></tr>{rows}</table>{screening_html}
<h2>Retrieved context</h2><p>Context does not establish effective or safe ingredient doses for these formulations.</p><ul>{evidence}</ul>
<h2>Impact comparison</h2><p>{escape(result.impact['explanation'])}</p><p>Estimated protein-density change (%): {number(result.impact.get('nutrition_change_pct'))}. Sensory change: unknown. Panel size: 0.</p>{nutrition}
<h2>Limitations</h2><ul>{limitations}</ul><p>The JSON run record contains the complete six-agent trace and evidence provenance.</p>
<button onclick="window.print()">Print / save as PDF</button></html>"""
