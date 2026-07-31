# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ITK-SNAP (v4.4.0) is a C++17 medical image segmentation application built on ITK, VTK, and Qt6. It provides interactive 3D segmentation tools including level-set methods, AI-assisted segmentation (nnInteractive), and mesh visualization.

## Repository Layout (wrapper repo)

This directory (`itksnap-developer`) is a **wrapper/meta-repository** that aggregates ITK-SNAP and its sibling projects as git submodules. Most build/test commands below run from this root and operate inside `itksnap/`.

Top-level submodules (all under `github.com/jilei-hao/`), each tracking the branch noted in `.gitmodules`:

| Path | Branch | Purpose |
|---|---|---|
| `itksnap/` | `sprint/caimi` | Main ITK-SNAP application (architecture documented below). `sprint/caimi` = `feature/cardiac-io` + the Linux/GCC build patches; it is the active sprint working branch. |
| `greedy_python/` | `test/integration` | Python bindings for Greedy (see below) |
| `convert-mesh/` | `main` | ConvertMesh CLI/library |
| `cmrep/` | `local` | cm-rep; ground-truth parity reference for ConvertMesh |
| `FireANTs/` | `main` | Registration project |
| `itksnap-dls/` | `main` | Deep-learning segmentation service |
| `segflow4d/` | `main` | 4D segmentation flow |

Note: `itksnap/` has its own nested submodules (`Submodules/{c3d,greedy,digestible}`), so clones must be recursive.

```bash
# Fresh clone (pulls every submodule, including itksnap's nested ones):
git clone --recursive git@github.com:jilei-hao/itksnap-developer.git
# After a plain clone, or to fill in new submodules:
git submodule update --init --recursive
```

**Updating submodules:**
- Bump all to the latest commit of their tracked branch: `git submodule update --remote`, then commit the resulting pointer changes in this wrapper.
- After editing inside a submodule: commit & push **inside the submodule first**, then `git add <path>` and commit in this wrapper to record the new pointer.

## Build System

**Dependencies:** ITK ≥ 5.4, VTK ≥ 9.5.2, Qt6 (Widgets, OpenGL, Concurrent, Qml, LinguistTools), libcurl, libssh. CI uses ITK v5.4.0, VTK 9.5.2, Qt 6.8.1.

> ⚠️ **VTK floor raised to 9.5.2 on `staging/v460` (2026-07-30, `7cc60053`).** Both dev machines are
> still on 9.3.x (macOS `lib/vtk/install` = 9.3.1, Linux `vtk-dev/installed` = 9.3.0), so **`cmake`
> will fail to configure against `staging/v460` until VTK is upgraded**. Existing build trees keep
> working until they are reconfigured. `config.local.sh` and the Linux paths below need updating
> alongside the upgrade.

**Critical:** After cloning, initialize submodules before building:
```bash
git submodule init
git submodule update
# or: git clone --recursive <url>
```

**Configure and build** (out-of-source, using Ninja):
```bash
mkdir build && cd build
cmake -G Ninja \
  -DITK_DIR=/path/to/itk/build \
  -DVTK_DIR=/path/to/vtk/install/lib/cmake/vtk-9.3 \
  -DCMAKE_BUILD_TYPE=Release \
  ../itksnap
ninja
```

### Building on Linux (Ubuntu 24.04)

ITK-SNAP builds and runs on Linux; the notes below capture the first successful build
on Ubuntu 24.04 (GCC 13, CMake 3.28, Ninja). A machine-local `config.local.sh`
(gitignored) records the dependency paths and is sourced by `scripts/build-release.sh`.

**1. System packages (Qt6 toolchain via apt).** The project's CMake uses the `Qt6Qml`
and `Qt6LinguistTools` modules, which are absent from a qtbase-only Qt build:
```bash
sudo apt-get install -y qt6-base-dev qt6-base-dev-tools \
  qt6-declarative-dev qt6-tools-dev qt6-l10n-tools
# build tooling, usually already present: cmake ninja-build g++ libcurl4-openssl-dev libssh-dev
```
Ubuntu 24.04 ships Qt 6.4.2. The project's CMake assumes Qt ≥ 6.7 for two macros (see
gotchas); these are version-guarded so 6.4.2 configures cleanly, losing only bundled UI
translations and the install-time deploy script (neither needed to build or run locally).

