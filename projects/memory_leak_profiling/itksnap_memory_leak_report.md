---
title: "ITK-SNAP Memory Leak Report"
subtitle: "Analysis, Fixes, and Future Prevention"
date: "March 2026"
author: "ITK-SNAP Development"
toc: true
toc-depth: 3
numbersections: true
geometry: margin=1in
fontsize: 11pt
colorlinks: true
---

<!-- To compile to PDF:
     brew install pandoc
     brew install --cask basictex   # or mactex for full TeX
     pandoc itksnap_memory_leak_report.md -o itksnap_memory_leak_report.pdf
-->

# Overall Memory Leak Report

## Methodology

Memory leaks were measured using the macOS `leaks` tool with `MallocStackLogging=1`.
This tool inspects the live heap at process exit, identifies allocations unreachable
from live roots (ROOT LEAKs) or trapped in reference cycles (ROOT CYCLEs), and
prints full allocation stack traces.

```bash
MallocStackLogging=1 leaks --atExit -- <binary> [args]
# exit 0 = clean, exit 1 = leaks found
```

> **Note:** AddressSanitizer (ASan) is incompatible with this tool because ASan
> replaces the system allocator, making the heap opaque to `leaks`. All builds
> were plain `Debug` without sanitizers. The test script is
> `memory_leak_profiling/run_memory_test.sh`; per-test logs are in
> `memory_leak_profiling/asan_logs/`.

## Test Results (Current State — After All Fixes)

### Non-GUI Tests

All logic-layer tests run clean.

| Test | Leaks | Bytes |
|------|------:|------:|
| `IRISApplicationTest` | 0 | 0 |
| `TDigestTest` | 0 | 0 |
| `BasicSlicingTestX39` | 0 | 0 |
| `BasicSlicingTestY55` | 0 | 0 |
| `BasicSlicingTestZ32` | 0 | 0 |

### GUI Tests

GUI tests are run by invoking `ITK-SNAP --test <name> --testdir <path>`.
The process exits after the test without a full application teardown, which
is the primary reason leaks remain (see Section 2.1).

| Test | Leaks | Bytes |
|------|------:|------:|
| `PreferencesDialog` | 564 | 83,888 |
| `RandomForestBailOut` | 564 | 83,888 |
| `ProbeIntensity` | 790 | 131,232 |
| `DiffSpace` | 1,738 | 254,480 |
| `MeshImport` | 1,451 | 217,728 |
| `MeshWorkspace` | 2,351 | 312,944 |
| `Workspace` | 1,988 | 282,448 |
| `Reloading` | 2,159 | 308,528 |
| `EchoCartesianDicomLoading` | 2,788 | 5,556,000 |
| `LabelSmoothing` | 2,017 | 2,602,128 |
| `SegmentationMesh` | 2,173 | 596,496 |
| `VolumeRendering` | 2,104 | 295,472 |
| `RegionCompetition` | 3,891 | 1,245,328 |
| `NaNs` | 9,290 | 1,016,112 |
| `RandomForest` | 14,684 | 5,049,696 |

## Remaining Root Leak Summary

The dominant category by count is Qt framework ROOT CYCLEs, which are
framework-internal and not addressable from ITK-SNAP code (see Section 2.1).
The table below covers only ITK-SNAP-attributable ROOT LEAKs.

| Root Leak Type | Count | Fixable? |
|----------------|------:|---------|
| `vector<double>` / `vector<unsigned long>` in RandomForest trainer | 2,693 each | Yes — RandomForest only |
| `Rebroadcaster::Association` | 126 | Partial — needs lifecycle cleanup |
| `GLRBufferResource` | 53 | No — Qt/OpenGL widget lifetime |
| `QtFrameBufferOpenGLWidget::initializeGL` | 52 | No — Qt/OpenGL widget lifetime |
| `itk::ParallelSparseFieldLevelSetImageFilter` | 20 | Yes |
| `Registry` | 14 | Yes |
| `SNAPImageData::SwapLabelImage…` | 2 | Yes |

