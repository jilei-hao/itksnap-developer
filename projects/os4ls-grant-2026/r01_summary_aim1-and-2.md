# ITK-SNAP R01 Proposal: Aim 1 & Aim 2 Summary

## Aim 1: Modernize ITK-SNAP GUI and Enable Remote Data Access

### Overview
Transform ITK-SNAP from a legacy Qt-based GUI to modern web technologies (React, Electron) and add seamless access to remote imaging archives (cloud-based, FlyWheel, XNAT).

### Critical Needs Addressed
1. **Technology obsolescence risk**: Qt is a single-company maintained C++ library; web technologies are more future-proof
2. **Data access patterns shifting**: Imaging increasingly stored on remote servers/cloud archives (FlyWheel, XNAT), forcing inefficient local download/upload workflows
3. **Developer recruitment**: Larger pool of web developers (HTML/JavaScript/React) than Qt experts

### Sub-Aim 1A: GUI Modernization (Qt → React + Electron)

**Approach:**
- Migrate ITK-SNAP GUI from legacy Qt to **React** (JavaScript/HTML reactive framework)
- Leverage existing clean architecture: GUI code separated into toolkit-independent "GUI model" layer + thin Qt-specific outer layer
  - This separation means only one layer of code needs replacing
  - Can be done in parallel with Aims 2 & 3
- Use **Electron** for multi-platform desktop deployment (embeds Chromium browser)
- Expose C++ GUI model layer as state variables via **WebSocket** technology for two-way communication between React frontend and C++ backend
  - Chosen over JavaScript bindings for better extensibility to running components in browser or on remote servers

**Benefits:**
- Future-proof for next 20 years
- Web-based derivatives possible (e.g., PACS integration, web viewers)
- Larger developer community can contribute
- Modern installation/update tools

**Key Decision:**
Uses network-based (WebSocket) interface rather than JavaScript bindings because it:
- Enables running ITK-SNAP components in browser
- Allows core processing on remote servers
- Better separation of concerns

### Sub-Aim 1B: Remote Archive Integration + BIDS Support

**Explorer Panel Design:**
Add new GUI explorer panel for navigating remote data with uniform UX across backends:
- **File system backends**: Organized by folders/files; auto-detect DICOM series and BIDS-organized folders; display metadata (participant, session, scan type)
- **Database backends** (e.g., FlyWheel): Organized by participant/session with advanced metadata-based search

**Workspace Integration:**
- Extend existing workspace files to reference remote images
- Workspaces describe how images organized/visualized in single session + preferences/metadata/anatomical labels
- Users can update workspace files on remote backend without downloading images locally

**Implementation Strategy:**
- Pluggable architecture with common interface between explorer GUI and backend-specific plugins
- Initial plugins: local filesystem, remote Linux filesystem (via SSH), FlyWheel (via CURL API)
- Framework for community to develop additional plugins (e.g., XNAT)

**Technical Details:**
- **Remote Linux backend**: Lightweight SSH agent for efficient browsing, DICOM/BIDS scanning, fast partial file access
- **FlyWheel plugin**: Uses CURL library over SSL protocol
- **Credentials**: Managed via OS keychain (secure best practices)
- **BIDS support**: Native compatibility with Brain Imaging Data Structure standard

**User Experience Goal:**
Finding, viewing, and segmenting remotely stored imaging datasets as seamless as working with local files.

### Aim 1 Rigor & Reproducibility

**Milestones & Use Cases:**
- Features organized into hierarchy with specific use cases (e.g., "locate, access, and edit segmentation from FlyWheel pipeline in ITK-SNAP")
- GUI tests scripted for automated testing
- Public GitHub issue tracking ensures community feedback and accountability

**Continuous Integration/Deployment:**
- Transition from traditional long-release cycles to modern CI/CD
- Electron auto-update features enable faster feature/bug-fix delivery

**Alternative Strategies:**
- Vue framework as alternative to React
- SCP/SFTP as simpler alternative to remote SSH agent
- Non-critical features (advanced FlyWheel search) can be delegated to community

**Risk Mitigation:**
- Parallel implementation with Aims 2 & 3 ensures Aim 1 failure doesn't block other work
- Initial Aims 2/3 implementation uses Qt GUI; transition to web in later years

---

## Aim 2: Transform ITK-SNAP into AI-Assisted Segmentation Platform

### Overview
Integrate a dynamically curated library of AI-based segmentation models (foundation models, task-specific, and interactive) into ITK-SNAP, accessible from GUI with optional local/remote/cloud GPU inference.

