"""Single source of truth for the AlgaMask dataset schema.
Run `python tools/build_schema.py` to regenerate CSV templates + dictionaries."""

# ---- controlled vocabularies: name -> [(value, description)] ----
ENUMS = {
 "review_status": [("discovered","Source candidate noted; no row data verified"),("extracted","Candidate row created with exact source location"),("verified","Identity, numbers, source match and licence checked"),("approved","Scientific review done; eligible for publication/runtime/index"),("rejected","Reviewed and not usable"),("superseded","Replaced by a newer record/version")],
 "evidence_status": [("database_derived","From a curated database (e.g. PubChem, USDA)"),("literature_derived","Extracted from a peer-reviewed source"),("calculated","Computed by project code from other records"),("ai_predicted","Predicted by a model; never headline evidence"),("assumed_for_demo","Placeholder for demo only"),("experimentally_measured","Original project measurement")],
 "evidence_type": [("direct_same_matrix","Direct sensory/formulation evidence in the same food matrix"),("related_food_matrix","Evidence from a related food matrix"),("analytical_detection","Analytical detection (e.g. GC-MS) only"),("review","Review article evidence"),("in_vitro","In-vitro or receptor evidence; not proof of bar performance"),("database_identity","Identity/property from a database"),("supplier_specification","Supplier spec, label or CoA"),("project_measurement","Original project measurement")],
 "evidence_strength": [("strong","Direct, well-matched evidence"),("moderate","Indirect or partly matched evidence"),("weak","Limited or loosely related evidence"),("hypothesis","Proposed, not demonstrated")],
 "confidence_band": [("high",""),("medium",""),("low","")],
 "support_class": [("direct","Direct evidence for the claim"),("indirect","Indirect evidence"),("hypothesis","Hypothesis only")],
 "relationship_type": [("associated_with","Reported association"),("odor_active","Odor-active compound"),("taste_active","Taste-active compound"),("suppresses","Suppresses a note"),("complements","Complements a note"),("hypothesized","Hypothesized, not demonstrated")],
 "species_material": [("spirulina",""),("chlorella","")],
 "ingredient_form_type": [("powder",""),("extract",""),("oil",""),("paste",""),("isolate",""),("whole",""),("other","")],
 "ingredient_role": [("algae_base","DRAFT - team to confirm role list"),("protein_base",""),("binder",""),("sweetener",""),("masking_agent",""),("flavour_modulator",""),("fat_source",""),("filler",""),("other","")],
 "sensory_modality": [("odor","Orthonasal smell"),("taste","Basic taste"),("flavour_retronasal","Retronasal flavour"),("mouthfeel",""),("aftertaste",""),("appearance","")],
 "observation_type": [("detection","Compound detected, no level"),("relative_abundance","Relative abundance (%)"),("peak_area","Instrument peak area - NOT concentration"),("concentration","Quantified concentration"),("qualitative","Figure/category only; do not invent a number")],
 "bound_type": [("hard_regulatory_max","Safety/regulatory maximum"),("experimental_screening","Experimental screening range")],
 "regulatory_region": [("BD",""),("US",""),("EU",""),("UK",""),("other","Name it in notes")],
 "allergen_relationship": [("contains",""),("may_contain",""),("free_from","Explicit statement that none apply")],
 "nutrition_source_type": [("supplier_label",""),("coa","Certificate of analysis"),("usda_fdc","USDA FoodData Central fallback"),("other_reviewed","")],
 "value_precision": [("label_rounded","Rounded label value"),("laboratory","Lab value"),("database_value","Database value")],
 "identity_verification_status": [("unverified",""),("pubchem_matched","Matched by name/CAS only"),("verified","Reviewer confirmed"),("conflict","Identity conflict; blocks publication")],
 "source_type": [("peer_reviewed",""),("database",""),("supplier_spec",""),("coa",""),("regulatory",""),("project_data",""),("other","")],
 "discovered_via": [("pubchem",""),("europepmc",""),("openalex",""),("crossref",""),("usda_fdc",""),("manual","")],
 "chunk_tag": [("diagnosis","Explains why an off-note arises"),("intervention","Supports a masking/formulation intervention")],
 "formulation_type": [("B0","Baseline without algae"),("A0","Algae, unmasked"),("generated_variant","Engine-generated variant"),("A1","Selected masked formulation")],
 "formulation_status": [("draft",""),("generated",""),("selected",""),("prototyped",""),("superseded","")],
 "unit": [("pct_ww","% w/w"),("g_per_batch",""),("g_per_100g",""),("kcal_per_100g",""),("mg_per_100g",""),("mg_per_kg",""),("ug_per_g",""),("ng_per_g",""),("ppm",""),("ppb",""),("peak_area",""),("relative_percent",""),("rating_1_9",""),("celsius",""),("count",""),("none","")],
 "comparator": [("higher_better",""),("lower_better",""),("none","")],
 "spread_type": [("sd",""),("sem",""),("iqr",""),("range","")],
 "bool": [("true",""),("false","")],
}

