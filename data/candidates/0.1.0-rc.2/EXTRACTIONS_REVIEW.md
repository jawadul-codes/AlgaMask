# Supplemental extraction review

These records are not normalized runtime data. Resolve the listed limitations before import.

## Source review

### SRC-FOODS-2024-1257

Volatile Profiling of Spirulina Food Supplements

Source: https://doi.org/10.3390/foods13081257

Access: existing_records

Permission note: See existing sources.csv; not re-audited in this pass.

### SRC-IJMS-2025-6767

Deciphering Important Odorants in a Spirulina (Arthrospira platensis) Dietary Supplement by Aroma Extract Dilution Analysis Using Offline and Online Fractionation Approaches

Source: https://doi.org/10.3390/ijms26146767

Access: existing_records

Permission note: See existing sources.csv; not re-audited in this pass.

### SRC-FOODS-2024-2174

The Volatile Composition and the Potential Health Benefits of Different Microalgae Strains

Source: https://doi.org/10.3390/foods13142174

Access: existing_records

Permission note: See existing sources.csv; not re-audited in this pass.

### SRC-BJDV-2021-662

Study of the volatile profile of the microalgal biomass of Chlorella vulgaris

Source: https://ojs.brazilianjournals.com.br/ojs/index.php/BRJD/article/view/30560

Access: existing_records

Permission note: Unconfirmed. PDF DOI and current journal DOI differ; retain existing identity pending reconciliation.

### SRC-FRI-2024-114142

Innovative vs classical methods for drying heterotrophic Chlorella vulgaris: Impact on protein quality and sensory properties

Source: https://pureportal.ilvo.be/en/publications/innovative-vs-classical-methods-for-drying-heterotrophic-chlorell/

Access: abstract

Permission note: CC BY-NC 4.0 reported by IRTA repository. Full text not included.

### SRC-FOODS-2025-1511

Lactic Acid Fermentation of Chlorella vulgaris to Improve the Aroma of New Microalgae-Based Foods: Impact of Composition and Bacterial Growth on the Volatile Fraction

Source: https://doi.org/10.3390/foods14091511

Access: abstract

Permission note: CC BY 4.0 shown on repository PDF first page. Full text not included.

### SRC-FRONTIERS-2025-1534438

Comparative nutrient and sensory analysis of eight different commercial Chlorella powders

Source: https://doi.org/10.3389/frfst.2025.1534438

Access: existing_records

Permission note: See existing sources.csv; not re-audited in this pass.

### SRC-JFS-2018-35546

The Capability of Cinnamon as an Off-Flavor Masking Agent for Spirulina platensis enriched Food Product

Source: https://journal.ugm.ac.id/jfs/article/download/35546/23625

Access: full_text_sections

Permission note: Only factual extractions included; full-text redistribution not assessed.

### SRC-FSN-2025-70154

Sensory Analyses Driven Formulation of Fruit Cereal Bars Enriched With Arthrospira platensis Dried Powder

Source: https://onlinelibrary.wiley.com/doi/full/10.1002/fsn3.70154

Access: full_text_sections

Permission note: Publisher labels Open Access; exact reuse licence not checked. No full text copied.

### SRC-LWT-2022-113955

Nutritional, physical, microbial, and sensory characteristics of gluten-and sugar-free cereal bar enriched with spirulina and flavored with neroli essential oil

Source: https://www.sciencedirect.com/science/article/pii/S0023643822008908

Access: publisher_abstract_snippet

Permission note: Publisher labels Creative Commons; exact variant unconfirmed. Full text not included.

### SRC-FST-2020-06719

Snack bars enriched with Spirulina for schoolchildren nutrition

Source: https://www.scielo.br/j/cta/a/QdmGJF4kWcRXhydHxpWfWnm/?lang=en

Access: full_text_sections

Permission note: Only factual extractions included; full-text redistribution not assessed.

### SRC-ITEPA-2024

Pengaruh Penambahan Spirulina Terhadap Sifat Fisikokimia, Sensoris, dan Aktivitas Antioksidan Snack Bar

Source: https://ojs.unud.ac.id/index.php/itepa/article/view/123629

Access: abstract

Permission note: Unconfirmed. Abstract and cached PDF first page read; methods/tables unavailable in this pass.

### SRC-CJAFS-2024-135

Effect of Spirulina platensis on Textural, Sensory and Some Physicochemical Characteristics in Gluten-free Functional Biscuit Production

Source: https://doi.org/10.36846/cjafs.2024.135

Access: existing_records

Permission note: See existing sources.csv; not re-audited in this pass.

### SRC-PUBCHEM

PubChem

Source: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest

Access: existing_records

Permission note: See existing sources.csv. Individual CID/property provenance remains in compounds.csv.

### SRC-USDA-FDC

USDA FoodData Central

Source: https://fdc.nal.usda.gov/

Access: existing_records

Permission note: See existing sources.csv. Individual FDC IDs remain in ingredient_nutrition.csv.

## Record decisions needed

### EXT-FSN-MATERIAL

Source: SRC-FSN-2025-70154; location: Section 2.1

Type: material; matrix: fruit cereal bar

- Project supplier and lot are unconfirmed.

### EXT-FSN-RECIPE

Source: SRC-FSN-2025-70154; location: Table 1, % in bar column; Section 2.3

Type: recipe; matrix: fruit cereal bar

- Base sums to 100.04 before algae; replacement/renormalization unspecified.

### EXT-FSN-PROCESS