**2. Dependency locations on this machine** (recorded in `config.local.sh`):

| Dep | Path | Notes |
|---|---|---|
| ITK 5.4.4 | `itk-dev/installed/lib/cmake/ITK-5.4` | Use the **installed** tree, **not** `build-release-dynamic-540rc02` (stale — see gotchas) |
| VTK 9.3.0 | `vtk-dev/build-release-dynamic-930` | Built with `RenderingExternal` and `cmake --install`-ed to `vtk-dev/installed` |
| Qt 6.4.2 | `/usr` (apt) | passed as `CMAKE_PREFIX_PATH=/usr` |

**3. Configure & build:**
```bash
scripts/build-release.sh          # sources config.local.sh; or run cmake directly:
cmake -G Ninja -S itksnap -B build-release -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=/usr \
  -DITK_DIR=/home/jileihao/dev/itk-dev/installed/lib/cmake/ITK-5.4 \
  -DVTK_DIR=/home/jileihao/dev/vtk-dev/build-release-dynamic-930
ninja -C build-release ITK-SNAP   # binary: build-release/ITK-SNAP
```

**4. Run (headless / over SSH).** ITK-SNAP is a Qt GUI app; with no display use Xvfb:
```bash
xvfb-run -a build-release/ITK-SNAP                                   # launch GUI
xvfb-run -a build-release/ITK-SNAP --test VolumeRendering \
  --testdir itksnap/Testing/TestData                                 # smoke test, exit 0 = OK
```

**Linux gotchas (and the fixes applied):**

- **Stale ITK build → link failure.** `itk-dev/build-release-dynamic-540rc02` had its
  source updated (Oct 2025: `itk::TransformBase` gained `Input/OutputSpaceName`) without
  recompiling, so its `libITKTransform` lacks those symbols and linking ITK-SNAP fails
  (`undefined reference to itk::TransformBaseTemplate<double>::GetOutputSpaceName`). ITK
  uses `extern template`, so consumers rely entirely on the lib. Fix: build against the
  consistent installed **ITK 5.4.4**. (To use the rc02 tree instead, rebuild ITK first.)

- **VTK missing `RenderingExternal`.** `QtFrameBufferOpenGLWidget` (the 3D render widget)
  uses `vtkExternalOpenGLRenderWindow`, so VTK must be built with
  `-DVTK_MODULE_ENABLE_VTK_RenderingExternal=YES`. The machine's VTK was also built against
  a since-deleted Qt 6.2.4; it was reconfigured against apt Qt 6.4.2, rebuilt, and
  `cmake --install`-ed to `vtk-dev/installed`. Because the shell's `LD_LIBRARY_PATH` points
  at `vtk-dev/installed`, the install step is **required** so the runtime VTK matches the
  build (it also refreshes VTK for the other projects that consume `vtk-dev/installed`).

- **Qt version-API guards.** `qt_add_translations(TARGETS …)` needs Qt ≥ 6.7 and
  `qt_generate_deploy_script` needs Qt ≥ 6.5; on `feature/cardiac-io` both are unguarded
  upstream, so each call is wrapped in `if(Qt6Widgets_VERSION VERSION_GREATER_EQUAL …)` in
  `itksnap/CMakeLists.txt` (the older `test/dls_sam2` branch used a `QTVERSION` guard; this
  branch has no such variable). ~~The `VTK 9.3.1` hard requirement in
  `itksnap/CMake/standalone.cmake` was relaxed to `9.3`.~~ **Reversed on `staging/v460`:** the floor
  was *raised* to 9.5.2 (`7cc60053`). The stated reason for the old relax — "CI's 9.3.1 still
  satisfies it" — was a misreading; `FIND_PACKAGE` declares a minimum and VTK's config-version is
  compatible-if-newer, so nothing needed relaxing. It was really a workaround for a local 9.3.0.

