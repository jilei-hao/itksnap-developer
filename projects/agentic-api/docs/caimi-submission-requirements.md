# SIIM-CAIMI26 — Submission Requirements Reference

> **Purpose of this file.** Authoritative, project-agnostic reference for drafting SIIM-CAIMI26
> submissions. Point Claude Code at this file when drafting or reviewing an abstract / showcase
> submission for any project. Source: <https://siim.org/learning-events/events/caimi/call-for-submissions/>
> (extracted 2026-07-16). If in doubt, re-fetch the source — the portal wins over this file.

**Event:** SIIM-CAIMI26 — Conference on Artificial Intelligence in Medical Imaging
**When / where:** Oct 26–27, 2026 · University of Pennsylvania, Philadelphia, PA

---

## 0. Per-submission working header (fill this in for each project)

```
Project:            <e.g. ITK-SNAP AI-assisted segmentation / cardiac US guidance / SegFlow4D>
Target track:       <Experiential Abstract | AI Builder Showcase | Scientific Abstract>
Presenting author:  <name>
Vendor co-authors?: <yes/no — see §5 Vendor rules; this can disqualify a track>
Demo/repo/video:    <URL(s) if Builder Showcase>
Status:             <drafting | internal review | submitted>
```

---

## 1. Hard deadlines & logistics (apply to ALL tracks)

- **Submission deadline:** **July 24, 2026, 11:59 PM PST**
  (= 2:59 AM EST on July 25 — for Eastern time, treat the practical cutoff as *early morning July 25*).
- **Notifications:** August 26, 2026.
- **Portal:** SIIM-CAIMI26 Submission Portal on AbstractScorecard — EventKey `QRFBVSUS`.
  <https://www.abstractscorecard.com/cfp/submit/login.asp?EventKey=QRFBVSUS>
  - Portal account is **separate** from a My SIIM account. New users: "JOIN NOW" with an email.
  - Save portal credentials — needed to log back in, check status, and edit before the deadline.
- **Browsers:** Chrome or Firefox only. **Do NOT use** Edge, Safari, or Internet Explorer.
- **No honoraria / no expense coverage** for presenters of accepted submissions.
- **Contact:** Anna Zawacki, Director, Programs and Corporate Relations — azawacki@siim.org

---

## 2. Which track? (decision guide)

| If the work is… | Track | Publication | Presentation | Rigor bar |
|---|---|---|---|---|
| Hypothesis-driven, translational, reproducible research (clear question → methods → results → conclusion) | **Scientific Abstract** | JIIM (Springer Nature supplement) | Leans **oral** (10 min + 5 min Q&A) | High |
| A new application/workflow/process, often with limited objective data; implementation lessons, operational insights, early findings | **Experiential Abstract** | JIIM (Springer Nature supplement) | Leans **poster** (4′×8′) | Moderate |
| A working tool / prototype / integration / MVP that solves a real clinical or operational problem; feedback wanted | **AI Builder Showcase** | **Not** published | **10-min live demo** + Q&A | Not primary — creativity & feasibility matter more |

Key tradeoff to decide consciously per project: **Experiential** buys a JIIM publication credit but reviewers
will *not* evaluate a linked web app (the abstract must stand alone). **Builder Showcase** gives a live-demo slot
and reviewers *do* engage with your demo/repo/video, but there is **no publication**. Same project can often fit
either — pick based on whether you want the publication or the demo-driven feedback.

> ⚠️ **Vendor gate:** the Builder Showcase forbids vendor submissions entirely, and Experiential is closed
> to any author list containing a vendor. See §5 before committing a project with commercial co-authors or
> product-promotion intent.

---

## 3. Experiential Abstract — full spec

**Scope.** Projects describing a new application, workflow, or process — often with limited objective data.
Good for sharing implementation lessons, operational insights, or early findings. Generally routed to poster.

**Hard format constraints**
- **350-word limit.** Figure/table captions, headings, keywords, and title do **not** count.
- **Up to 3 figures and/or tables**, uploaded via the portal **with captions**.
- **Blind review** — do **NOT** include institution or corporate names anywhere in the abstract.
- Must be **original and not previously published**; substantial overlap with work accepted elsewhere is ineligible.
- **Published as submitted** — no revisions permitted after acceptance. (Proofread accordingly.)
- Supplemental links are allowed, **but the abstract must stand alone** — reviewers are **not** expected to
  evaluate web-based applications for this track.

