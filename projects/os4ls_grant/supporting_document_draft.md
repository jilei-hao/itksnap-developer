# Supporting Document — ITK-SNAP: Human-in-the-Loop AI Image Segmentation

> **What this is.** Draft content for the **optional Section-4 upload** (1 PDF, **≤ 4 pages**: PI/co-PI
> bios, references, figures, and other supporting documentation). This is *not* the Section-4 narrative
> (Section 4 is the character-limited fields in `section4_fields.md` + the work-plan-template PDF). Content
> reframed from the earlier draft. **Check that this renders to ≤ 4 pages before exporting; trim figures or
> bios to fit.** `[bracketed italics]` = the team must complete/verify.

---

## 1. PI and Co-PI biographies

*(The optional upload asks for PI/co-PI bios only. Other key personnel — e.g. lead developer Jilei Hao —
are captured in Section 1 of the application form, not here.)*

**Paul A. Yushkevich, PhD — Principal Investigator.** Professor of Radiology at the University of
Pennsylvania (Perelman School of Medicine), in the Penn Image Computing and Science Laboratory (PICSL), with
a graduate-group appointment in Bioengineering; PhD in Computer Science, University of North Carolina at
Chapel Hill (2003). He is the creator and long-standing lead maintainer of ITK-SNAP across its ~20-year
history. His NIH-funded research develops statistical-shape and biomedical image-analysis methods —
including automatic segmentation and morphometry of the hippocampal formation for Alzheimer's-disease
imaging biomarkers, and machine-learning methods that improve general-purpose segmentation — with a
sustained record of building open-source imaging software (NIH; CZI EOSS). *[Add "Director of PICSL" if
accurate; the source page lists PICSL as affiliation but not a directorship.]*

**Alison M. Pouch, PhD — Co-Principal Investigator.** Assistant Professor of Radiology at the University of
Pennsylvania (Perelman School of Medicine), with core-faculty appointments in the Penn Center for Biomedical
Image Computing and Analysis (CBICA), the Penn Cardiovascular Institute, and the Penn Institute for
Computational Sciences (PICS), and a graduate-group appointment in Bioengineering; PhD in Bioengineering,
University of Pennsylvania (2013). Her research centers on cardiac image analysis — 3D/4D echocardiography,
heart-valve modeling, and 3D-ultrasound and foundation-model segmentation — and she is a senior author on
the ITK-SNAP 4 / 4D cardiac tools paper (Hao et al., FIMH 2025 — ref 2), collaborating directly with the
project's lead developer. In this project she leads the cardiac use cases and the Year-2 evaluation of
expert-in-the-loop model improvement.

*[Add any additional co-PIs with a 2–3 sentence bio each; do not exceed the ≤4-page budget.]*

## 2. Project maturity, adoption, and ecosystem role

ITK-SNAP is among the most established and most-cited tools for 3D/4D biomedical image segmentation:

- **Scientific impact & adoption:** ~20 years of continuous development; **11,082 citations** of the methods
  paper (incl. *Science* and *Nature* venues); **1.16M+ downloads** (SourceForge); a large international user
  base across neuroimaging, radiology, and cardiology. *[Add a recent 12–24-month download/citation-growth
  figure — reviewers weigh recent growth explicitly. See Fig. 2.]*
- **Sustained, open development:** **2,284 non-merge commits** and contributions from **~24 individual
  developers** over the project's lifetime, with active development continuing through the current
  4.6.0-alpha series and the 4.8 / 4.10 release train tracked as public GitHub Milestones.
- **Ecosystem role:** built on the ITK/VTK/Qt stack; nnInteractive (CVPR 2025 interactive-segmentation
  challenge winner) is now integrated across napari, MITK, 3D Slicer, and ITK-SNAP, and our itksnap-dls
  server is ITK-SNAP's path into that shared model ecosystem. Cross-ecosystem engagement is concrete: past
  contributors include developers from **Kitware/ITK** (Dženan Zukić, Matt McCormick, Jared Vicory) and
  **ANTs** (Nicholas Tustison) — evidence of real ties across the open-source imaging ecosystem.

## 3. Technical approach and feasibility

The effort is **integration-heavy, not greenfield**: it composes mature, working components (ITK-SNAP,
itksnap-dls, greedy/Convert3D, SegFlow4D) behind small, well-scoped new interfaces, validated at each step by
ITK-SNAP's existing automated test harness. A key feasibility fact is that **both technical substrates
already exist**:

- **A toolkit-independent, GUI-free logic tier.** ITK-SNAP's core logic already builds free of GUI
  dependencies — proven today by the shipped headless `itksnap-wt` binary — so the Python/agent-callable
  surface (Aim 1) is a binding-and-interface exercise, not a rewrite.
- **A working remote-data transport layer.** ITK-SNAP already loads images and workspaces over Flywheel,
  SSH, and HTTP, with caching; Aim 2 adds a browsable explorer UI and agent API over that transport, plus
  DICOM/BIDS-aware organization.

The genuinely new work is therefore concentrated and independently testable — the Python binding, the
agent-callable review/command surface, the provenance/audit record, the MCP server, and the explorer UI —
with a single larger new subsystem (DICOM-SEG interchange) isolated as a discrete Year-2 deliverable and
validated by round-trip against an external tool (e.g. 3D Slicer). The model-improvement loop (milestone
1.3) relies only on mature techniques — supervised fine-tuning on expert-corrected labels and uncertainty-
based case routing (active learning) — so it depends on no unproven advance; the novel element is the
capture plumbing, which is squarely in the team's competency. This shape — small interfaces over shipped
code, continuously validated — is well matched to AI-assisted development within a focused two-year effort.