---

# Explanation of Each Leak Type

## Application Exit Without Teardown (The Primary Cause of GUI Leaks)

The `--test` runner invokes `ITK-SNAP --test <name>` and exits via `exit()`
after the test completes. This bypasses the normal `QApplication::quit()` path,
which means:

- Qt widgets and models are not destroyed — their destructors never run.
- ITK objects are not destroyed — their `DeleteEvent` observers never fire.
- `Rebroadcaster::Association` entries in the static maps are never cleaned up.
- VTK objects held by renderer members are not released.

This explains the large counts of Qt ROOT CYCLEs (`QStandardItem`,
`QObjectPrivate::ConnectionData`, `QHashPrivate`, `QOpenGLVertexArrayObjectPrivate`,
`QTimerPrivate`, `QCocoaNSMenuItem`, etc.) — these are inherent to Qt's own
signal-slot and model-view machinery and appear whenever a Qt application
exits without a proper shutdown sequence. They are **not addressable from
ITK-SNAP code**.

The fixes described in this document eliminate leaks that occur regardless of
teardown order, and which therefore represent true resource management errors.

## `Rebroadcaster::Association` Leaks (126 instances)

`Rebroadcaster` maintains two process-lifetime static maps
(`m_SourceMap`, `m_TargetMap`) that store raw `Association*` pointers.
Cleanup relies entirely on ITK `DeleteEvent` callbacks: when a source or
target object is destroyed, its associations are removed and freed.

Because the test runner exits without destroying application-lifetime objects,
their DeleteEvent callbacks never fire, leaving associations in the static
maps indefinitely. The `leaks` tool reports these as ROOT LEAKs because the
only reference to each `Association` is through the static maps.

A secondary issue — now fixed (Section 3.2) — is that `Rebroadcast()` would
create duplicate associations if called multiple times with identical arguments.

## RandomForest Decision-Tree Data (2,693 instances each)

These leaks appear exclusively in the `RandomForest` test. The allocation
stack traces to `SnakeWizardModel::TrainClassifier()` →
`RFClassificationEngine::TrainClassifier()` → `Trainer::DepthFirst()` →
`DTSplitFull` → `Histogram` copy constructor.

The `Histogram` struct stores per-bin data in `std::vector<double>` and
`std::vector<unsigned long>`. Thousands of these are allocated as the decision
forest is trained and stored as split-node data inside each `DecisionTree`.
The `DecisionForest` object is held by `RFClassificationEngine`, which is
owned by `SnakeWizardModel`. Since none of these are destroyed at test exit,
the entire forest data leaks (~5 MB in the `RandomForest` test).

## `GLRBufferResource` and Qt OpenGL Leaks (53 + 52 instances)

These appear in mesh-heavy tests (`MeshImport`, `MeshWorkspace`,
`VolumeRendering`). `GLRBufferResource` objects are OpenGL VBOs (vertex buffer
objects) allocated by VTK's OpenGL backend during rendering. They are owned by
VTK's render pipeline and are only released when the render window is destroyed.
`QtFrameBufferOpenGLWidget::initializeGL()` root leaks are Qt-side OpenGL
framebuffer objects with the same lifecycle dependency.

Because neither the render window nor the Qt OpenGL widget is destroyed in
the `--test` exit path, these remain. They are **not addressable without
application teardown**.

## `itk::ParallelSparseFieldLevelSetImageFilter` (20 instances)

Allocated during `SNAPLevelSetDriver` construction
(`SNAPImageData::InitializeSegmentation()` → `SNAPLevelSetDriver::ctor`).
The filter is held for the lifetime of the SNAP segmentation session.
Since the `RegionCompetition` test starts a snake segmentation but exits
without calling `IRISApplication::TerminateSNAPImageData()`, the level-set
filter and its internal state are never released.

## `Registry` (14 instances)