### Critical Need Addressed
**Gap between AI advances and clinical accessibility**: Latest deep learning models achieve state-of-the-art performance but require:
- Data science/coding expertise
- Access to powerful GPUs
- Complex environment setup

Most clinicians/researchers stuck with outdated commercial tools or must collaborate with data scientists. ITK-SNAP's wide adoption + generalist design makes it ideal to democratize access to cutting-edge AI.

### Preliminary Work: nnInteractive Integration (2025)

**Current Implementation:**
- Integrated **nnInteractive** foundation model for interactive 3D segmentation
- Transforms simple prompts (clicks, scribbles, lasso, erasures) into complex 3D segmentations
- Zero-shot adaptation: works on new domains without retraining (trained on >64k images from 120 datasets)
- Supports multi-slice-plane edits (axial, coronal, sagittal)
- **Winner of CVPR 2025 Foundation Models for Interactive 3D Biomedical Image Segmentation Challenge**

**GPU Infrastructure Design:**
- Service runs separately from ITK-SNAP over secure network connection
- Can run locally, on remote GPU server (SSH), or in cloud (Google Colab)
- Solves problem: many users lack powerful local GPU but need near real-time performance (1-5 sec vs. minutes on CPU)

### Sub-Aim 2A: Dynamically Curated Model Library

**Goal:** Provide ITK-SNAP users access to broad, continuously updated collection of models via GUI without coding expertise.

**Model Classes to Support:**
1. **Task-specific fully automatic** (e.g., spleen segmentation in CT)
2. **Foundation/generalist interactive models** (e.g., MedSAM2 with basic interactions; nnInteractive with iterative editing)
3. **Medical language-vision models** (LVMs) using text prompts for segmentation

**Implementation: Deep Learning Extensions (DLE) Python Module**
- Serves as conduit between ITK-SNAP GUI and Python APIs (MONAI, Hugging Face, PyTorch)
- **FastAPI + WebSockets** for secure bidirectional communication
- Handles: finding, downloading, executing, fine-tuning models

**Model Discovery & Management:**
- New "model explorer" panel in ITK-SNAP GUI
- Browse, search available models
- Rate/review models (crowdsourced quality assessment)
- Familiar ITK-SNAP tools (paintbrush, polygon, ROI, landmarks) map to model prompts
- Outputs (segmentations, confidence maps) load as native ITK-SNAP objects

**Aggregator Integration:**
- Leverage **Hugging Face** (universal model aggregator) and **MONAI** (medical imaging specific)
- MONAI "bundles" already describe preprocessing/postprocessing
- DLE wraps models with ITK-SNAP-specific mappings (prompt-to-input, output-to-object)

**Curation Strategy:**
- GitHub pull request system for wrapper oversight
- Model ecosystem grows quickly/dynamically
- Community can contribute wrappers following provided templates/examples

**Seamless Remote GPU Access:**
- Lightweight SSH agent (from Aim 1B) launches DLE on remote server on user's behalf
- Handles GPU allocation/queueing across multiple ITK-SNAP frontend users
- Caches images server-side; supports partial image updates to minimize communication overhead

### Sub-Aim 2B: Continuous Learning via Domain Adaptation

