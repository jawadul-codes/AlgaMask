from html import escape

from .schemas import RunResult
from .report_interpretation import display_name, interpret


def render_report(result: RunResult) -> str:
    interpretation = interpret(result)
    ingredient_names = interpretation['ingredient_names']
    controls = {f.id for f in result.controls}
    rows = "".join(f"<tr><td>{escape(display_name(result, f.id))} ({escape(f.id)}; {'comparison control' if f.id in controls else 'candidate'})</td><td>{escape(f.name)}</td><td>{f.total_g:g} g</td><td>{escape(', '.join(f'{ingredient_names.get(i.ingredient_id, i.ingredient_id)} [{i.ingredient_id}]: {i.grams:g} g' for i in f.ingredients))}</td></tr>" for f in result.controls + result.formulations)
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
    screening = result.impact.get("screening") or {}
    if screening.get("search_version"):
        provenance += f"<p>Search policy: {escape(screening['search_version'])}. {escape(screening.get('scope') or '')}</p>"
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
    def summary_number(value):
        return "Unknown" if value is None else f"{value:.2f}"
    selected = result.formulations[0] if result.status == 'report_ready' and result.formulations else None
    summary = ''
    if selected:
        cards = []
        for option in result.formulations:
            values = result.impact.get('nutrition', {}).get(option.id, {}).get('per_serving', {})
            amounts = ''.join(f'<li>{escape(ingredient_names.get(item.ingredient_id, item.ingredient_id))}: {item.grams:.2f} g</li>'
                              for item in option.ingredients)
            cards.append(f'<section class="recipe-option"><h2>{escape(display_name(result, option.id))}</h2>'
                   f'<p>Estimated for {result.request.serving_g:g} g of ingredients before processing.</p>'
                   f'<p>Protein: {summary_number(values.get("protein_g"))}{" g" if values.get("protein_g") is not None else ""}'
                   f' &nbsp; Energy: {summary_number(values.get("energy_kcal"))}{" kcal" if values.get("energy_kcal") is not None else ""}'
                   f' &nbsp; Total sugar: {summary_number(values.get("sugar_g"))}{" g" if values.get("sugar_g") is not None else ""}</p>'
                   f'<h3>Ingredients in this option</h3><ul>{amounts}</ul></section>')
        summary = ('<div class="recipe-options">' + ''.join(cards) + '</div>'
                   '<p>Next step: review the ingredient estimates and evidence limits before deciding what to investigate further.</p>')
    else:
        summary = (f'<p>{escape(interpretation["primary_blocker"])}</p>'
                   '<p>Next step: adjust your choices and run the check again. Detailed checks below explain what stopped this run.</p>')
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
<style>body{{font:16px system-ui;max-width:900px;margin:48px auto;padding:24px;color:#183c32}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}li{{margin-bottom:12px}}details{{border-top:1px solid #ddd;padding:14px 0}}summary{{cursor:pointer;font-weight:700}}@media print{{button{{display:none}}details{{display:block}}details>*{{display:block!important}}}}</style>
<style>.recipe-options{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px}}.recipe-option{{padding:16px;border:1px solid #ddd;border-radius:16px;overflow-wrap:anywhere;break-inside:avoid}}@media print{{.recipe-options{{display:block}}.recipe-option{{margin-bottom:16px}}}}</style>
<h1>{escape(interpretation['outcome'])}</h1><p>AlgaMask screening result</p>
<p>Experimental screening only. This does not establish flavour performance, food safety, or approval to make or eat this recipe.</p>
{('<p>Demo result using synthetic fixtures. These numbers are illustrative.</p>' if result.mode == 'mock' else '')}
{summary}<p>These are calculations from ingredient records, not measurements of a finished bar. Unknown does not mean zero.</p>
<details><summary>How these recipes were compared</summary><p>{escape(interpretation['controls'])}</p><table><tr><th>Option</th><th>Concept</th><th>Mass</th><th>Ingredients</th></tr>{rows}</table></details>
<details><summary>Nutrition details</summary>{nutrition}</details>
<details><summary>Sources and what they can tell us</summary>{explanation}
<h2>Retrieved context</h2><p>Context does not establish effective or safe ingredient doses for these formulations.</p><ul>{evidence}</ul></details>
<details><summary>Screening checks</summary>{screening_html}</details>
<details><summary>Full research details</summary><p>{label} • {escape(result.status)} • Run {escape(result.run_id)}</p>{outcome}
<p>{escape(result.request.algae.value)} · {result.request.inclusion_pct:g}% inclusion · {result.request.serving_g:g} g ingredient input</p>
{provenance}<h2>Workflow trace</h2><ol>{trace}</ol>
<h2>{heading}</h2><p>{'No formulations were returned for this run.' if not rows else 'Amounts below retain calculation precision.'}</p>
<h2>Impact comparison</h2><p>{escape(result.impact['explanation'])}</p><p>Estimated protein-density change (%): {number(result.impact.get('nutrition_change_pct'))}. Sensory change: unknown. Panel size: 0.</p>
<h2>Limitations</h2><ul>{limitations}</ul><p>The JSON run record contains the complete six-agent trace and evidence provenance.</p>
<button onclick="document.querySelectorAll('details').forEach(d=>d.open=true);window.print()">Print / save as PDF</button></details></html>"""
