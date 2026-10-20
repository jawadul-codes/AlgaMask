"""Validate data/reviewed against the schema. Usage: python tools/validate.py [root]
Exit code 1 if any ERROR. Only implements a subset of the plan's gates (see README)."""
import csv, sys, pathlib
from datetime import datetime, date
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema import TABLES, ENUMS, full_cols

root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent.parent
errors, warns = [], []
E = lambda t,r,m: errors.append(f"[{t} row {r}] {m}")
W = lambda t,r,m: warns.append(f"[{t} row {r}] {m}")
enum_vals = {e:{v for v,_ in vs} for e,vs in ENUMS.items()}
CONC_UNITS = {"ug_per_g","ng_per_g","mg_per_kg","ppm","ppb","mg_per_100g","g_per_100g","pct_ww"}

data = {}
for t in TABLES:
    p = root/"data/reviewed"/f"{t}.csv"
    if not p.exists(): errors.append(f"[{t}] missing file"); continue
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        exp = [c[0] for c in full_cols(t)]
        if rd.fieldnames != exp:
            errors.append(f"[{t}] header mismatch. expected {exp}, got {rd.fieldnames}"); continue
        data[t] = list(rd)

pks = {t:{r[TABLES[t]["pk"]] for r in rows} for t,rows in data.items()}
approved = {t:{r[TABLES[t]["pk"]] for r in rows if r["review_status"]=="approved"} if "review_status" in TABLES[t]["cols"][0:0] or any(c[0]=="review_status" for c in full_cols(t)) else pks[t] for t,rows in data.items()}

def check_type(t,i,col,ty,val):
    base = ty.split(":")[0]
    try:
        if base=="int": int(val)
        elif base=="float": float(val)
        elif base=="date": date.fromisoformat(val)
        elif base=="datetime": datetime.fromisoformat(val)
        elif base=="enum":
            if val not in enum_vals[ty.split(":")[1]]: E(t,i,f"{col}='{val}' not in enum {ty.split(':')[1]}")
    except ValueError: E(t,i,f"{col}='{val}' is not a valid {base}")

for t,rows in data.items():
    cols = full_cols(t); seen=set()
    for i,r in enumerate(rows, start=2):
        pk = r[TABLES[t]["pk"]]
        if pk in seen: E(t,i,f"duplicate primary key {pk}")
        seen.add(pk)
        is_app = r.get("review_status")=="approved"
        for n,ty,req,_,_d in cols:
            v = (r[n] or "").strip()
            if req=="always" and not v: E(t,i,f"{n} required"); continue
            if req=="approved" and is_app and not v: E(t,i,f"{n} required for approved rows")
            if not v: continue
            check_type(t,i,n,ty,v)
            if ty.startswith("fk:"):
                tt,cc = ty[3:].split(".")
                if v not in pks.get(tt,set()): E(t,i,f"{n}='{v}' orphan reference to {tt}")
                elif is_app and v not in approved.get(tt,set()): E(t,i,f"approved row references non-approved {tt}:{v}")
            if ty.startswith("fklist:"):
                tt,cc = ty[7:].split(".")
                for x in filter(None,(s.strip() for s in v.split(";"))):
                    if x not in pks.get(tt,set()): E(t,i,f"{n} item '{x}' orphan reference to {tt}")
        # ---- table-specific gates ----
        g = lambda k: (r.get(k) or "").strip()
        if t=="algae_compound_observations":
            if g("reported_value") and (not g("reported_unit") or not g("measurement_basis")):
                E(t,i,"reported_value needs reported_unit and measurement_basis")
            ot,u = g("observation_type"),g("reported_unit")
            if ot=="peak_area" and u and u not in {"peak_area","relative_percent"}: E(t,i,"peak area must not carry a concentration unit")
            if ot=="concentration" and u and u not in CONC_UNITS: E(t,i,"concentration needs a concentration unit")
            if ot=="qualitative" and g("reported_value"): E(t,i,"qualitative observation must not have an invented number")
        if t=="screening_bounds" and g("min_pct_ww") and g("max_pct_ww"):
            try:
                if float(g("min_pct_ww"))>float(g("max_pct_ww")): E(t,i,"min_pct_ww > max_pct_ww")
            except ValueError: pass
        if t=="evidence_chunks" and is_app:
            if g("support_class")=="direct" and g("evidence_type")=="in_vitro": E(t,i,"in-vitro evidence cannot be classed 'direct'")
            if g("verbatim_text") and g("verbatim_permitted")!="true": E(t,i,"verbatim_text stored without permission")
        if t=="sensory_trials":
            try:
                if not 1<=int(g("rating_1_9"))<=9: E(t,i,"rating outside 1-9")
            except ValueError: pass
        if t=="ingredient_nutrition" and is_app:
            for k in ["protein_g","energy_kcal","carbohydrate_g","fat_g","fibre_g","iron_mg"]:
                if not g(k): W(t,i,f"{k} empty (unknown) - result will be 'unknown' where it matters")
        if t=="compounds" and g("identity_verification_status")=="conflict": E(t,i,"identity conflict blocks publication")
        if t=="compounds" and is_app and g("identity_verification_status")!="verified": E(t,i,"approved compound must have identity_verification_status=verified")
        if t=="formulation_ingredients" and is_app:
            f_ = g("ingredient_form_id")
            for tt,label in [("screening_bounds","bound"),("ingredient_nutrition","nutrition"),("ingredient_allergens","allergen")]:
                if not any(x["ingredient_form_id"]==f_ and x["review_status"]=="approved" for x in data.get(tt,[])):
                    E(t,i,f"ingredient {f_} lacks approved {label} coverage")

print(f"{sum(len(v) for v in data.values())} rows in {len(data)} tables")
for m in warns: print("WARN ", m)
for m in errors: print("ERROR", m)
print(f"{len(errors)} error(s), {len(warns)} warning(s)")
sys.exit(1 if errors else 0)
