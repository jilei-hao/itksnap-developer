# Supporting Document — ITK-SNAP: Human-in-the-Loop AI Image Segmentation

## 1. Principal Investigator biography

**Paul A. Yushkevich, PhD — Principal Investigator.** Professor of Radiology at the University of
Pennsylvania (Perelman School of Medicine), in the Penn Image Computing and Science Laboratory (PICSL), and
Co-Leader of the Neuroimaging Core of the Penn Alzheimer's Disease Core Center; PhD in Computer Science,
University of North Carolina at Chapel Hill (2003). He is the creator and lead developer of ITK-SNAP and has
led its development for ~20 years, funded by two NIH R01 grants and a Chan Zuckerberg Initiative EOSS award.
His NIH-funded research develops statistical-shape and biomedical image-analysis methods for Alzheimer's-
disease imaging biomarkers (including hippocampal-subfield segmentation and morphometry) and machine-learning
methods that improve general-purpose segmentation; his teams have won multiple international segmentation
challenges (MICCAI 2012 and 2013), and he maintains a family of widely used open-source imaging tools
(ITK-SNAP, Convert3D, GreedyReg, ASHS).

## 2. Project maturity, adoption, and ecosystem role

ITK-SNAP is among the most established and most-cited tools for 3D/4D biomedical image segmentation, and —
important for this call — its adoption is still **growing**, not merely large:

- **Scientific impact & adoption:** ~20 years of continuous development; **>11,000 citations** of the methods
  paper (incl. *Nature*- and *Science*-family journals); **>1.1 million total downloads**, with **monthly
  downloads roughly doubling since 2020, to >12,000/month**. As of 2025, update analytics indicated **~5,000
  weekly active installations, spanning top NIH-funded US universities.**
- **Recent growth & reach (the criterion reviewers weigh explicitly):** annual downloads and citations have
  climbed steadily year over year (2013–2025 SourceForge/Scopus series on file). More than **300 citations appear in top-tier journals**
  (CiteScore ≥ 20), including *Nature*, *Cell*, *Lancet*, *Nature Medicine*, *Science Translational
  Medicine*, and *Neuron*. ITK-SNAP is cited across Alzheimer's disease and dementia, stroke, epilepsy,
  neuro-oncology, thoracic and pancreatic oncology, cardiology, pulmonology, nephrology, psychiatry,
  neurodevelopment, and systems neuroscience — evidence of broad, cross-domain use in the life sciences.
- **Sustained, open development:** **2,284 non-merge commits** from **~24 individual developers** over the
  project's lifetime — including contributors from **Kitware/ITK** (Dženan Zukić, Matt McCormick, Jared
  Vicory) and **ANTs** (Nicholas Tustison) — with active development continuing through the current
  4.6.0-alpha series and a public roadmap (GitHub Milestones 4.8 / 4.10).
- **Ecosystem role:** built on the ITK/VTK/Qt stack; nnInteractive (CVPR 2025 interactive-segmentation
  challenge winner) is now integrated across napari, MITK, 3D Slicer, and ITK-SNAP, and our itksnap-dls
  server is ITK-SNAP's path into that shared model ecosystem — positioning ITK-SNAP as the human checkpoint
  inside agentic, data-intensive pipelines.

## 3. Technical approach and feasibility

The effort **extends and connects mature, already-shipping components rather than building from scratch**:
it composes ITK-SNAP, itksnap-dls, greedy/Convert3D, and SegFlow4D behind small, well-scoped new interfaces,
validated at each step by ITK-SNAP's existing automated test harness. A key feasibility fact is that **both
technical substrates already exist**:

- **A toolkit-independent, GUI-free logic tier.** ITK-SNAP's core logic already builds free of GUI
  dependencies — proven today by the shipped headless `itksnap-wt` binary. This is by design: when ITK-SNAP
  adopted Qt (2011–2014), the team deliberately separated a toolkit-independent "GUI-model" layer from the
  thin Qt presentation layer, anticipating a future migration. Exposing that logic as a Python/agent-callable
  surface (Aim 1) therefore touches one existing layer rather than requiring a rewrite.
- **A working remote-data transport layer.** ITK-SNAP already loads images and workspaces over Flywheel,
  SSH, and HTTP, with caching; Aim 2 adds a browsable explorer UI and agent API over that transport, plus
  DICOM/BIDS-aware organization.