`Registry` objects loaded during workspace parsing are not all released at
test exit. These are typically small (a few KB total) and indicate that the
workspace loading code path does not have balanced creation and deletion of
registry nodes across all exit paths.

## `SNAPImageData::SwapLabelImageWithCompressedAlternative` (2 instances)

A temporary image buffer allocated during label image compression swap. The
label image lifecycle code leaves this buffer allocated in certain exit paths.

---

# Changes Made

## Fix 1 — Reference Cycle: `GenericImageData` ↔ `ImageMeshLayers`

**Files:** `Logic/Mesh/ImageMeshLayers.h`, `Logic/Mesh/ImageMeshLayers.cxx`

**Root cause.** `GenericImageData` owns its mesh layer manager via a `SmartPtr`:

```cpp
SmartPtr<ImageMeshLayers> m_MeshLayers;  // GenericImageData.h
```

`ImageMeshLayers::Initialize()` stored its back-pointer to the owner also as
a `SmartPtr`:

```cpp
SmartPtr<GenericImageData> m_ImageData;  // before fix
```

This formed a cycle: neither object's reference count could reach zero, so
neither was ever destroyed.

```
GenericImageData  ──SmartPtr──►  ImageMeshLayers
       ▲                               │
       └───────────SmartPtr────────────┘
```

The leak detector reported 104 leaked allocations (≈ 16 KB) rooted at
`GenericImageData` instances.

**Fix.** Changed `m_ImageData` to a raw (non-owning) pointer:

```cpp
GenericImageData* m_ImageData = nullptr;  // after fix
```

This is safe because `ImageMeshLayers` is always created and owned by
`GenericImageData` (or a subclass), so the raw pointer is guaranteed valid
for the full lifetime of the `ImageMeshLayers` object. Two `.GetPointer()`
casts in the `.cxx` file were simplified to direct pointer use.

**Result.** `IRISApplicationTest`: 104 leaks / 16,000 bytes → **0 / 0**.

---

## Fix 2 — `Rebroadcaster` Duplicate Registration

**Files:** `Common/Rebroadcaster.h`, `Common/Rebroadcaster.cxx`

**Root cause.** `Rebroadcaster::Rebroadcast()` unconditionally allocated a new
`Association` object every call, even when called with identical arguments.
The original code contained an explicit TODO acknowledging this:

```cpp
// TODO: for now, we allow the user to call this method twice with the same
// input without checking if the rebroadcast has already been set up.
```

When a model's `Initialize()` method is invoked more than once on the same
object pair — for example `ImageLayerTableRowModel::ReloadAsMultiComponent()`
calls `this->Initialize(parentModel, layer)` after reloading — each call
created a new batch of `Association` heap objects for connections that already
existed. Because source and target were not destroyed between calls, the
cleanup callbacks never ran and the old associations accumulated indefinitely
in the static dispatch maps.

**Fix.** Added a deduplication check before allocating a new `Association`.
A `m_SourceEventName` field was added to `Association` to record the source
event type. Before creating a new `Association`, `Rebroadcast()` now scans
the existing source-map entry:

```cpp
const char *srcEvtName = sourceEvent.GetEventName();
const char *tgtEvtName = targetEvent.GetEventName();
if(m_SourceMap.count(source))
  {
  for(Association *a : m_SourceMap[source])
    {
    if(a->m_Target == target &&
       strcmp(a->m_SourceEventName, srcEvtName) == 0 &&
       strcmp(a->m_TargetEvent->GetEventName(), tgtEvtName) == 0)
      return a->m_SourceTag;
    }
  }
```

`itk::EventObject::GetEventName()` returns a vtable-backed string literal,
so comparisons are stable and effectively free on the common (non-duplicate) path.

**Result.** Prevents unbounded `Association` accumulation when `Initialize()`
is called repeatedly on the same object pair.

---

## Fix 3 — `vtkScalarBarActor` Double Reference Count in `Generic3DRenderer`

**File:** `GUI/Renderer/Generic3DRenderer.cxx`