**Required sections (in this order)**
1. Introduction / Background
2. Methods / Intervention
3. Results / Outcome
4. Conclusion
5. Statement of Impact
6. Keywords

**Review criteria** (each scored 1–10): Relevance/Interest to SIIM Audience · Clarity · Innovation · Scientific Rigor.

**Presentation format**
- Poster: single or team presenters, 4′×8′ boards. (If routed to oral: 10-min talk + 5-min Q&A.)

**Publication:** Yes — accepted abstracts published by Springer Nature as a JIIM Supplement.

**Eligible awards:** Top 3 Posters (or Top 3 Oral Abstract Presentations if presented orally).

---

## 4. CAIMI AI Builder Showcase — full spec

**Scope.** Early-stage tools, workflows, prototypes, integrations, and practical AI solutions aimed at real
clinical problems. Explicitly welcomes workflow automations, LLM-powered tools, deployment pipelines,
"vibe-coded" prototypes, and clinical integrations. **No hypothesis required.** Ethos: *less polish, more innovation.*
Ideal for trainees, developers, and clinical informaticists who built something that works and want feedback.

**Hard format constraints**
- **500-word limit.** Captions, headings, keywords, and title do **not** count.
- **Links to live demos, GitHub repos, and short video walkthroughs are strongly encouraged** — and
  **reviewers ARE expected to engage with linked materials.** (Opposite of the abstract track — invest in the demo.)
- **VENDOR SUBMISSIONS ARE NOT ALLOWED.**
- **Not** eligible for JIIM publication.
- Submitted through the official portal.

**Required sections (six)**
1. **Problem Statement** — what clinical or operational challenge does this address?
2. **Approach / What You Built** — the tool/workflow/solution and how it works.
3. **Demo or Evidence of Function** — link to video, live web app, or GitHub (strongly encouraged).
4. **Clinical or Operational Impact** — who benefits, and how?
5. **Current Stage** — Concept / Prototype / Deployed (all stages welcome).
6. **What Feedback You're Seeking** — what questions do you want the audience to help answer?

**Review criteria** (each scored 1–10): Problem Relevance · Creativity & Innovation ·
Feasibility & Real-World Potential · Quality of Demo or Evidence.
*Traditional scientific rigor is explicitly not a primary criterion.*

**Presentation format:** 10-minute live demo or video walkthrough with Q&A.

**Award:** Best AI Builder Showcase Idea.

---

## 5. Vendor rules (read before choosing a track for any commercial-adjacent project)

- **AI Builder Showcase:** vendor submissions are **not allowed**, full stop.
- **Experiential Abstract:** if the author list includes one or more vendors, it is **not eligible** — vendor
  abstracts must be **hypothesis-driven (Scientific), oral only** (no vendor posters), any product evaluation
  must be **blinded and measurable**, and **no company/product logos on slides** (product may be named in methods).
- Practical read for tooling built *on* a commercial platform (e.g., a probe SDK): using a vendor's hardware
  or SDK is not automatically a "vendor submission." The problem arises if a vendor is a **co-author** or the
  submission is effectively **promoting the product**. When unsure, confirm with the SIIM contact before choosing
  the Showcase or Experiential track.

---

## 6. Pre-submission compliance checklist (validate every draft against this)

Shared:
- [ ] Correct track chosen for the work type (§2), and vendor gate cleared (§5).
- [ ] Word count within limit **excluding** title, headings, captions, keywords.
- [ ] Original / not previously published; no substantial overlap with work accepted elsewhere.
- [ ] Submitted via portal `QRFBVSUS` before **July 24, 2026 11:59 PM PST**, in Chrome/Firefox.

Experiential only:
- [ ] ≤ 350 words.
- [ ] ≤ 3 figures/tables, each with a caption, uploaded via portal.
- [ ] **No institution or corporate names anywhere** (blind review).
- [ ] All six required sections present and ordered (Intro → Methods → Results → Conclusion → Impact → Keywords).
- [ ] Abstract stands alone without any linked web app.
- [ ] Final text is submission-ready — **no post-acceptance edits allowed.**

Builder Showcase only:
- [ ] ≤ 500 words.
- [ ] All six sections present (Problem / Approach / Demo / Impact / Stage / Feedback).
- [ ] Working demo link included and reachable (video, live app, or GitHub) — reviewers **will** open it.
- [ ] Not a vendor submission.