*[Optional: insert the layered-architecture figure here — see Fig. 1.]*

## 4. Team, governance, and sustainability

**Governance.** *[Articulate the project's governance and maintainer model: how releases are approved, how
external contributions are reviewed and merged, and how maintainership is shared. If no formal document
exists, a short public GOVERNANCE/MAINTAINERS statement created before submission would directly address the
"open-source quality" review criterion.]*

**Contributor base and growth.** Development is currently concentrated in a small core team (the PI and lead
developer account for the large majority of commits), within a real ~24-developer lifetime base that
includes ITK/ANTs-ecosystem collaborators. **Broadening the active contributor and maintainer base is an
explicit objective (Goal 3):** the contributor hackathon and developer documentation for the new interfaces
are designed to lower the barrier to entry, with a concrete target of *[N]* new external contributors /
merged community pull requests.

**Sustainability beyond the grant.** The pip-installable API and MCP server are lightweight, auto-updatable
artifacts published to PyPI, with pip-based download metrics for transparent ongoing adoption tracking; the
GUI continues on ITK-SNAP's established release and installer channels; and institutional cost-share
contributes a portion of the lead maintainer's time, existing CI/test infrastructure, and the mature
codebases the work builds on. Together with the contributor-growth activities, this maintains the project's
trajectory after the funding period.

## 5. Figures and tables

**Table 1 — The landscape gap.** *Legend: ✓ available today · ◐ partial · ★ delivered by this proposal · ✗ not available.*

| Capability | ITK-SNAP | 3D Slicer | MITK | napari | MONAI Label |
|---|---|---|---|---|---|
| Established, widely adopted for its audience | ✓ | ✓ | ✓ | ✓ (microscopy) | ✓ (framework) |
| Interactive foundation-model segmentation | ✓ | ✓ | ✓ | ✓ | ✓ |
| Remote / cloud data access | ✓ | ✓ | ◐ | ◐ | ✓ |
| Lossless open-format interchange (DICOM-SEG) | ★ | ✓ | ✓ | ◐ | ✓ |
| Agent-callable API for external pipelines | ★ | ◐ | ✗ | ◐ | ◐ |
| **Expert review/correction as a callable, resumable, audited pipeline step** | **★** | ✗ | ✗ | ✗ | ✗ |

*No existing tool exposes the bottom-row primitive — competitors keep the human inside their own UI or
labeling loop rather than offering expert review as a step an external agent invokes. That gap is this
proposal's core contribution. (Mirrors the LOI Landscape Analysis.)*

**Fig. 1 — Human-in-the-loop workflow** *(created).* Model proposes (itksnap-dls) → the agent's confidence
gate flags an uncertain case → control hands to a live ITK-SNAP session where the expert corrects on screen
→ a structured, audited result returns to the agent.

**Fig. 2 — System architecture** *(created).* The net-new agent/MCP surface over ITK-SNAP's existing
Qt-free core, the itksnap-dls model plane, and the remote/cloud data plane; ★ marks net-new capabilities
added within existing components (audit record, DICOM-SEG, explorer).

**Fig. 3 — ITK-SNAP 4 on a 4D cardiac study** *(reuse, with attribution).* Reproduced from Fig. 1 of Hao
et al., FIMH 2025 [ref 2]: 20 time points, with ventricle segmentations across tri-planar and 3D views;
grounds ITK-SNAP as a mature, actively developed, natively-4D tool.

> All three figures plus the table exceed the 4-page limit — trim before submission (drop or shrink a
> figure, or lay figures out more compactly).

> Export figures at ≥300 dpi; reused paper figures carry a citation to ref 2; keep the whole supporting
> document to ≤4 pages.

## 6. References

*[Verify exact citation details before submission.]*

1. Yushkevich PA, Piven J, Hazlett HC, Smith RG, Ho S, Gee JC, Gerig G. *User-guided 3D active contour
   segmentation of anatomical structures: significantly improved efficiency and reliability.* NeuroImage.
   2006;31(3):1116–1128. — ITK-SNAP methods paper (canonical).
2. Hao J, Yushkevich PA, Dong NJ, Amin S, Guo Z, Yushkevich N, Aggarwal A, Pouch AM. *Streamlining 4D
   Cardiac Image Workflows: Open-Source Tools for Segmentation, Registration, and Visualization.* Functional
   Imaging and Modeling of the Heart (FIMH) 2025. *[verify volume/pages/DOI]* — recent ITK-SNAP 4 paper;
   source of Fig. 3.
3. Isensee F, Rokuss M, Krämer L, Dinkelacker S, Ravindran A, Stritzke F, et al. *nnInteractive: Redefining
   3D Promptable Segmentation.* arXiv:2503.08373. 2025. — interactive-segmentation foundation model
   integrated in ITK-SNAP via itksnap-dls.
4. Diaz-Pinto A, Alle S, Ihsani A, Asad M, Nath V, Pérez-García F, et al. *MONAI Label: A framework for
   AI-assisted interactive labeling of 3D medical images.* Medical Image Analysis. 2024;95:103207.
   doi:10.1016/j.media.2024.103207.
5. Wasserthal J, et al. *TotalSegmentator: robust segmentation of anatomical structures in CT images.*
   Radiology: Artificial Intelligence. 2023. — *[verify.]*
6. Antonelli M, et al. *The Medical Segmentation Decathlon.* Nature Communications. 2022. — *[verify;
   hippocampus benchmark, Task 04.]*
7. Zhuang X, et al. *Evaluation of algorithms for Multi-Modality Whole Heart Segmentation: an open-access
   grand challenge (MM-WHS).* Medical Image Analysis. 2019. — *[verify; cardiac CT benchmark.]*