**Root cause.** VTK uses its own reference-counting system. The rules are:

- `T::New()` creates an object with ref count = **1**.
- Assigning a raw `T*` to a `vtkSmartPointer<T>` calls `Register()`,
  incrementing the ref count to **2**.
- When the `vtkSmartPointer` is destroyed, it calls `UnRegister()`,
  decrementing to **1** — never to **0** — so the object leaks.

The correct idiom is `vtkSmartPointer<T>::New()`, which creates the object
and hands its initial reference directly to the smart pointer (ref count stays
at 1, reaches 0 when the smart pointer is destroyed).

In `Generic3DRenderer::Generic3DRenderer()`, every other VTK member used the
correct form, but `m_ScalarBarActor` was initialised with the raw factory:

```cpp
// Before — leaks: ref count is 2 after assignment, drops to 1 on destroy
m_ScalarBarActor = vtkScalarBarActor::New();

// After — correct: ref count stays at 1
m_ScalarBarActor = vtkSmartPointer<vtkScalarBarActor>::New();
```

**Result.** `vtkScalarBarActor` ROOT LEAK eliminated from every GUI test.
`PreferencesDialog`: 2,258 leaks / 297 KB → **564 leaks / 84 KB**.

---

## Fix 4 — `LayerHistogramPlotAssembly` Not Deleted in `GMMRenderer`

**Files:** `GUI/Renderer/GMMRenderer.h`, `GUI/Renderer/GMMRenderer.cxx`

**Root cause.** `GMMRenderer` allocates a `LayerHistogramPlotAssembly` on the
heap in its constructor:

```cpp
m_HistogramAssembly = new LayerHistogramPlotAssembly();
```

The member is a raw pointer (`LayerHistogramPlotAssembly *m_HistogramAssembly`)
and the destructor was an empty inline body. The two sibling renderers,
`IntensityCurveVTKRenderer` and `ThresholdSettingsRenderer`, both correctly
`delete m_HistogramAssembly` in their destructors; `GMMRenderer` simply
omitted it.

**Fix.** Added the destructor definition to `GMMRenderer.cxx` (rather than
inline in the header, where `LayerHistogramPlotAssembly` is only
forward-declared and the compiler cannot generate the destructor call for an
incomplete type):

```cpp
GMMRenderer::~GMMRenderer()
{
  delete m_HistogramAssembly;
}
```

**Result.** `LayerHistogramPlotAssembly` ROOT LEAK eliminated from all GUI tests.

---

## Fix 5 — VTK Double Reference Count in `VTKMeshPipeline` and `MeshDisplayMappingPolicy`

**Files:** `Logic/Mesh/VTKMeshPipeline.cxx`,
`Logic/ImageWrapper/MeshDisplayMappingPolicy.cxx`

**Root cause.** The same double-ref-count pattern as Fix 3 appeared in two
additional locations:

1. `VTKMeshPipeline.cxx` — `vtkCellArray` initialised with raw `::New()`:

    ```cpp
    // Before — leaks
    vtkSmartPointer<vtkCellArray> trg = vtkCellArray::New();
    ```

2. `VTKMeshPipeline.cxx` — `vtkCellArrayIterator` obtained from
   `vtkCellArray::NewIterator()`, which is annotated `VTK_NEWINSTANCE` and
   returns a raw owning pointer (ref count = 1). Assigning it directly to a
   `vtkSmartPointer` increments the ref count to 2:

    ```cpp
    // Before — leaks
    for (vtkSmartPointer<vtkCellArrayIterator> it = src->NewIterator(); ...)
    ```

    The VTK-recommended fix for `VTK_NEWINSTANCE` return values is
    `vtk::TakeSmartPointer()`, which absorbs the existing reference without
    calling `Register()`:

    ```cpp
    // After — correct
    for (auto it = vtk::TakeSmartPointer(src->NewIterator()); ...)
    ```