The genuinely new work is therefore concentrated and independently testable — the Python binding, the
agent-callable review/command surface, the provenance/audit record, the MCP server, and the explorer UI —
with a single larger new subsystem (DICOM-SEG interchange) isolated as a discrete Year-2 deliverable and
validated by round-trip against an external tool (e.g. 3D Slicer). The model-improvement loop (milestone
1.3) relies only on mature techniques — supervised fine-tuning on expert-corrected labels and uncertainty-
based case routing (active learning) — so it depends on no unproven advance; the novel element is the
capture plumbing, which is squarely in the team's competency.

**Track record of delivering on this roadmap.** Prior grants produced major, shipped features on schedule:
NIH R01 EB014346 (2011–2015) funded a complete GUI rewrite and added multi-channel/multi-contrast support,
machine-learning-based semi-automatic segmentation, and built-in deformable registration; a CZI EOSS award
(2020–2021) added 3D+time (4D) visualization and segmentation, free-form image rotation, and loading of
external 3D/4D meshes with associated data such as biomechanical strain maps. ITK-SNAP has also remained
active and viable *between* awards — direct evidence the team can complete a focused two-year effort. As **preliminary evidence that expert-in-the-loop foundation-model segmentation works in
practice**, ITK-SNAP's nnInteractive integration reached a Dice overlap of **0.884 after only four expert
edits** on a 3D fetal-ultrasound placenta case — a domain absent from nnInteractive's training data —
demonstrating out-of-distribution generalization under expert guidance (ref 3). Finally, the team already
uses AI coding assistants day to day and estimates a **50–60% acceleration** on routine and mid-level
development tasks — well matched to this extend-and-connect effort.

## 4. Team, governance, and sustainability

**Governance.** ITK-SNAP is developed fully in the open on GitHub under the GPL-3.0 license — source,
issues, and full history are public, and anyone can contribute through pull requests and issues. In practice
the project follows a lead-maintainer model: the PI, as long-time maintainer, reviews and merges
contributions and manages releases. There is no formal written governance document yet, and how best to
broaden it is under active discussion. Reducing reliance on a single maintainer and moving toward a more
explicit, shared governance structure is an explicit aim of this proposal (Goal 3); options being considered
include a written maintainers policy, a code of conduct, and a succession plan, informed by models such as
the Insight Software Consortium.

**Contributor base and growth.** Development is currently concentrated in a small core team (the PI and lead
developer account for the large majority of commits), within a real ~24-developer lifetime base that
includes ITK/ANTs-ecosystem collaborators. **Broadening the active contributor and maintainer base is an
explicit objective (Goal 3):** developer documentation for the new interfaces plus a hybrid training +
contributor hackathon are designed to lower the barrier to entry, with concrete targets of **≥5 new external
contributors or merged community pull requests**, **≥5 video tutorials (10K+ cumulative views)**, and a
**hybrid event with ≥20 participants**.

**Sustainability beyond the grant.** The work directly addresses the project's three principal long-term
risks: reliance on a single-vendor GUI toolkit (mitigated by moving toward a scriptable, less toolkit-bound
surface), the migration of imaging data into remote/cloud archives (Goal 2), and over-reliance on a small
core of developers (Goal 3 and the governance broadening above). The pip-installable API and MCP server are
lightweight, auto-updatable artifacts published to PyPI, with transparent download metrics; the GUI
continues on ITK-SNAP's established signed-installer channels; and the work builds on substantial existing
foundations — the lead maintainer's established role in the project, mature CI/test infrastructure, and the
codebases it extends. Together with the contributor-growth activities, this maintains the project's
trajectory after the funding period.

## 5. Figures

**Fig. 1 — ITK-SNAP across imaging modalities.** Three representative sessions: multi-modal visualization
(brain MRI with diffusion-derived directional and scalar maps), semi-automatic segmentation (lung CT with
3D rendering), and interactive registration. One familiar, easy-to-learn interface serves many imaging
domains — the generalist design behind ITK-SNAP's broad, cross-domain adoption.

**Fig. 2 — Interactive, AI-assisted segmentation is already in ITK-SNAP.** Positive (red) and negative
(green) scribble prompts drive a served foundation model (nnInteractive) to a 3D placenta segmentation in
fetal ultrasound; after four expert edits the result reaches Dice 0.884 against the manual reference —
even though fetal ultrasound was absent from the model's training data. This model-proposes /
expert-corrects loop is precisely the primitive the proposal exposes to external agents.

