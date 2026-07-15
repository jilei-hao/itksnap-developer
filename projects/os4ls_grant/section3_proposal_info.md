# Section 3 — Proposal Information (draft)

Form fields for Section 3. ✅ = pre-filled from LOI. `[bracketed italics]` = verify/complete.
Character-limited fields are measured below.

---

## Title — limit 60 characters · ✅ prefilled · measured **49 / 60** ✅

<!--TITLE-->
ITK-SNAP: Human-in-the-Loop AI Image Segmentation
<!--/TITLE-->

## Proposal Purpose — limit 200 characters · **NEW** · measured **188 / 200** ✅

*"Briefly describe your software project(s) and the specific technical bottleneck or capability gap this
proposal will address."*

<!--PURPOSE-->
ITK-SNAP, a widely used open-source 3D/4D biomedical image segmentation tool, gains an agent-callable API for expert-in-the-loop review, plus remote/cloud data access and interoperability.
<!--/PURPOSE-->

## Funding track

**Track 1 — Domain-specific Tools.** (Cannot change from the LOI.)

---

## Software projects to be supported (up to 5)

### 1. ITK-SNAP — *primary*

- **Repository:** `https://github.com/pyushkevich/itksnap` *[verify this is the canonical repo URL you want listed]*
- **Website:** `https://www.itksnap.org` *[verify]*
- **Short description** — limit 500 characters · measured **429 / 500** ✅:

<!--DESC1-->
ITK-SNAP is an open-source application for interactive segmentation of 3D and 4D biomedical images, widely used in neuroimaging, radiology, and cardiology. It offers manual and semi-automatic (active-contour) segmentation, multi-modal 2D/3D visualization, and—via the itksnap-dls server—foundation-model interactive segmentation. Built on ITK, VTK, and Qt, with a 20-year track record, 11,000+ citations, and 1.1M+ downloads.
<!--/DESC1-->

- **License:** GPL-3.0 *(confirmed: `itksnap/COPYING` = GNU GPL v3)*
- **Main programming language:** C++ (C++17)
- **Canonical citation:** Yushkevich PA, Piven J, Hazlett HC, et al. *User-guided 3D active contour segmentation of anatomical structures.* NeuroImage. 2006;31(3):1116–1128. *[verify]*
- **Recent citation (ITK-SNAP 4 / 4D cardiac):** Hao J, Yushkevich PA, Dong NJ, Amin S, Guo Z, Yushkevich N, Aggarwal A, Pouch AM. *Streamlining 4D Cardiac Image Workflows: Open-Source Tools for Segmentation, Registration, and Visualization.* FIMH 2025. *[verify volume/pages/DOI]* — evidence of recent, active development (supports the "recent growth / activity" criterion). Use alongside the canonical citation.
- **Code of conduct (link):** *[none in repo — add if one exists, or create]*
- **End-user documentation (link):** `https://www.itksnap.org` *[verify exact docs URL]*
- **Contributor / developer guidelines (link):** *[none in repo — see governance gap; create a CONTRIBUTING before submission if possible]*
- **Package-manager entry (link):** *[GUI ships as SourceForge installers, not a package manager; the pip-installable Python API/MCP (this project) → PyPI]*
- **Community engagement / Q&A forum (link):** *[ITK-SNAP mailing list / support forum — add exact URL]*

### 2. itksnap-dls — *AI model server (extended by Aim 1)*

- **Repository:** `https://github.com/jilei-hao/itksnap-dls` *[verify canonical URL]*
- **Short description** — limit 500 characters · measured **424 / 500** ✅:

<!--DESC2-->
itksnap-dls is a Python/FastAPI server that serves AI segmentation models to ITK-SNAP and other clients over HTTP. It exposes foundation-model interactive segmentation (nnInteractive, SAM2) and fully-automatic segmentation (TotalSegmentator) through a pluggable model registry with asynchronous job management, bringing AI-assisted segmentation into the ITK-SNAP GUI and, through this project, into agent-callable pipelines.
<!--/DESC2-->

- **License:** MIT *(per `pyproject.toml`)* — ⚠ *`LICENSE.txt` appears to contain GPL text; reconcile the license file with the declared MIT before submission.*
- **Main programming language:** Python (≥3.10)
- **Canonical citation:** *[none]*
- **Docs / contributor guidelines / code of conduct / forum:** *[none in repo — verify]*
- **Package-manager entry:** *[verify whether v0.1.3 is published to PyPI]*

### *(optional)* 3–5

*[Decide whether to also list greedy and/or SegFlow4D as supported projects. They are components the work
builds on; list them only if the funded work meaningfully develops them, since reviewers read this as the
set of projects the grant supports.]*

---

## Software project usage and impact metrics (whole numbers; ≤200-char comment each)

- **Monthly users (estimate):** *[N — estimate from SourceForge monthly download stats or site analytics]*
- **Number of dependent software projects/packages:** *[N — e.g. tools that call itksnap-wt or the workspace format; verify]*
- **Scholarly citations (estimate):** **11082** — comment: *"citations of the ITK-SNAP methods paper (Yushkevich et al., NeuroImage 2006); additional related papers add more."*

## Categories (check up to 3)

1. **Biological and Biomedical imaging** (Enabling technologies)
2. **Neuroscience** (Translational / application areas)
3. *[Third tag — choose one: Computational biology or Predictive modeling. Cardiology/radiology aren't listed options, so pick the closest fit for your audience.]*

---

## Open items for Section 3

- Proposal Purpose fits (see count above); adjust if you reword.
- **Usage metrics numbers** — monthly users, dependent packages (scholarly citations = 11,082, done).
- **itksnap-dls license reconciliation** — pyproject says MIT, LICENSE.txt contains GPL text.
- **Community/repo links** — none of code-of-conduct / contributor-guidelines exist in either repo today; this both fills the form and is the same gap Goal 3 / the governance statement should close.
- **Canonical repo URLs & website** — verify the exact URLs you want listed.
