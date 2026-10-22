# Traceable dataset records

The [data packet](../data/extractions/day2_sources.json) contains 25 new records
and a register covering all 15 selected sources. Each new record has a stable ID,
source link, exact location, structured finding and limitations. Existing chemistry
and nutrition records are linked rather than duplicated.

## What has been extracted

| Paper | New records | Inspection depth | Main use |
| --- | ---: | --- | --- |
| [Fruit cereal bars, 2025](https://doi.org/10.1002/fsn3.70154) | 6 | Full-text methods and tables | Recipe, process, panel, sensory finding, nutrition issue |
| [Schoolchildren snack bars, 2020](https://doi.org/10.1590/fst.06719) | 7 | Full-text sections; recipe and nutrition tables visually checked | Complete control recipe, replacement rule, processing, protein, panel |
| [Cinnamon, 2018](https://doi.org/10.22146/jfs.35546) | 5 | Full-text methods and results | Ingredient forms, doses, separate sensory panels, residual aroma |
| [ITEPA snack bars](https://doi.org/10.24843/itepa.2024.v13.i04.p11) | 3 | Abstract | Experimental design and provisional results |
| [Chlorella drying, 2024](https://doi.org/10.1016/j.foodres.2024.114142) | 2 | Author institution abstract and dataset listing | Process effects and linked research dataset |
| [Chlorella fermentation, 2025](https://doi.org/10.3390/foods14091511) | 1 | Repository abstract | Processing intervention candidate |
| [Neroli cereal bar, 2022](https://doi.org/10.1016/j.lwt.2022.113955) | 1 | Indexed publisher abstract | Reported dose with original units |

The remaining eight selected sources retain their earlier extractions. Those
rows have not been re-audited against full text in this pass. No paper's full text
is redistributed in this packet.

## Findings that affect implementation

1. **Recipe mass balance needs its own check.** The fruit-bar table totals
   100.04 before adding spirulina. Its replacement rule is unresolved. Keep that
   recipe incomplete. The schoolchildren control totals 100 and specifies equal
   oat replacement for its algae variants.
2. **Nutrition basis matters.** Schoolchildren-study protein is dry-weight data.
   The fruit-bar paper labels macronutrients in mg and derives nutrition from
   USDA. These records must not silently become as-sold laboratory nutrition.
3. **Sensory methods are different.** The papers use expert ratings, child
   liking scores, and separate cinnamon hedonic/QDA panels. Preserve the original
   scales and populations; do not pool their scores.
4. **Ingredient forms are specific.** Cinnamon powder and neroli essential oil
   are different interventions. The neroli dose uses volume per mass, so a mass
   percentage requires density information.
5. **Tested inclusion is not an approved maximum.** All treatment levels remain
   study observations. A study cannot establish a universal screening limit.

## Open items, with affected record IDs

| Record(s) | What remains unresolved | Effect |
| --- | --- | --- |
| EXT-FSN-RECIPE | Algae replacement rule and rounding | Cannot reproduce enriched formula exactly |
| EXT-FSN-NUTRITION | Published unit inconsistency | Do not import normalized nutrition |
| EXT-LUCAS-PROTEIN | Conversion to project as-sold basis | Keep original dry-weight values |
| EXT-CIN-LEVELS | Full recipe denominator and finished yield | Do not turn into a bar dosing bound |
| EXT-ITEPA-* | Full methods/tables, panel size, percentage basis | Abstract-only evidence remains provisional |
| EXT-NEROLI-DOSE | Full recipe, panel, oil density, treatment comparisons | No isolated masking efficacy or mass conversion |
| EXT-DRYING-*, EXT-FERMENTATION-FINDING | Full process-specific data and methods | Processing leads only |
| Existing BJDV source | Old PDF DOI versus current journal DOI | Resolve identity before publication |

The drying paper also links a [research dataset](https://doi.org/10.34810/data1436).
Its files have not been imported; the link is recorded for the next data pass.

## Next project decision

This finishes a first traceable extraction packet, not the full Day 2 data release.
Use it to choose and document the project's B0/A0 recipe and an initial masking
candidate. The studied recipes differ from the current date/oat mock formulation,
so selecting one is a project decision. Resolve relevant open items and review
individual claims before promoting them into the approved dataset and retrieval
index. The app still uses mock data.