- **Stricter compiler than macOS.** GCC/libstdc++ rejected code Clang accepted: streaming
  `std::string` into `qDebug()`/`qInfo()` is ambiguous (wrap with `QString::fromStdString`),
  and `<QTimeZone>` / `<QDialogButtonBox>` must be included explicitly rather than relied on
  transitively.

- **`build-release.sh` rejected `itksnap` after the submodule conversion.** The script
  guarded on `[ -d "$SNAP_DIR/.git" ]`, but once `itksnap/` became a git submodule its `.git`
  is a gitlink **file**, not a directory, so the guard failed with "itksnap not found …".
  Fixed to accept either (`[ -e .git ]` + require `CMakeLists.txt`).

**Source patches.** Originally applied on `test/dls_sam2`; the submodule now tracks
**`feature/cardiac-io`** (branched from upstream `master`, which has since moved VTK to 9.5.2).
**All six were re-verified as still required on `feature/cardiac-io` and re-applied** in the
2026-07-17 Linux build (the branch ships none of them). Each row notes the exact site:

| File | Change |
|---|---|
| `CMake/standalone.cmake` | ~~`VTK 9.3.1` → `9.3`~~ — **superseded**: raised to `9.5.2` on `staging/v460` (`7cc60053`). Do not re-apply the relax. |
| `CMakeLists.txt` | wrap `qt_add_translations` in `if(Qt6Widgets_VERSION VERSION_GREATER_EQUAL 6.7)` and the Linux `qt_generate_deploy_script` block in `… ≥ 6.5` |
| `GUI/Qt/Components/SSHTunnelWorkerThread.cxx` | `QString::fromStdString(…)` around 3 std::string streams (lines 67, 74, 82: `message` ×2, `ready_info.hostname`) |
| `GUI/Qt/Components/SNAPQtCommon.cxx` | add `#include <QTimeZone>` — needed for `.timeZone()`/`.toTimeZone()` at line ~636 (the type name never appears literally, so grep for it misses; only the compiler catches it) |
| `GUI/Qt/Windows/DeepLearningServerPanel.cxx` | add `#include <QDialogButtonBox>`, wrap `p->GetHostname()` (std::string) in the line-181 qDebug stream |
| `Testing/GUI/Qt/SSHTunnelTest/main.cxx` | `QString::fromStdString(…)` around 3 std::string streams (built only by the `all` target, not `ITK-SNAP` alone) |

> Note: `ninja ITK-SNAP` builds just the app, but `scripts/build-release.sh` / `ninja`
> build the `all` target (CLI tools + test executables). Build `all` to catch everything.

**Build a specific target:**
```bash
ninja ITK-SNAP          # main application
ninja SlicingPerformanceTest testTDigest iteratorTests
```

**Known test status on Linux headless (Xvfb + llvmpipe software OpenGL), 2026-07-17.**
`xvfb-run -a ctest` → **30/33 pass**. The 3 failures are pre-existing on `feature/cardiac-io`
and unrelated to the Linux build patches above:

- **`4DContinuousRenderingD`** — CMake `GUI_TESTS` typo. The runner maps a test name to
  `:/scripts/Scripts/test_<name>.js`, but the entry has a stray trailing `D`, so it looks for
  `test_4DContinuousRenderingD.js` (does not exist). The real script `test_4DContinuousRendering.js`
  exists and is in `TestingScripts.qrc` but is orphaned (no matching entry). Fix: rename the
  `GUI_TESTS` entry `4DContinuousRenderingD` → `4DContinuousRendering` in `itksnap/CMakeLists.txt`.