**Problem:** Most workflows involve sequential segmentation of images from same domain (e.g., monitoring ARIA in Alzheimer's patients, training data generation). Without adaptation, users repeat same corrections repeatedly.

**Conventional Solution (problematic):**
- Fine-tuning (retraining) foundation models on new domain is expensive/slow
- Introduces workflow interruptions
- Foundation models too large to retrain efficiently

**Proposed Solution: Low-Rank Adaptation (LoRA)**

**LoRA Mechanism:**
- Decomposes weight matrices into low-rank + high-rank components: **W = AB^T + Ŵ**
- Fine-tuning only optimizes small low-rank matrices (A, B) instead of full weights
- **Reduces parameters by orders of magnitude** compared to full fine-tuning
- Doesn't alter model architecture (no retraining needed)

**Implementation:**
- Server-side storage of user edits/corrections provides training data for continuous learning
- GUI tracks related segmentation tasks via workflow tags
- Users can launch/revert continuous learning checkpoints via GUI
- Integrated with DLE module and MONAI Label framework (already provides some features)

**Alternative Strategy:**
- **UniverSeg approach**: Models trained to accept "support set" (prior examples) at inference time
- Learns how to adapt by example without explicit fine-tuning
- Trade-off: requires foundation model backbone modifications + retraining on large multi-domain dataset
- Preferred approach: **LoRA** (simpler, doesn't require model retraining)

### Aim 2 Evaluation Strategy

**Benchmark Datasets & Metrics:**
- **CVPR 2025 MedSegFM challenge** [158] + IMed-361M benchmark dataset
- Simulated user interactions for quantifying model performance
- Tools readily adaptable to measure Sub-Aim 2B continuous learning

**Human Raters Study:**
- 3 public datasets (cardiac CT, brain tumor MRI, mitral valve ultrasound)
- Radiology residents/fellows perform segmentation with:
  - No AI assistance (baseline)
  - nnInteractive without adaptation
  - nnInteractive + naive fine-tuning
  - nnInteractive + support set adaptation
  - nnInteractive + LoRA
- Measure: intra/inter-rater reliability, task completion time, system usability surveys (standardized SUS)

**Primary Success Criterion:**
- Statistically significant + practically meaningful improvement (ΔDice > 0.02) for LoRA vs. baseline nnInteractive
- Power analysis indicates **n=156 images** sufficient for 80% power at α=0.05
- Both simulated + human evaluation adequately powered

### Aim 2 Rigor & Reproducibility

**Development Practices:**
- Same milestone-centered strategy + use case-driven success criteria as Aim 1
- Continuous integration/testing
- GitHub pull request review system

**Risk Mitigation:**
- Sub-Aim 2A builds on proven nnInteractive integration (low risk)
- Even partial completion yields significant expansion over current functionality
- Sub-Aim 2B alternative strategies: UniverSeg approach or naive fine-tuning fallback
- Features integrate into platform in parallel with Aims 1 & 3 (failure doesn't block others)

---

## Connecting Aims 1 & 2

**Synergy:** 
- Web-based Aim 1 GUI enables browser-embedded segmentation workflows
- Remote DLE service (Aim 2) runs on same remote servers as data archives (Aim 1B)
- Unified remote architecture: both data access + GPU inference available to users without powerful local hardware
- WebSocket communication layer (Aim 1A) naturally extends to DLE model serving (Aim 2A)

**Parallel Development:**
- Years 1-3: Aims 1-3 developed in parallel on Qt platform
- Year 4: Integration of new AI/longitudinal features with web GUI
- Year 5: System testing (Aim 4) using all integrated features

---

## Key Technologies & Frameworks

**Frontend Stack:**
- React (state management, reactive components)
- Electron (multi-platform desktop)
- WebSocket (bidirectional communication)

**Backend/AI Stack:**
- C++ core (ITK, VTK, GreedyReg)
- Python DLE module (FastAPI, PyTorch, MONAI, Hugging Face)
- nnInteractive (foundation model winner, CVPR 2025)

**Infrastructure:**
- GitHub (version control, CI/CD, issue tracking)
- SSH agent (remote server access)
- FlyWheel/XNAT APIs (remote archive backends)
- Google Colab support (cloud GPU access)

---

## Summary of Deliverables

### Aim 1 Deliverables
1. React-based GUI replacing legacy Qt
2. Electron desktop application
3. Remote archive explorer (FlyWheel, Linux filesystem, XNAT-ready)
4. BIDS-aware file organization
5. Workspace management for remote data
6. Continuous integration/deployment pipeline

### Aim 2 Deliverables
1. Deep Learning Extensions (DLE) Python module
2. Model explorer GUI panel
3. Curated library of segmentation models (task-specific + foundation models + LVMs)
4. LoRA-based continuous learning implementation
5. Human evaluation study validating performance improvements
6. Community templates/documentation for model wrapping

---

## Timeline (from proposal)

- **Years 1-3**: Parallel development of Aims 1-3 (Qt platform)
- **Year 4**: Integration of Aims 2-3 features with new web GUI (Aim 1)
- **Year 5**: System testing (Aim 4), final integration, dissemination

---

## Note for Claude Code Development

This proposal positions ITK-SNAP for two-decade sustainability while democratizing AI-driven medical image analysis. The architecture separates:
- **UI layer** (React/Electron) — replaceable, maintainable, future-proof
- **Business logic layer** (GUI model) — toolkit-independent, stable
- **Core imaging layer** (ITK/VTK) — well-maintained open-source libraries
- **AI service layer** (DLE) — pluggable, extensible via community contributions

This clean separation enables:
- Parallel development of independent components
- Community contributions (model wrappers, new backends, UI components)
- Future evolution to web-only deployment
- Sustainable long-term maintenance