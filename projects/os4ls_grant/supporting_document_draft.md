# Supporting Document — ITK-SNAP: Human-in-the-Loop AI Image Segmentation

> **What this is.** Draft content for the **optional Section-4 upload** (1 PDF, **≤ 4 pages**: PI/co-PI
> bios, references, figures, and other supporting documentation). This is *not* the Section-4 narrative
> (Section 4 is the character-limited fields in `section4_fields.md` + the work-plan-template PDF). Content
> reframed from the earlier draft. **Check that this renders to ≤ 4 pages before exporting; trim figures or
> bios to fit.** `[bracketed italics]` = the team must complete/verify.

---

## 1. Key personnel

**Paul Yushkevich, PhD — Principal Investigator.** *[Title, institution: Professor, Penn Image Computing and
Science Laboratory (PICSL), University of Pennsylvania.]* Creator and long-standing lead maintainer of
ITK-SNAP; ~20 years leading its development. *[2–3 sentences: research focus (image analysis, segmentation,
computational anatomy); leadership of prior open-source infrastructure funded by CZI EOSS and the NIH; key
publications/roles. Keep to ~4 lines.]*

**Jilei Hao — Lead Developer.** *[Title/affiliation.]* Lead developer on the agentic-API and data-layer
work; contributor to ITK-SNAP's 4.x releases, the itksnap-dls model server, and related components
(greedy_python, SegFlow4D, ConvertMesh). *[2–3 sentences on relevant engineering background.]*

*[Add any co-PIs and key personnel — e.g. collaborators supporting the Year-2 training/hackathon event and
the model-improvement evaluation — with a 2–3 sentence bio each. Do not exceed the page budget.]*

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

## 5. Figures

> *[Insert as images before export. A layered-architecture diagram exists in the team's internal
> `architecture_and_plan.md` and can be rendered to a figure.]*

- **Fig. 1 — System architecture.** The agent/MCP surface over ITK-SNAP's Qt-free logic tier and the
  itksnap-dls model plane; the remote/cloud data plane; and where each new interface attaches. *[Insert.]*
- **Fig. 2 — Adoption / contributor context.** Download or citation growth over recent years, and/or the
  lifetime contributor distribution. *[Insert; supports §2.]*

## 6. References

*[Verify exact citation details before submission.]*

1. Yushkevich PA, Piven J, Hazlett HC, Smith RG, Ho S, Gee JC, Gerig G. *User-guided 3D active contour
   segmentation of anatomical structures: significantly improved efficiency and reliability.* NeuroImage.
   2006;31(3):1116–1128. — the ITK-SNAP methods paper.
2. nnInteractive — *[interactive-segmentation foundation model; CVPR 2025 challenge winner; add full
   citation.]*
3. MONAI Label — *[Diaz-Pinto et al.; add full citation.]*
4. Wasserthal J, et al. *TotalSegmentator: robust segmentation of anatomical structures in CT images.*
   Radiology: Artificial Intelligence. 2023. — *[verify.]*
5. Antonelli M, et al. *The Medical Segmentation Decathlon.* Nature Communications. 2022. — *[verify;
   hippocampus benchmark, Task 04.]*
6. Bernard O, et al. *Deep learning techniques for automatic MRI cardiac multi-structures segmentation …
   (ACDC).* IEEE TMI. 2018. — *[verify; cardiac benchmark.]*