COMMON_PROV = [  # appended to each reviewed table
 ("record_version","int","always","", "Increment on each correction; old versions stay reproducible"),
 ("review_status","enum:review_status","always","", "Only 'approved' rows enter runtime tables/index"),
 ("reviewer","str","approved","", "Person who approved"),
 ("reviewed_at","datetime","approved","", "ISO 8601 timestamp of approval"),
 ("source_id","fk:sources.source_id","approved","", "Decisive source for this row"),
 ("source_location","str","approved","", "Exact page/table/figure/section/DB field"),
 ("evidence_status","enum:evidence_status","approved","", "How the value was obtained"),
 ("notes","str","no","", "Reviewer notes, limitations"),
]
def prov_cols(mode):
    if mode == "full": return COMMON_PROV
    if mode == "light":  # no mandatory source (calculated/measured/meta records)
        return [(n,t,("no" if n in ("source_id","source_location") else r),e,d) for n,t,r,e,d in COMMON_PROV]
    if mode == "self": return [c for c in COMMON_PROV if c[0] not in ("source_id","source_location")]
    return []

A, N, AL = "approved", "no", "always"
# column: (name, type, required, enum(unused), description)
def c(n,t,r,d=""): return (n,t,r,"",d)

TABLES = {
"sources": dict(pk="source_id", prov="self", desc="Decisive sources with licence/provenance", cols=[
  c("source_id","id",AL,"Stable ID, e.g. SRC-0001"),c("source_type","enum:source_type",A),c("title","str",A),c("authors","str",N),
  c("year","int",N),c("doi","str",N,"DOI without URL prefix"),c("url","str",N),c("database_name","str",N),
  c("discovered_via","enum:discovered_via",N),c("retrieved_at","date",A),c("licence","str",A,"Licence/redistribution note"),
  c("redistribution_allowed","enum:bool",A),c("full_text_stored","enum:bool",A,"Only true if licence permits"),c("why_it_matters","str",N)]),
"algae_materials": dict(pk="material_id", prov="full", desc="Purchasable algae material/batch (distinct from species)", cols=[
  c("material_id","id",AL),c("species_material","enum:species_material",A),c("species_name","str",A),c("strain","str",N),
  c("material_form","str",A),c("processing","str",A),c("supplier","str",A),c("batch_lot","str",N),
  c("inclusion_default_pct_ww","float",N,"Default inclusion, % w/w"),c("composition_source_id","fk:sources.source_id",N)]),
"compounds": dict(pk="compound_id", prov="full", desc="Chemical identity from PubChem (database provenance only)", cols=[
  c("compound_id","id",AL),c("compound_name","str",AL),c("pubchem_cid","int",A),c("pubchem_smiles","str",A),c("pubchem_inchikey","str",A),
  c("molecular_formula","str",A),c("molecular_weight","float",A),c("xlogp","float",N),c("pubchem_retrieved_at","date",A),
  c("raw_response_path","str",N,"Path under data/raw (ignored by Git)"),c("identity_verification_status","enum:identity_verification_status",AL)]),
"compound_features": dict(pk="feature_id", prov="light", desc="Locally computed RDKit features (separate provenance from PubChem)", cols=[
  c("feature_id","id",AL),c("compound_id","fk:compounds.compound_id",AL),c("rdkit_version","str",A),c("fingerprint_algorithm","str",A),
  c("fingerprint_radius","int",N),c("fingerprint_bits","int",A),c("chirality_included","enum:bool",A),c("standardization_rule","str",A),
  c("descriptor_set","str",N),c("computed_at","datetime",A),c("feature_hash","str",N)]),
"algae_compound_observations": dict(pk="observation_id", prov="full", desc="Reported detection/level of a compound in a material/process", cols=[
  c("observation_id","id",AL),c("material_id","fk:algae_materials.material_id",AL),c("compound_id","fk:compounds.compound_id",AL),
  c("observation_type","enum:observation_type",AL),c("reported_value","float",N,"Leave empty if study gives only a figure/category"),
  c("reported_unit","enum:unit",N,"Required when reported_value is set"),c("measurement_basis","str",N,"Required when reported_value is set (e.g. dry weight)"),
  c("qualitative_value","str",N),c("analytical_method","str",A),c("process_context","str",N)]),
"sensory_descriptors": dict(pk="descriptor_id", prov="full", desc="Controlled sensory vocabulary", cols=[
  c("descriptor_id","id",AL),c("term","str",AL),c("normalized_term","str",A),c("sensory_modality","enum:sensory_modality",A),
  c("category_group","str",A,"One of the 5 required groups (team to define)"),c("synonym_of","fk:sensory_descriptors.descriptor_id",N),c("definition","str",N)]),
"compound_sensory_links": dict(pk="link_id", prov="full", desc="Compound-to-descriptor relationships with evidence class", cols=[
  c("link_id","id",AL),c("compound_id","fk:compounds.compound_id",AL),c("descriptor_id","fk:sensory_descriptors.descriptor_id",AL),
  c("relationship_type","enum:relationship_type",AL),c("evidence_type","enum:evidence_type",A),c("evidence_strength","enum:evidence_strength",A),
  c("confidence_band","enum:confidence_band",A),c("matrix","str",A),c("odor_threshold_value","float",N),c("threshold_unit","enum:unit",N),c("threshold_medium","str",N)]),
"ingredient_forms": dict(pk="ingredient_form_id", prov="full", desc="Non-interchangeable ingredient forms (cocoa powder vs extract etc.)", cols=[
  c("ingredient_form_id","id",AL),c("ingredient_name","str",AL),c("form_type","enum:ingredient_form_type",A),c("ingredient_role","enum:ingredient_role",A),
  c("supplier","str",N),c("product_code","str",N),c("material_id","fk:algae_materials.material_id",N,"Only for algae ingredient forms"),c("description","str",N)]),
"screening_bounds": dict(pk="bound_id", prov="full", desc="One bound per ingredient form, matrix, role, region and source", cols=[
  c("bound_id","id",AL),c("ingredient_form_id","fk:ingredient_forms.ingredient_form_id",AL),c("product_matrix","str",AL),
  c("ingredient_role","enum:ingredient_role",A),c("regulatory_region","enum:regulatory_region",A),c("bound_type","enum:bound_type",AL),
  c("min_pct_ww","float",A,"Normalized % w/w"),c("max_pct_ww","float",A,"Normalized % w/w"),c("reported_value_text","str",A,"Value as in source"),
  c("reported_unit_basis","str",A,"Source unit/basis, e.g. g per batch"),c("evidence_type","enum:evidence_type",A)]),
"allergens": dict(pk="allergen_id", prov="full", desc="Controlled allergen list", cols=[
  c("allergen_id","id",AL),c("allergen_name","str",AL),c("regulatory_list_ref","str",N)]),
"ingredient_allergens": dict(pk="ingredient_allergen_id", prov="full", desc="Allergen relationships per ingredient form", cols=[
  c("ingredient_allergen_id","id",AL),c("ingredient_form_id","fk:ingredient_forms.ingredient_form_id",AL),
  c("allergen_id","fk:allergens.allergen_id",AL),c("relationship","enum:allergen_relationship",AL)]),
"ingredient_nutrition": dict(pk="nutrition_id", prov="full", desc="Per-100 g nutrition; empty = unknown (never 0 for missing)", cols=[
  c("nutrition_id","id",AL),c("ingredient_form_id","fk:ingredient_forms.ingredient_form_id",AL),c("basis","str",A,"e.g. per_100g"),
  c("protein_g","float",N),c("energy_kcal","float",N),c("carbohydrate_g","float",N),c("fat_g","float",N),c("fibre_g","float",N),c("iron_mg","float",N),
  c("omega3_g","float",N,"Only when supported"),c("nutrition_source_type","enum:nutrition_source_type",A),c("value_precision","enum:value_precision",A),
  c("fdc_id","int",N),c("fdc_food_type","str",N),c("fdc_data_release","str",N),c("match_rationale","str",N),c("transformation_record","str",N)]),
"evidence_chunks": dict(pk="chunk_id", prov="full", desc="Reviewer-written evidence notes for retrieval (1-4 sentences)", cols=[
  c("chunk_id","id",AL),c("chunk_tag","enum:chunk_tag",AL),c("claim_summary","str",A,"Reviewer-written note"),c("support_class","enum:support_class",A),
  c("evidence_type","enum:evidence_type",A),c("matrix","str",A),c("related_material_ids","fklist:algae_materials.material_id",N,"semicolon-separated"),
  c("related_compound_ids","fklist:compounds.compound_id",N),c("related_ingredient_form_ids","fklist:ingredient_forms.ingredient_form_id",N),
  c("related_descriptor_ids","fklist:sensory_descriptors.descriptor_id",N),c("verbatim_text","str",N,"Only if licence permits"),
  c("verbatim_permitted","enum:bool",A)]),
"formulations": dict(pk="formulation_id", prov="light", desc="B0, A0, generated variants, selected A1", cols=[
  c("formulation_id","id",AL),c("formulation_code","str",AL),c("formulation_type","enum:formulation_type",AL),
  c("parent_formulation_id","fk:formulations.formulation_id",N),c("formulation_status","enum:formulation_status",AL),c("serving_size_g","float",N),
  c("engine_version","str",N),c("run_id","str",N),c("random_seed","int",N),c("dataset_version","fk:dataset_versions.dataset_version",N),
  c("recipe_json","str",N,"Export/import only; queryable data lives in formulation_ingredients")]),
"formulation_ingredients": dict(pk="row_id", prov="light", desc="Normalized recipe lines", cols=[
  c("row_id","id",AL),c("formulation_id","fk:formulations.formulation_id",AL),c("ingredient_form_id","fk:ingredient_forms.ingredient_form_id",AL),
  c("amount_pct_ww","float",A),c("amount_g_per_batch","float",N),c("ingredient_role","enum:ingredient_role",A),c("bound_id","fk:screening_bounds.bound_id",N)]),
"metric_definitions": dict(pk="metric_id", prov="light", desc="Impact metric formulas and rules", cols=[
  c("metric_id","id",AL),c("metric_name","str",AL),c("formula","str",A),c("unit","enum:unit",A),c("comparator","enum:comparator",A),
  c("precision_decimals","int",N),c("allowed_evidence_statuses","str",A,"semicolon-separated evidence_status values")]),
"prototype_processes": dict(pk="process_id", prov="light", desc="Batch/mixing/storage/serving records for B0/A0/A1", cols=[
  c("process_id","id",AL),c("formulation_id","fk:formulations.formulation_id",AL),c("batch_size_g","float",A),c("mixing_method","str",A),
  c("process_temperature_c","float",N),c("storage_conditions","str",A),c("serving_temperature_c","float",A),c("prepared_at","datetime",N),c("deviations","str",N)]),
"sensory_trials": dict(pk="observation_id", prov="light", desc="One row per panelist-sample observation. Pseudonymous codes only; never overwrite - amend", cols=[
  c("observation_id","id",AL),c("protocol_version","str",AL),c("session_id","str",N),c("panelist_code","str",AL,"Pseudonymous"),
  c("blinding_code","str",AL,"Resolves to formulation only in protected mapping outside repo"),c("sample_order","int",AL),
  c("attribute_descriptor_id","fk:sensory_descriptors.descriptor_id",AL),c("rating_1_9","int",AL),c("scale_anchor_version","str",AL),
  c("serving_temperature_c","float",N),c("preparation_deviation","str",N),c("amends_observation_id","fk:sensory_trials.observation_id",N),c("amendment_reason","str",N)]),
"sensory_summaries": dict(pk="summary_id", prov="light", desc="Calculated trial summaries", cols=[
  c("summary_id","id",AL),c("metric_id","fk:metric_definitions.metric_id",AL),c("formulation_id","fk:formulations.formulation_id",AL),
  c("comparator_formulation_id","fk:formulations.formulation_id",N),c("sample_size","int",AL),c("exclusions_count","int",AL),c("exclusion_reasons","str",N),
  c("mean","float",AL),c("spread","float",AL),c("spread_type","enum:spread_type",AL),c("formula_version","str",AL),c("created_at","datetime",AL)]),
"dataset_versions": dict(pk="dataset_version", prov="none", desc="Published immutable versions", cols=[
  c("dataset_version","id",AL,"Semantic version e.g. 0.1.0"),c("schema_version","str",AL),c("content_hash","str",AL),c("row_counts","str",AL),
  c("reviewer","str",AL),c("published_at","datetime",AL),c("rdkit_version","str",N),c("embedding_model","str",N),c("embedding_revision","str",N),
  c("embedding_dims","int",N),c("faiss_settings","str",N),c("index_hash","str",N),c("validation_report_hash","str",AL),c("code_commit","str",AL),c("release_notes","str",N)]),
"retrieval_evaluations": dict(pk="eval_id", prov="light", desc="Reviewer-authored golden retrieval questions", cols=[
  c("eval_id","id",AL),c("question","str",AL),c("chunk_tag","enum:chunk_tag",A),c("filters","str",N),c("expected_source_ids","str",A,"semicolon-separated"),
  c("expected_chunk_ids","str",N),c("evidence_family","str",A),c("min_rank","int",A),c("reviewer_rationale","str",A)]),
}

def full_cols(t):
    return TABLES[t]["cols"] + prov_cols(TABLES[t]["prov"])
