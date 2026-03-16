# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ITK-SNAP (v4.4.0) is a C++17 medical image segmentation application built on ITK, VTK, and Qt6. It provides interactive 3D segmentation tools including level-set methods, AI-assisted segmentation (nnInteractive), and mesh visualization.

## Build System

**Dependencies:** ITK ≥ 5.4, VTK ≥ 9.3.1, Qt6 (Widgets, OpenGL, Concurrent, Qml, LinguistTools), libcurl, libssh. The CI uses ITK v5.4.0, VTK 9.3.1, Qt 6.8.1.

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

**Build a specific target:**
```bash
ninja ITK-SNAP          # main application
ninja SlicingPerformanceTest testTDigest iteratorTests
```

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

Python bindings for the [Greedy](https://github.com/pyushkevich/greedy) diffeomorphic registration library. Source lives at `greedy_python/` (branch `test/integration` of https://github.com/jilei-hao/greedy_python). Listed in `.gitignore` — tracked separately.

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