Source: SRC-FSN-2025-70154; location: Section 2.3

Type: process; matrix: fruit cereal bar

- Manufactured mass differs from 30 g nutrition serving.

### EXT-FSN-PANEL

Source: SRC-FSN-2025-70154; location: Sections 2.4.2 and 2.4.2.1

Type: sensory_design; matrix: fruit cereal bar

- Small expert panel; not consumer validation.

### EXT-FSN-SENSORY

Source: SRC-FSN-2025-70154; location: Abstract; Table 4 off-odor/off-flavor columns

Type: finding; matrix: fruit cereal bar

- Cannot isolate citrus efficacy from the complete recipe.

### EXT-FSN-NUTRITION

Source: SRC-FSN-2025-70154; location: Section 2.2; Tables 2A and 2B

Type: quality_issue; matrix: fruit cereal bar

- Resolve unit inconsistency before nutrition import.

### EXT-LUCAS-MATERIAL

Source: SRC-FST-2020-06719; location: Section 2.1, pp.146-147

Type: material; matrix: oat/rice snack bar

- Research biomass; project lot differs.

### EXT-LUCAS-C

Source: SRC-FST-2020-06719; location: Table 1, p.147, C column

Type: recipe; matrix: oat/rice snack bar

- Not the project's date/oat recipe.

### EXT-LUCAS-REPLACEMENT

Source: SRC-FST-2020-06719; location: Table 1; Section 2.2, p.147

Type: formulation_rule; matrix: oat/rice snack bar

- Tested levels, not allowable maxima.

### EXT-LUCAS-PROCESS

Source: SRC-FST-2020-06719; location: Section 2.2, p.147

Type: process; matrix: oat/rice snack bar

- Final mass/yield unspecified.

### EXT-LUCAS-PANEL

Source: SRC-FST-2020-06719; location: Section 2.3 Sensory properties, p.147

Type: sensory_design; matrix: oat/rice snack bar

- Child panel does not represent adult project testers.

### EXT-LUCAS-PROTEIN

Source: SRC-FST-2020-06719; location: Table 2 and footnote, p.148; Section 2.3, p.147

Type: measurement; matrix: oat/rice snack bar

- Do not import as as-sold nutrition.

### EXT-LUCAS-ACCEPTANCE

Source: SRC-FST-2020-06719; location: Abstract; Section 3.5; Figure 3

Type: finding; matrix: oat/rice snack bar

- Non-significance does not establish equivalence.

### EXT-CIN-MATERIAL

Source: SRC-JFS-2018-35546; location: Bahan dan Metode, p.96

Type: material; matrix: cookies/flakes/dried noodles

- Powder cannot substitute directly for oil or extract.

### EXT-CIN-LEVELS

Source: SRC-JFS-2018-35546; location: Metode, p.96

Type: measurement; matrix: cookies/flakes/dried noodles

- No complete recipe quantities; no normalized bar bound.

### EXT-CIN-PANEL

Source: SRC-JFS-2018-35546; location: Uji Hedonik; Analisis Deskripsi Kuantitatif, p.97

Type: sensory_design; matrix: cookies/flakes/dried noodles

- QDA and hedonic panels differ.

### EXT-CIN-SELECTED

Source: SRC-JFS-2018-35546; location: Results discussion, p.100; Abstract, p.95

Type: measurement; matrix: cookies/flakes/dried noodles

- Selection is matrix-specific; not a protein-bar dose recommendation.

### EXT-CIN-RESIDUAL

Source: SRC-JFS-2018-35546; location: Results discussion, p.100, paragraph following Figure 3 discussion; scale p.97

Type: measurement; matrix: cookies/flakes/dried noodles

- Residual aroma persists; no complete masking claim.

### EXT-ITEPA-DESIGN

Source: SRC-ITEPA-2024; location: Abstract, journal page; PDF p.823

Type: study_design; matrix: snack bar

- 15 is experimental-unit count, not panel size.
- Full method/recipe still needed.

### EXT-ITEPA-PROTEIN

Source: SRC-ITEPA-2024; location: Abstract, result for 5% treatment

Type: measurement; matrix: snack bar

- Moisture basis and assay method require full text.

### EXT-ITEPA-SENSORY

Source: SRC-ITEPA-2024; location: Abstract, sensory result

Type: finding; matrix: snack bar

- Panel size and numeric scale unavailable.

### EXT-DRYING-COMPARISON

Source: SRC-FRI-2024-114142; location: Author institution abstract; publisher Highlights

Type: finding; matrix: heterotrophic Chlorella vulgaris biomass

- Processing comparison, not an ingredient masking dose.
- Panel and process settings not extracted.

### EXT-DRYING-DATASET

Source: SRC-FRI-2024-114142; location: Author institution page, Datasets section

Type: dataset_link; matrix: heterotrophic Chlorella vulgaris biomass

- Dataset files not yet downloaded or validated.

### EXT-FERMENTATION-FINDING

Source: SRC-FOODS-2025-1511; location: Abstract, repository PDF first page

Type: finding; matrix: Chlorella vulgaris biomass

- Analytical aroma evidence; no protein-bar efficacy established.
- Strain-specific values and treatment conditions not extracted.

### EXT-NEROLI-DOSE

Source: SRC-LWT-2022-113955; location: Publisher indexed abstract, CB and CBS formulations

Type: measurement; matrix: gluten-and sugar-free cereal bar

- Volume cannot become mass percent without density.
- Full recipe, panel and isolated masking effect not verified.