---

## 7. Fill-in skeletons

### 7a. Experiential Abstract (≤350 words, blind)

```
Title: <descriptive, no institution/vendor names>
Keywords: <5–8 terms; align with CAIMI topic areas in §8>

Introduction / Background
<The clinical/operational gap. 1–3 sentences. No institution names.>

Methods / Intervention
<What you built/deployed and how it was evaluated or rolled out.>

Results / Outcome
<Observed outcomes; qualitative or limited quantitative is acceptable for this track.>

Conclusion
<What was learned; where it goes next.>

Statement of Impact
<Why this matters to the SIIM/imaging-informatics community.>

[Figures/tables: up to 3, with captions, uploaded separately in the portal.]
```

### 7b. AI Builder Showcase (≤500 words)

```
Title: <what it does, plainly>
Keywords: <align with §8>

Problem Statement
<The clinical or operational challenge. Concrete and specific.>

Approach / What You Built
<The tool/workflow, architecture, and how it works in practice.>

Demo or Evidence of Function
<Live demo URL / GitHub / short video walkthrough. Make sure it works — reviewers open it.>

Clinical or Operational Impact
<Who benefits and how; where it plugs into a real workflow.>

Current Stage
<Concept | Prototype | Deployed>

What Feedback You're Seeking
<The specific questions you want the audience/reviewers to help answer.>
```

---

## 8. CAIMI topic areas (for framing & keyword alignment)

Useful for choosing keywords and positioning any project against reviewer expectations:

- **Computer Vision & Image Analysis** — classification/detection/localization; segmentation (anatomy, lesions,
  RT planning); generative models (GAN/diffusion/VAE) for augmentation, synthesis, super-resolution, anomaly
  detection; registration (rigid/non-rigid/cross-modality); reconstruction (accelerated MRI, low-dose CT);
  image quality assessment/enhancement.
- **NLP & Structured Data** — radiology/pathology report analysis & generation; extraction from notes/EHR;
  protocol optimization & decision support; workflow automation & operational efficiency; business/admin
  applications; RAG for grounding and hallucination reduction.
- **AI in Radiation Therapy, Theranostics & Medical Physics** — automated planning/optimization; dose
  prediction/verification; auto-segmentation of targets/OARs; response prediction; adaptive RT; QA.
- **Clinical Integration, Validation & Governance** — deployment/implementation science; barriers to
  translation; prospective validation & real-world evidence; benchmarking & VLM-output evaluation; bias/
  fairness; explainability/interpretability/trustworthiness; governance & regulatory (e.g., FDA pathways);
  QA protocols; post-deployment monitoring/maintenance; cost-effectiveness/health economics.
- **Toolkits, Infrastructure, Datasets & Standards** — open-source toolkits (MONAI, PyTorch, TensorFlow);
  annotation & data-management platforms; visualization for model dev/interpretation; MLOps;
  compute architectures & cloud; standardized datasets/benchmarks/reporting (e.g., DICOM-for-AI);
  privacy/security/anonymization.
- **Emerging AI Methodologies & Frontiers** — foundation models (LLMs, ViTs) for imaging; self-/weakly-/
  unsupervised learning; few-/one-/zero-shot; federated & privacy-preserving; RL & active learning;
  multimodal fusion (imaging + clinical/genomics/pathology); causal inference; quantum computing.
- **AI in Specific Clinical Domains** — digital pathology; AI-guided intervention & surgical planning;
  cardiology/neurology/oncology/ophthalmology/dermatology/POCUS applications; drug discovery & trials via
  imaging biomarkers.

---

## 9. Notes for Claude Code when drafting

- Enforce the **word limit for the chosen track** on the body text; report the count and confirm the exclusions
  (title, headings, figure/table captions, keywords are not counted).
- For **Experiential**, actively **strip any institution/vendor identifiers** (blind review) and warn if the
  provided source material contains them.
- For **Builder Showcase**, insist on a **working demo/repo/video link** and treat "Demo or Evidence of Function"
  as load-bearing — reviewers open these.
- Never silently reclassify a project across tracks; surface the §2 tradeoff and the §5 vendor gate and let the
  author decide.
- Keep all six required sections for the chosen track, in order, with the exact section labels.
```
