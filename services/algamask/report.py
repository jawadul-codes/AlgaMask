from html import escape

from .schemas import RunResult


def render_report(result: RunResult) -> str:
    rows = "".join(f"<tr><td>{escape(f.id)}</td><td>{escape(f.name)}</td><td>{f.total_g:g} g</td><td>{escape(', '.join(f'{i.ingredient_id}: {i.grams:g} g' for i in f.ingredients))}</td></tr>" for f in result.controls + result.formulations)
    limitations = "".join(f"<li>{escape(text)}</li>" for text in result.limitations)
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>AlgaMask mock report</title><style>body{{font:16px system-ui;max-width:900px;margin:48px auto;padding:24px;color:#183c32}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}@media print{{button{{display:none}}}}</style><h1>AlgaMask concept report</h1><p>MOCK • Assumed for demo • {escape(result.status)}</p><p>Run {escape(result.run_id)}</p><p>{escape(result.request.algae.value)} · {result.request.inclusion_pct:g}% inclusion · {result.request.serving_g:g} g serving</p><table><tr><th>Code</th><th>Concept</th><th>Mass</th><th>Ingredients</th></tr>{rows}</table><h2>Impact comparison</h2><p>{escape(result.impact['explanation'])}</p><p>Nutrition change: unknown. Sensory change: unknown. Panel size: 0.</p><h2>Limitations</h2><ul>{limitations}</ul><p>Export the JSON record for the complete six-agent trace and synthetic evidence.</p><button onclick="window.print()">Print / save as PDF</button></html>"""