- **`4DReplayWithMeshUpdate`** — **timing-flaky under llvmpipe, not a logic regression.** Same
  binary passes when the cold-start mesh build is fast (verified: replay free-runs through all 11
  frames and Phase B passes); it fails only when the first software-rendered mesh build exceeds
  the test's 8 s Phase-A budget, so `on4DReplayTimeout` (`MainImageWindow.cxx:1769`) stays gated
  on `IsMeshUpdating`. Latent fragility worth noting: that guard is set in `ViewPanel3D.cxx:391`
  before the `QtConcurrent::run` and cleared **only from inside the worker** (`Generic3DModel.cxx:282`)
  — there is no `QFutureWatcher::finished` main-thread completion handler, so a worker that hangs or
  throws anything other than `bad_alloc`/`IRISException` leaves replay blocked permanently.
- **`RemoteImageLoadTest_Cache`** — network test; the download succeeds but `CacheMetadata.xml`
  is not written afterward.

Note: some GUI tests are timing-sensitive under software rendering — `4DReplayWithMeshUpdate`
also intermittently fails to populate the layer-inspector rows when launched as a standalone
`ITK-SNAP --test …` process, yet reaches Phase A reliably under `ctest`.

## Running Tests

Tests use CTest. All commands run from the build directory:

```bash
# Run all tests
ctest

# Run a single test by name
ctest -R BasicSlicingTestX39

# Run tests with verbose output
ctest -V

# On Linux (headless), GUI tests require Xvfb:
xvfb-run -a ctest

# Submit to CDash dashboard (as done in CI)
ctest -D ExperimentalStart
ctest -D ExperimentalUpdate
ctest -D ExperimentalConfigure
ctest -D ExperimentalBuild
ctest -D ExperimentalTest
ctest -D ExperimentalSubmit
```

Test data lives in `Testing/TestData/`. GUI tests are run by invoking the main application with `--test <TestName> --testdir <path>`.

## Code Architecture

The codebase follows a strict three-layer architecture:

### 1. Logic Layer (`Logic/`)
Pure computational layer with no GUI dependencies. Key components:
- `Logic/Framework/IRISApplication.cxx` — top-level application state and coordination
- `Logic/Framework/IRISImageData.cxx` / `SNAPImageData.cxx` — image data containers for manual vs. semi-automatic segmentation modes
- `Logic/ImageWrapper/` — abstraction over ITK images; `ImageWrapper<T>` wraps a typed ITK image and provides display/slice/IO services
- `Logic/LevelSet/` — snake/level-set segmentation algorithms
- `Logic/Mesh/` — VTK-based mesh generation and processing
- `Logic/Slicing/` — 2D slice extraction pipeline (OpenGL2-accelerated)
- `Logic/WorkspaceAPI/` — public API for workspace manipulation

### 2. GUI Model Layer (`GUI/Model/`)
Mediates between Logic and Qt widgets. Models inherit from `AbstractModel` and use the property/event system defined in `Common/PropertyModel.h` and `Common/SNAPEvents.h`. This layer has no direct Qt widget dependencies—it communicates through events and properties.

### 3. GUI Qt Layer (`GUI/Qt/`)
Pure Qt6 presentation. Organized into:
- `Components/` — reusable widgets
- `Coupling/` — bindings between GUI model properties and Qt widgets (the "coupling" pattern connects `PropertyModel` values to Qt controls bidirectionally)
- `View/` — OpenGL-backed slice and 3D views
- `Windows/` — top-level window and dialog classes
- `main.cxx` — application entry point

### Common Layer (`Common/`)
Shared infrastructure used by all layers:
- `AbstractModel.cxx/h` — base class for all models, provides ITK-style event firing
- `PropertyModel.h` — typed, observable property system (45K lines, central to the GUI model pattern)
- `SNAPEvents.h` — event type definitions
- `Registry.cxx` — hierarchical settings/serialization system

