const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const FA = require("react-icons/fa");

// ---------- palette ----------
const NAVY = "0B2545";
const NAVY2 = "13315C";
const TEAL = "1496A6";
const TEAL_D = "13678A";
const MINT = "2BB3A3";
const AMBER = "E8924A";
const LIGHT = "F4F7FB";
const CARD = "FFFFFF";
const MUTED = "6B7B8C";
const SLATE = "33495C";
const LINE = "DCE5EF";

const HEAD = "Trebuchet MS";
const BODY = "Calibri";

// ---------- icon rasterization ----------
async function icon(Comp, color = "#FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Comp, { color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

const shadow = () => ({ type: "outer", color: "0B2545", blur: 9, offset: 3, angle: 90, opacity: 0.16 });

async function main() {
  // preload icons (white + colored variants as needed)
  const W = "#FFFFFF";
  const I = {};
  const need = {
    bullseye: FA.FaBullseye, lightbulb: FA.FaLightbulb, calendar: FA.FaCalendarAlt,
    ban: FA.FaBan, robot: FA.FaRobot, userMd: FA.FaUserMd, database: FA.FaDatabase,
    plug: FA.FaPlug, code: FA.FaCode, userCheck: FA.FaUserCheck, server: FA.FaServer,
    brain: FA.FaBrain, grid: FA.FaThLarge, cloud: FA.FaCloud, network: FA.FaNetworkWired,
    bolt: FA.FaBolt, layers: FA.FaLayerGroup, clock: FA.FaClock, diagram: FA.FaProjectDiagram,
    cube: FA.FaCube, share: FA.FaShareAlt, window: FA.FaWindowMaximize, comments: FA.FaComments,
    eye: FA.FaEye, rocket: FA.FaRocket, checkDouble: FA.FaCheckDouble, vial: FA.FaVial,
    route: FA.FaRoute, users: FA.FaUsers, flag: FA.FaFlagCheckered, arrow: FA.FaArrowRight,
    check: FA.FaCheckCircle, sitemap: FA.FaSitemap,
  };
  for (const [k, C] of Object.entries(need)) I[k] = await icon(C, W);
  const arrowTeal = await icon(FA.FaArrowRight, "#1496A6");

  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.author = "ITK-SNAP team";
  pres.title = "OS4LS 2026 — ITK-SNAP AI-Native Platform";
  const PW = 13.33, PH = 7.5, M = 0.6;

  // ---------- helpers ----------
  function footer(s, n) {
    s.addText("OS4LS 2026  ·  ITK-SNAP AI-Native, Human-in-the-Loop Segmentation", {
      x: M, y: 7.05, w: 9, h: 0.3, fontSize: 9, color: MUTED, fontFace: BODY, margin: 0,
    });
    s.addText(String(n), { x: PW - 1.0, y: 7.05, w: 0.4, h: 0.3, fontSize: 9, color: MUTED, align: "right", fontFace: BODY, margin: 0 });
  }
  function head(s, kicker, title, sub) {
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 0.46, w: 0.16, h: 0.5, fill: { color: TEAL } });
    s.addText(kicker.toUpperCase(), { x: M + 0.28, y: 0.44, w: 11.5, h: 0.3, fontSize: 13, bold: true, color: TEAL_D, charSpacing: 2, fontFace: HEAD, margin: 0 });
    s.addText(title, { x: M + 0.28, y: 0.72, w: 12.2, h: 0.62, fontSize: 27, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
    if (sub) s.addText(sub, { x: M + 0.28, y: 1.38, w: 12.2, h: 0.4, fontSize: 14, italic: true, color: SLATE, fontFace: BODY, margin: 0 });
  }
  // card with icon-in-circle, header, description lines
  function card(s, x, y, w, h, iconData, header, lines, accent) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: shadow() });
    s.addShape(pres.shapes.OVAL, { x: x + 0.32, y: y + 0.32, w: 0.72, h: 0.72, fill: { color: accent } });
    s.addImage({ data: iconData, x: x + 0.32 + 0.20, y: y + 0.32 + 0.20, w: 0.32, h: 0.32 });
    s.addText(header, { x: x + 0.32, y: y + 1.2, w: w - 0.6, h: 0.55, fontSize: 15.5, bold: true, color: NAVY, fontFace: HEAD, margin: 0, valign: "top" });
    s.addText(lines.map((t, i) => ({ text: t, options: { bullet: false, breakLine: i < lines.length - 1, paraSpaceAfter: 4 } })),
      { x: x + 0.32, y: y + 1.92, w: w - 0.56, h: h - 2.1, fontSize: 12, color: SLATE, fontFace: BODY, margin: 0, valign: "top" });
  }
  function bottomStrip(s, txt, y = 6.25) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: PW - 2 * M, h: 0.62, fill: { color: "E8F1F4" }, line: { color: "C9DEE4", width: 1 }, rectRadius: 0.06 });
    s.addImage({ data: I.check, x: M + 0.22, y: y + 0.17, w: 0.28, h: 0.28 });
    s.addText(txt, { x: M + 0.62, y: y, w: PW - 2 * M - 0.8, h: 0.62, fontSize: 12.5, color: TEAL_D, bold: true, fontFace: BODY, margin: 0, valign: "middle" });
  }

  const three = [M, M + 4.07, M + 8.14]; // x positions for 3 cards w=3.8

  // =========================================================== SLIDE 1 — title
  let s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: PH, fill: { color: TEAL } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.28, y: 0, w: 0.08, h: PH, fill: { color: AMBER } });
  s.addText("OPEN SOURCE FOR THE LIFE SCIENCES (OS4LS) · 2026", { x: 1.0, y: 1.55, w: 11, h: 0.4, fontSize: 14, bold: true, color: MINT, charSpacing: 2, fontFace: HEAD, margin: 0 });
  s.addText("ITK-SNAP for AI-Native,\nHuman-in-the-Loop Segmentation", { x: 1.0, y: 2.0, w: 11.5, h: 1.9, fontSize: 44, bold: true, color: "FFFFFF", fontFace: HEAD, lineSpacingMultiple: 1.0, margin: 0 });
  s.addText("Bringing expert judgment into agentic medical-imaging workflows", { x: 1.02, y: 3.95, w: 11, h: 0.5, fontSize: 18, italic: true, color: "CADCFC", fontFace: BODY, margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 1.02, y: 4.75, w: 6.2, h: 0, line: { color: TEAL, width: 1.5 } });
  s.addText([
    { text: "Internal planning — proposed PIs: ", options: { color: "9FB3C8" } },
    { text: "Alison Pouch", options: { color: "FFFFFF", bold: true } },
    { text: "  &  ", options: { color: "9FB3C8" } },
    { text: "Paul Yushkevich", options: { color: "FFFFFF", bold: true } },
  ], { x: 1.02, y: 4.95, w: 11, h: 0.4, fontSize: 15, fontFace: BODY, margin: 0 });
  s.addText("Letter of Intent due June 8, 2026", { x: 1.02, y: 5.45, w: 11, h: 0.35, fontSize: 13, color: AMBER, bold: true, fontFace: BODY, margin: 0 });

  // =========================================================== SLIDE 2 — opportunity
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "The opportunity", "OS4LS: funding open source for AI-native life science",
    "A Renaissance Philanthropy fund (successor to CZI's EOSS) for adopted scientific software.");
  // left two mini cards stacked
  function panel(x, y, w, h, title, items, accent, ic) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.07, shadow: shadow() });
    s.addShape(pres.shapes.OVAL, { x: x + 0.28, y: y + 0.26, w: 0.6, h: 0.6, fill: { color: accent } });
    s.addImage({ data: ic, x: x + 0.28 + 0.16, y: y + 0.26 + 0.16, w: 0.28, h: 0.28 });
    s.addText(title, { x: x + 1.04, y: y + 0.3, w: w - 1.2, h: 0.5, fontSize: 16, bold: true, color: NAVY, fontFace: HEAD, margin: 0, valign: "middle" });
    s.addText(items.map((t, i) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 5 } })),
      { x: x + 0.34, y: y + 1.0, w: w - 0.6, h: h - 1.1, fontSize: 12.5, color: SLATE, fontFace: BODY, margin: 0, valign: "top" });
  }
  panel(M, 1.95, 6.0, 2.05, "What it funds", [
    "Technical advances in widely-adopted open-source tools",
    "AI-native, data-intensive, agentic capabilities",
    "Interoperability & hardware acceleration",
  ], TEAL, I.lightbulb);
  panel(M, 4.15, 6.0, 2.0, "Out of scope", [
    "AI-assisted rewrite of a legacy tool",
    "Developing new AI/ML models themselves",
    "Hosting / repository infrastructure",
  ], AMBER, I.ban);
  // right: facts
  const rx = 6.95, rw = 5.78;
  function fact(y, big, label, accent) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: rx, y, w: rw, h: 0.92, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.07, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y, w: 0.12, h: 0.92, fill: { color: accent } });
    s.addText(big, { x: rx + 0.35, y, w: 3.0, h: 0.92, fontSize: 23, bold: true, color: NAVY, fontFace: HEAD, margin: 0, valign: "middle" });
    s.addText(label, { x: rx + 3.0, y, w: rw - 3.1, h: 0.92, fontSize: 12.5, color: SLATE, fontFace: BODY, margin: 0, valign: "middle" });
  }
  fact(1.95, "$250K", "Track 1 — Domain-specific tool\nover 2 years", TEAL);
  fact(3.0, "$1M", "Track 2 — Ecosystem / shared\ninteroperability, over 2 years", TEAL_D);
  fact(4.05, "Jun 8", "Letter of Intent due (2026).\nFull application by invitation.", AMBER);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: rx, y: 5.1, w: rw, h: 1.05, fill: { color: NAVY }, rectRadius: 0.07, shadow: shadow() });
  s.addText("Priorities", { x: rx + 0.3, y: 5.2, w: rw - 0.6, h: 0.3, fontSize: 12, bold: true, color: MINT, charSpacing: 1, fontFace: HEAD, margin: 0 });
  s.addText("agentic workflows  ·  composable AI pipelines  ·  large-scale data  ·  hardware acceleration  ·  interoperability", { x: rx + 0.3, y: 5.5, w: rw - 0.6, h: 0.55, fontSize: 12.5, color: "E6EEF7", fontFace: BODY, margin: 0, valign: "top" });
  footer(s, 2);

  // =========================================================== SLIDE 3 — thesis (dark)
  s = pres.addSlide(); s.background = { color: NAVY };
  s.addText("THE CORE IDEA", { x: M, y: 0.6, w: 11, h: 0.35, fontSize: 14, bold: true, color: MINT, charSpacing: 3, fontFace: HEAD, margin: 0 });
  s.addText("“Model proposes, human disposes.”", { x: M, y: 0.98, w: 12.1, h: 0.9, fontSize: 40, bold: true, color: "FFFFFF", fontFace: HEAD, margin: 0 });
  s.addText([
    { text: "MONAI and Hugging Face already make ", options: {} },
    { text: "models", options: { italic: true, color: MINT } },
    { text: " programmable. What agentic medical-imaging pipelines lack is a way to bring ", options: {} },
    { text: "expert human judgment", options: { italic: true, color: MINT } },
    { text: " in.", options: {} },
  ], { x: M, y: 1.95, w: 12.1, h: 0.7, fontSize: 16, color: "CADCFC", fontFace: BODY, margin: 0 });
  // 3-step flow
  const fy = 3.05, fw = 3.55, fh = 2.1;
  const fx = [M, M + 4.27, M + 8.54];
  const steps = [
    { ic: I.robot, t: "AI proposes", d: "Automatic / interactive / language models generate a draft segmentation.", a: TEAL },
    { ic: I.userMd, t: "Expert disposes", d: "The human verifies, corrects, and approves it in ITK-SNAP — fast, spatial, trusted.", a: AMBER },
    { ic: I.database, t: "Captured as data", d: "Corrections & interactions become labels, prompts, and training data — a feedback loop.", a: MINT },
  ];
  steps.forEach((st, i) => {
    const x = fx[i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: fy, w: fw, h: fh, fill: { color: NAVY2 }, line: { color: "27496B", width: 1 }, rectRadius: 0.08 });
    s.addShape(pres.shapes.OVAL, { x: x + 0.32, y: fy + 0.3, w: 0.74, h: 0.74, fill: { color: st.a } });
    s.addImage({ data: st.ic, x: x + 0.32 + 0.21, y: fy + 0.3 + 0.21, w: 0.32, h: 0.32 });
    s.addText(`${i + 1}`, { x: x + fw - 0.85, y: fy + 0.2, w: 0.7, h: 0.7, fontSize: 30, bold: true, color: "33526F", fontFace: HEAD, align: "right", margin: 0 });
    s.addText(st.t, { x: x + 0.32, y: fy + 1.18, w: fw - 0.6, h: 0.4, fontSize: 17, bold: true, color: "FFFFFF", fontFace: HEAD, margin: 0 });
    s.addText(st.d, { x: x + 0.32, y: fy + 1.55, w: fw - 0.6, h: 0.5, fontSize: 12, color: "B9C9DC", fontFace: BODY, margin: 0, valign: "top" });
    if (i < 2) s.addImage({ data: arrowTeal, x: x + fw + 0.08, y: fy + fh / 2 - 0.18, w: 0.36, h: 0.36 });
  });
  s.addText("ITK-SNAP's irreplaceable asset is the expert at the screen. We make that judgment callable.", { x: M, y: 5.7, w: 12.1, h: 0.5, fontSize: 15, bold: true, italic: true, color: AMBER, fontFace: BODY, margin: 0 });
  footer(s, 3);

  // =========================================================== SLIDE 4 — overview
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "The plan", "One composable surface, many capabilities");
  // connective tissue bar
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 1.65, w: PW - 2 * M, h: 0.95, fill: { color: NAVY }, rectRadius: 0.08, shadow: shadow() });
  s.addShape(pres.shapes.OVAL, { x: M + 0.3, y: 1.83, w: 0.6, h: 0.6, fill: { color: TEAL } });
  s.addImage({ data: I.sitemap, x: M + 0.3 + 0.16, y: 1.83 + 0.16, w: 0.28, h: 0.28 });
  s.addText([
    { text: "Aim 1 — Headless API + MCP endpoint", options: { bold: true, color: "FFFFFF" } },
    { text: "   the connective tissue every other capability plugs into", options: { color: "9FB3C8" } },
  ], { x: M + 1.05, y: 1.65, w: PW - 2 * M - 1.3, h: 0.95, fontSize: 16, fontFace: HEAD, margin: 0, valign: "middle" });
  // 5 pillar cards
  const pcs = [
    { ic: I.server, t: "AI model serving", d: "itksnap-dls → DLE", a: TEAL },
    { ic: I.cloud, t: "Remote data access", d: "SSH · Flywheel · BIDS", a: TEAL_D },
    { ic: I.bolt, t: "Registration & 4D", d: "FireANTs · SegFlow4D", a: AMBER },
    { ic: I.share, t: "Interoperability", d: "Slicer · FEBio · napari", a: MINT },
    { ic: I.comments, t: "Viewers & agents", d: "web · IDE · in-app", a: TEAL_D },
  ];
  const pw = 2.3, gap = 0.18, py = 3.0, ph = 2.7;
  pcs.forEach((p, i) => {
    const x = M + i * (pw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: py, w: pw, h: ph, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: py, w: pw, h: 0.14, fill: { color: p.a } });
    s.addShape(pres.shapes.OVAL, { x: x + pw / 2 - 0.38, y: py + 0.42, w: 0.76, h: 0.76, fill: { color: p.a } });
    s.addImage({ data: p.ic, x: x + pw / 2 - 0.18, y: py + 0.42 + 0.2, w: 0.36, h: 0.36 });
    s.addText(p.t, { x: x + 0.12, y: py + 1.35, w: pw - 0.24, h: 0.7, fontSize: 14.5, bold: true, color: NAVY, align: "center", fontFace: HEAD, margin: 0, valign: "top" });
    s.addText(p.d, { x: x + 0.12, y: py + 2.0, w: pw - 0.24, h: 0.5, fontSize: 11.5, color: MUTED, align: "center", fontFace: BODY, margin: 0 });
  });
  bottomStrip(s, "Build the tools once; every frontend (GUI, Python, agents, other tools) plugs into the same surface.");
  footer(s, 4);

  // =========================================================== AIM SLIDES
  function aimSlide(n, kicker, title, sub, cards, strip) {
    const sl = pres.addSlide(); sl.background = { color: LIGHT };
    head(sl, kicker, title, sub);
    cards.forEach((c, i) => card(sl, three[i], 2.2, 3.8, 3.85, c.ic, c.h, c.l, c.a));
    if (strip) bottomStrip(sl, strip);
    footer(sl, n);
    return sl;
  }

  aimSlide(5, "Aim 1", "Composable human-in-the-loop core",
    "Not headless inference (MONAI/HF do that) — making expert judgment an orchestrable step.",
    [
      { ic: I.code, h: "Headless API + Python wrapper", l: ["Scriptable core over the toolkit-independent layer.", "pip-installable; batch & reproducible workflows.", "Builds on existing Logic/WorkspaceAPI."], a: TEAL },
      { ic: I.plug, h: "Local MCP server", l: ["Agent-facing endpoint (MCP / tool-style).", "Client-launched stdio — no hosting, PHI stays local.", "Optional remote (HTTP) mode for cloud."], a: TEAL_D },
      { ic: I.userCheck, h: "Human-in-the-loop primitives", l: ["request_review() → corrected seg + decision.", "Capture clicks/scribbles/edits as labels & signals.", "A human-in-the-loop data engine."], a: AMBER },
    ],
    "The differentiator: expert verification, correction & interaction-capture — callable from any agent.");

  aimSlide(6, "Aim 2", "AI model serving — itksnap-dls → DLE",
    "Generalize our shipped server from one model into a model-agnostic serving layer.",
    [
      { ic: I.brain, h: "Three model classes", l: ["Interactive (nnInteractive, MedSAM2).", "Fully-automatic (e.g. spleen / organ in CT).", "Language-vision (text-prompted)."], a: TEAL },
      { ic: I.grid, h: "Dynamic model discovery", l: ["No hardcoded model list in the GUI.", "Clients query the server for models + capabilities.", "New models appear without a GUI release."], a: TEAL_D },
      { ic: I.users, h: "Contributor toolkit", l: ["Vendor-neutral wrapper contract + scaffolding.", "Agent-assisted, CI-conformance-gated PRs.", "The scaling & sustainability engine."], a: AMBER },
    ],
    "Builds on the shipped itksnap-dls (nnInteractive, REST) — preliminary work, not a prototype.");

  aimSlide(7, "Aim 3", "Remote data access",
    "Find, view, and segment imaging wherever it lives — without download/upload cycles.",
    [
      { ic: I.network, h: "Pluggable backends", l: ["Local filesystem, remote Linux (SSH), Flywheel.", "Common interface; framework for community plugins.", "XNAT-ready."], a: TEAL },
      { ic: I.database, h: "DICOM / BIDS aware", l: ["Auto-detect series & BIDS structure.", "Metadata display + search.", "Partial / range reads on large remote files."], a: TEAL_D },
      { ic: I.cloud, h: "Remote-aware workspaces", l: ["Reference remote images in a workspace.", "Edit / save without pulling full image data.", "Credentials via OS keychain."], a: AMBER },
    ],
    "Serves the data-intensive priority; lowest-risk, soundest plumbing.");

  aimSlide(8, "Registration & 4D", "GPU-accelerated registration & longitudinal propagation",
    "A hardware-acceleration pillar — and the real within-subject longitudinal capability.",
    [
      { ic: I.bolt, h: "FireANTs + greedy", l: ["GPU (PyTorch) and CPU registration.", "One backend-agnostic surface.", "~10× faster / lighter than DL & traditional."], a: AMBER },
      { ic: I.layers, h: "SegFlow4D propagation", l: ["Propagate a segmentation across all 4D frames.", "Warps label maps AND surface meshes.", "Pluggable backends (FireANTs / greedy / ANTs)."], a: TEAL },
      { ic: I.clock, h: "Longitudinal reuse", l: ["ARIA monitoring, serial imaging.", "Training-data generation across time.", "Registration-based — no model retraining."], a: TEAL_D },
    ],
    "Within-subject reuse via registration; lower-risk complement to model adaptation.");

  aimSlide(9, "Interoperability", "Composable with the tools researchers use",
    "Open formats + one or two reference integrations — not a pairwise connector zoo.",
    [
      { ic: I.share, h: "3D Slicer interchange", l: ["Preserve label names, colors, hierarchy, coding.", "DICOM-SEG as the lingua franca.", "ITK-SNAP as the human checkpoint for Slicer."], a: TEAL },
      { ic: I.cube, h: "Segmentation → biomechanics", l: ["Multi-label seg → material-tagged tet mesh.", "Export to FEBio / OpenSim.", "Cardiac / mitral-valve / musculoskeletal."], a: AMBER },
      { ic: I.diagram, h: "Pipeline interop", l: ["ITK-SNAP as a node in napari / MONAI.", "Driven by the Aim 1 API + serving protocol.", "Reusable recipes, not bespoke glue."], a: TEAL_D },
    ],
    "4D meshes (SegFlow4D) → time-resolved biomechanics: e.g. mitral valve over the cardiac cycle.");

  aimSlide(10, "Human surfaces", "Where the human meets the agent",
    "The same viewer, reachable from browser, IDE, and inside ITK-SNAP.",
    [
      { ic: I.eye, h: "Web viewer / QC panel", l: ["2D + 3D rendering (niivue / WebAssembly).", "Inspect, correct, accept/reject results.", "Loads from the headless API."], a: TEAL },
      { ic: I.window, h: "VS Code / Cursor webview", l: ["Same viewer embedded in the AI IDE.", "No context switch from the agent.", "URL handoff: summon → inspect → callback."], a: TEAL_D },
      { ic: I.comments, h: "In-app agent panel", l: ["Bring-your-own-agent (MCP), not a clone.", "Shared GUI context: 'segment this'.", "Vendor-neutral; undo/provenance for safety."], a: AMBER },
    ],
    "Agent summons the right view (deep-linked) → human disposes → structured result flows back.");

  // =========================================================== SLIDE 11 — in practice (use cases)
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "Use cases", "What it looks like in practice",
    "Automation does the rote work; the expert is pulled in only where judgment matters.");
  const ucs = [
    { ic: I.grid, h: "Cohort segmentation at scale", d: "Agent segments 200 scans; the expert reviews only the ~12 flagged. Every decision logged.", tag: "Aims 1 + 2", a: TEAL },
    { ic: I.cube, h: "Valve → biomechanics", d: "Segment the mitral valve, export a FEBio-ready mesh — 4D over the cardiac cycle.", tag: "Aims 1.3 + 4.2", a: AMBER },
    { ic: I.users, h: "Reader study & auditable QC", d: "Route cases to multiple readers; capture decisions + provenance for reliability/audit.", tag: "Aim 1.3", a: MINT },
    { ic: I.code, h: "Reproducible pipeline / notebook", d: "Drive ITK-SNAP from Python or an agent in a versioned, reproducible pipeline.", tag: "Aims 1.1–1.2", a: TEAL_D },
  ];
  const ucw = (PW - 2 * M - 0.4) / 2;
  ucs.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * (ucw + 0.4), y = 2.0 + row * 2.05;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: ucw, h: 1.85, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: shadow() });
    s.addShape(pres.shapes.OVAL, { x: x + 0.32, y: y + 0.34, w: 0.74, h: 0.74, fill: { color: c.a } });
    s.addImage({ data: c.ic, x: x + 0.32 + 0.21, y: y + 0.34 + 0.21, w: 0.32, h: 0.32 });
    s.addText(c.h, { x: x + 1.3, y: y + 0.3, w: ucw - 1.55, h: 0.4, fontSize: 16, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
    s.addText(c.d, { x: x + 1.3, y: y + 0.72, w: ucw - 1.55, h: 0.85, fontSize: 12, color: SLATE, fontFace: BODY, margin: 0, valign: "top" });
    s.addText(c.tag, { x: x + 1.3, y: y + 1.45, w: ucw - 1.55, h: 0.3, fontSize: 10.5, bold: true, color: c.a, fontFace: HEAD, margin: 0 });
  });
  footer(s, 11);

  // =========================================================== SLIDE 12 — technical feasibility (codebase)
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "Technical feasibility", "Built on what already ships",
    "Most of Aims 1–4 extends existing, working components — not new subsystems.");
  const chips = [
    ["Programmable workspaces, labels, display", "Logic/WorkspaceAPI"],
    ["Headless operation today", "itksnap-wt CLI"],
    ["REST + SSH transport", "RESTClient · SSHTunnel"],
    ["DL-server client (local / remote / SSH)", "DeepLearningSegmentationModel"],
    ["Async submit → await → return", "DistributedSegmentationModel"],
    ["Python bindings toolchain", "pybind11 · greedy_python"],
  ];
  const chw = (PW - 2 * M - 0.4) / 2, chh = 0.82;
  chips.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * (chw + 0.4), y = 2.0 + row * 0.98;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: chw, h: chh, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.06, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.1, h: chh, fill: { color: TEAL } });
    s.addImage({ data: I.check, x: x + 0.28, y: y + chh / 2 - 0.16, w: 0.32, h: 0.32 });
    s.addText([
      { text: c[0] + "  ", options: { color: NAVY, bold: true } },
      { text: "→ " + c[1], options: { color: TEAL_D, fontFace: BODY } },
    ], { x: x + 0.72, y, w: chw - 0.9, h: chh, fontSize: 12, fontFace: HEAD, margin: 0, valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.15, w: PW - 2 * M, h: 1.05, fill: { color: NAVY }, rectRadius: 0.07, shadow: shadow() });
  s.addText([
    { text: "~70–80% extends shipped components.  ", options: { color: AMBER, bold: true } },
    { text: "Even ", options: { color: "CADCFC" } },
    { text: "request_review", options: { color: "FFFFFF", bold: true } },
    { text: " reuses the async ticket workflow already shipped in DistributedSegmentationModel — with a human as the “worker.”", options: { color: "CADCFC" } },
  ], { x: M + 0.35, y: 5.15, w: PW - 2 * M - 0.7, h: 1.05, fontSize: 13.5, fontFace: BODY, margin: 0, valign: "middle" });
  footer(s, 12);

  // =========================================================== SLIDE 13 — delivery capacity (coding-agent multiplier)
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "Delivery capacity", "Why we can build it in two years");
  const fcards = [
    { ic: I.rocket, h: "Coding-agent multiplier", d: "Modern AI coding agents turn a ~3–4 FTE-year scope into something a focused team can deliver — and it dogfoods the very thing we're building.", a: TEAL },
    { ic: I.checkDouble, h: "Integration, not invention", d: "Most work wires together mature components: itksnap-dls, greedy, SegFlow4D, FireANTs, WorkspaceAPI, MONAI, Hugging Face.", a: AMBER },
    { ic: I.sitemap, h: "Clean architecture", d: "ITK-SNAP's strict three-layer separation gives agents clear contracts to target — fast, low-error work.", a: TEAL_D },
    { ic: I.vial, h: "Automated safety net", d: "The scripted --test harness + CI conformance gate agent-generated code by tests, not trust.", a: MINT },
  ];
  const cw = (PW - 2 * M - 0.4) / 2; // two cols
  fcards.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * (cw + 0.4), y = 1.85 + row * 2.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: 1.95, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: shadow() });
    s.addShape(pres.shapes.OVAL, { x: x + 0.32, y: y + 0.38, w: 0.78, h: 0.78, fill: { color: c.a } });
    s.addImage({ data: c.ic, x: x + 0.32 + 0.22, y: y + 0.38 + 0.22, w: 0.34, h: 0.34 });
    s.addText(c.h, { x: x + 1.35, y: y + 0.32, w: cw - 1.6, h: 0.45, fontSize: 17, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
    s.addText(c.d, { x: x + 1.35, y: y + 0.78, w: cw - 1.6, h: 1.05, fontSize: 12.5, color: SLATE, fontFace: BODY, margin: 0, valign: "top" });
  });
  bottomStrip(s, "Anchored on shipped, adopted code — a mature project, not a prototype or a rewrite.");
  footer(s, 13);

  // =========================================================== SLIDE 14 — deployment model
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "Deployment", "One core — install what your role needs",
    "Not two ITK-SNAPs: one codebase, the face(s) each user needs.");
  const rows = [
    { ic: I.server, who: "Automation / HPC / CI", inst: "pip headless library (no GUI)", a: TEAL },
    { ic: I.userMd, who: "Interactive expert", inst: "Desktop app (also agent-ready via MCP)", a: AMBER },
    { ic: I.eye, who: "Notebook + occasional human", inst: "pip library + web viewer (browser — no extra install)", a: MINT },
  ];
  const dpw = PW - 2 * M, dph = 0.92;
  rows.forEach((r, i) => {
    const y = 1.95 + i * 1.05;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: dpw, h: dph, fill: { color: CARD }, line: { color: LINE, width: 1 }, rectRadius: 0.07, shadow: shadow() });
    s.addShape(pres.shapes.OVAL, { x: M + 0.28, y: y + dph / 2 - 0.3, w: 0.6, h: 0.6, fill: { color: r.a } });
    s.addImage({ data: r.ic, x: M + 0.28 + 0.16, y: y + dph / 2 - 0.3 + 0.16, w: 0.28, h: 0.28 });
    s.addText(r.who, { x: M + 1.05, y, w: 4.0, h: dph, fontSize: 15, bold: true, color: NAVY, fontFace: HEAD, margin: 0, valign: "middle" });
    s.addImage({ data: arrowTeal, x: M + 5.0, y: y + dph / 2 - 0.16, w: 0.34, h: 0.34 });
    s.addText(r.inst, { x: M + 5.55, y, w: dpw - 5.8, h: dph, fontSize: 14, color: SLATE, fontFace: BODY, margin: 0, valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.2, w: dpw, h: 1.1, fill: { color: NAVY }, rectRadius: 0.07, shadow: shadow() });
  s.addText("Principles", { x: M + 0.32, y: 5.3, w: dpw - 0.6, h: 0.3, fontSize: 12, bold: true, color: MINT, charSpacing: 1, fontFace: HEAD, margin: 0 });
  s.addText([
    { text: "Headless core makes human-in-the-loop callable & scalable — not optional.", options: { breakLine: true } },
    { text: "Web viewer = zero-install human surface  ·  MCP can be C++ or Python (not Python-locked)  ·  pip = the engine, not the GUI app.", options: {} },
  ], { x: M + 0.32, y: 5.6, w: dpw - 0.64, h: 0.65, fontSize: 12.5, color: "E6EEF7", fontFace: BODY, margin: 0, valign: "top" });
  footer(s, 14);

  // =========================================================== SLIDE 15 — two tracks
  s = pres.addSlide(); s.background = { color: LIGHT };
  head(s, "Strategy", "Two routes — pick the ambition");
  function trackCard(x, w, color, tag, price, title, items, rec) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.9, w, h: 3.95, fill: { color: CARD }, line: { color: rec ? TEAL : LINE, width: rec ? 2.5 : 1 }, rectRadius: 0.09, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.9, w, h: 0.85, fill: { color } });
    s.addText(tag, { x: x + 0.35, y: 1.98, w: w - 2.2, h: 0.32, fontSize: 12, bold: true, color: "FFFFFF", charSpacing: 1.5, fontFace: HEAD, margin: 0 });
    s.addText(price, { x: x + 0.35, y: 2.26, w: w - 0.7, h: 0.45, fontSize: 22, bold: true, color: "FFFFFF", fontFace: HEAD, margin: 0 });
    s.addText(title, { x: x + 0.35, y: 2.9, w: w - 0.7, h: 0.55, fontSize: 14, bold: true, color: NAVY, fontFace: HEAD, margin: 0, valign: "top" });
    s.addText(items.map((t, i) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 6, color: SLATE } })),
      { x: x + 0.4, y: 3.62, w: w - 0.75, h: 2.15, fontSize: 12.5, fontFace: BODY, margin: 0, valign: "top" });
    if (rec) {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 1.95, y: 2.02, w: 1.6, h: 0.42, fill: { color: AMBER }, rectRadius: 0.1 });
      s.addText("RECOMMENDED", { x: x + w - 1.95, y: 2.02, w: 1.6, h: 0.42, fontSize: 10, bold: true, color: NAVY, align: "center", fontFace: HEAD, margin: 0, valign: "middle" });
    }
  }
  const tw = (PW - 2 * M - 0.5) / 2;
  trackCard(M, tw, TEAL, "TRACK 1 · DOMAIN-SPECIFIC TOOL", "$250K / 2 yr", "Focused: ITK-SNAP as agentic, human-in-the-loop hub", [
    "Aim 1 — API + MCP + human-in-the-loop primitives",
    "Aim 2 — model serving (itksnap-dls → DLE)",
    "Aim 3 — remote data access (one backend)",
    "Aim 4 — Slicer/DICOM-SEG interchange (FEBio stretch)",
  ], true);
  trackCard(M + tw + 0.5, tw, NAVY, "TRACK 2 · ECOSYSTEM", "$1M / 2 yr", "Ecosystem: ITK-SNAP + greedy + c3d + FireANTs + SegFlow4D", [
    "Everything in Track 1, fully built out",
    "GPU registration + 4D propagation as a pillar",
    "Full interop: Slicer + FEBio/OpenSim + napari",
    "LoRA domain-adaptation (stretch)",
  ], false);
  bottomStrip(s, "Recommendation: lead with a tight Track 1; Track 2 if we can staff ~4+ FTE-years across the ecosystem.", 6.05);
  footer(s, 15);

  // =========================================================== SLIDE 16 — next steps (dark)
  s = pres.addSlide(); s.background = { color: NAVY };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: PH, fill: { color: TEAL } });
  s.addText("DECISIONS & NEXT STEPS", { x: M, y: 0.6, w: 11, h: 0.35, fontSize: 14, bold: true, color: MINT, charSpacing: 3, fontFace: HEAD, margin: 0 });
  s.addText("What we need from the PIs", { x: M, y: 0.98, w: 12, h: 0.7, fontSize: 32, bold: true, color: "FFFFFF", fontFace: HEAD, margin: 0 });
  const ns = [
    { ic: I.route, t: "Choose a track", d: "Track 1 (focused, $250K) vs. Track 2 (ecosystem, $1M)." },
    { ic: I.users, t: "Confirm PI & maintainer alignment", d: "Roadmap fit + core-maintainer buy-in (required by the RFA)." },
    { ic: I.flag, t: "Host org / fiscal sponsor", d: "One organization receives & coordinates the grant." },
    { ic: I.share, t: "Interop partners", d: "Even informal interest from a Slicer / FEBio user strengthens the case." },
    { ic: I.bullseye, t: "Adoption evidence", d: "ITK-SNAP citation & usage numbers for the impact case." },
    { ic: I.calendar, t: "Timeline", d: "LOI due Jun 8 → invitations Jun 23 → full app Jul 21, 2026." },
  ];
  const nw = (PW - 2 * M - 0.5) / 2, nh = 1.25;
  ns.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * (nw + 0.5), y = 1.95 + row * 1.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: nw, h: nh, fill: { color: NAVY2 }, line: { color: "27496B", width: 1 }, rectRadius: 0.07 });
    s.addShape(pres.shapes.OVAL, { x: x + 0.28, y: y + 0.3, w: 0.64, h: 0.64, fill: { color: TEAL } });
    s.addImage({ data: c.ic, x: x + 0.28 + 0.17, y: y + 0.3 + 0.17, w: 0.3, h: 0.3 });
    s.addText(c.t, { x: x + 1.12, y: y + 0.2, w: nw - 1.3, h: 0.4, fontSize: 14.5, bold: true, color: "FFFFFF", fontFace: HEAD, margin: 0 });
    s.addText(c.d, { x: x + 1.12, y: y + 0.58, w: nw - 1.3, h: 0.55, fontSize: 11.5, color: "B9C9DC", fontFace: BODY, margin: 0, valign: "top" });
  });
  footer(s, 16);

  await pres.writeFile({ fileName: "ideas.pptx" });
  console.log("wrote ideas.pptx");
}
main().catch(e => { console.error(e); process.exit(1); });
