# Methods source audit - Step 2

Checked 2026-10-24. Source verification is complete for the sections below;
scientific approval remains pending. No physical recipe was approved.

## Cinnamon study

[Original PDF](https://journal.ugm.ac.id/jfs/article/download/35546/23625),
DOI 10.22146/jfs.35546. Visually checked printed pp.96-97; selection text p.99.
SHA-256: fb2b01e4b5042c75ed59221f0e3975237ecceee3e059c54f9bdc761e78403804.

Methods identify dried spirulina from PT Trans Pangan Spirulindo and commercial
cinnamon powder. They specify 9.5% spirulina and cinnamon treatments of
0/2.5/5/7.5/10% by weight. The 60-person liking panel is separate from trained
aroma panels of 6/6/5 participants, using a 15 cm scale. Complete recipe masses
and finished yield are not supplied by these sections. No 1% protein-bar dose
is validated. Added a study-specific material record and corrected the evidence
join; quantities remain unsuitable as project screening bounds.

## Snack-bar study

[Original PDF](https://ojs.unud.ac.id/index.php/itepa/article/download/123629/58196),
DOI 10.24843/itepa.2024.v13.i04.p11. Checked methods pp.825-826 and visually
checked Tables 1 and 5 on pp.827 and 832; aroma narrative p.831.
SHA-256: aae5789110e2e3eeffa04187c79c4bcdaa5f87771de8f0370a7f53e8c5c60778.

Table 1 lists an unchanged 100 g base plus algae; its g/100 g heading conflicts
with column totals of 100/102/103/104/105 g. Do not silently normalize treatment
labels into finished-bar percentages. Cleared the unverified normalized min/max
fields while retaining reported treatment labels. Table 5 confirms 20 panelists,
a seven-point scale and identical overall-acceptance significance letters, but
aroma letters differ despite the narrative's no-significant-effect statement.
Revised the evidence note to retain that inconsistency. Added the correct study
material. The landing page reports January 2025 publication for a 2024 issue.

## Dataset actions and boundaries

- New materials: MAT-SPI-CINNAMON and MAT-SPI-ITEPA.
- Revised sources: SRC-JFS-2018-35546 and SRC-ITEPA-2024.
- Revised evidence: CHK-CIN-OTHER-FOODS, CHK-SNACK-RANGE, CHK-BOUND-LIMIT.
- Revised bound: BND-SPI-SNACK-0-5; normalized values are now unknown.
- Revised rows increment record_version; all remain extracted.
- Original supplemental extractions are retained as historical notes. Their earlier
  abstract-only access statements and null panel count are superseded by this audit
  and the revised normalized records; do not treat them as current resolved facts.
- Active rc.1/dev.2 is unchanged. These corrections enter the next candidate;
  they do not reach the app until a matching dataset/index switch is performed.

The source PDFs and renders are temporary inspection copies under tmp/pdfs/review,
not redistributed runtime evidence. Store only original summaries in the dataset.

Next: review the spirulina analytical claims against their original tables, then
prepare the matching development index once review corrections are consolidated.
Supplier documents and qualified review remain separate unresolved inputs.

Verification completed: 290 rows in 21 tables, zero structural errors/warnings;
supplemental packet passes. Candidate `data/candidates/0.1.0-rc.3` created and
verified with 23 evidence notes and six study materials. Previous rc.2 integrity
passes. No source discrepancy was converted into an approved scientific value.