### Submodules (`Submodules/`)
- `c3d/` — Convert3D command-line tool (shared with ITK-SNAP's `c3d` CLI)
- `greedy/` — diffeomorphic image registration (used for propagation)
- `digestible/` — t-digest algorithm for approximate quantile computation

## Key Patterns

**Property/Event System:** GUI models expose `AbstractPropertyModel<T>` properties. Qt couplings in `GUI/Qt/Coupling/` bind these to Qt widgets without the model knowing about Qt. When logic changes a value, events propagate through the `AbstractModel` event system.

**ImageWrapper:** All image data is accessed via `ImageWrapperBase` and its subclasses. `ScalarImageWrapper`, `VectorImageWrapper`, and `LabelImageWrapper` wrap ITK images and provide display policies, histograms, and slicing.

**IRIS vs. SNAP modes:** The application has two modes: IRIS (manual segmentation with paintbrush/polygon/contour tools) and SNAP (semi-automatic level-set segmentation). `IRISImageData` and `SNAPImageData` hold the respective image data.

## Memory Leak Testing (macOS)

Full guide: `Documentation/Developer/MemoryLeakTestingMacOS.md`. Quick reference:

```bash
# 1. Build without sanitizers (Debug or RelWithDebInfo)
# 2. Sign binary after every relink:
codesign --force -s - --entitlements /dev/stdin build-leaks/ITK-SNAP <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>com.apple.security.get-task-allow</key><true/></dict></plist>
EOF

# 3. Run a single test:
MallocStackLogging=1 leaks --atExit -- build-leaks/ITK-SNAP \
  --test PreferencesDialog --testdir itksnap/Testing/TestData
```

**Canary tests:** `PreferencesDialog` and `RandomForestBailOut` should report ≤ 600 leaks / ≤ 90 KB (all Qt ROOT CYCLEs). A spike above this baseline indicates a regression. See `Documentation/Developer/MemoryManagement.md` for the owning-vs-non-owning pointer patterns that caused past leaks.

**Local leak build:** `/Users/jileihao/dev/itksnap-dev/build-leaks/` (binary at `build-leaks/ITK-SNAP`). Re-sign after every `ninja` relink.

## greedy_python Project

Python bindings for the [Greedy](https://github.com/pyushkevich/greedy) diffeomorphic registration library. Source lives at `greedy_python/`, a submodule of this wrapper tracking branch `test/integration` of https://github.com/jilei-hao/greedy_python.

### Build order

greedy_python depends on a standalone Greedy build (not the subproject build inside itksnap):

```bash
# 1. Build standalone Greedy (first time or after itksnap submodule updates)
scripts/build-greedy.sh

# 2. Build the Python extension
scripts/build-greedy-python.sh
```

**Key paths:**
- Standalone Greedy build: `build-greedy/` (sources from `itksnap/Submodules/greedy/`)
- Greedy install: `build-greedy/install/` (contains `GreedyConfig.cmake`)
- Python extension: `/Users/jileihao/dev/greedy_python/build/_picsl_greedy.cpython-*.so` (copied to `src/picsl_greedy/`)

**Why a separate Greedy build?** itksnap builds greedy as a subproject (`GREEDY_BUILD_AS_SUBPROJECT=ON`) which does not produce a `GreedyConfig.cmake`. The standalone build in `build-greedy/` installs the config and library headers needed by greedy_python.

**Eigen3** (needed for lmshoot): provided by Homebrew at `/opt/homebrew/Cellar/eigen@3/3.4.1`.

### Running tests

```bash
# Run all tests (uses greedy test data from itksnap/Submodules/greedy/testing/data)
scripts/run-greedy-python-tests.sh

# Run a single test file
scripts/run-greedy-python-tests.sh -k test_registration

# Override greedy_python source path if needed
GP_SRC=/custom/path/greedy_python scripts/run-greedy-python-tests.sh
```

Tests require `SimpleITK` and `numpy` (`pip install SimpleITK numpy pytest`). Test data is read from `itksnap/Submodules/greedy/testing/data` via `GREEDY_TEST_DATA_DIR`.

**Known test status:** 14/15 pass. `test_propagation_basic` fails due to an in-memory image-passing bug in `src/picsl_greedy/_greedy_api.py` (PropagationWrapper does not yet support in-memory sitk.Image arguments).

## Code Style

Uses `.clang-format` at the repository root. The CMake code uses a mix of old-style (`SET`, `IF`) and modern CMake conventions; prefer matching the existing style in the file being edited. C++17 is required.
