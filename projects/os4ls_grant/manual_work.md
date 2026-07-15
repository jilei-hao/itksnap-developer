# OS4LS — Manual Work Before Submission

**Deadline:** Full Application due **July 21, 2026, 2 pm PDT / 9 pm UTC** (no extensions).
**Purpose:** the things that must be done by a human (or with a human decision) — capturing screenshots,
GitHub/repo actions, co-PI reconciliation, and final assembly. Software/text edits Claude can do are *not*
listed here (those are already applied to `supporting_document_draft.md`).

Legend: 🔴 blocker · 🟡 high-leverage · 🟢 nice-to-have · ✅ done

---

## 0. Team change — Alison Pouch removed as co-PI 🔴

Alison will not be on the budget, so she is no longer a co-PI. Applied to the supporting doc (§1 is now
PI-only; §4 roster dropped her; her name stays only in ref 2's author list). Cascade elsewhere:

- [ ] 🔴 **Online form → Section 1 "Proposal Team"** — remove Alison Pouch (she was listed as co-PI). Confirm
    the remaining team is PI Yushkevich + key personnel Hao (add any others actually on the grant).
- [ ] 🔴 **Budget** — remove Alison's personnel line and re-balance (this change originated from the budget).
- [ ] 🟡 **Decide her ongoing role** — if she remains an *unfunded collaborator* (she is a real cardiac-imaging
    collaborator and FIMH-2025 co-author, and was Paul's postdoc), tell Claude and a one-line mention can be
    added back under "other supporting documentation." If she is fully off the project, no further action.
- [ ] 🟢 Sanity-check the work plan / Section-3 / Section-4 text for any remaining co-PI-role phrasing (checked
    2026-07-15: only ref-2's author list mentions her, which correctly stays).

---

## A. Figures — DONE ✅ (2026-07-15, per PI feedback)

Table 1 (landscape gap) removed; §5 is now a 4-figure set, all embedded, 4 pages verified.

- [x] ✅ **Fig 1 UI capabilities** (`supporting_docs/fig_ui-screenshots.png`) + **Fig 2 interactive AI**
    (`supporting_docs/fig_ai-placenta.png`) — reuse the R01 figures. This **resolves** the earlier
    "capture fresh 4.6 screenshots" task (you chose to reuse the R01 UI shots instead).
- [x] ✅ **Fig 3 workflow** + **Fig 4 architecture** shown at full page width → text now legible.
- [ ] 🟢 **Architecture (Fig 4) sub-labels are still on the small side.** The PNG is already at max page
    width, so to enlarge them further you'd regenerate the diagram *source* with fewer labels / bigger
    fonts (no source file is in the repo — only the PNG). Optional; current version is readable.
- [ ] 🟢 **Growth-charts figure was dropped** for space (its numbers remain in §2 text).
    `supporting_docs/figures/fig1_growth_charts.png` + generator are retained if you want it back — you'd
    need to cut or shrink another figure to fit ≤4 pages.

---

## B. Repo / GitHub actions (open-source-quality criterion — your softest reviewed lens) 🟡

These make §4's/§2's roadmap claims *literal* and verifiable. Cheap points on the softest criterion.

- [ ] 🟢 (Optional) **Create a `GOVERNANCE.md` / `MAINTAINERS.md`** in the ITK-SNAP repo. §4 no longer claims
    one exists — it honestly states the lead-maintainer model + that no formal doc exists yet + broadening is
    under discussion (a Goal-3 aim). So this is now optional, but a short written policy (who merges, how
    contributions are reviewed, release process; maintainers: Yushkevich + Hao) would further strengthen the
    open-source-quality criterion.
- [ ] 🟡 **Create the public GitHub Milestones `4.8` and `4.10`** in the ITK-SNAP repo, seeded with the
    Goal-1/Goal-2 deliverables, so "published roadmap (GitHub Milestones 4.8/4.10)" in §2 and §4 is literal.
- [ ] 🟢 Confirm the repo has a visible **CODE_OF_CONDUCT** and **contributor/developer guidelines** links
    (Section-3 form fields ask for these; a code of conduct also supports the ISC-style governance claim).

---

## C. Work plan reconciliation ✅ (resolved in v6)

- [x] ✅ **ACDC → MM-WHS — RESOLVED.** The current work plan **`OS4LS_Work_Plan_ITK-SNAP_v6.docx`**
  (2026-07-15) uses **MM-WHS** (+ MSD hippocampus) and names **GPL-3.0**. The stale
  `reference_docs/work-plan-draft_v5_PY.docx` (ACDC) is superseded.
- [ ] 🟢 **Confirm v6 is the version uploaded** as the work-plan PDF — not v5 or the older filled docx.

---

## D. Final assembly of the supporting-document PDF 🔴

Source of truth is `supporting_document_draft.md`. The shipped upload is the `.docx` → PDF.

- [ ] 🔴 **Re-export the `.docx`** from the revised markdown. Fig. 2 (workflow) and Fig. 3 (architecture)
    PNGs are already embedded in the current `OS4LS_Supporting_Document_ITK-SNAP.docx` — reuse them.
- [ ] 🔴 **Insert Fig. 1 (Overview)** at the top of Section 5, above Fig. 2.
- [ ] 🔴 **Delete the entire `PRODUCTION NOTES` comment block** (bottom of the markdown) before exporting —
    it must not appear in the uploaded PDF.
- [ ] 🔴 **Re-check ≤ 4 pages** after inserting Fig. 1. Proxy render says the text + 3 figures fit at 4
    pages, but the margin is thin. If it overflows, trim in this order: (1) shrink Fig. 3 architecture;
    (2) tighten the Section 3 paragraph on grant track record.
- [ ] 🟢 Export all figures at **≥300 dpi**; keep attributions (Fig. 2/3 are "created"; growth charts cite
    SourceForge + OpenAlex in the data JSON).

---

## E. Verification pass 🟢

- [ ] 🟢 **Reference details** — verify DOIs / volume / pages, especially **ref 2** (Hao et al., FIMH 2025:
    confirm volume/pages/DOI once the proceedings are final).
- [ ] 🟢 **Bios** — Paul's bio was refreshed from his one-page CV (2026-07-15); spot-check the wording
    (PICSL + AD Core Center co-leadership, MICCAI challenge wins, open-source portfolio). Alison removed (§0).
- [ ] 🟢 **Metric currency** — the "~5,000 weekly active / top NIH-funded universities" line is softened to
    "as of 2025" ✅; re-confirm only if you want to strengthen it back to a specific claim.
- [ ] 🟢 **git add the new figure assets** — `supporting_docs/figures/` is currently untracked in the
    wrapper repo; commit it if you want the chart + generator under version control.

---

## F. Online form fields sourced from Paul's CV 🟡

No CV is uploaded anywhere (the application has no biosketch/CV slot — confirmed by scanning the
instructions). But two form fields draw on it:

- [ ] 🟡 **Section 5 → "Recent financial support"** (active/recently-completed grants, 2025–2026; duration +
    USD amount + source; ≤1,500 chars). From the CV, qualifying active grants: **P30 AG069474** (2018–2026,
    Neuroimaging Core, Penn ADCC), **R01 AG072979** (2021–2026), **R01 AG056014** (2017–2028). CV gives
    titles/dates but **not dollar amounts** — pull those from records. Emphasize any ITK-SNAP-related support.
- [ ] 🟢 **Section 1 → "Previously received CZI EOSS funding as PI?"** → **Yes** (CZI EOSS2, 2020–2021,
    "Bridging the Gap in Medical Image Analysis and Biomechanics with ITK-SNAP").
- [x] ✅ **Full CV NOT needed** — the only bio requirement is the "short biographies" in the §4 optional upload
    (done). `supporting_docs/{yushkevich_bio.pdf, pouch_bio.pdf}` are not required for the application.

---

## Already handled by Claude (no action needed) ✅

- ✅ Alison Pouch removed as co-PI in the supporting doc (§1 PI-only, §4 roster, retitled heading); Paul's
  bio refreshed from his one-page CV; supporting `.docx` regenerated to match. Cascade to form/budget → §0.
- ✅ Section 2 enriched with recent-growth evidence (downloads doubling since 2020; >300 top-tier-journal
  citations; cross-domain field list); weekly-active claim softened to "as of 2025."
- ✅ Section 3 enriched (deliberate Qt-free-boundary design; R01 EB014346 + CZI EOSS track record;
  nnInteractive placenta preliminary result, Dice 0.884 OOD; ~50–60% AI-assisted-dev acceleration).
- ✅ Section 4 governance filled (open-GitHub dev + PR review + milestone-approved releases → ISC-modeled
  shared governance + succession plan); `[N]` targets filled with Paul's Goal-3 numbers; sustainability
  framed around the three viability risks.
- ✅ Table 1 "Lossless" → "Open-format" (matches the softened work-plan claim).
- ✅ Growth charts (d,e) generated from live SourceForge + OpenAlex data (2013–2025), saved to
  `supporting_docs/figures/`.
- ✅ Scaffolding removed; working notes consolidated into the delete-before-export `PRODUCTION NOTES` block.