3. `MeshDisplayMappingPolicy.cxx` — `vtkLookupTable` initialised with raw
   `::New()` despite the member being declared as `vtkSmartPointer<vtkLookupTable>`:

    ```cpp
    // Before — leaks
    m_LookupTable = vtkLookupTable::New();

    // After — correct
    m_LookupTable = vtkSmartPointer<vtkLookupTable>::New();
    ```

**Result.** `vtkCellArray`, `vtkCellArrayIterator`, and `vtkLookupTable` ROOT
LEAKs eliminated. Mesh-heavy tests reduced significantly:

| Test | Before (all fixes) | After Fix 5 |
|------|-----------------:|------------:|
| `MeshImport` | 18,053 / 1.62 MB | 1,451 / 218 KB |
| `MeshWorkspace` | 22,477 / 1.90 MB | 2,351 / 313 KB |
| `SegmentationMesh` | 3,871 / 817 KB | 2,173 / 596 KB |

---

## Fix 6 — VTK Double Reference Count in `VTKMeshPipeline` (Constructor Members)

**File:** `Logic/Mesh/VTKMeshPipeline.cxx`

**Root cause.** All nine VTK filter members of `VTKMeshPipeline` (e.g.
`m_VTKImporter`, `m_MarchingCubesFilter`, `m_DecimateFilter`) were initialised
with the raw factory `T::New()` and immediately assigned into
`vtkSmartPointer<T>` member variables. This doubles the ref count (1 from
`New()` + 1 from `SmartPtr::Register()`), so the count reaches 1 — not 0 —
when the `VTKMeshPipeline` destructor destroys the smart pointers. The
`vtkDecimatePro` → `vtkCompositeDataPipeline` → `vtkInformationVector` →
`vtkInformation` chain formed a ROOT CYCLE.

**Fix.** Changed all nine member initialisations to `vtkSmartPointer<T>::New()`,
which hands the initial reference directly to the smart pointer (ref count stays at 1):

```cpp
// Before — leaks (ref count = 2 after assignment)
m_VTKImporter = vtkImageImport::New();
m_DecimateFilter = vtkDecimatePro::New();
// ...

// After — correct (ref count = 1)
m_VTKImporter = vtkSmartPointer<vtkImageImport>::New();
m_DecimateFilter = vtkSmartPointer<vtkDecimatePro>::New();
// ...
```

**Result.** `vtkDecimatePro` ROOT CYCLE eliminated from all mesh-related tests.

---

## Fix 7 — Circular Reference: `AbstractLayerTableRowModel` ↔ `WrapperBase`

**Files:** `GUI/Model/LayerTableRowModel.h`, `GUI/Model/LayerTableRowModel.cxx`

**Root cause.** `AbstractLayerTableRowModel` held the layer wrapper via a
`SmartPtr`:

```cpp
SmartPtr<WrapperBase> m_Layer;          // AbstractLayerTableRowModel
SmartPtr<ImageWrapperBase> m_ImageLayer; // ImageLayerTableRowModel
SmartPtr<MeshWrapperBase> m_MeshLayer;  // MeshLayerTableRowModel
```

At the same time, `LayerInspectorDialog::GenerateModelsForLayers()` stores the
model as user data on its layer:

```cpp
it.GetLayer()->SetUserData("LayerTableRowModel", model);
// WrapperBase::m_UserDataMap["LayerTableRowModel"] = SmartPtr<itk::Object>(model)
```

This creates a cycle:

```
AbstractLayerTableRowModel  ─SmartPtr(m_Layer)──►  WrapperBase
          ▲                                              │
          └──────SmartPtr(m_UserDataMap["..."])──────────┘
```

Whenever the application replaced a layer (e.g. during 4D DICOM loading), the
old `WrapperBase` was removed from the app's layer collection but lived on
because the model's `m_Layer` SmartPtr still held it. The model in turn lived
on because the old wrapper's user-data map still held it. Neither object's
reference count could reach zero, leaking both the wrapper and the model along
with all their `Rebroadcaster::Association` entries (≈88,000 per bad run of
`EchoCartesianDicomLoading`, occurring in ~40–50% of runs non-deterministically
depending on load timing).