**Fig. 3 — Human-in-the-loop workflow.** The model proposes (itksnap-dls) → the agent's confidence gate
flags an uncertain case → control hands to a live ITK-SNAP session where the expert corrects on screen →
a structured, audited result returns to the agent. The proposal's core differentiator.

**Fig. 4 — System architecture.** The net-new agent/MCP surface over ITK-SNAP's existing Qt-free core,
the itksnap-dls model plane, and the remote/cloud data plane; ★ marks net-new capabilities added within
existing components (audit record, DICOM-SEG, explorer). Grounds the feasibility claim — the work extends
already-shipping components rather than building from scratch.

## 6. References

1. Yushkevich PA, Piven J, Hazlett HC, Smith RG, Ho S, Gee JC, Gerig G. *User-guided 3D active contour
   segmentation of anatomical structures: significantly improved efficiency and reliability.* NeuroImage.
   2006;31(3):1116–1128. — ITK-SNAP methods paper (canonical).
2. Hao J, Yushkevich PA, Dong NJ, Amin S, Guo Z, Yushkevich N, Aggarwal A, Pouch AM. *Streamlining 4D
   Cardiac Image Workflows: Open-Source Tools for Segmentation, Registration, and Visualization.* Functional
   Imaging and Modeling of the Heart (FIMH) 2025. — recent ITK-SNAP 4 paper; source of the cardiac use case.
3. Isensee F, Rokuss M, Krämer L, Dinkelacker S, Ravindran A, Stritzke F, et al. *nnInteractive: Redefining
   3D Promptable Segmentation.* arXiv:2503.08373. 2025. — interactive-segmentation foundation model
   integrated in ITK-SNAP via itksnap-dls; CVPR 2025 challenge winner.
4. Diaz-Pinto A, Alle S, Ihsani A, Asad M, Nath V, Pérez-García F, et al. *MONAI Label: A framework for
   AI-assisted interactive labeling of 3D medical images.* Medical Image Analysis. 2024;95:103207.
   doi:10.1016/j.media.2024.103207.
5. Wasserthal J, et al. *TotalSegmentator: robust segmentation of anatomical structures in CT images.*
   Radiology: Artificial Intelligence. 2023;5(5):e230024.
6. Antonelli M, et al. *The Medical Segmentation Decathlon.* Nature Communications. 2022;13:4128. —
   public hippocampus benchmark (Task 04).
7. Zhuang X, et al. *Evaluation of algorithms for Multi-Modality Whole Heart Segmentation: an open-access
   grand challenge (MM-WHS).* Medical Image Analysis. 2019;58:101537. — public cardiac-CT benchmark.

---

<!-- ============================================================================
PRODUCTION NOTES — DELETE THIS ENTIRE BLOCK BEFORE EXPORTING THE FINAL PDF.
These are working notes, not part of the ≤4-page upload.

SCOPE / SPEC (authoritative). Full-Application-Instructions, Section 4:
"Optional Upload: Up to 1 PDF file upload to include PI/co-PI short biographies,
references, figures or other supporting documentation. Please keep the total page
count to 4 pages." → short bios (NOT the full CV PDFs in supporting_docs/), refs,
figures. Much project metadata (license, repo URLs, monthly-users, citations, code
of conduct, docs links) is captured in Section-3 form fields — don't duplicate it
here; the supporting doc's value-add is FIGURES + a tight synthesis.

PAGE BUDGET. Current committed set = Table 1 + Fig 1 (Overview) + Fig 2 (workflow)
+ Fig 3 (architecture) + bios + refs → fits 4 pages. Re-render after any edit
(scripts note below). If it overflows, trim in this order: (1) shrink Fig 3
architecture; (2) tighten Section 3 prose.

