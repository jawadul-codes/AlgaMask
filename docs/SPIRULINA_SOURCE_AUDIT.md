# Spirulina analytical source audit - Step 2

Checked 2026-10-24. This is source verification, not scientific approval or
validation of the project's protein bar. All revised records remain extracted.

## Sources and reproducibility

- Foods 2024, DOI [10.3390/foods13081257](https://doi.org/10.3390/foods13081257).
  Checked methods, Table 1 and Table 3 including footnotes using the
  [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11049305/fullTextXML).
  SHA-256: dbea06ac2e73ddf069d65b62df29fc18ba3bf16d483aaf10312a5d4d76268e87.
- IJMS 2025, DOI [10.3390/ijms26146767](https://doi.org/10.3390/ijms26146767).
  Checked methods section 3.1, Table 2 and static-headspace results using the
  [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12296105/fullTextXML).
  SHA-256: e38b972ffefd6d87ca2985f0e629ecae2e3bd2cde795c3f7cca21d520aef39e3.

XML inspection copies are temporary files under tmp/pdfs/review, not runtime
evidence. Dataset changes contain original summaries, not copied paper passages.

## Findings and corrections

1. Foods methods specify 16 commercial products plus one raw biomass sample.
   Corrected the source, material, six profile evidence notes, nutrition caveat
   and OBS-0001 through OBS-0015 contexts. The group is not all powder.
2. Compared the 15 stored relative-area ranges, sample counts and identification
   levels in OBS-0001 through OBS-0015 with Table 3. They match. Values remain
   percentages of identified VOC peak area per sample, not concentrations.
3. Table 3 aroma descriptors cite references 37/38; they are not direct sensory
   measurements on these samples. Added that limit to the five compound-specific
   RAG claims themselves as well as the accompanying notes.
4. The AEDA study used dried flakes. Manufacturer-reported greenhouse raceway
   cultivation and natural drying are now recorded in MAT-SPI-AEDA. Neither a
   supplier lot nor a project-specific composition is established.
5. Seven Table 2 FD values match OBS-0038/0039/0040/0042/0043/0044/0045:
   2048, 1024, 1024, 128, 16, 32 and 64 respectively. The separate headspace
   methanethiol result in OBS-0041 matches FD at least 32. No FD values changed.
6. Corrected the outdated source note claiming geosmin had no observation row.
   Clarified that absence of 2-methylisoborneol from the table does not establish
   absence from the sample. CHK-AEDA-POTENT is a selected subset, not a complete
   ranking; the co-eluting methylbutanoic acids also have FD 2048 in Table 2.

## Boundaries and next action

These checks cover the two spirulina analytical sources, not all sources or all
chemical identifiers. No measured masking efficacy, safe dose or project-bar
sensory performance follows from these analytical results. Supplier specifications,
qualified review and physical experiments remain pending.

Prepare a matching development RAG index after consolidating the corrections,
then test retrieval and generated reports before switching the active dataset.
Do not describe an extracted review candidate as a scientifically approved release.

## Verification result

Candidate `data/candidates/0.1.0-rc.4` created and independently verified.
Dataset validation: 290 rows across 21 tables, zero errors and zero warnings.
Supplemental extraction validation passes; previous rc.3 integrity also passes.
There are still 23 evidence notes and six study materials. The active rc.1 dataset
and dev.2 index remain unchanged. Structural validity does not grant scientific
approval or production runtime eligibility.