**Fix.** Changed `m_Layer`, `m_ImageLayer`, and `m_MeshLayer` to raw
(non-owning) pointers. The existing `itk::DeleteEvent` handler in `OnUpdate()`
already nulled `m_Layer` when the layer was destroyed; a new virtual
`OnLayerDeleted()` hook was added so `ImageLayerTableRowModel` and
`MeshLayerTableRowModel` can also null their typed sub-pointers:

```cpp
// Header (LayerTableRowModel.h) — before:
SmartPtr<WrapperBase>      m_Layer;
SmartPtr<ImageWrapperBase> m_ImageLayer;
SmartPtr<MeshWrapperBase>  m_MeshLayer;

// After — raw pointers, no cycle:
WrapperBase      *m_Layer      = nullptr;
ImageWrapperBase *m_ImageLayer = nullptr;
MeshWrapperBase  *m_MeshLayer  = nullptr;
```

```cpp
// OnUpdate() in AbstractLayerTableRowModel (LayerTableRowModel.cxx):
if(this->m_EventBucket->HasEvent(itk::DeleteEvent(), m_Layer))
  {
  m_Layer = NULL;
  OnLayerDeleted();  // NEW — lets subclasses null m_ImageLayer/m_MeshLayer
  ...
  }
```

```cpp
// ImageLayerTableRowModel (header inline):
void OnLayerDeleted() override { m_ImageLayer = nullptr; }

// MeshLayerTableRowModel (header inline):
void OnLayerDeleted() override { m_MeshLayer = nullptr; }
```

**Result.** `EchoCartesianDicomLoading` bad-run rate dropped from ~40–50%
(≈88,000 leaked `Rebroadcaster::Association` objects per bad run) to **0%**
(10/10 good runs after fix, all showing the normal ~2,000 lifecycle leaks).

---

## Summary of All Fixes

| Fix | File(s) | Issue | Result |
|-----|---------|-------|--------|
| 1 | `ImageMeshLayers.h/.cxx` | `SmartPtr` cycle between `GenericImageData` and `ImageMeshLayers` | `IRISApplicationTest` 104 leaks → 0 |
| 2 | `Rebroadcaster.h/.cxx` | `Rebroadcast()` created duplicate `Association` objects on repeated calls | Prevents unbounded accumulation |
| 3 | `Generic3DRenderer.cxx` | `vtkScalarBarActor::New()` assigned to `vtkSmartPointer` → ref count 2 | `PreferencesDialog` 297 KB → 84 KB |
| 4 | `GMMRenderer.h/.cxx` | `LayerHistogramPlotAssembly` never deleted | Eliminated from all GUI tests |
| 5 | `VTKMeshPipeline.cxx`, `MeshDisplayMappingPolicy.cxx` | `vtkCellArray::New()`, `NewIterator()`, `vtkLookupTable::New()` double ref count | `MeshImport` 1.62 MB → 218 KB |
| 6 | `VTKMeshPipeline.cxx` | All VTK filter members initialised with `T::New()` → double ref count (ROOT CYCLE via `vtkDecimatePro`) | VTK filter ROOT CYCLE eliminated |
| 7 | `LayerTableRowModel.h/.cxx` | `SmartPtr` cycle between `AbstractLayerTableRowModel::m_Layer` and `WrapperBase::m_UserDataMap` | `EchoCartesianDicomLoading` ~90K transient leaks → 0 |

---

# Best Practices

## Owning vs. Non-Owning Back-Pointers (ITK `SmartPtr`)

When two objects have a parent-child relationship, only the **parent should
hold a `SmartPtr` to the child**. The child should refer back to the parent
via a **raw pointer**:

```cpp
// Parent owns child:
SmartPtr<Child> m_Child;

// Child refers back — raw pointer, NOT SmartPtr:
Parent* m_Parent = nullptr;
```

