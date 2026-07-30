# W3 — itksnap-dls refactor

**Status:** largely written, unmerged — needs promotion, not implementation
**Branch:** `itksnap-dls:feature/agentic-api` @ `bbaac51` (what the wrapper tracks)
**Depends on:** `segflow4d:main` @ `ed143db`
**Blocks:** W4 (auto-seg UI), W5 (propagation UI)

## Goal

`itksnap-dls:main` carries the modular server — pluggable segmentation models including
TotalSegmentator, a propagation module backed by segflow4d, and a test suite — with a stable HTTP API
that W4 and W5 can build against without it moving under them.

## Current state

> **Read this before writing any code.** The refactor already exists on `feature/agentic-api`.
> Verified 2026-07-30 by `git diff --stat origin/main origin/feature/agentic-api`: 21 files,
> **+1333 / −361**.

Shipped on `feature/agentic-api`, absent from `main`:

| Area | Detail |
|---|---|
| Module split | `itksnap_dls/segment.py` → `modules/segmentation/{models,router,session}.py`; `server.py` shrank by 249 lines |
| Propagation | `modules/propagation/{jobs,router}.py` — async job model, segflow4d-backed (`7ecf586`) |
| Shared | `common/image_utils.py` (117 lines) |
| Models | `bbaac51` — TotalSegmentator automatic-segmentation wrapper |
| Tests | `tests/{conftest,test_api,test_integration_nni,test_integration_sam2}.py` + `MRIcrop-orig/seg.gipl.gz` fixtures |
| Packaging | `pyproject.toml` +18 lines |

Branch topology (all subsets of `feature/agentic-api`):

| Branch | vs `main` | Unique content |
|---|---|---|
| `feature/agentic-api` | +6 / −0 | everything, plus TotalSegmentator |
| `features/segflow4d` | +4 / −8 | segflow4d integration |
| `test/dls_sam2` | +3 / −8 | tests + import/dependency fixes |
| `claude/create-developer-guide-xaMCx` | +1 / −7 | `developer.md` code-structure guide |

## Plan

1. Audit `feature/agentic-api` for anything genuinely agentic-API-specific (endpoints that exist only
   for the MCP server). Expectation from the diff: little to nothing — the module split, propagation,
   and TotalSegmentator are all general. Confirm, don't assume.
2. Open a PR from `feature/agentic-api` → `main` (or a clean `feature/dls-modules` if step 1 finds
   agentic-only code to leave behind).
3. Fold in `claude/create-developer-guide-xaMCx` (1 commit) or delete the branch.
4. Delete `features/segflow4d` and `test/dls_sam2` once subsumed.
5. Run the test suite on a GPU box and record pass/fail per file in `PROGRESS_LOG.md` — the
   integration tests need real inference.
6. **Freeze and version the HTTP API.** Write it down (endpoints, request/response shapes, job
   lifecycle) before W4/W5 start coding against it.
7. Re-point the wrapper: `.gitmodules` and `SUBMODULE_SYNC.md` move `itksnap-dls` from
   `feature/agentic-api` back to `main`. Note `SUBMODULE_SYNC.md` currently says `main` is wrong on
   purpose — that note is what this step retires.
8. Check `8ea18264` (upstream raised the minimum DLS version) still matches the promoted server.

## Open questions

1. **Does `sprint/caimi` depend on anything that would be left behind?** The agentic branch is what
   the October demo runs against; promoting to `main` must not break it.
2. **TotalSegmentator licensing and model weights** — how are weights distributed, and does that
   constrain what ITK-SNAP can ship or auto-download? Bears on W4's UX.
3. **API versioning scheme** — an explicit `/v1/` prefix, or negotiate via `/status`? ITK-SNAP already
   has a minimum-DLS-version check (`8ea18264`), which suggests the latter is the established pattern.
4. **Does propagation stay in the same server process** as segmentation, given it is long-running and
   GPU-heavy? The async job model in `modules/propagation/jobs.py` suggests yes; confirm it holds
   under a real 4D case.

## Done-criteria

- `itksnap-dls:main` contains the module split, TotalSegmentator, propagation, and tests.
- The wrapper tracks `main` again, and `SUBMODULE_SYNC.md` §1 says so.
- `pytest tests/` passes on a GPU box; the result and the box are recorded in `PROGRESS_LOG.md`.
- A written, versioned API contract exists that W4 and W5 cite.
- A test fails if a model is registered but not reachable through the router — the point of a
  pluggable-model design is that adding a model is enough.
