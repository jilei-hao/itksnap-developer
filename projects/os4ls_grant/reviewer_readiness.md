# OS4LS Reviewer Criteria — Reference & Self-Assessment

**Source:** OS4LS reviewer-criteria slide *"What reviewers will be looking for"* (captured 2026-07-13).
These are stated as *examples of factors* reviewers take into account — the **full RFA instructions are
authoritative**. This document pairs each factor with where ITK-SNAP stands today and what to shore up
before the **Full Application deadline: July 21, 2026**.

**Legend:** 🟢 strong · 🟡 adequate, can strengthen · 🔴 needs work / verify

---

## At-a-glance scorecard

| Category | Standing | One-line |
|---|---|---|
| **1. Existing impact** | 🟢 | Flagship strength — 20+ yr, 11k+ citations, 1.1M+ downloads |
| **2. Open source quality** | 🟡 | **The soft spot** — but a real ~24-dev base (concentrated: Paul+Jilei ≈81%); focus = governance/sustainability + contributor growth |
| **3. Feasibility** | 🟢 | Sharpened, code-grounded plan + long track record + integration-not-greenfield |
| **4. Value of the proposal** | 🟢 | The differentiator — expert human-in-the-loop as a callable AI-pipeline step |

**Strategic read:** ITK-SNAP is strong on **1 / 3 / 4**. Reviewers' softest lens is **#2 (open-source
quality)** — *not* because the contributor base is thin (git history shows ~24 lifetime developers,
including Kitware/ITK-ecosystem names), but because it is *concentrated* (Paul + Jilei ≈ 81% of commits)
and the governance model is implicit. Put disproportionate effort on *governance / sustainability* and on
framing the concentration as exactly what Goal 3 exists to fix — the cheapest place to lose points, and one
we already have a plan to improve.

---

## 1. Existing impact

**Reviewers weigh:** demonstrated scientific impact & adoption in the life sciences · role in the broader
open-source ecosystem (esp. data-intensive & AI applications) · adoption trends, downstream users, recent
growth · citations or mentions in scientific literature.

| Factor | Standing | Evidence to cite / action |
|---|---|---|
| Scientific impact & adoption | 🟢 | 11,000+ citations, 1.1M+ downloads, 20+ years (per work plan narrative) |
| Role in OSS ecosystem (data/AI) | 🟢 | Built on ITK/VTK/Qt; this grant makes it **AI-native** (agent-callable API, foundation-model serving via itksnap-dls). Cross-ecosystem ties are real — past contributors include **Kitware/ITK** devs (Dženan Zukić, Matt McCormick, Jared Vicory) and **ANTs**' Nick Tustison. *Make the AI-pipeline role explicit — "the human checkpoint inside agentic pipelines."* |
| Adoption trends & recent growth | 🟡 | **Action:** pull a recent download-trend and citation-growth figure — reviewers explicitly score *recent* growth, not just cumulative totals |
| Citations / mentions | 🟢 | Cite the original ITK-SNAP paper(s) + a few representative recent downstream uses |

**Why this is our strongest card:** OS4LS Track 1 *requires* demonstrated adoption. Our maturity is the
qualifying asset — lean into it rather than underselling it as "already built."

---

## 2. Open source quality  ← focus area

**Reviewers weigh:** team composition, leadership & governance structure · breadth of the contributor
base · clarity & recency of the project roadmap and documentation · commit / issue-resolution / PR-review
activity over time.

| Factor | Standing | Evidence to cite / action |
|---|---|---|
| Team, leadership, governance | 🟡 | Leadership 🟢 (PI Yushkevich, PICSL, 20-yr record, prior CZI EOSS + NIH). **Action:** articulate an explicit **governance / decision-making + maintainer structure** — reviewers ask for it and it feeds sustainability |
| Breadth of contributor base | 🟡 | **~24 lifetime human developers** over 20 yr (git history) — a real base, but concentrated (Paul ≈65%, Jilei ≈16%); ~10 occasional external contributors in the last 3 yr. **Action:** (a) cite the ~24-dev + ITK-ecosystem figure honestly; (b) foreground **Goal 3** (hackathon → contributors, dev docs lowering the barrier) as the growth engine; (c) set a concrete new-contributor target (fills a `[N]`) |
| Roadmap & docs — clarity/recency | 🟡→🟢 | We now have a current, code-grounded roadmap (`architecture_and_plan.md`). **Action:** publish **GitHub Milestones (4.8, 4.10)** and link current docs — this converts a 🟡 to 🟢 cheaply and makes "published roadmap" literal |
| Commit / issue / PR activity | 🟢 | Active development (4.6.0-alpha.1; 2,284 non-merge commits; 16 contributor identities active in the last 3 yr). *External PR-review is thin — same root as contributor concentration; Goal 3 addresses it* |

**Contributor data (itksnap git history, all refs, as of 2026-07-13):** 2,284 non-merge commits over ~20
years (2006–2026); **≈ 24 individual human developers** (from ~37 raw author names / 50 emails, after
merging duplicate identities and removing bots + build-automation + unattributable commits).