A bidirectional `SmartPtr` cycle is the most common cause of
reference-counted leaks in ITK-based code. The canonical pattern in ITK-SNAP
is: the object that logically "contains" another holds a `SmartPtr`; the
contained object may hold a raw pointer back to its container, which is valid
for the container's lifetime.

## VTK Object Ownership (`vtkSmartPointer`)

Always initialise `vtkSmartPointer` members using `vtkSmartPointer<T>::New()`,
never the raw `T::New()`. The root issue is that `T::New()` returns a pointer
with ref count = 1, and assigning it to a `vtkSmartPointer` increments that
count to 2. When the smart pointer is eventually destroyed, the count drops to
1 — never to 0 — so the object leaks.

```cpp
// Correct:
m_Actor = vtkSmartPointer<vtkActor>::New();

// Wrong — ref count is 2 from the start, object leaks:
m_Actor = vtkActor::New();
```

For factory methods annotated `VTK_NEWINSTANCE` (such as
`vtkCellArray::NewIterator()`), use `vtk::TakeSmartPointer()` to absorb the
returned owning raw pointer without an extra `Register()` call:

```cpp
// Correct for VTK_NEWINSTANCE return values:
auto it = vtk::TakeSmartPointer(cellArray->NewIterator());

// Wrong — same double-ref-count leak:
vtkSmartPointer<vtkCellArrayIterator> it = cellArray->NewIterator();
```

## Matching `new` with `delete` for Plain C++ Members

For plain C++ heap members (not ITK or VTK objects), every constructor that
calls `new` must have a corresponding `delete` in the destructor. Prefer
`std::unique_ptr<T>` to make this automatic and exception-safe:

```cpp
// Preferred — ownership is automatic:
std::unique_ptr<LayerHistogramPlotAssembly> m_HistogramAssembly;
// constructor: m_HistogramAssembly = std::make_unique<LayerHistogramPlotAssembly>();
// no destructor needed

// Acceptable — matches the existing sibling renderer pattern:
LayerHistogramPlotAssembly *m_HistogramAssembly;
// constructor: m_HistogramAssembly = new LayerHistogramPlotAssembly();
// destructor:  delete m_HistogramAssembly;
```

When a class has a forward-declared type as a raw pointer member and the
destructor needs to `delete` it, the destructor body **must** be defined in
the `.cxx` file (where the full type is included), not inline in the header.
Deleting an incomplete type is undefined behaviour.

## `Rebroadcaster::Rebroadcast()` — Call-Once Semantics

`Rebroadcaster::Rebroadcast()` (and the `AbstractModel::Rebroadcast()` wrapper)
should be treated as a **one-time setup call** per source-target-event triple.
After the deduplication fix (Fix 2), duplicate calls are silently ignored
rather than leaked, but the intent is still that `Rebroadcast()` is called
once, typically in a constructor or a first-time initialization guard.

If a model's `Initialize()` method may be called multiple times (e.g., when
reloading a layer), verify that it either:

1. Is only called once (preferred), or
2. Clears existing connections before re-establishing them.

## Detecting Leaks During Development

To check a specific test for regressions during development:

```bash
# Quick check on a single test:
cd /Users/jileihao/dev/itksnap-dev/memory_leak_profiling
MallocStackLogging=1 leaks --atExit -- build/ITK-SNAP \
  --test PreferencesDialog --testacc 1.0 \
  --testdir /path/to/Testing/TestData --lang en \
  2>&1 | grep -E "leaks for|ROOT LEAK"

# Full suite:
bash run_memory_test.sh
```

The two best "canary" tests for catching regressions in the core model and
renderer setup are `PreferencesDialog` and `RandomForestBailOut`: they exercise
full GUI initialization with minimal test-specific logic, currently reporting
**564 leaks / 84 KB**, all attributable to Qt framework ROOT CYCLEs and the
residual `Rebroadcaster::Association` entries that require application teardown
to clean up.
