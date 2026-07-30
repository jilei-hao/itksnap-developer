# W7 — cmesh release and itksnap mesh refactor

**Status:** library exists; release and itksnap side not started
**Branch:** `convert-mesh:main` @ `45482ca`
**Depends on:** a cmesh release tag

## Goal

`cmesh` is a released, versioned library; ITK-SNAP consumes it as a submodule; and the mesh
operations currently open-coded in `Logic/Mesh/` call it instead of reimplementing it.

## Current state

`convert-mesh` @ `45482ca` — *"Reorganize sources under `src/cmesh/` and add session/version
support"*, 2026-06-25. Layered as `src/cmesh/{core,cli,impl}`:

- `core/` — `ComputeNormals`, `DecimateMesh`, `ExtractIsoSurface`, `FlipNormals`,
  `FlipPolyFacesFilter`, `ImageIO`, `MergeArrays`, `MeshDiff`, plus `Backend.h` / `Error.h`
- `cli/` — `Run.{h,cxx}` + `internal/` (`Adapters`, `DataStack`, `DataItem`, `Driver`, `ParseUtil`)
- Installable: `CMakeLists.txt`, `Config.cmake.in`, `ConvertMeshLibrary.cmake`, `Testing/`, `docs/`

**No git tags.** There has never been a cmesh release.

Parity reference: `cmrep` (wrapper submodule on `local`) — ground truth for ConvertMesh output. See
`projects/` memory notes on the Eigen3-vs-ITK-Eigen pitfall and the `mesh2img -ref` bug; both bite
when linking cmesh into another CMake project.

ITK-SNAP side: `Logic/Mesh/` is VTK-based mesh generation and processing. Nothing has been surveyed
against cmesh's `core/` yet — step 1 below is the real starting point.

## Plan

1. **Survey first.** Map each `Logic/Mesh/` operation to a `cmesh/core/` equivalent. Produce a table:
   replaceable / partly replaceable / itksnap-only. This determines whether W7 is a small win or a
   large refactor, and therefore whether it belongs in 4.6.0 at all.
2. Tag `cmesh` v1.0.0 — settle the public API surface, the version scheme, and what `session/version
   support` (`45482ca`) is meant to guarantee.
3. Run the cmrep parity tests against the tag; record results.
4. Add `convert-mesh` as a submodule under `itksnap/Submodules/`. Note the existing convention there:
   nested submodules are **pinned by SHA, not tracked by branch** (`SUBMODULE_SYNC.md`). A tag fits
   that convention.
5. Build integration: cmesh as a subproject alongside `c3d`/`greedy`/`digestible`. Watch for the
   Eigen3-vs-ITK-Eigen collision.
6. Refactor `Logic/Mesh/` per the step-1 table, incrementally, keeping mesh tests green throughout.

## Open questions

1. **Does this belong in 4.6.0?** It is the broadest-reach item on the list and the least specified.
   Step 1 should answer it; if the survey shows a deep refactor, defer to 4.8 — this is the first
   named cut candidate in `SPRINT_PLAN.md`.
2. **Nested-submodule policy.** All three existing nested submodules are upstream repos not owned by
   this fork; `cmesh` would be the first fork-owned one. Does it move to `pyushkevich` first?
3. **Duplicate VTK usage.** Both ITK-SNAP and cmesh use VTK. One VTK, one version, one config —
   confirm cmesh does not pin a different VTK than ITK-SNAP's (which is itself unsettled; see
   [../change_tracking.md](../change_tracking.md) §6.1).
4. **What does the user gain?** If it is purely internal, it earns no release-note line and competes
   with W4/W5 for time. Name the user-visible benefit, or accept it as internal-only.
5. **Eigen3 vs ITK-Eigen** — a known parity-testing pitfall; verify at link time, not at debug time.

## Done-criteria

- A `cmesh` release tag exists, and cmrep parity results against that tag are recorded.
- `itksnap/Submodules/convert-mesh` pinned to the tag; a fresh recursive clone builds.
- The step-1 survey table is committed — it is the artifact that justifies the scope, and it stays
  useful even if the workstream is cut.
- Mesh tests pass before and after each refactor step, and at least one test would fail if a
  cmesh-backed operation returned different geometry than the VTK path it replaced.
