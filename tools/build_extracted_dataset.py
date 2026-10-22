"""Build an extracted, human-review dataset. Nothing is marked approved.

PubChem and USDA values are fetched at runtime and cached under data/raw.
Literature numbers below were transcribed from the cited tables. They stay
review_status=extracted until a person checks them.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from schema import full_cols

ROOT = Path(__file__).resolve().parent.parent
REVIEWED = ROOT / "data" / "reviewed"
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "manifests" / "source_manifest.csv"
RETRIEVED = "2026-10-21"
NOTE = "PENDING HUMAN REVIEW. Not approved. "

COMPOUND_QUERIES = [
    ("CMP-HEXANAL", ["hexanal"]),
    ("CMP-PENTANAL", ["pentanal"]),
    ("CMP-HEPTANAL", ["heptanal"]),
    ("CMP-DECANAL", ["decanal"]),
    ("CMP-BENZAL", ["benzaldehyde"]),
    ("CMP-B-CYCLO", ["beta-cyclocitral", "2,6,6-trimethylcyclohexene-1-carbaldehyde"]),
    ("CMP-SAFRANAL", ["safranal"]),
    ("CMP-B-IONONE", ["beta-ionone"]),
    ("CMP-A-IONONE", ["alpha-ionone"]),
    ("CMP-HEPTADEC", ["heptadecane"]),
    ("CMP-PENTADEC", ["pentadecane"]),
    ("CMP-HEXADEC", ["hexadecane"]),
    ("CMP-NONADEC", ["nonadecane"]),
    ("CMP-OCTENOL", ["1-octen-3-ol"]),
    ("CMP-OCTENONE", ["1-octen-3-one"]),
    ("CMP-OCTEN2OL", ["oct-3-en-2-ol", "3-octen-2-ol"]),
    ("CMP-HEXANOL", ["1-hexanol"]),
    ("CMP-PENTANOL", ["1-pentanol"]),
    ("CMP-HEPTANOL", ["1-heptanol"]),
    ("CMP-OCTANOL", ["1-octanol"]),
    ("CMP-LIMONENE", ["(R)-limonene", "limonene"]),
    ("CMP-DECADIENAL", ["(2E,4E)-2,4-decadienal", "2,4-decadienal"]),
    ("CMP-3MBUTANAL", ["3-methylbutanal"]),
    ("CMP-2MBUTANAL", ["2-methylbutanal"]),
    ("CMP-DMPYRAZ", ["2,5-dimethylpyrazine"]),
    ("CMP-EDMPYRAZ", ["2-ethyl-3,5-dimethylpyrazine"]),
    ("CMP-ACETIC", ["acetic acid"]),
    ("CMP-METHANETHIOL", ["methanethiol"]),
    ("CMP-GEOSMIN", ["geosmin"]),
    ("CMP-MIB", ["2-methylisoborneol"]),
]

FOODS = [
    ("IF-SPI-PWD", [("spirulina dried", "seaweed, spirulina, dried")]),
    ("IF-CHL-PWD", [("chlorella dried", "chlorella"), ("chlorella", "chlorella")]),
    ("IF-OAT-DRY", [("oats regular quick dry", "oats, regular and quick"), ("oats dry", "oats")]),
    ("IF-DATE-DRIED", [("dates deglet noor", "dates, deglet noor")]),
    ("IF-COCOA-PWD", [("cocoa powder unsweetened", "cocoa, dry powder, unsweetened")]),
    ("IF-CINN-PWD", [("cinnamon ground", "spices, cinnamon, ground")]),
    ("IF-VAN-EXT", [("vanilla extract", "vanilla extract")]),
    ("IF-ORANGE-PEEL", [("orange peel raw", "orange peel, raw")]),
    ("IF-WHEY-PWD", [("whey protein powder", "whey protein powder")]),
    ("IF-SOY-ISO", [("soy protein isolate", "soy protein isolate")]),
    ("IF-PEANUT-BUTTER", [("peanut butter smooth", "peanut butter, smooth")]),
    ("IF-ALMOND-BUTTER", [("almond butter", "almond butter")]),
    ("IF-TAHINI", [("sesame butter tahini", "sesame butter, tahini")]),
    ("IF-COCO-OIL", [("coconut oil", "oil, coconut")]),
    ("IF-HONEY", [("honey", "honey")]),
    ("IF-SALT", [("salt table", "salt, table")]),
    ("IF-SUNFLOWER", [("sunflower seed kernels dried", "sunflower seed kernels, dried")]),
    ("IF-MAPLE", [("maple syrup", "syrups, maple")]),
    ("IF-PUMPKIN", [("pumpkin seed kernels dried", "pumpkin and squash seed kernels, dried")]),
]

SR_EXACT = {
    "IF-SPI-PWD": "Seaweed, spirulina, dried",
    "IF-OAT-DRY": "Cereals, oats, regular and quick, not fortified, dry",
    "IF-DATE-DRIED": "Dates, deglet noor",
    "IF-COCOA-PWD": "Cocoa, dry powder, unsweetened",
    "IF-CINN-PWD": "Spices, cinnamon, ground",
    "IF-VAN-EXT": "Vanilla extract",
    "IF-ORANGE-PEEL": "Orange peel, raw",
    "IF-SOY-ISO": "Soy protein isolate",
    "IF-PEANUT-BUTTER": "Peanut butter, smooth style, without salt",
    "IF-ALMOND-BUTTER": "Nuts, almond butter, plain, without salt added",
    "IF-TAHINI": "Seeds, sesame butter, tahini, from roasted and toasted kernels (most common type)",
    "IF-COCO-OIL": "Oil, coconut",
    "IF-HONEY": "Honey",
    "IF-SALT": "Salt, table",
    "IF-SUNFLOWER": "Seeds, sunflower seed kernels, dried",
    "IF-MAPLE": "Syrups, maple",
    "IF-PUMPKIN": "Seeds, pumpkin and squash seed kernels, dried",
    "IF-WHEY-PWD": "Beverages, Whey protein powder isolate",
    "IF-RICE-PUFF": "Cereals ready-to-eat, rice, puffed, fortified",
}

NUTRIENT_IDS = {
    1003: "protein_g",
    1008: "energy_kcal",
    1005: "carbohydrate_g",
    1004: "fat_g",
    1079: "fibre_g",
    1089: "iron_mg",
    1404: "omega3_g",  # PUFA 18:3 n-3 (ALA) only
}


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "AlgaMask-dataset-extract/0.1"})
    delay = 5
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            print(f"429, waiting {delay}s")
            time.sleep(delay)
            delay *= 2


def write_table(name: str, rows: list[dict]) -> None:
    cols = [c[0] for c in full_cols(name)]
    path = REVIEWED / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: "" if row.get(k) is None else row.get(k, "") for k in cols})


def prov(source_id: str, location: str, status: str, notes: str) -> dict:
    return {
        "record_version": "1",
        "review_status": "extracted",
        "reviewer": "",
        "reviewed_at": "",
        "source_id": source_id,
        "source_location": location,
        "evidence_status": status,
        "notes": NOTE + notes,
    }


def fetch_pubchem() -> dict[str, dict]:
    out = {}
    dest = RAW / "pubchem"
    dest.mkdir(parents=True, exist_ok=True)
    props = "Title,MolecularFormula,MolecularWeight,SMILES,ConnectivitySMILES,InChIKey,XLogP"
    for cid_local, names in COMPOUND_QUERIES:
        path = dest / f"{cid_local}.json"
        payload = None
        used = None
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            used = "cache"
        for name in names:
            if payload:
                break
            url = (
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                + urllib.parse.quote(name)
                + f"/property/{props}/JSON"
            )
            try:
                payload = get_json(url)
                used = name
                break
            except Exception as exc:
                print(f"pubchem miss {cid_local} '{name}': {exc}")
                time.sleep(0.3)
        if not payload:
            print(f"FAILED compound {cid_local}")
            continue
        if used != "cache":
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        prop = payload["PropertyTable"]["Properties"][0]
        smiles = prop.get("SMILES") or prop.get("ConnectivitySMILES") or ""
        out[cid_local] = {
            "compound_id": cid_local,
            "compound_name": prop.get("Title") or used,
            "pubchem_cid": str(prop["CID"]),
            "pubchem_smiles": smiles,
            "pubchem_inchikey": prop.get("InChIKey") or "",
            "molecular_formula": prop.get("MolecularFormula") or "",
            "molecular_weight": str(prop.get("MolecularWeight") or ""),
            "xlogp": "" if prop.get("XLogP") is None else str(prop.get("XLogP")),
            "pubchem_retrieved_at": RETRIEVED,
            "raw_response_path": f"data/raw/pubchem/{cid_local}.json",
            "identity_verification_status": "pubchem_matched",
            **prov(
                "SRC-PUBCHEM",
                f"PUG REST compound/name/{used} property JSON; CID {prop['CID']}",
                "database_derived",
                "Name lookup only. Stereochemistry was not checked against the analytical papers. Geosmin and 2-methylisoborneol are included as identities only where no observation row was entered.",
            ),
        }
        print(f"pubchem {cid_local} CID {prop['CID']} via {used}")
        time.sleep(0.25)
    return out


def search_food(query: str) -> list[dict]:
    url = "https://api.nal.usda.gov/fdc/v1/foods/search?" + urllib.parse.urlencode({
        "api_key": "DEMO_KEY",
        "query": query,
        "dataType": "SR Legacy,Foundation",
        "pageSize": 15,
    })
    return get_json(url).get("foods") or []


def food_detail(fdc_id: int) -> dict:
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key=DEMO_KEY"
    return get_json(url)


def pick_nutrients(detail: dict) -> tuple[dict, list[str]]:
    values = {k: "" for k in NUTRIENT_IDS.values()}
    skipped = []
    for row in detail.get("foodNutrients") or []:
        nutrient = row.get("nutrient") or {}
        nid = nutrient.get("id") or row.get("nutrientId")
        if nid not in NUTRIENT_IDS:
            continue
        amount = row.get("amount")
        if amount is None:
            amount = row.get("value")
        deriv = row.get("foodNutrientDerivation") or {}
        code = deriv.get("code") or row.get("derivationCode") or ""
        desc = (deriv.get("description") or row.get("derivationDescription") or "") + " " + code
        if amount is None:
            continue
        points = row.get("dataPoints")
        if "assumed zero" in desc.lower() or code == "Z":
            skipped.append(f"{NUTRIENT_IDS[nid]} assumed-zero left blank")
            continue
        if float(amount) == 0 and not code and points == 0:
            skipped.append(f"{NUTRIENT_IDS[nid]} zero with no derivation and no data points left blank")
            continue
        values[NUTRIENT_IDS[nid]] = format(float(amount), ".10g")
    if values["omega3_g"]:
        skipped.append("omega3_g is FDC nutrient 1404 ALA (18:3 n-3) only, not total omega-3")
    return values, skipped


def materialize_sr_legacy() -> None:
    """Read the local SR Legacy CSV zip. Does not call the rate-limited API."""
    import csv
    import io
    import zipfile

    zip_path = RAW / "usda" / "sr_legacy_2018-04.zip"
    if not zip_path.exists():
        print("SR Legacy zip not present")
        return
    with zipfile.ZipFile(zip_path) as zf:
        def load(name: str) -> list[dict]:
            full = next(item for item in zf.namelist() if item.endswith("/" + name))
            return list(csv.DictReader(io.StringIO(zf.read(full).decode("utf-8"))))

        foods = {row["description"]: row for row in load("food.csv")}
        derivations = {row["id"]: row for row in load("food_nutrient_derivation.csv")}
        nutrient_names = {row["id"]: row for row in load("nutrient.csv")}
        ala = nutrient_names.get("1404", {})
        print(f"nutrient 1404 = {ala.get('name')} {ala.get('unit_name')}")
        wanted = {}
        for form_id, description in SR_EXACT.items():
            food = foods.get(description)
            if not food:
                print(f"SR MISS {form_id} {description}")
                continue
            wanted[food["fdc_id"]] = (form_id, food)
        buckets = {fdc: [] for fdc in wanted}
        nutrient_file = next(item for item in zf.namelist() if item.endswith("/food_nutrient.csv"))
        with zf.open(nutrient_file) as handle:
            for row in csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8")):
                if row["fdc_id"] in buckets and int(row["nutrient_id"]) in NUTRIENT_IDS:
                    buckets[row["fdc_id"]].append(row)
    dest = RAW / "usda"
    for fdc, (form_id, food) in wanted.items():
        items = []
        for row in buckets[fdc]:
            deriv = derivations.get(row["derivation_id"], {})
            nid = int(row["nutrient_id"])
            meta = nutrient_names.get(str(nid), {})
            items.append({
                "nutrient": {"id": nid, "name": meta.get("name", ""), "unitName": meta.get("unit_name", "")},
                "amount": None if row["amount"] == "" else float(row["amount"]),
                "dataPoints": int(row["data_points"]) if row["data_points"] else 0,
                "foodNutrientDerivation": {"code": deriv.get("code", ""), "description": deriv.get("description", "")},
            })
        detail = {
            "fdcId": int(fdc),
            "description": food["description"],
            "dataType": "SR Legacy",
            "publicationDate": food["publication_date"],
            "snapshot": "FoodData_Central_sr_legacy_food_csv_2018-04.zip",
            "foodNutrients": items,
        }
        (dest / f"{form_id}.json").write_text(json.dumps(detail, indent=2), encoding="utf-8")
        print(f"sr {form_id} -> {fdc} {food['description']}")


def fetch_nutrition() -> list[dict]:
    dest = RAW / "usda"
    dest.mkdir(parents=True, exist_ok=True)
    materialize_sr_legacy()
    rows = []
    for form_id, attempts in FOODS:
        cached = RAW / "usda" / f"{form_id}.json"
        chosen = None
        if cached.exists():
            detail = json.loads(cached.read_text(encoding="utf-8"))
            chosen = {"fdcId": detail.get("fdcId"), "description": detail.get("description"), "dataType": detail.get("dataType"), "publishedDate": detail.get("publicationDate")}
        elif os.environ.get("USDA_OFFLINE") == "1":
            print(f"NO USDA MATCH {form_id} (offline)")
            continue
        for query, expect in attempts:
            if chosen:
                break
            try:
                hits = search_food(query)
            except Exception as exc:
                print(f"usda search fail {form_id}: {exc}")
                time.sleep(0.5)
                continue
            for hit in hits:
                if expect in hit.get("description", "").lower() and hit.get("dataType") in {"SR Legacy", "Foundation"}:
                    chosen = hit
                    break
            if chosen:
                break
            print(f"  no '{expect}' in {[h.get('description') for h in hits[:5]]}")
            time.sleep(1.2)
        if not chosen:
            print(f"NO USDA MATCH {form_id}")
            continue
        if not cached.exists():
            detail = chosen
            cached.write_text(json.dumps(chosen, indent=2), encoding="utf-8")
        nutrients, notes = pick_nutrients(detail)
        desc = detail.get("description") or chosen["description"]
        dtype = detail.get("dataType") or chosen.get("dataType")
        published = (detail.get("publicationDate") or detail.get("publishedDate") or "")[:10]
        rows.append({
            "nutrition_id": "NUT-" + form_id.removeprefix("IF-"),
            "ingredient_form_id": form_id,
            "basis": "per_100g",
            **nutrients,
            "nutrition_source_type": "usda_fdc",
            "value_precision": "database_value",
            "fdc_id": str(chosen["fdcId"]),
            "fdc_food_type": dtype,
            "fdc_data_release": published,
            "match_rationale": (
                f"Generic FDC '{desc}' ({dtype}), publication date {published}. "
                + (f"Read from {detail.get('snapshot')}. " if detail.get("snapshot") else "")
                + "Not a supplier label or the prototype lot."
                + (" Dry regular and quick oats are one SR Legacy food, not a single rolled-oat brand." if form_id == "IF-OAT-DRY" else "")
                + (" Dried fruit, not date paste." if form_id == "IF-DATE-DRIED" else "")
                + (" Raw peel, not citrus oil." if form_id == "IF-ORANGE-PEEL" else "")
                + (" Soy protein isolate, not soy flour." if form_id == "IF-SOY-ISO" else "")
                + (" Beverage whey-protein isolate, not sweet dried whey and not a named supplier concentrate." if form_id == "IF-WHEY-PWD" else "")
                + (" Fortified ready-to-eat cereal. Not an unfortified puffed-rice grain." if form_id == "IF-RICE-PUFF" else "")
            ),
            "transformation_record": "",
            **prov(
                "SRC-USDA-FDC",
                (f"{detail.get('snapshot')} " if detail.get("snapshot") else "")
                + f"FDC ID {chosen['fdcId']}; nutrients 1003,1008,1005,1004,1079,1089,1404",
                "database_derived",
                "Assumed-zero FDC derivations were left blank. " + "; ".join(notes),
            ),
        })
        print(f"usda {form_id} -> {chosen['fdcId']} {desc}")
    rows.append({
        "nutrition_id": "NUT-CHL-ALGOMED",
        "ingredient_form_id": "IF-CHL-PWD",
        "basis": "per_100g",
        "protein_g": "40.1",
        "energy_kcal": "",
        "carbohydrate_g": "18.6",
        "fat_g": "6.0",
        "fibre_g": "",
        "iron_mg": "",
        "omega3_g": "",
        "nutrition_source_type": "other_reviewed",
        "value_precision": "laboratory",
        "fdc_id": "",
        "fdc_food_type": "",
        "fdc_data_release": "",
        "match_rationale": "Sample A only: Algomed Chlorella vulgaris, green, phototrophic commercial powder. Not the 2021 culture and not the Gracio biomass.",
        "transformation_record": "Protein is Kjeldahl nitrogen times 4.78. Carbohydrate is HPLC after chemical hydrolysis. Fat is FAME lipid, not a total-fat method. The paper's residual was not entered as fibre.",
        **prov(
            "SRC-FRONTIERS-2025-1534438",
            "Front. Food Sci. Technol. 2025, Table 3, column A. Protein SD 0.3, carbohydrate SD 0.4, lipid SD 0.3.",
            "literature_derived",
            "One commercial powder in an eight-powder comparison. Energy and iron were not in that table.",
        ),
    })
    return rows


def sources() -> list[dict]:
    def src(**kw):
        evidence = kw.pop("evidence_status", "literature_derived")
        notes = kw.pop("notes", "")
        base = {
            "authors": "", "year": "", "doi": "", "url": "", "database_name": "",
            "discovered_via": "manual", "why_it_matters": "",
            "record_version": "1", "review_status": "extracted", "reviewer": "", "reviewed_at": "",
            "evidence_status": evidence, "notes": NOTE + notes,
        }
        base.update(kw)
        return base

    return [
        src(source_id="SRC-PUBCHEM", source_type="database", title="PubChem", authors="NCBI", database_name="PubChem",
            url="https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest", discovered_via="pubchem", retrieved_at=RETRIEVED,
            licence="NCBI PubChem is freely accessible. Cite the CID and retrieval date. Third-party annotations inside PubChem are not copied here.",
            redistribution_allowed="true", full_text_stored="false", evidence_status="database_derived",
            why_it_matters="Chemical identity only. It does not show that a compound occurs in an algae material.",
            notes="Raw property JSON is cached locally under data/raw and is gitignored."),
        src(source_id="SRC-USDA-FDC", source_type="database", title="USDA FoodData Central", authors="U.S. Department of Agriculture",
            database_name="FoodData Central", url="https://fdc.nal.usda.gov/", discovered_via="usda_fdc", retrieved_at=RETRIEVED,
            licence="FoodData Central data are published under CC0. This extract still cites the FDC ID.",
            redistribution_allowed="true", full_text_stored="false", evidence_status="database_derived",
            why_it_matters="Fallback per-100 g nutrition when no supplier label or certificate of analysis exists.",
            notes="Values were read from the April 2018 SR Legacy CSV archive. Branded foods were not used. The API was rate-limited."),
        src(source_id="SRC-FRONTIERS-2025-1534438", source_type="peer_reviewed",
            title="Comparative nutrient and sensory analysis of eight different commercial Chlorella powders",
            year="2025", doi="10.3389/frfst.2025.1534438", url="https://doi.org/10.3389/frfst.2025.1534438",
            retrieved_at=RETRIEVED, licence="Frontiers open-access article. Full text is not stored. Confirm the licence on the article page before redistribution.",
            redistribution_allowed="false", full_text_stored="false",
            why_it_matters="Laboratory composition of one commercial Chlorella vulgaris powder, sample A.",
            notes="Protein uses conversion factor 4.78. Only sample A was entered."),
        src(source_id="SRC-FDA-ALLERGEN", source_type="regulatory", title="FDA food allergen labeling guidance, edition 5, and 2025 FAQ",
            url="https://www.fda.gov/food/food-allergensgluten-free-guidance-documents-regulatory-information/frequently-asked-questions-food-allergen-labeling-guidance-industry",
            retrieved_at=RETRIEVED, year="2025", licence="U.S. government guidance. Public domain.",
            redistribution_allowed="true", full_text_stored="false", evidence_status="literature_derived",
            why_it_matters="Defines the major-allergen list used for contains relationships. It is not a lot analysis.",
            notes="Coconut is not recorded as a tree nut, following the 2025 FAQ statement that coconut was removed from that list."),
        src(source_id="SRC-FOODS-2024-1257", source_type="peer_reviewed",
            title="Volatile Profiling of Spirulina Food Supplements",
            authors="Paraskevopoulou A; Kaloudis T; Hiskia A; Steinhaus M; Dimotikali D; Triantis TM",
            year="2024", doi="10.3390/foods13081257", url="https://doi.org/10.3390/foods13081257",
            retrieved_at=RETRIEVED, licence="CC BY 4.0. Full text is not stored in this repo.",
            redistribution_allowed="true", full_text_stored="false",
            why_it_matters="HS-SPME-GC-MS relative VOC profile of 17 commercial spirulina supplements.",
            notes="Relative abundances are ranges across products, percent of identified VOC area, not concentrations."),
        src(source_id="SRC-IJMS-2025-6767", source_type="peer_reviewed",
            title="Deciphering Important Odorants in a Spirulina (Arthrospira platensis) Dietary Supplement by Aroma Extract Dilution Analysis",
            authors="Paraskevopoulou A; Mall V; Triantis TM; Kaloudis T; Hiskia AE; Dimotikali D; Steinhaus M",
            year="2025", doi="10.3390/ijms26146767", url="https://doi.org/10.3390/ijms26146767",
            retrieved_at=RETRIEVED, licence="MDPI open-access article. Full text is not stored in this repo. Confirm CC BY on the article page before redistribution.",
            redistribution_allowed="false", full_text_stored="false",
            why_it_matters="GC-O/AEDA odorants in one commercial spirulina supplement suspension.",
            notes="FD factors are dilution ranks, not concentrations. Geosmin was not given an observation row."),
        src(source_id="SRC-BJDV-2021-662", source_type="peer_reviewed",
            title="Study of the volatile profile of the microalgal biomass of Chlorella vulgaris",
            authors="de Oliveira AS; Vieira KR; Pinheiro PN; Caetano PA; Wagner R; Jacob-Lopes E; Zepka LQ",
            year="2021", doi="10.34117/bjdv7n5-662",
            url="https://doi.org/10.34117/bjdv7n5-662", retrieved_at=RETRIEVED,
            licence="Open journal PDF. Redistribution rights were not confirmed. Full text is not stored.",
            redistribution_allowed="false", full_text_stored="false",
            why_it_matters="HS-SPME-GC-MS relative areas for a phototrophic Chlorella vulgaris culture.",
            notes="Table 2 is culture biomass, not a dried commercial powder and not a protein bar."),
        src(source_id="SRC-FOODS-2024-2174", source_type="peer_reviewed",
            title="The Volatile Composition and the Potential Health Benefits of Different Microalgae Strains",
            authors="Gracio M; Ferreira JPA; Steinrucken P; Kleinegris DMM; de Sousa IMN; Nunes MC; Raymundo A",
            year="2024", doi="10.3390/foods13142174", url="https://doi.org/10.3390/foods13142174",
            retrieved_at=RETRIEVED, licence="CC BY 4.0. Full text is not stored in this repo.",
            redistribution_allowed="true", full_text_stored="false",
            why_it_matters="Separate GC-MS relative profile for Chlorella vulgaris biomass.",
            notes="Means are percent of normalized TIC peak area. Do not merge with the 2021 culture percentages. The paper's protein figure was not entered because the captured table text was inconsistent."),
        src(source_id="SRC-ITEPA-2024", source_type="peer_reviewed",
            title="Pengaruh Penambahan Spirulina Terhadap Sifat Fisikokimia, Sensoris, dan Aktivitas Antioksidan Snack Bar",
            year="2024", doi="10.24843/itepa.2024.v13.i04.p11", url="https://doi.org/10.24843/itepa.2024.v13.i04.p11",
            retrieved_at=RETRIEVED, licence="Abstract used. Full text was not read. Redistribution not confirmed.",
            redistribution_allowed="false", full_text_stored="false",
            why_it_matters="Snack-bar spirulina addition levels of 0, 2, 3, 4 and 5 percent in the abstract.",
            notes="Abstract only. Whether those percentages are finished-bar % w/w was not confirmed."),
        src(source_id="SRC-CJAFS-2024-135", source_type="peer_reviewed",
            title="Effect of Spirulina platensis on Textural, Sensory and Some Physicochemical Characteristics in Gluten-free Functional Biscuit Production",
            authors="Cakir E", year="2024", doi="10.36846/cjafs.2024.135", url="https://doi.org/10.36846/cjafs.2024.135",
            retrieved_at=RETRIEVED, licence="Journal page reviewed. Redistribution of the full text was not confirmed. Full text is not stored.",
            redistribution_allowed="false", full_text_stored="false",
            why_it_matters="Gluten-free biscuits tested 0, 0.5, 1 and 5 percent spirulina as a share of rice flour, not of the whole formula.",
            notes="Supplier of the spirulina powder in that study was named Aktarix. That lot is not this project's material."),
    ]


def materials() -> list[dict]:
    rows = [
        ("MAT-SPI-SUPP", "spirulina", "Arthrospira / Spirulina, commercial supplements", "dried food-supplement powder",
         "Sixteen retail supplements plus one raw biomass; drying was not the same for every product.",
         "Multiple products bought in Athens, Greece; not one supplier lot", "SRC-FOODS-2024-1257",
         "Foods 2024, 13, 1257, Materials section and Table 1",
         "Group of 17 products. Do not treat a relative-abundance range as one batch."),
        ("MAT-SPI-AEDA", "spirulina", "Arthrospira platensis", "dietary supplement, flakes or powder",
         "Water was added before solvent extraction. Product drying was not fixed in the sections used.",
         "Unnamed commercial dietary supplement", "SRC-IJMS-2025-6767",
         "IJMS 2025, 26, 6767, sample-preparation narrative",
         "One supplement, analyzed as an aqueous suspension. Not a protein bar."),
        ("MAT-CHL-CULT", "chlorella", "Chlorella vulgaris", "phototrophic culture biomass",
         "Phototrophic culture as described in the 2021 methods. Not a dried retail powder.",
         "Laboratory culture, not a purchased lot", "SRC-BJDV-2021-662",
         "Braz. J. Dev. 2021, 7(5), Table 2 and methods",
         "Relative peak areas during cultivation."),
        ("MAT-CHL-BIO", "chlorella", "Chlorella vulgaris", "biomass",
         "Form (fresh culture versus dried powder) was not confirmed from the table caption used.",
         "Not a named prototype lot", "SRC-FOODS-2024-2174",
         "Foods 2024, 13, 2174, Table 3",
         "Separate study from MAT-CHL-CULT. Do not average the two profiles."),
    ]
    out = []
    for mid, species, name, form, processing, supplier, source, loc, notes in rows:
        out.append({
            "material_id": mid, "species_material": species, "species_name": name, "strain": "",
            "material_form": form, "processing": processing, "supplier": supplier, "batch_lot": "",
            "inclusion_default_pct_ww": "", "composition_source_id": source,
            **prov(source, loc, "literature_derived", notes),
        })
    return out


def rel_obs(i, material, compound, low, high, method, loc, source, extra) -> dict:
    return {
        "observation_id": f"OBS-{i:04d}",
        "material_id": material,
        "compound_id": compound,
        "observation_type": "relative_abundance",
        "reported_value": "",
        "reported_unit": "",
        "measurement_basis": "",
        "qualitative_value": f"{low}-{high} percent of identified VOC peak area",
        "analytical_method": method,
        "process_context": "Range across commercial supplements, not one batch and not a concentration.",
        **prov(source, loc, "literature_derived", extra),
    }


def num_obs(i, material, compound, value, method, basis, loc, source, extra, context) -> dict:
    return {
        "observation_id": f"OBS-{i:04d}",
        "material_id": material,
        "compound_id": compound,
        "observation_type": "relative_abundance",
        "reported_value": value,
        "reported_unit": "relative_percent",
        "measurement_basis": basis,
        "qualitative_value": "",
        "analytical_method": method,
        "process_context": context,
        **prov(source, loc, "literature_derived", extra),
    }


def qual_obs(i, material, compound, text, method, loc, source, extra, context) -> dict:
    return {
        "observation_id": f"OBS-{i:04d}",
        "material_id": material,
        "compound_id": compound,
        "observation_type": "qualitative",
        "reported_value": "",
        "reported_unit": "",
        "measurement_basis": "",
        "qualitative_value": text,
        "analytical_method": method,
        "process_context": context,
        **prov(source, loc, "literature_derived", extra),
    }


def observations(have: set[str]) -> list[dict]:
    rows = []
    n = 1
    method_s = "HS-SPME-GC-MS, two columns; relative area of identified VOCs"
    loc_s = "Foods 2024, 13, 1257, Table 3"
    spirulina_ranges = [
        ("CMP-HEPTADEC", "10.5", "48.7", "Level A identification. n=17. Odor word in the table is alkane, which is not treated as an off-note."),
        ("CMP-PENTADEC", "1.3", "17.0", "Level A. n=17."),
        ("CMP-HEXADEC", "0.4", "18.6", "Level B. n=17."),
        ("CMP-B-IONONE", "7.0", "21.1", "Level A. n=17. Table odor word: floral."),
        ("CMP-A-IONONE", "0.6", "1.7", "Level B. n=17. Table odor words: woody, violet."),
        ("CMP-HEXANAL", "1.2", "8.7", "Level A. n=17. Table odor words: green, grassy."),
        ("CMP-B-CYCLO", "1.2", "4.2", "Level A. n=17. Table odor word: minty."),
        ("CMP-SAFRANAL", "0.6", "2.4", "Level D identification, not confirmed with an authentic standard in that table. n=17."),
        ("CMP-BENZAL", "0.02", "1.1", "Level A. n=16. Table odor words: bitter almond-like."),
        ("CMP-OCTENOL", "2.2", "8.6", "Level A. n=17. Table odor word: mushroom-like."),
        ("CMP-HEXANOL", "0.1", "4.3", "Level A. n=16. Table odor words: grassy, marzipan-like."),
        ("CMP-PENTANAL", "0.02", "0.2", "Level D. n=13. Table odor words: green, fatty."),
        ("CMP-PENTANOL", "0.01", "0.2", "Level A. n=9."),
        ("CMP-HEPTANOL", "0.04", "1.5", "Level A. n=13."),
        ("CMP-OCTANOL", "0.2", "0.6", "Level A. n=4."),
    ]
    for compound, low, high, extra in spirulina_ranges:
        if compound not in have:
            continue
        rows.append(rel_obs(n, "MAT-SPI-SUPP", compound, low, high, method_s, loc_s, "SRC-FOODS-2024-1257", extra))
        n += 1

    method_c = "HS-SPME-GC-MS"
    loc_c = "Braz. J. Dev. 2021, 7(5), Table 2"
    basis_c = "percent relative peak area of identified VOCs in the phototrophic culture; not a concentration"
    context_c = "Phototrophic Chlorella vulgaris culture biomass."
    culture = [
        ("CMP-HEXANAL", "20.21", "Main aldehyde in that table. Descriptors in the table: grass, tallow, fat."),
        ("CMP-PENTANAL", "9.11", "Table descriptors: almond, malt, pungent."),
        ("CMP-OCTEN2OL", "9.41", "Table descriptor: mushroom."),
        ("CMP-OCTENOL", "6.63", "Table descriptors: mushroom, fungal, earthy."),
        ("CMP-OCTENONE", "0.39", "Table descriptors: mushroom."),
        ("CMP-B-CYCLO", "0.50", "Table descriptor: mint."),
        ("CMP-LIMONENE", "0.27", "Table descriptors: lemon, orange."),
        ("CMP-A-IONONE", "0.87", "Row is trans-alpha-ionone. Table descriptors: wood, violet. Stereochemistry of the PubChem record may not match."),
        ("CMP-3MBUTANAL", "0.28", "Table descriptors: malt, smell of oil."),
        ("CMP-2MBUTANAL", "0.21", "Table descriptors: cocoa, almond."),
        ("CMP-DECADIENAL", "0.13", "Table descriptor: seaweed. Isomer was not specified in the table."),
        ("CMP-HEXANOL", "1.96", "Row name in the table is Hexanol. Descriptors: gum, flowers, green."),
    ]
    for compound, value, extra in culture:
        if compound not in have:
            continue
        rows.append(num_obs(n, "MAT-CHL-CULT", compound, value, method_c, basis_c, loc_c, "SRC-BJDV-2021-662", extra, context_c))
        n += 1

    method_g = "GC-MS"
    loc_g = "Foods 2024, 13, 2174, Table 3, C. vulgaris column"
    basis_g = "mean percent of normalized TIC peak area, n=3; not a concentration"
    context_g = "Chlorella vulgaris biomass in Gracio et al. SD is in the note, not in reported_value."
    gracio = [
        ("CMP-HEXANAL", "4.40", "SD 0.004 in the captured table."),
        ("CMP-HEPTANAL", "1.76", "SD 0.001."),
        ("CMP-DECANAL", "0.67", "SD 0.003."),
        ("CMP-BENZAL", "1.82", "SD 0.010."),
        ("CMP-B-CYCLO", "0.97", "Row name b-cyclocitral. SD 0.012."),
        ("CMP-A-IONONE", "0.30", "Row name a-ionone. SD 0.000 in the captured table."),
        ("CMP-B-IONONE", "0.49", "SD 0.025."),
        ("CMP-DMPYRAZ", "4.19", "SD 0.474."),
        ("CMP-PENTADEC", "4.92", "SD 0.031."),
        ("CMP-NONADEC", "10.56", "SD 1.041."),
    ]
    for compound, value, extra in gracio:
        if compound not in have:
            continue
        rows.append(num_obs(n, "MAT-CHL-BIO", compound, value, method_g, basis_g, loc_g, "SRC-FOODS-2024-2174", extra, context_g))
        n += 1

    method_a = "GC-O aroma extract dilution analysis, plus static headspace for methanethiol"
    loc_a = "IJMS 2025, 26, 6767, abstract and odorant table"
    context_a = "Aqueous suspension of one commercial spirulina supplement. FD factor is not a concentration."
    aeda = [
        ("CMP-EDMPYRAZ", "FD factor 2048; odor words roasty, earthy, shrimp-like", "Highest FD group in the abstract."),
        ("CMP-B-IONONE", "FD factor 1024; odor words floral, violet-like", "GC-O result, separate from the relative-area range in Foods 2024."),
        ("CMP-ACETIC", "FD factor 1024; odor word vinegar-like", "Acidic fraction."),
        ("CMP-METHANETHIOL", "FD factor at least 32; odor words sulfuric, cabbage-like", "Static headspace dilution, not the solvent-extract AEDA."),
        ("CMP-OCTENONE", "FD factor 128; odor word mushroom", "Odorant 4 in the extracted table."),
        ("CMP-3MBUTANAL", "FD factor 16; odor word malty", "Odorant 1 in the extracted table."),
        ("CMP-2MBUTANAL", "FD factor 32; odor word malty", "Odorant 2 in the extracted table."),
        ("CMP-GEOSMIN", "FD factor 64; odor words musty, earthy, beetroot", "Odorant 22 in Table 2. This is a dilution rank, not a concentration. 2-methylisoborneol is not in that table."),
    ]
    for compound, text, extra in aeda:
        if compound not in have:
            continue
        rows.append(qual_obs(n, "MAT-SPI-AEDA", compound, text, method_a, loc_a, "SRC-IJMS-2025-6767", extra, context_a))
        n += 1
    print(f"observations {len(rows)}")
    return rows


def descriptors() -> list[dict]:
    items = [
        ("DES-EARTHY", "earthy", "earthy", "odor", "earthy_muddy", "Odor word used for geosmin-like and some alcohol notes."),
        ("DES-MUDDY", "muddy", "muddy", "odor", "earthy_muddy", "Product off-note group. No compound row in this extract uses this exact word."),
        ("DES-BEET", "beetroot-like", "beetroot-like", "odor", "earthy_muddy", "Odor word used for geosmin in the AEDA discussion. No geosmin observation was entered."),
        ("DES-MUSHROOM", "mushroom", "mushroom", "odor", "earthy_muddy", "Odor word for 1-octen-3-ol and 1-octen-3-one in the cited tables."),
        ("DES-GRASSY", "grassy", "grassy", "odor", "grassy_green", "Odor word for hexanal in the spirulina supplement table."),
        ("DES-GREEN", "green", "green", "odor", "grassy_green", "Odor word used for several aldehydes and alcohols."),
        ("DES-LEAF", "green-leaf", "green leaf", "odor", "grassy_green", "Leafy green odor. Used only where a table says leaf or green leaf."),
        ("DES-FATTY", "fatty", "fatty", "odor", "fatty", "Odor word including tallow and fat in the chlorella culture table."),
        ("DES-SEAWEED", "seaweed", "seaweed", "odor", "marine_fishy", "Odor word for 2,4-decadienal in the chlorella culture table."),
        ("DES-SHRIMP", "shrimp-like", "shrimp-like", "odor", "marine_fishy", "Odor word for 2-ethyl-3,5-dimethylpyrazine in the AEDA abstract."),
        ("DES-FISHY", "fishy", "fishy", "odor", "marine_fishy", "Product off-note group. The papers used here did not assign this word to a compound row."),
        ("DES-SULFURIC", "sulfuric", "sulfuric", "odor", "sulfurous", "Odor word for methanethiol in the static-headspace result."),
        ("DES-CABBAGE", "cabbage-like", "cabbage-like", "odor", "sulfurous", "Odor word for methanethiol in the static-headspace result."),
        ("DES-BITTER-ALMOND", "bitter-almond", "bitter almond", "odor", "bitter", "Odor word for benzaldehyde in the spirulina table. This is not a measured bitter taste."),
        ("DES-FLORAL", "floral", "floral", "odor", "floral", "Odor word for beta-ionone."),
        ("DES-VIOLET", "violet-like", "violet", "odor", "floral", "Odor word for ionones."),
        ("DES-WOODY", "woody", "woody", "odor", "floral", "Odor word for alpha-ionone in the cited tables."),
        ("DES-MINTY", "minty", "minty", "odor", "grassy_green", "Odor word for beta-cyclocitral in the spirulina table."),
        ("DES-HERB", "herb", "herb", "odor", "grassy_green", "Odor word for safranal in the spirulina table."),
        ("DES-ROASTY", "roasty", "roasty", "odor", "roasted", "Odor word for 2-ethyl-3,5-dimethylpyrazine."),
        ("DES-MALTY", "malty", "malty", "odor", "roasted", "Odor word for methylbutanals."),
        ("DES-SWEATY", "sweaty", "sweaty", "odor", "other", "Odor word for methylbutanoic acids in the AEDA abstract. Those acids are not compound rows in this extract."),
        ("DES-VINEGAR", "vinegar-like", "vinegar", "odor", "sour", "Odor word for acetic acid."),
        ("DES-LEMON", "lemon", "lemon", "odor", "floral", "Odor word for limonene in the chlorella culture table."),
        ("DES-ALMOND", "almond", "almond", "odor", "bitter", "Odor word for pentanal and 2-methylbutanal in the chlorella culture table. Not the tree-nut allergen."),
    ]
    rows = []
    for did, term, norm, modality, group, definition in items:
        source = "SRC-FOODS-2024-1257" if did in {"DES-GRASSY", "DES-MINTY", "DES-BITTER-ALMOND", "DES-FLORAL", "DES-MUSHROOM"} else "SRC-IJMS-2025-6767"
        if did in {"DES-SEAWEED", "DES-LEMON", "DES-ALMOND", "DES-FATTY"}:
            source = "SRC-BJDV-2021-662"
        if did in {"DES-MUDDY", "DES-FISHY", "DES-BEET"}:
            source = "SRC-IJMS-2025-6767"
        rows.append({
            "descriptor_id": did, "term": term, "normalized_term": norm, "sensory_modality": modality,
            "category_group": group, "synonym_of": "", "definition": definition,
            **prov(source, "Odor vocabulary taken from the cited paper's odor words, plus two product group labels with no compound link.",
                   "literature_derived", "category_group is still a draft vocabulary. floral, roasted, fatty, sour and other were kept because the sources use those words."),
        })
    return rows


def links(have: set[str]) -> list[dict]:
    raw = [
        ("CMP-B-IONONE", "DES-FLORAL", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3 odor column", "Odor word attached by the GC-MS paper, not a GC-O result."),
        ("CMP-A-IONONE", "DES-WOODY", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level B identification."),
        ("CMP-A-IONONE", "DES-VIOLET", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level B identification."),
        ("CMP-HEXANAL", "DES-GRASSY", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level A."),
        ("CMP-HEXANAL", "DES-GREEN", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level A."),
        ("CMP-B-CYCLO", "DES-MINTY", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level A."),
        ("CMP-SAFRANAL", "DES-HERB", "associated_with", "analytical_detection", "weak", "low", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Identification level D."),
        ("CMP-BENZAL", "DES-BITTER-ALMOND", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Odor word, not a bitter-taste measurement."),
        ("CMP-OCTENOL", "DES-MUSHROOM", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level A."),
        ("CMP-HEXANOL", "DES-GRASSY", "associated_with", "analytical_detection", "moderate", "medium", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Level A."),
        ("CMP-PENTANAL", "DES-GREEN", "associated_with", "analytical_detection", "weak", "low", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Identification level D."),
        ("CMP-PENTANAL", "DES-FATTY", "associated_with", "analytical_detection", "weak", "low", "commercial spirulina supplements", "SRC-FOODS-2024-1257", "Table 3", "Identification level D."),
        ("CMP-EDMPYRAZ", "DES-ROASTY", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Abstract and odorant 8", "GC-O. Not a protein bar."),
        ("CMP-EDMPYRAZ", "DES-EARTHY", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Abstract", "GC-O. Not a protein bar."),
        ("CMP-EDMPYRAZ", "DES-SHRIMP", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Abstract", "GC-O. Not a protein bar."),
        ("CMP-B-IONONE", "DES-VIOLET", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Abstract, FD 1024", "GC-O. Separate from the relative-area table."),
        ("CMP-B-IONONE", "DES-FLORAL", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Abstract, FD 1024", "GC-O."),
        ("CMP-ACETIC", "DES-VINEGAR", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Abstract, FD 1024", "GC-O."),
        ("CMP-METHANETHIOL", "DES-SULFURIC", "odor_active", "analytical_detection", "moderate", "medium", "headspace above spirulina supplement suspension", "SRC-IJMS-2025-6767", "Static headspace dilution", "FD factor reported as at least 32."),
        ("CMP-METHANETHIOL", "DES-CABBAGE", "odor_active", "analytical_detection", "moderate", "medium", "headspace above spirulina supplement suspension", "SRC-IJMS-2025-6767", "Static headspace dilution", "FD factor reported as at least 32."),
        ("CMP-OCTENONE", "DES-MUSHROOM", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Odorant table, FD 128", "GC-O."),
        ("CMP-3MBUTANAL", "DES-MALTY", "odor_active", "analytical_detection", "moderate", "medium", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Odorant 1, FD 16", "GC-O."),
        ("CMP-2MBUTANAL", "DES-MALTY", "odor_active", "analytical_detection", "moderate", "medium", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Odorant 2, FD 32", "GC-O."),
        ("CMP-GEOSMIN", "DES-EARTHY", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Table 2, odorant 22, FD 64", "GC-O. Not a concentration."),
        ("CMP-GEOSMIN", "DES-BEET", "odor_active", "analytical_detection", "strong", "high", "spirulina supplement aqueous suspension", "SRC-IJMS-2025-6767", "Table 2, odorant 22, FD 64", "GC-O. Not a concentration."),
        ("CMP-HEXANAL", "DES-GRASSY", "associated_with", "analytical_detection", "moderate", "medium", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Library-style descriptor in the table, not GC-O."),
        ("CMP-HEXANAL", "DES-FATTY", "associated_with", "analytical_detection", "moderate", "medium", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Table says tallow, fat."),
        ("CMP-PENTANAL", "DES-ALMOND", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Not a tree-nut allergen statement."),
        ("CMP-PENTANAL", "DES-MALTY", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Library-style descriptor."),
        ("CMP-OCTEN2OL", "DES-MUSHROOM", "associated_with", "analytical_detection", "moderate", "medium", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Relative area 9.41 percent."),
        ("CMP-OCTENOL", "DES-MUSHROOM", "associated_with", "analytical_detection", "moderate", "medium", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Relative area 6.63 percent."),
        ("CMP-OCTENOL", "DES-EARTHY", "associated_with", "analytical_detection", "moderate", "medium", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Table also says fungal, earthy."),
        ("CMP-OCTENONE", "DES-MUSHROOM", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Relative area 0.39 percent."),
        ("CMP-B-CYCLO", "DES-MINTY", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Relative area 0.50 percent."),
        ("CMP-LIMONENE", "DES-LEMON", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Table also says orange."),
        ("CMP-A-IONONE", "DES-WOODY", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2 trans-alpha-ionone", "Stereochemistry may not match the PubChem name lookup."),
        ("CMP-A-IONONE", "DES-VIOLET", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Library-style descriptor."),
        ("CMP-DECADIENAL", "DES-SEAWEED", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Isomer unspecified. Relative area 0.13 percent."),
        ("CMP-3MBUTANAL", "DES-MALTY", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2", "Library-style descriptor."),
        ("CMP-HEXANOL", "DES-GREEN", "associated_with", "analytical_detection", "weak", "low", "Chlorella vulgaris phototrophic culture", "SRC-BJDV-2021-662", "Table 2 Hexanol", "Table also says gum, flowers."),
    ]
    rows = []
    i = 1
    for compound, desc, rel, etype, strength, conf, matrix, source, loc, extra in raw:
        if compound not in have:
            continue
        rows.append({
            "link_id": f"LNK-{i:04d}", "compound_id": compound, "descriptor_id": desc,
            "relationship_type": rel, "evidence_type": etype, "evidence_strength": strength,
            "confidence_band": conf, "matrix": matrix, "odor_threshold_value": "", "threshold_unit": "",
            "threshold_medium": "",
            **prov(source, loc, "literature_derived", extra + " No odor threshold was copied."),
        })
        i += 1
    print(f"links {len(rows)}")
    return rows


def forms() -> list[dict]:
    spec = [
        ("IF-SPI-PWD", "spirulina", "powder", "algae_base", "MAT-SPI-SUPP", "Dried powder. VOC rows are for the cited supplement studies, not a purchased lot."),
        ("IF-CHL-PWD", "chlorella", "powder", "algae_base", "MAT-CHL-BIO", "Dried-powder form is assumed for formulation search. The 2021 observations are a culture, not this powder."),
        ("IF-OAT-DRY", "rolled oats", "whole", "filler", "", "Dry rolled oats. Not a flavoured cereal."),
        ("IF-DATE-DRIED", "dates, dried", "whole", "sweetener", "", "Dried fruit. Not date paste. Do not treat the two forms as interchangeable."),
        ("IF-COCOA-PWD", "cocoa", "powder", "flavour_modulator", "", "Unsweetened dry powder. No masking trial is attached."),
        ("IF-CINN-PWD", "cinnamon", "powder", "flavour_modulator", "", "Ground spice. No masking trial is attached."),
        ("IF-VAN-EXT", "vanilla", "extract", "flavour_modulator", "", "Extract, not vanilla sugar or powder."),
        ("IF-ORANGE-PEEL", "orange peel", "other", "flavour_modulator", "", "Raw peel standing in for a citrus direction. Not citrus oil."),
        ("IF-WHEY-PWD", "whey protein isolate", "isolate", "protein_base", "", "Matched to SR Legacy whey-protein isolate sold as a beverage powder. Not sweet dried whey."),
        ("IF-SOY-ISO", "soy protein isolate", "isolate", "protein_base", "", "Soy protein isolate."),
        ("IF-PEANUT-BUTTER", "peanut butter", "paste", "fat_source", "", "Peanut paste."),
        ("IF-ALMOND-BUTTER", "almond butter", "paste", "fat_source", "", "Almond paste. Tree-nut allergen is almond, not a generic nut."),
        ("IF-TAHINI", "tahini", "paste", "fat_source", "", "Sesame seed paste."),
        ("IF-COCO-OIL", "coconut oil", "oil", "fat_source", "", "Oil. Not recorded as a major tree-nut allergen under the 2025 FDA FAQ used here."),
        ("IF-HONEY", "honey", "other", "sweetener", "", "Honey. Not date paste."),
        ("IF-SALT", "salt", "other", "other", "", "Table salt."),
        ("IF-SUNFLOWER", "sunflower seed", "whole", "fat_source", "", "Dried kernels, not sunflower butter."),
        ("IF-MAPLE", "maple syrup", "other", "sweetener", "", "Syrup."),
        ("IF-PUMPKIN", "pumpkin seed", "whole", "fat_source", "", "Dried kernels."),
        ("IF-RICE-PUFF", "puffed rice, fortified", "whole", "filler", "", "SR Legacy fortified ready-to-eat puffed rice. Not an unfortified grain."),
    ]
    rows = []
    for fid, name, form, role, material, desc in spec:
        rows.append({
            "ingredient_form_id": fid, "ingredient_name": name, "form_type": form, "ingredient_role": role,
            "supplier": "", "product_code": "", "material_id": material, "description": desc,
            **prov("SRC-USDA-FDC" if not material else ("SRC-FOODS-2024-1257" if "SPI" in fid else "SRC-FOODS-2024-2174"),
                   "Form defined for the formulation search. Nutrition, when present, is a separate USDA row.",
                   "literature_derived", desc),
        })
    return rows


def allergens() -> tuple[list[dict], list[dict]]:
    names = [
        ("ALG-MILK", "milk"), ("ALG-EGG", "egg"), ("ALG-FISH", "fish"),
        ("ALG-SHELLFISH", "crustacean shellfish"), ("ALG-TREENUT", "tree nuts"),
        ("ALG-ALMOND", "almond"), ("ALG-PEANUT", "peanut"), ("ALG-WHEAT", "wheat"),
        ("ALG-SOY", "soybean"), ("ALG-SESAME", "sesame"),
    ]
    alist = []
    for aid, name in names:
        alist.append({
            "allergen_id": aid, "allergen_name": name,
            "regulatory_list_ref": "FD&C Act major food allergens; FDA allergen labeling guidance edition 5 and 2025 FAQ",
            **prov("SRC-FDA-ALLERGEN", "FDA FAQ and edition 5 tree-nut interpretation", "literature_derived",
                   "Controlled list only. A row here does not mean a product contains it."),
        })
    pairs = [
        ("IAL-WHEY", "IF-WHEY-PWD", "ALG-MILK"),
        ("IAL-SOY", "IF-SOY-ISO", "ALG-SOY"),
        ("IAL-PEANUT", "IF-PEANUT-BUTTER", "ALG-PEANUT"),
        ("IAL-ALMOND", "IF-ALMOND-BUTTER", "ALG-ALMOND"),
        ("IAL-TAHINI", "IF-TAHINI", "ALG-SESAME"),
    ]
    links_ = []
    for iid, form, allergen in pairs:
        links_.append({
            "ingredient_allergen_id": iid, "ingredient_form_id": form, "allergen_id": allergen, "relationship": "contains",
            **prov("SRC-FDA-ALLERGEN", "Ingredient identity matched to the FDA major-allergen list", "literature_derived",
                   "Contains because the ingredient is that food. Not a laboratory assay and not a free-from claim."),
        })
    return alist, links_


def bounds() -> list[dict]:
    return [{
        "bound_id": "BND-SPI-SNACK-0-5",
        "ingredient_form_id": "IF-SPI-PWD",
        "product_matrix": "snack bar",
        "ingredient_role": "algae_base",
        "regulatory_region": "other",
        "bound_type": "experimental_screening",
        "min_pct_ww": "0",
        "max_pct_ww": "5",
        "reported_value_text": "spirulina addition levels 0%, 2%, 3%, 4% and 5%",
        "reported_unit_basis": "percent addition as stated in the abstract; finished-bar % w/w was not confirmed from the full paper",
        "evidence_type": "related_food_matrix",
        **prov("SRC-ITEPA-2024", "Abstract only", "literature_derived",
               "Indonesia snack-bar study. This is a tested range, not a regulatory maximum. The 5% biscuit figure is a different matrix and is not stored as this bound."),
    }]


def chunks() -> list[dict]:
    spec = [
        ("CHK-SPI-PROFILE", "diagnosis", "direct", "analytical_detection",
         "Seventeen commercial spirulina supplements contained 128 identified VOCs by HS-SPME-GC-MS. The largest classes were alkanes, ketones, aldehydes and alcohols. The figures are relative areas, not concentrations, and they vary by product.",
         "commercial spirulina supplement", "MAT-SPI-SUPP", "", "", "", "SRC-FOODS-2024-1257", "Results and Table 3"),
        ("CHK-SPI-IONONE", "diagnosis", "direct", "analytical_detection",
         "Beta-ionone was reported in all 17 spirulina supplements, at 7.0 to 21.1 percent of identified VOC area, with the odor word floral. That range is not an odor-activity value.",
         "commercial spirulina supplement", "MAT-SPI-SUPP", "CMP-B-IONONE", "", "DES-FLORAL", "SRC-FOODS-2024-1257", "Table 3"),
        ("CHK-SPI-HEXANAL", "diagnosis", "direct", "analytical_detection",
         "Hexanal was reported in all 17 spirulina supplements, at 1.2 to 8.7 percent of identified VOC area, with the odor words green and grassy.",
         "commercial spirulina supplement", "MAT-SPI-SUPP", "CMP-HEXANAL", "", "DES-GRASSY;DES-GREEN", "SRC-FOODS-2024-1257", "Table 3"),
        ("CHK-SPI-CYCLO", "diagnosis", "direct", "analytical_detection",
         "Beta-cyclocitral was reported in all 17 spirulina supplements, at 1.2 to 4.2 percent of identified VOC area, with the odor word minty.",
         "commercial spirulina supplement", "MAT-SPI-SUPP", "CMP-B-CYCLO", "", "DES-MINTY", "SRC-FOODS-2024-1257", "Table 3"),
        ("CHK-SPI-OCTENOL", "diagnosis", "direct", "analytical_detection",
         "1-Octen-3-ol was reported in all 17 spirulina supplements, at 2.2 to 8.6 percent of identified VOC area, with the odor word mushroom-like.",
         "commercial spirulina supplement", "MAT-SPI-SUPP", "CMP-OCTENOL", "", "DES-MUSHROOM", "SRC-FOODS-2024-1257", "Table 3"),
        ("CHK-SPI-HYDROCARBON", "diagnosis", "direct", "analytical_detection",
         "Heptadecane was the most abundant hydrocarbon in the spirulina supplements, at 10.5 to 48.7 percent of identified VOC area. The table's odor word is alkane. A large relative area is not evidence that it drives an off-note.",
         "commercial spirulina supplement", "MAT-SPI-SUPP", "CMP-HEPTADEC", "", "", "SRC-FOODS-2024-1257", "Table 3 and alkanes paragraph"),
        ("CHK-AEDA-POTENT", "diagnosis", "direct", "analytical_detection",
         "GC-O of one spirulina supplement suspension rated 2-ethyl-3,5-dimethylpyrazine at FD 2048 and beta-ionone and acetic acid at FD 1024. These are dilution ranks for that suspension, not concentrations and not a protein-bar result.",
         "spirulina supplement aqueous suspension", "MAT-SPI-AEDA", "CMP-EDMPYRAZ;CMP-B-IONONE;CMP-ACETIC", "", "DES-ROASTY;DES-FLORAL;DES-VINEGAR", "SRC-IJMS-2025-6767", "Abstract"),
        ("CHK-AEDA-THIOL", "diagnosis", "direct", "analytical_detection",
         "Static headspace above the spirulina supplement suspension detected methanethiol, sulfuric and cabbage-like, at an FD factor of at least 32.",
         "headspace above spirulina supplement suspension", "MAT-SPI-AEDA", "CMP-METHANETHIOL", "", "DES-SULFURIC;DES-CABBAGE", "SRC-IJMS-2025-6767", "Static headspace paragraph"),
        ("CHK-GEOSMIN-GAP", "diagnosis", "direct", "analytical_detection",
         "GC-O identified geosmin in the spirulina supplement suspension at FD factor 64, with odor words musty, earthy and beetroot. That factor is not a concentration. 2-methylisoborneol was not in the odorant table.",
         "spirulina supplement aqueous suspension", "MAT-SPI-AEDA", "CMP-GEOSMIN", "", "DES-EARTHY;DES-BEET", "SRC-IJMS-2025-6767", "Table 2, odorant 22"),
        ("CHK-CHL-HEXANAL", "diagnosis", "indirect", "analytical_detection",
         "In a phototrophic Chlorella vulgaris culture, hexanal was 20.21 percent of relative VOC area, with table descriptors grass, tallow and fat. That is not a dried-powder concentration and not a bar result.",
         "Chlorella vulgaris phototrophic culture", "MAT-CHL-CULT", "CMP-HEXANAL", "", "DES-GRASSY;DES-FATTY", "SRC-BJDV-2021-662", "Table 2"),
        ("CHK-CHL-MUSHROOM", "diagnosis", "indirect", "analytical_detection",
         "The same culture table reports oct-3-en-2-ol at 9.41 percent and 1-octen-3-ol at 6.63 percent of relative area, both with a mushroom descriptor.",
         "Chlorella vulgaris phototrophic culture", "MAT-CHL-CULT", "CMP-OCTEN2OL;CMP-OCTENOL", "", "DES-MUSHROOM", "SRC-BJDV-2021-662", "Table 2"),
        ("CHK-CHL-SEAWEED", "diagnosis", "indirect", "analytical_detection",
         "2,4-Decadienal is listed at 0.13 percent of relative area in the chlorella culture, with the descriptor seaweed. The isomer is not specified, so this is a weak association.",
         "Chlorella vulgaris phototrophic culture", "MAT-CHL-CULT", "CMP-DECADIENAL", "", "DES-SEAWEED", "SRC-BJDV-2021-662", "Table 2"),
        ("CHK-CHL-GRACIO", "diagnosis", "indirect", "analytical_detection",
         "A second study reports Chlorella vulgaris volatiles as percent of normalized TIC area, including hexanal at 4.40 percent and beta-ionone at 0.49 percent. Those means must not be averaged with the 2021 culture percentages.",
         "Chlorella vulgaris biomass", "MAT-CHL-BIO", "CMP-HEXANAL;CMP-B-IONONE", "", "", "SRC-FOODS-2024-2174", "Table 3, C. vulgaris column"),
        ("CHK-NOT-A-BAR", "diagnosis", "hypothesis", "review",
         "A detected peak and an odor word in a GC-MS table do not show that the compound causes that note in a protein bar. None of the analytical rows in this extract were measured in the project's oat and date matrix.",
         "protein bar", "MAT-SPI-SUPP;MAT-CHL-CULT", "", "", "", "SRC-FOODS-2024-1257", "Scope of Foods 2024 versus a protein bar"),
        ("CHK-SNACK-RANGE", "intervention", "indirect", "related_food_matrix",
         "A snack-bar abstract reports spirulina addition at 0, 2, 3, 4 and 5 percent, with no significant sensory difference in that study and a slightly-liked score at 5 percent. This is acceptance of a snack bar, not a measured drop in a named off-note.",
         "snack bar", "MAT-SPI-SUPP", "", "IF-SPI-PWD", "", "SRC-ITEPA-2024", "Abstract"),
        ("CHK-BISCUIT-FLOUR", "diagnosis", "indirect", "related_food_matrix",
         "Gluten-free biscuits were made with spirulina at 0, 0.5, 1 and 5 percent of the rice flour. The 0.5 percent flour replacement was most preferred, and higher rates lowered sensory scores. Those percentages are not the share of the whole biscuit.",
         "gluten-free biscuit", "", "", "IF-SPI-PWD", "", "SRC-CJAFS-2024-135", "Abstract and methods: rates of rice flour"),
        ("CHK-NO-MASK", "intervention", "hypothesis", "review",
         "This extract does not contain a trial showing that cocoa, cinnamon, vanilla or citrus reduces a named algae off-note in a protein bar. Those ingredient forms are search-space candidates only.",
         "protein bar", "", "", "IF-COCOA-PWD;IF-CINN-PWD;IF-VAN-EXT;IF-ORANGE-PEEL", "", "SRC-FOODS-2024-1257", "Absence noted against the formulation candidate list"),
        ("CHK-NUTRITION-GAP", "diagnosis", "indirect", "database_identity",
         "USDA spirulina and other ingredient rows are generic FoodData Central foods. They are not the composition of the 17 supplements, the AEDA product, or a chosen supplier lot. An empty nutrient is unknown, not zero.",
         "generic food", "MAT-SPI-SUPP", "", "IF-SPI-PWD", "", "SRC-USDA-FDC", "FDC food records cited on each nutrition row"),
        ("CHK-ALLERGEN-IDENTITY", "diagnosis", "direct", "database_identity",
         "Milk, soy, peanut, almond and sesame contains-links are identity matches to the FDA major-allergen list. They are not assays of a lot. Coconut oil is not linked as a tree nut under the 2025 FAQ used here. No ingredient is marked free-from.",
         "ingredient identity", "", "", "IF-WHEY-PWD;IF-SOY-ISO;IF-PEANUT-BUTTER;IF-ALMOND-BUTTER;IF-TAHINI;IF-COCO-OIL", "", "SRC-FDA-ALLERGEN", "FDA major-allergen list and 2025 coconut FAQ"),
        ("CHK-BOUND-LIMIT", "intervention", "indirect", "related_food_matrix",
         "The stored 0 to 5 percent spirulina bound is the snack-bar abstract's tested range. It is not a safety or regulatory maximum, and it was not confirmed as finished-bar percent weight from the full paper.",
         "snack bar", "", "", "IF-SPI-PWD", "", "SRC-ITEPA-2024", "Abstract"),
        ("CHK-DATE-FORM", "intervention", "hypothesis", "review",
         "The dried-date nutrition row must not be used as date paste. The plan forbids combining nutrients across ingredient forms without an explicit transformation, and none is recorded.",
         "protein bar", "", "", "IF-DATE-DRIED", "", "SRC-USDA-FDC", "Form note on IF-DATE-DRIED"),
        ("CHK-TWO-CHLORELLA", "diagnosis", "indirect", "review",
         "Chlorella observations come from two materials: a 2021 phototrophic culture and a 2024 biomass profile. A formulator should not treat either profile as the sensory identity of an unnamed commercial powder.",
         "Chlorella vulgaris", "MAT-CHL-CULT;MAT-CHL-BIO", "", "IF-CHL-PWD", "", "SRC-BJDV-2021-662", "Table 2 compared with Foods 2024 Table 3"),
    ]
    rows = []
    for cid, tag, support, etype, summary, matrix, materials, compounds, forms_, descs, source, loc in spec:
        rows.append({
            "chunk_id": cid, "chunk_tag": tag, "claim_summary": summary, "support_class": support,
            "evidence_type": etype, "matrix": matrix,
            "related_material_ids": materials, "related_compound_ids": compounds,
            "related_ingredient_form_ids": forms_, "related_descriptor_ids": descs,
            "verbatim_text": "", "verbatim_permitted": "false",
            **prov(source, loc, "literature_derived", "Reviewer-written note. No paper text is stored."),
        })
    return rows


def evaluations() -> list[dict]:
    spec = [
        ("EV-01", "Which volatile classes were reported in commercial spirulina supplements, and were they concentrations?",
         "diagnosis", "CHK-SPI-PROFILE", "SRC-FOODS-2024-1257", "spirulina VOC profile",
         "The chunk must say relative area, not concentration."),
        ("EV-02", "What odorants had the highest FD factors in the spirulina supplement AEDA?",
         "diagnosis", "CHK-AEDA-POTENT", "SRC-IJMS-2025-6767", "spirulina GC-O",
         "FD 2048 pyrazine and FD 1024 ionone and acetic acid."),
        ("EV-03", "What geosmin result does this extract store for the spirulina supplement?",
         "diagnosis", "CHK-GEOSMIN-GAP", "SRC-IJMS-2025-6767", "geosmin FD factor",
         "FD factor 64. Not a concentration, and not 2-methylisoborneol."),
        ("EV-04", "What relative area did the chlorella culture paper report for hexanal?",
         "diagnosis", "CHK-CHL-HEXANAL", "SRC-BJDV-2021-662", "chlorella culture hexanal",
         "20.21 percent relative area, culture biomass."),
        ("EV-05", "Can a GC-MS odor word be used as proof of a protein-bar off-note?",
         "diagnosis", "CHK-NOT-A-BAR", "SRC-FOODS-2024-1257", "matrix limit",
         "No. The analytical rows are not from the project's bar matrix."),
        ("EV-06", "What spirulina addition levels does the snack-bar abstract report?",
         "intervention", "CHK-SNACK-RANGE", "SRC-ITEPA-2024", "snack bar inclusion",
         "0, 2, 3, 4 and 5 percent, abstract only."),
        ("EV-07", "Is there a cocoa, cinnamon, vanilla or citrus masking trial in this extract?",
         "intervention", "CHK-NO-MASK", "SRC-FOODS-2024-1257", "masking gap",
         "No such trial is included."),
        ("EV-08", "Can the USDA spirulina row stand in for a chosen supplement lot?",
         "diagnosis", "CHK-NUTRITION-GAP", "SRC-USDA-FDC", "nutrition provenance",
         "No. It is a generic FDC food."),
    ]
    rows = []
    for eid, question, tag, chunk, source, family, rationale in spec:
        rows.append({
            "eval_id": eid, "question": question, "chunk_tag": tag, "filters": "",
            "expected_source_ids": source, "expected_chunk_ids": chunk, "evidence_family": family,
            "min_rank": "1", "reviewer_rationale": rationale,
            **prov(source, chunk, "literature_derived", "Draft golden question. A person should confirm it before publication."),
        })
    return rows


def metrics() -> list[dict]:
    return [
        {
            "metric_id": "MET-PROT-100KCAL",
            "metric_name": "protein_g_per_100_kcal",
            "formula": "(protein_g per serving / energy_kcal per serving) * 100. Result is unknown if either input is empty or if forms were mixed without a transformation record.",
            "unit": "none",
            "comparator": "higher_better",
            "precision_decimals": "2",
            "allowed_evidence_statuses": "database_derived;experimentally_measured",
            **prov("", "", "calculated", "Definition only. Not computed for a recipe in this extract."),
        },
        {
            "metric_id": "MET-OFFNOTE-DELTA",
            "metric_name": "offnote_rating_change",
            "formula": "mean rating of formulation A minus mean rating of formulation B on the 1-9 scale for one descriptor. Not computed. Requires sensory_summaries.",
            "unit": "rating_1_9",
            "comparator": "lower_better",
            "precision_decimals": "2",
            "allowed_evidence_statuses": "experimentally_measured",
            **prov("", "", "calculated", "No trial observations exist. Do not fill this from GC-MS areas."),
        },
    ]


def manifest(paths: list[Path]) -> None:
    rows = []
    for path in paths:
        data = path.read_bytes()
        rel = path.relative_to(ROOT).as_posix()
        source = "SRC-PUBCHEM" if "pubchem" in rel else "SRC-USDA-FDC"
        origin = "https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest" if source == "SRC-PUBCHEM" else "https://fdc.nal.usda.gov/"
        licence = "PubChem PUG REST property JSON" if source == "SRC-PUBCHEM" else "USDA FoodData Central CC0 food detail"
        rows.append({
            "file_path": rel,
            "source_id": source,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": str(len(data)),
            "retrieved_at": RETRIEVED,
            "licence": licence,
            "origin_url": origin,
            "committed_to_git": "false",
        })
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file_path", "source_id", "sha256", "bytes", "retrieved_at", "licence", "origin_url", "committed_to_git"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def features(compounds: dict[str, dict]) -> list[dict]:
    from datetime import datetime, timezone
    from rdkit import Chem
    from rdkit import rdBase
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

    computed = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    version = rdBase.rdkitVersion
    rows = []
    for index, (cid, compound) in enumerate(compounds.items(), start=1):
        mol = Chem.MolFromSmiles(compound["pubchem_smiles"])
        if mol is None:
            print(f"rdkit fail {cid}")
            continue
        fingerprint = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048, useChirality=True)
        digest = hashlib.sha256(fingerprint.ToBitString().encode()).hexdigest()
        descriptor_set = ";".join([
            f"MolWt={Descriptors.MolWt(mol):.4f}",
            f"TPSA={rdMolDescriptors.CalcTPSA(mol):.4f}",
            f"NumHDonors={rdMolDescriptors.CalcNumHBD(mol)}",
            f"NumHAcceptors={rdMolDescriptors.CalcNumHBA(mol)}",
            f"MolLogP={Descriptors.MolLogP(mol):.4f}",
        ])
        rows.append({
            "feature_id": f"FEA-{index:04d}",
            "compound_id": cid,
            "rdkit_version": version,
            "fingerprint_algorithm": "Morgan",
            "fingerprint_radius": "2",
            "fingerprint_bits": "2048",
            "chirality_included": "true",
            "standardization_rule": "MolFromSmiles on the stored pubchem_smiles; no salt strip, tautomer enumeration, or charge neutralization",
            "descriptor_set": descriptor_set,
            "computed_at": computed,
            "feature_hash": digest,
            **prov("", "", "calculated", "Hash is SHA-256 of the Morgan bit string. Descriptors are local RDKit values, not the PubChem fields."),
        })
    print(f"features {len(rows)}")
    return rows


def demo_formulations() -> tuple[list[dict], list[dict]]:
    """Current software demonstration proportions. Not laboratory recipes."""
    serving = 45.0
    recipes = {
        "FRM-B0": ("B0", "B0", "Baseline bar, no algae", [("IF-COCOA-PWD", 0.9, "flavour_modulator"), ("IF-DATE-DRIED", 13.5, "sweetener"), ("IF-OAT-DRY", 30.6, "filler")]),
        "FRM-A0": ("A0", "A0", "Unmasked blend control", [("IF-SPI-PWD", 1.125, "algae_base"), ("IF-CHL-PWD", 1.125, "algae_base"), ("IF-DATE-DRIED", 13.5, "sweetener"), ("IF-OAT-DRY", 29.25, "filler")]),
        "FRM-A1": ("A1", "generated_variant", "Cocoa concept from the mock engine", [("IF-SPI-PWD", 1.125, "algae_base"), ("IF-CHL-PWD", 1.125, "algae_base"), ("IF-COCOA-PWD", 0.9, "flavour_modulator"), ("IF-DATE-DRIED", 13.5, "sweetener"), ("IF-OAT-DRY", 28.35, "filler")]),
    }
    forms_ = []
    lines = []
    line_no = 1
    for fid, (code, kind, name, items) in recipes.items():
        forms_.append({
            "formulation_id": fid,
            "formulation_code": code,
            "formulation_type": kind,
            "parent_formulation_id": "",
            "formulation_status": "draft",
            "serving_size_g": "45",
            "engine_version": "mock-optimizer-0.1",
            "run_id": "",
            "random_seed": "",
            "dataset_version": "",
            "recipe_json": json.dumps({"name": name}),
            **prov("", "", "assumed_for_demo", "Same arithmetic as the current mock optimizer at 45 g, 5 percent blend. Dried dates stand in for the mock date paste and are not paste. Not a laboratory recipe."),
            "record_version": "2",
        })
        for form_id, grams, role in items:
            lines.append({
                "row_id": f"RLN-{line_no:04d}",
                "formulation_id": fid,
                "ingredient_form_id": form_id,
                "amount_pct_ww": format(grams / serving * 100, ".10g"),
                "amount_g_per_batch": format(grams, ".10g"),
                "ingredient_role": role,
                "bound_id": "",
                **prov("", "", "assumed_for_demo", "Demonstration line. No screening bound is attached."),
            })
            line_no += 1
    return forms_, lines


def main() -> None:
    compounds = fetch_pubchem()
    have = set(compounds)
    nutrition = fetch_nutrition()
    allergen_rows, allergen_links = allergens()
    write_table("sources", sources())
    write_table("algae_materials", materials())
    write_table("compounds", list(compounds.values()))
    write_table("compound_features", features(compounds))
    write_table("algae_compound_observations", observations(have))
    write_table("sensory_descriptors", descriptors())
    write_table("compound_sensory_links", links(have))
    write_table("ingredient_forms", forms())
    write_table("screening_bounds", bounds())
    write_table("allergens", allergen_rows)
    write_table("ingredient_allergens", allergen_links)
    write_table("ingredient_nutrition", nutrition)
    write_table("evidence_chunks", chunks())
    formula_rows, formula_lines = demo_formulations()
    write_table("formulations", formula_rows)
    write_table("formulation_ingredients", formula_lines)
    write_table("metric_definitions", metrics())
    write_table("prototype_processes", [])
    write_table("sensory_trials", [])
    write_table("sensory_summaries", [])
    write_table("dataset_versions", [])
    write_table("retrieval_evaluations", evaluations())
    raw_files = sorted((RAW / "pubchem").glob("*.json")) + sorted((RAW / "usda").glob("*.json"))
    legacy = RAW / "usda" / "sr_legacy_2018-04.zip"
    if legacy.exists():
        raw_files.append(legacy)
    manifest(raw_files)
    print(f"compounds {len(compounds)} nutrition {len(nutrition)} raw files {len(raw_files)}")


if __name__ == "__main__":
    main()
