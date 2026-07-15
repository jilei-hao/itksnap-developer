# OS4LS Supporting Document — Findings & Decisions Summary

**Date:** 2026-07-15 · **Proposal:** ITK-SNAP: Human-in-the-Loop AI Image Segmentation (PI Yushkevich)
**Deadline:** 2026-07-21 (2 pm PDT) · **Track 1** (up to $250K / 2 yr)
**Scope of this doc:** work on the Section-4 **optional upload** (`supporting_document_draft.md` →
`OS4LS_Supporting_Document_ITK-SNAP.docx`). Companions: `manual_work.md` (pre-submission checklist),
`work_plan_draft.md` + `OS4LS_Work_Plan_ITK-SNAP_v6.docx` (the v6 work plan).

---

## Current state

- **`supporting_document_draft.md`** — final draft; renders to **4 pages** (the upload's hard limit).
- **`OS4LS_Supporting_Document_ITK-SNAP.docx`** — regenerated from the markdown by
  `gen_supporting_doc_docx.py`, with 4 figures embedded. It is a Claude render (Calibri, coral headings);
  the markdown is the source of truth, so re-export via the team's own pipeline if a specific template is
  preferred.
- **Structure:** §1 PI biography · §2 maturity/adoption · §3 technical approach & feasibility ·
  §4 team/governance/sustainability · §5 four figures · §6 references. All working notes live in a
  **delete-before-export** HTML-comment block at the end of the markdown (the generator strips it).

## Key findings

1. **Fund requirement (from scanning the instructions).** The optional upload is ≤ 4 pages: PI/co-PI
   **short** biographies + references + figures. **No CV/biosketch is required anywhere in the application**
   — the full CV PDFs are not needed. Paul's CV feeds only two *form* fields: Section-5 "Recent financial
   support" and the Section-1 "previously received CZI EOSS?" question.
2. **Reference docs (per PI instruction, do NOT upload these for model training).** Paul's R01
   (`itksnap-r01-2026.pdf`) is the same project told at full length — the source for the sharpened framing,
   the updated adoption metrics, and the two reused figures. The CZI-2020 submission overview is the layout
   template (modality-screenshot row + downloads/citations charts).
3. **Real adoption data (pulled live, 2026-07-15).** SourceForge annual downloads 2013–2025 total
   **1,012,891** (2025 complete at 167,444; > 1.1M lifetime; roughly doubled since 2020). OpenAlex
   methods-paper citations ≈ **8,047** in range (close to the > 7,800 Scopus figure). Charts, generator, and
   raw JSON are in `supporting_docs/figures/`.

## Key decisions (with rationale)

- **Team — sole PI.** Alison Pouch removed as co-PI (she will not be on the budget) → **Paul is sole PI**.
  Her name remains only in ref 2's author list (FIMH 2025). Paul's bio refreshed from his one-page CV
  (AD Core Center Neuroimaging-Core co-leadership, MICCAI 2012/2013 wins, OSS portfolio).
- **Figures (§5) — table → figures.** Dropped the landscape-comparison **Table 1**; replaced with two
  figures reused from the R01: **Fig 1** UI capabilities (3 modality screenshots) and **Fig 2** interactive
  AI segmentation (nnInteractive placenta, Dice 0.884 out-of-distribution). Kept **Fig 3** human-in-the-loop
  workflow and **Fig 4** system architecture, shown at **full page width** so their text is legible (they
  had been shrunk). The standalone growth-charts figure was **dropped for space** — its numbers remain in
  §2 text; the chart assets are retained in `supporting_docs/figures/`.
- **Benchmark — MM-WHS** (cardiac CT), not ACDC (which is cardiac MRI, off the team's CT/TEE data). Matches
  the v6 work plan.
- **License — GPL-3.0** (corrected an earlier "permissive" error; GPL is copyleft).
- **Governance — deliberately modest (PI call).** States the honest lead-maintainer model (PI reviews and
  merges, anyone contributes via PR), that **no formal governance document exists yet**, and frames
  broadening as a **Goal-3 aim** with a written policy / code of conduct / succession plan (ISC-informed) as
  **"options being considered," not commitments**. Avoided the absolute single-writer claim (repo history
  shows Hao as a second contributor).
- **Synced to the v6 work plan (Paul's feedback).** Removed "greenfield" / "integration-heavy" jargon →
  "extends and connects mature, already-shipping components rather than building from scratch"; reframed
  "institutional cost-share" as "substantial existing foundations."

## Open items (full checklist in `manual_work.md`)

- Remove Alison from the online **Proposal Team** and the **Budget**; decide if she stays as an unfunded
  collaborator (if so, a one-line mention can be added back).
- Create public **GitHub Milestones 4.8 / 4.10** (backs the §2 "published roadmap" claim). *Optional:* a
  short `GOVERNANCE.md`.
- Populate **Section-5 "Recent financial support"** and the **Section-1 CZI-EOSS** answer from Paul's CV.
- Confirm **v6** is the work-plan version uploaded (not v5 / the older filled docx).
- *Optional:* enlarge Fig-4 architecture sub-labels (needs the diagram source, which is not in the repo —
  only the PNG); re-confirm the "~5,000 weekly active installations" metric currency.

## Assets in this folder

| File | Role |
|---|---|
| `supporting_document_draft.md` | Supporting-doc **source** (markdown) |
| `OS4LS_Supporting_Document_ITK-SNAP.docx` | The **upload** (regenerated from the markdown) |
| `gen_supporting_doc_docx.py` | Regenerates the supporting-doc `.docx` from the markdown |
| `manual_work.md` | Pre-submission human checklist |
| `work_plan_draft.md`, `OS4LS_Work_Plan_ITK-SNAP_v6.docx`, `gen_work_plan_docx.js` | v6 work plan + generator |
| `supporting_docs/` | short-bio PDFs, citation files, the two R01 figures (`fig_ui-screenshots.png`, `fig_ai-placenta.png`) |
| `supporting_docs/figures/` | growth charts + generator + raw data; `fig_workflow.png`, `fig_architecture.png` |
| `Full-Application-Instructions_-OS4LS.pdf` | The RFA (scanned to confirm requirements) |
