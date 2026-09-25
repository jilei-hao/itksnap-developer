# Q-001 — Which graphics card is recommended for the deep-learning server?

<!-- Public repo: no names, emails, institutions, home paths, patient IDs, or pasted data.
     Identity → users.local.md. Files → attachments/Q-001/. See README.md. -->

| | |
|---|---|
| Opened | 2026-09-24 |
| User | U-001 |
| Channel | not recorded |
| ITK-SNAP version | not stated. Question is about `itksnap-dls` 0.1.3/0.1.4 (nnInteractive + SAM2 only) |
| Platform | not stated |
| Type | question |
| Status | closed (2026-09-24) |
| Escalated to | — |
| Attachments | — |

## The question

The user wants to know which graphics card to use with the ITK-SNAP deep-learning server (DLS)
as it stands today, when it serves only nnInteractive and SAM2. Jilei asked for a simple, generic
answer rather than a benchmark.

## Conversation log

### 2026-09-24 — user

Asked which graphics card is recommended.

### 2026-09-24 — us (sent)

A short version of the draft:

> For the current ITK-SNAP deep-learning server, which runs nnInteractive and SAM2 (will be
> released with itksnap 4.6), we recommend any recent NVIDIA GPU with at least 12 GB of memory
> (VRAM).

## Investigation

**Which version.** Our submodule is `itksnap-dls` 0.1.3 (`76f609f`, branch `developer-doc`). PyPI's
latest is 0.1.4 (uploaded 2026-07-08). Diffing the 0.1.4 sdist against our tree shows one change:
the nnInteractive Hugging Face repo id moved from `nnInteractive/nnInteractive` to
`MIC-DKFZ/nnInteractive`. Everything below holds for both versions.

**What runs on the GPU** (`itksnap_dls/segment.py`):
- **nnInteractive v1.0** is 3D. It uses `nnInteractiveInferenceSession(device=…,
  use_torch_compile=False, do_autozoom=True)` at `segment.py:82`.
- **SAM 2.1 hiera-large** (`facebook/sam2.1-hiera-large`, `segment.py:148`) is 2D and slice-based.
  It's loaded through HF `transformers` with no dtype argument, so the weights are fp32:
  about 224M params, or roughly 0.9 GB. That weight figure is arithmetic, not a measurement.
- The device is chosen by `--device` in `__main__.py:37`: `cuda` if available, otherwise `cpu`,
  with `mps` also accepted. The DLS quick start (`docs/quick_start.md:17`) says an **NVIDIA GPU
  is required**. Nothing documents MPS as working.

**The official VRAM figure.** The nnInteractive README says:
"NVIDIA GPU (10 GB VRAM recommended; small objects work with <6 GB)". It doesn't mention Apple
Silicon or MPS. Fetched 2026-09-24 from github.com/MIC-DKFZ/nnInteractive.

**Only one model is resident per client.** Every `v2/start_session/{model}` call builds a fresh
model wrapper (`server.py:40-45`), which loads a new copy of the weights. ITK-SNAP ends the old
session before starting one with a different model (`DeepLearningSegmentationModel.cxx:805-812`
@ `62588ffc`). So a single ITK-SNAP never holds nnInteractive and SAM2 at the same time, and
nnInteractive alone sets the card size.

**Consequences for shared servers.**
- Each ITK-SNAP connected at the same time holds its own model copy. VRAM therefore grows with
  the number of simultaneous users.
- A client that exits without ending its session leaves its copy on the GPU until the server
  restarts. `docs/developer.md:134` documents this.

**How the recommendation was derived.**
- Consumer cards come in 8, 12, 16 and 24 GB tiers. The first common tier at or above nnInteractive's
  10 GB is 12 GB, hence "at least 12 GB".
- 16 GB or more is recommended for headroom with large images and shared servers.
- Memory is the constraint to prioritise. Speed only changes how long each interaction takes.

**Not measured**, so the reply avoids precise numbers for these:
- Actual peak VRAM of one nnInteractive session on a large CT
- SAM2-large runtime VRAM

If a precise number is ever needed, run one session on the Linux box with
`torch.cuda.max_memory_allocated()`.

**Possible follow-ups. None are escalated; none were raised by the user.**
- *Windows install.* PyPI's Windows `torch` wheels are, as far as I know, CPU-only, and CUDA builds
  come from download.pytorch.org. If so, a plain `pip install itksnap-dls` on Windows would quietly
  run on the CPU. **Unverified.** Check before it ever goes into a reply.
- *RTX 50-series (Blackwell).* These need torch built against CUDA ≥ 12.8. The `torch<=2.8.0` pin
  allows 2.7 and 2.8, which have cu128 builds, so they should work. **Untested by us.**

## Draft reply

None; the reply has been sent. The fuller draft, with its reasoning and card examples, is kept as
the detail of the KNOWN_ANSWERS.md entry for this question.

## For a fix session

Not applicable. This is a question, not a bug.