| Tier | Who | Share of commits |
|---|---|---|
| Core | Paul Yushkevich (~1,481) · Jilei Hao (~369) | **≈ 81%** |
| Substantial | Gary Zhang (159), Octavian Soldea (~73), Dženan Zukić (55), JLasserv (36) | ~14% |
| Occasional | Ravikumar, Vicory, Singla, Goodlett, Tustison, McCormick + ~13 one-off contributors | ~5% |

*Caveats:* Kitware/ITK/ANTs attributions are by name recognition (worth a sanity check); `PICSL *` / `SBP`
accounts are treated as build automation, not people. A `.mailmap` would make this count canonical and
reproducible via `git shortlog`.

**Bottom line:** the yellow here is *concentration*, not absence — a real ~24-developer base exists, with
ecosystem ties. The fix is a crisp **governance + contributor-growth + sustainability-beyond-the-grant**
narrative that frames the concentration as exactly what Goal 3 exists to address. Highest-leverage edit
left before July 21.

---

## 3. Feasibility

**Reviewers weigh:** specificity & clarity of the proposed plan of work · appropriateness of the proposed
use of funds · likelihood of completion given team & project history · plan for tracking progress and
sustainability beyond the grant.

| Factor | Standing | Evidence to cite / action |
|---|---|---|
| Specificity & clarity of plan | 🟢 | Milestones sharpened to be checkable; `architecture_and_plan.md` grounds every deliverable in real code (exists / thin / net-new ledger). This is exactly what this criterion rewards |
| Appropriateness of use of funds | 🟡 | **Action:** budget-justification narrative — ~1 FTE-equivalent over 2 yr + the Year-2 hybrid event; confirm the indirect-rate treatment |
| Likelihood of completion | 🟢 | 20-yr track record; delivered CZI EOSS + NIH; **integration-heavy, not greenfield** — both data planes (Qt-free logic; remote transport) already exist, so technical risk is low. Say this explicitly |
| Progress tracking & sustainability | 🟡 | Progress: GitHub Milestones + the existing CTest/`SNAPTestQt` harness + the 4.8/4.10 release train. Sustainability: pip-distribution + download metrics, institutional cost-share, Goal-3 maintainer pipeline. **Action:** state both plainly (sustainability overlaps with #2) |

**Leverage the "we sharpened this" work:** the checkable-not-gamble milestone pass we just did is the
direct answer to "specificity and clarity of the plan of work."

---

## 4. Value of the proposal

**Reviewers weigh:** advances adoption or unlocks new computational capabilities · addresses unmet needs
in the life sciences · improves integration with other tools researchers use · advances data-intensive or
AI capabilities that support scientific needs.

| Factor | Standing | Evidence to cite / action |
|---|---|---|
| Unlocks new capabilities | 🟢 | The agent-callable **`request_review`** primitive — expert human judgment as a callable, resumable, audited pipeline step — is genuinely new (Goal 1) |
| Addresses unmet needs | 🟢 | No tool today exposes expert human adjudication as an orchestrable step for AI pipelines; "model proposes, human disposes" is the gap |
| Improves integration with other tools | 🟢 | Goal 2 maps directly: DICOM-SEG round-trip vs. 3D Slicer, remote/cloud data access (Flywheel/SSH/HTTP), BIDS awareness |
| Advances data-intensive / AI capabilities | 🟢 | The human-in-the-loop-for-AI thesis + foundation-model serving (itksnap-dls) + the Year-2 model-improvement loop (1.3) |

**This is where the proposal shines** — every sub-factor has a direct, named deliverable. Keep the
framing on *capability and unmet need*, not on the plumbing that enables it.

---

## Priority actions before July 21 (ordered by leverage)

1. **[#2 — highest] Governance + contributor-growth + sustainability narrative.** The softest reviewed
   dimension. Cite the real base honestly ("~24 developers over 20 yr, incl. Kitware/ITK-ecosystem
   contributors; led by Yushkevich & Hao"), articulate the governance/maintainer model, and make Goal 3
   visibly the engine for broadening the active contributor base. Set a concrete new-contributor target.
2. **[#2 — cheap win] Publish GitHub Milestones (4.8, 4.10)** and link the current roadmap/docs. Converts
   "roadmap clarity/recency" from 🟡 to 🟢; `architecture_and_plan.md` already *is* the roadmap.
3. **[#1] Recent-growth figure.** Pull a download-trend and/or citation-growth number — reviewers score
   *recent* growth explicitly, and cumulative totals alone don't answer it.
4. **[#3] Budget justification.** One paragraph tying the funds to ~1 FTE-equivalent + the Year-2 event;
   confirm indirect-rate handling.
5. **[#3] Progress-tracking statement.** Name the mechanism: GitHub Milestones + the existing automated
   test harness + the 4.8/4.10 release train.
6. **[#1/#4 — framing] Make the AI-ecosystem role explicit** throughout: ITK-SNAP as the human checkpoint
   inside agentic, data-intensive pipelines.

**Cross-references:** impact & value → `work_plan_draft.md` (narrative + Goals 1/2); plan specificity &
feasibility → `work_plan_draft.md` milestones + `architecture_and_plan.md` (roadmap + capability ledger);
roadmap/docs & community → `architecture_and_plan.md` §4 + Goal 3.
