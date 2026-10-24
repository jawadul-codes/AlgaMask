# Step 2 - Scientific evidence preparation and review

Updated: 2026-10-24
Status: first source-verification and normalization pass completed; scientific approval pending.
Scope: five ingredient forms in FIRST_RELEASE_SCOPE.md.

## Findings for the first experiment

Latest analytical review: [SPIRULINA_SOURCE_AUDIT.md](SPIRULINA_SOURCE_AUDIT.md).
The two spirulina studies' stored ranges and FD values match their source tables.
Sample descriptions and descriptor limitations are corrected in review inputs.
Scientific approval remains pending; the active app dataset is unchanged.

Latest methods correction: see [METHODS_SOURCE_AUDIT.md](METHODS_SOURCE_AUDIT.md).
ITEPA full text is now recovered; 20 panelists are confirmed, but its formula totals
and aroma significance reporting conflict. Normalized bound values are cleared.
Cinnamon methods are checked and its study-material mapping is now present in review
inputs. Earlier first-pass descriptions below are historical, superseded where noted.

| Form | Nutrition record / FDC ID | Existing bounds | Allergen relationships | Decision |
| --- | --- | --- | --- | --- |
| IF-SPI-PWD | NUT-SPI-PWD / 170495 | One snack-bar abstract range; mass denominator unresolved | None | Keep as provisional generic estimate; no validated bar bound |
| IF-OAT-DRY | NUT-OAT-DRY / 173904 | None | None | Verify exact purchased form and supplier declaration |
| IF-DATE-DRIED | NUT-DATE-DRIED / 171726 | None | None | Deglet Noor database match requires confirmation; no date-paste substitution |
| IF-COCOA-PWD | NUT-COCOA-PWD / 169593 | None | None | Generic unsweetened powder; no verified masking result in this recipe |
| IF-CINN-PWD | NUT-CINN-PWD / 171320 | None | None | Other-food intervention evidence exists; 1% in this bar remains an assumption |

These counts describe local records, not an assertion that no relevant research exists.
All five nutrition rows are per 100 g and remain extracted, not approved. Supplier
and product-code fields are empty. Missing allergen relationships cannot establish
absence of allergens or cross-contact. All five require actual product specifications.

## Sources checked in this pass

1. [USDA data documentation](https://fdc.nal.usda.gov/data-documentation/)
   and [FAQ](https://fdc.nal.usda.gov/faq/): confirm that SR Legacy is historical
   reference composition, with its final release in April 2018. This supports the
   generic-reference qualification, not each transcribed numeric value. The local
   source archive was absent during the first pass; the follow-up audit below now
   reproduces all five records. The rows' 2019 publication date
   must not be confused with the archive's 2018 release date.
2. [Spirulina profiling paper, PubMed](https://pubmed.ncbi.nlm.nih.gov/38672929/):
   title, DOI, authors and abstract support the study's 17 supplements, 128 VOCs and
   HS-SPME-GC-MS method. This is analytical context, not validation of our ingredient
   lot or cinnamon intervention. Individual Table 3 values were not reverified in
   this pass. Publisher access returned 429; direct PMC opening hit a browser check.
3. [Cinnamon primary paper](https://journal.ugm.ac.id/jfs/article/view/35546):
   checked the journal abstract, author list, DOI and licence footer. It studies
   cookies, flakes and noodles, with a 60-person hedonic panel. Selected cinnamon
   additions differ by matrix. The page displays CC BY-SA 4.0; full text was not
   copied. The full methods and denominator remain pending independent verification.
4. [ITEPA snack-bar page](https://ojs.unud.ac.id/index.php/itepa/article/view/123629):
   returned a database connection failure; the DOI opener also failed. Existing
   abstract-only records are preserved with their unresolved percentage basis and
   panel size. No existing range was promoted into a protein-bar limit.

## Actual dataset change

Normalized supplemental source SRC-JFS-2018-35546 into sources.csv and added
CHK-CIN-OTHER-FOODS to evidence_chunks.csv. The new note records only abstract-backed
findings and explicitly excludes support for the proposed 1% bar setting.

Both rows remain extracted. No reviewer identity or approval was fabricated.
No numeric bounds, nutrient values, or existing record statuses changed.
The source is already in the supplemental packet: normalization does not constitute
discovery of an additional independent study.

The new note intentionally has no related material ID: MAT-SPI-SUPP describes a
different study's supplements. An accurate study-material record must be prepared
from the methods before the note can qualify for species-filtered retrieval.
Do not make an inaccurate material join merely to get a search hit.

The active development app still uses rc.1/dev.2. A new candidate snapshot can contain
the extracted addition, but only a rebuilt matching index can make it searchable.

## Remaining record-level queue

Verification: 288 rows across 21 tables pass structural validation with zero errors
and warnings; the supplemental 15-source/25-record packet passes its validator.
Created and verified immutable candidate `data/candidates/0.1.0-rc.2` with 23 evidence
notes and 11 normalized sources. Verified rc.1 still passes its integrity check.
Both candidates remain ineligible for production. The app/index configuration is
unchanged; rc.2 is a review snapshot, not a RAG deployment.

| Priority | Records | Required work | Closure evidence |
| --- | --- | --- | --- |
| Verified transcription; review pending | Five NUT rows above and SRC-USDA-FDC | All 31 populated values match original USDA archive; supplier fit remains open | See NUTRITION_SOURCE_AUDIT.md and hashed audit artifact |
| 1 | Five IF rows above | Identify supplier, exact product, lot, preparation form and specifications | Supplier documents plus qualified review |
| 1 | All five forms' allergens | Establish documented contains/cross-contact/unknown information | Product-specific declarations; missing is never false |
| 1 | BND-SPI-SNACK-0-5; CHK-SNACK-RANGE; CHK-BOUND-LIMIT | Recover ITEPA full methods, formula and denominator | Exact page/table and reviewer decision |
| 1 | SRC-JFS-2018-35546; EXT-CIN-*; CHK-CIN-OTHER-FOODS | Verify methods, dose basis, study material and actual limitations | Accurate material mapping; reviewed indirect note |
| 2 | CHK-SPI-PROFILE and remaining CHK-SPI-* | Verify each numerical claim against tables, with compound identity checks | Record-by-record supported/correct/reject decisions |
| 2 | CHK-AEDA-*; CHK-GEOSMIN-GAP | Verify original odorant tables, FD basis and identity | Correct study-specific analytical notes |
| 2 | SRC-FSN-2025-70154 / supplemental fruit-bar records | Check recipe sums, nutrition basis, process and licence | Normalized related-matrix evidence if eligible |
| 2 | Proposed B0/A0/A1 quantities | Review process feasibility and supported ingredient bounds | Versioned recipe review; revise scope if needed |

## Human inputs needed to finish the scientific gate

Follow-up completed 2026-10-24: [Nutrition source audit](NUTRITION_SOURCE_AUDIT.md).
Five records checked directly against the original downloaded archive; 31 values
match, four missing ALA fields preserved. Reproducible checker and three negative
checks pass. No record was promoted to approved.

- Exact supplier/product specifications for the five purchased ingredients.
- A qualified reviewer for the scientific decisions and physical experiment.

The earlier user approval is already recorded; asking for it again would not resolve
these missing facts. Engineering can continue source retrieval and corrections while
the team supplies product information. Step 2 remains open until the relevant rows,
dependency records and coverage are verified and approved.