FIGURES — REVISED (2026-07-15, per PI feedback). Table 1 (landscape gap) REMOVED and
replaced by two figures from the team's R01. Set = 4 figures, all shown FULL-WIDTH
(~6.6") so diagram text is legible. Files:
  Fig 1 = UI capabilities   → supporting_docs/fig_ui-screenshots.png   (R01 fig 1 screenshots)
  Fig 2 = interactive AI seg → supporting_docs/fig_ai-placenta.png     (R01 fig 3)
  Fig 3 = workflow          → supporting_docs/figures/fig_workflow.png
  Fig 4 = system architecture→ supporting_docs/figures/fig_architecture.png
  Captions rephrased from the R01 (not copied). The standalone growth-charts figure was
  DROPPED for space (its numbers stay in §2 text; fig1_growth_charts.png + generator kept
  in figures/ if you want it back — you'd need to cut/shrink another figure).
  LEGIBILITY: Fig 3/4 are now at max page width. Fig 4's small sub-labels are readable but
  still small — the PNG is already at full page width, so to make them larger you must
  regenerate the diagram SOURCE with fewer labels / bigger fonts (no source file is in the
  repo; only the PNG). Fig 1/2 UI screenshots read at the layout level (menus are small by
  nature — that's expected and matches how the R01 uses them).

METRICS — DONE (2026-07-15). The weekly-active/university claim in Section 2 was
softened to "As of 2025, update analytics indicated ~5,000 weekly active
installations, spanning top NIH-funded US universities" (past tense + year scope;
dropped the harder "all of the top-50"). The download growth ("roughly doubling
since 2020, to >12,000/month") is backed by live SourceForge data (2020 ≈ 6.9K/mo →
2025 ≈ 14K/mo) and needs no softening.

GOVERNANCE — DELIBERATELY MODEST (2026-07-15, PI call). §4 no longer promises a
governance doc. It now honestly states the current lead-maintainer model (PI reviews/
merges, anyone contributes via PR), says NO formal governance document exists yet +
broadening is under active discussion, and frames a written policy / code of conduct /
succession plan (ISC-informed) as Goal-3 "options being considered," NOT commitments.
Dropped the over-promises: "all changes reviewed via PR", "core maintainer team approves",
"is documenting a GOVERNANCE statement", "rotating leadership", and the absolute
single-writer claim (repo history shows Hao as a 2nd contributor). So a GOVERNANCE.md is
now OPTIONAL — it would further strengthen the open-source-quality criterion but is no
longer needed to back any claim. NOTE: the GitHub Milestones 4.8/4.10 claim still lives
in §2 — creating them is still a cheap win (see manual_work.md).

BENCHMARK CONSISTENCY — DECIDED (2026-07-15): use MM-WHS. This doc already lists
MM-WHS (ref 7) + MSD hippocampus (ref 6) and names no cardiac benchmark in prose, so
it is consistent. Our work_plan_draft.md already uses MM-WHS. REMAINING manual fix:
Paul's v5 work plan (reference_docs/work-plan-draft_v5_PY.docx) still says ACDC in
success-indicator 1.3 — change ACDC → MM-WHS in the final work-plan PDF, and loop
Paul in on the rationale (ACDC is cardiac MRI, off the team's CT/TEE data). See
manual_work.md.

LEAD-DEVELOPER BIO — DECIDED (2026-07-15): excluded here. Lead developer Jilei Hao
stays in the Section-1 form fields (key personnel); the upload keeps strictly to
PI/co-PI bios per spec.

TEAM CHANGE (2026-07-15): Alison Pouch REMOVED as co-PI (she will not be on the
budget). §1 is now PI-only (retitled "Principal Investigator biography"); the §4
maintainer roster dropped her (now "Yushkevich and lead developer Hao"). Her name
remains ONLY in ref 2's author list (Hao et al., FIMH 2025) — a historical fact, kept.
Paul's bio was refreshed from his one-page CV (CV_yushkevich_onepage_2026.docx): added
AD Core Center Neuroimaging-Core co-leadership + MICCAI segmentation-challenge wins +
open-source portfolio; grant dates set to the CV (EB014346 2011–2015, CZI EOSS2
2020–2021). CASCADE (see manual_work.md): remove Alison from the online form's
"Proposal Team" and from the Budget; decide whether she stays on as an UNFUNDED
collaborator (if so, a one-line mention could be added back under "other supporting
documentation").

EXPORT. Source is this markdown. The shipped upload OS4LS_Supporting_Document_ITK-SNAP.docx
is now regenerated FROM this markdown by scratchpad `build_docx.py` (python-docx), which
embeds all 4 figures at full width and drops this trailing notes block automatically
(everything from the first HTML-comment open onward). To rebuild: run build_docx.py, then
re-check ≤4 pages. NOTE this is a
Claude-generated render (Calibri, coral headings) — if the team prefers its own template,
export from this markdown via that pipeline instead; all 4 figure PNGs are in
supporting_docs/ and supporting_docs/figures/.
============================================================================ -->
