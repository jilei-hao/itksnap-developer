# RESUME — ITK-SNAP Agentic API (implementation phase)

You are resuming the ITK-SNAP "agentic API" prototype after a machine switch.
The PLANNING phase is complete; implementation has begun. Thesis unchanged:
"model proposes, human disposes" — expose expert human judgment as a callable,
resumable, audited pipeline step an external agent can invoke, shown on camera.

## Read first (authoritative)
- `projects/agentic-api/docs/agentic-prototype-plan.md`
  - §0.1 = locked decisions + the `features/segflow4d` findings
  - §5   = recommended MVP + video suite (P2 first, then flagship P1)
  - §6   = risks / things to verify
  - §8   = foundation-model roadmap (TotalSegmentator flagship, VISTA3D strategic)
  - §9   = pip-distribution + download-metrics strategy
- `projects/agentic-api/PROGRESS_LOG.md` — what happened, newest first.
- Auto-memory `project_agentic_api` — condensed state + citations.

## Machine-switch setup (do this first on the new machine)
The DLS work lives on a NEW branch of the `itksnap-dls` submodule, pushed to origin
(`github.com/jilei-hao/itksnap-dls`):

  `feature/agentic-api`  =  origin/main  +  origin/features/segflow4d (merged)  +  TotalSegmentator wrapper

From the wrapper repo root:
```bash
git pull                              # gets this handoff + plan on wrapper `main`
cd itksnap-dls
git fetch origin
git switch feature/agentic-api        # branch is on origin; sets up tracking
git pull
```
NOTE: the wrapper repo's `.gitmodules` still tracks itksnap-dls `main` (deliberate),
and the submodule pointer was NOT committed — so check out the branch manually as above.
(itksnap-dls is MIT; branch naming here is `feature/` singular, unlike the sibling
`features/segflow4d` which is plural.)

## State at this handoff
DONE and pushed:
- `feature/agentic-api` created + `features/segflow4d` merged (merge `4c92155`).
- `TotalSegmentatorWrapper` implemented (commit `bbaac51`):
  - `itksnap_dls/modules/segmentation/models.py` — `ModelWrapper.AUTOMATIC` flag +
    `run()` contract; `TotalSegmentatorWrapper` (set_image→run→multi-label result;
    lazy TS import; cuda→"gpu" device map; NIfTI temp-file round-trip, `ml=True`;
    fast/3mm default; `get_label_map()`); registered in `get_model_listing()` (+
    `"automatic"` field) and `instantiate_model_wrapper()`.
  - `itksnap_dls/common/image_utils.py` — `encode_label_result()` (label-preserving
    int16; the existing `encode_seg_result` binarizes and would flatten TS's labels).
  - `itksnap_dls/modules/segmentation/router.py` — `GET /v2/run_automatic/{session_id}`
    and `GET /v2/models/{model_id}/labels`.
  - `pyproject.toml` — `TotalSegmentator` as optional `[totalseg]` extra.
- STATIC-VERIFIED ONLY (compile + AST + existing test-compat). NOT run live —
  this machine lacks fastapi/torch/SimpleITK/TotalSegmentator.

## Next steps (prioritized)
1. SMOKE-TEST on a GPU box: `pip install -e '.[totalseg]'`, start the server, then
   `GET /v2/start_session/TotalSegmentator` → `upload_raw` →
   `GET /v2/run_automatic/{id}?fast=true`. Confirm the multi-label result decodes
   with correct geometry vs the input (int16, client reshapes to uploaded dims).
2. SYNC→ASYNC: full-res TS is multi-minute; move automatic inference to the async
   job pattern (`modules/propagation/{router,jobs}.py`) per §8. Keep the sync
   endpoint for fast-mode demos.
3. (If heading to a shippable product) hard-whitelist the Apache `total`/`total_mr`
   tasks; several TS subtasks carry non-commercial weights (§8 license note).
4. Start the MVP vertical slice (§5): P2 "audited callable" first — the audit-record
   serializer over `UndoDataManager` — then the live-GUI command channel over
   `SNAPTestQt`, then stitch into one local MCP tool namespace.
5. Packaging nit for §9: `[tool.setuptools] packages=["itksnap_dls"]` omits the new
   `modules`/`common` subpackages — fine for editable/source runs, must fix before
   building a wheel.

## How to work
- Integration over invention; ground every claim in real files + line numbers.
- The human-correction step is the visual star — keep it a real code path.
- Ask before consequential assumptions; state the ones you make.
