from html import escape

from .schemas import RunResult


def render_report(result: RunResult) -> str:
    rows = "".join(f"<tr><td>{escape(f.id)}</td><td>{escape(f.name)}</td><td>{f.total_g:g} g</td><td>{escape(', '.join(f'{i.ingredient_id}: {i.grams:g} g' for i in f.ingredients))}</td></tr>" for f in result.controls + result.formulations)
    limitations = "".join(f"<li>{escape(text)}</li>" for text in result.limitations)
    label = {"mock": "MOCK • Assumed for demo", "rag_development": "LOCAL RETRIEVAL • Development data • Demonstration recipes",
             "rag": "LOCAL RETRIEVAL • Demonstration recipes"}[result.mode]
    evidence = "".join(
        f"<li id=\"evidence-{escape(item['chunk_id'])}\"><strong>{escape(item['chunk_id'])}</strong> — {escape(item.get('claim_summary', item.get('text', '')))}"
        f"<br>Source: {escape(item['source_id'])}; {escape(item.get('source_title', item.get('title', '')))}"
        f"<br>Location: {escape(item.get('source_location', 'demo'))}; review: {escape(item.get('review_status', 'mock'))}</li>"
        for item in result.evidence)
    trace = "".join(f"<li>{escape(step.agent)}: {escape(step.state)} ({escape(step.status)})</li>" for step in result.trace)
    provenance = ""
    if result.retrieval:
        provenance = f"<p>Dataset: {escape(result.retrieval['dataset_version'])}; index: {escape(result.retrieval['index_version'])}</p>"
    explanation = ""
    if result.generation:
        generated = result.generation
        claims = "".join(f"<li>{escape(c.text)} <a href=\"#evidence-{escape(c.citation.chunk_id)}\">[{escape(c.citation.chunk_id)}]</a>"
                         f"<br>Matrix: {escape(c.citation.matrix)}; support: {escape(c.citation.support_class)}; review: {escape(c.citation.review_status)}</li>"
                         for c in generated.claims)
        explanation = (f"<h2>Cited evidence explanation</h2><p>Method: {escape(generated.method)}; "
                       f"provider: {escape(generated.provider)}; model: {escape(generated.model or 'none')}; "
                       f"status: {escape(generated.status)}</p><p>{escape(generated.limitation)}</p><ul>{claims}</ul>")
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>AlgaMask concept report</title>
<style>body{{font:16px system-ui;max-width:900px;margin:48px auto;padding:24px;color:#183c32}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}li{{margin-bottom:12px}}@media print{{button{{display:none}}}}</style>
<h1>AlgaMask concept report</h1><p>{label} • {escape(result.status)}</p><p>Run {escape(result.run_id)}</p>
<p>{escape(result.request.algae.value)} · {result.request.inclusion_pct:g}% inclusion · {result.request.serving_g:g} g serving</p>
{provenance}<h2>Workflow trace</h2><ol>{trace}</ol>{explanation}
<h2>Demonstration formulations</h2><table><tr><th>Code</th><th>Concept</th><th>Mass</th><th>Ingredients</th></tr>{rows}</table>
<h2>Retrieved context</h2><p>Context does not establish support for the demonstration formulations.</p><ul>{evidence}</ul>
<h2>Impact comparison</h2><p>{escape(result.impact['explanation'])}</p><p>Nutrition change: unknown. Sensory change: unknown. Panel size: 0.</p>
<h2>Limitations</h2><ul>{limitations}</ul><p>The JSON run record contains the complete six-agent trace and evidence provenance.</p>
<button onclick="window.print()">Print / save as PDF</button></html>"""
