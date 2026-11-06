# Higher-protein screening

New development runs use `protein-source-grid-v3`, dataset `0.1.0-rc.6` and
index `0.1.0-dev.5`. These are reference-product calculations, not validated
bar recipes, approved doses or confirmed local supplier lots.

## Inputs and selection

`POST /runs/preflight` and `POST /runs` accept optional `protein_source`:

- `auto` (default): all paths, including no powder. Select highest estimated
  protein first. If the other protein path has a passing option, reserve the
  second slot for its highest-ranked option. Fill the third slot by protein.
- `milk`: require USDA beverage whey or the named Myprotein whey.
- `plant`: require the named unflavoured pea–fava blend.

Ties use candidate ID. All choices still respect combined nutrition limits
and exclusions. `passing_ids` lists every passing recipe by protein and ID;
`selected_ids` gives the actual presentation order, which may differ in auto.
Preflight margins describe structurally eligible recipes. Suggested limits
hold the other nutrition targets fixed. No universal protein target is promised.

Example body (both endpoints):

```json
{
  "algae": "chlorella",
  "inclusion_pct": 3,
  "serving_g": 45,
  "flavour": "vanilla",
  "protein_source": "plant",
  "min_protein_g": 12,
  "max_energy_kcal": 200,
  "max_sugar_g": 10
}
```

## Exact grid and controls

Dates 25/30/35% × flavour 1/2/3% × ten powder configurations = 90 options.
The ten configurations are no powder once, plus each of three powders at
10/20/30%. Algae inclusion stays as requested; blend splits algae 50:50;
oats fill the remaining input mass. Cocoa and cinnamon split flavour equally.
The old USDA whey remains a separate product reference at 58.14 g protein
per 100 g. It is never relabelled as the new 86 g product.

The shared generator feeds preflight and execution. Critic independently
checks every returned candidate. B0/A0 controls match the first selected
option: replace flavour and then algae with oats, retaining powder. Controls
do not need to meet candidate nutrition targets. Fixed `spirulina-proof-v1`
amounts stay unchanged and require `protein_source: auto`.

The 30% level is a software search level. Texture, processing, taste and safe
use remain untested. Evidence retrieval does not establish recipe performance.

## Reference labels

Retrieved 2026-11-07; all values below are declared per 100 g.

| Exact reference | Protein | Energy | Total sugar | Ingredient/allergen facts |
| --- | ---: | ---: | ---: | --- |
| [Myprotein Impact Whey Isolate Unflavoured 1 kg AU](https://nz.myprotein.com/p/sports-nutrition/myprotein-impact-whey-isolate-unflavoured-1kg-au-localised/15370280/) | 86 g | 369 kcal | 1.7 g | Whey, sunflower and soy lecithin; contains milk and soy |
| [Myprotein Vegan Protein Blend Unflavoured pea–fava 250 g UK](https://www.myprotein.com/p/sports-nutrition/vegan-protein-blend-250g/12007121/) | 81 g | 340 kcal | 0 g (rounded label) | Pea and fava isolates; facility also handles milk |

Full declared nutrition, ingredient and allergen facts are retained in
`data/extractions/myprotein_labels_2026-11-07.json`; source IDs, dates, URLs,
record IDs and limitations are preserved in the dataset. Product names flow
into result and HTML report ingredient names through the nutrition records.

Ingredient preferences exclude actual declared ingredients: the new whey is
excluded by either milk or soy. The plant product's facility warning is possible
cross-contact, not an intentional milk ingredient. It does not establish
milk-free or soy-free status. All verified-free-from requests still require
supplier verification and remain blocked.

Label sugar zero is not an assumed or measured chemical zero. Dates contribute
sugar to every recipe, so a zero-sugar cap still fails. Raw orange peel sugar
is unknown; citrus with a sugar target remains blocked. Soy isolate stays
disabled because its total-sugar record is unsupported.

## Supported example range

For chlorella 3%, 45 g ingredient input, vanilla, no exclusions or nutrition
limits, v2 supports 4.57866–9.22707 g estimated protein. V3 supports:

- Auto: 4.57866–15.01272 g across 90 options.
- Milk powder required: 6.60321–15.01272 g across 54 options.
- Pea–fava required: 7.63191–14.33772 g across 27 options.

These are computed ranges for that configuration, not promised targets or
measured finished-bar values. Other limits change which recipes can pass.

## Reproducibility

rc.5/dev.4 and all older artifacts remain unchanged. Saved policy v1/v2 runs
retain their generation and ranking rules. Retrying a saved job uses its saved
runtime configuration and search policy; it does not upgrade to the latest
dataset. Missing historical search policy means v1. Default `auto` is omitted
from the submission hash, preserving old idempotency keys. Explicit milk/plant
changes the hash. Mock execution rejects explicit protein choices.

The new index uses the same 23 scientific evidence notes and is bound to the
new dataset hash. Product composition is read from structured label records;
supplier nutrition is not promoted into sensory evidence or scientific approval.

To reproduce the data append in a new staging directory:

```sh
.venv/bin/python tools/extend_protein_dataset.py \
  --output /tmp/new-protein-staging \
  --audit /tmp/new-protein-audit.json
```

The tool verifies the frozen rc.5 hash and refuses to overwrite staging or
audit files. `--sync-working-copy` also checks that working CSV records still
match the base before updating. Published snapshots and indexes are immutable.
