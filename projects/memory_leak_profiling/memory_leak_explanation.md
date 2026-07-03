# ITK-SNAP Memory Leak Analysis and Fixes

**Date:** March 2026
**Tool:** macOS `leaks --atExit` with `MallocStackLogging=1`
**Build type:** Debug (plain, without ASan — macOS `leaks` is incompatible with AddressSanitizer's custom allocator)

---

## Summary

Three distinct memory leak root causes were identified and fixed.

| Fix | Scope | Effect |
|-----|----|-----|
| Reference cycle: `GenericImageData` ↔ `ImageMeshLayers` | Non-GUI + GUI | 16,000 bytes / 104 leaks in `IRISApplicationTest` → 0 |
| `Rebroadcaster` duplicate registration | GUI | Prevents unbounded `Association` accumulation on repeated `Initialize()` calls |
| `vtkScalarBarActor` double-ref-count in `Generic3DRenderer` | GUI | Eliminates `vtkScalarBarActor` root leak present in every GUI test; `PreferencesDialog` 297 KB → 87 KB |

---

## Fix 1 — Reference Cycle: `GenericImageData` ↔ `ImageMeshLayers`

### Root cause

`GenericImageData` (base of `IRISImageData` and `SNAPImageData`) owns its mesh layer manager via a `SmartPtr`:

```cpp
// GenericImageData.h
SmartPtr<ImageMeshLayers> m_MeshLayers;
```

`ImageMeshLayers::Initialize(GenericImageData*)` stored its back-pointer to the owning image data object also as a `SmartPtr`:

```cpp
// ImageMeshLayers.h (before fix)
SmartPtr<GenericImageData> m_ImageData;
```

This is a classical reference-counted cycle:

```
GenericImageData  --SmartPtr-->  ImageMeshLayers
       ^                               |
       +----------SmartPtr-------------+
```

Neither object's reference count ever reached zero, so neither was ever destroyed.

The leak detector reported 104 leaked heap allocations (~16 KB) rooted at `GenericImageData` instances that were unreachable from any live pointer.

### Fix

Changed `m_ImageData` in `ImageMeshLayers` from an owning `SmartPtr` to a raw (non-owning) pointer:

```cpp
// ImageMeshLayers.h (after fix)
GenericImageData* m_ImageData = nullptr;
```

This is safe because `ImageMeshLayers` is always created and owned by `GenericImageData` (or its subclass), so `m_ImageData` is guaranteed to remain valid for the entire lifetime of the `ImageMeshLayers` object. Two `.GetPointer()` call sites in `ImageMeshLayers.cxx` (casts involving `m_ImageData`) were updated to use the raw pointer directly.

### Result

`IRISApplicationTest`: **104 leaks / 16,000 bytes → 0 leaks / 0 bytes.**

---

## Fix 2 — `Rebroadcaster` Duplicate Registration

### How `Rebroadcaster` works

`Rebroadcaster` routes ITK events from a *source* object to a *target* object. It maintains two **process-lifetime static maps**:

```cpp
static DispatchMap m_SourceMap;  // source  -> list<Association*>
static DispatchMap m_TargetMap;  // target  -> list<Association*>
```

Every call to `Rebroadcaster::Rebroadcast(source, srcEvt, target, tgtEvt)`:
1. Allocates a new `Association` object on the heap.
2. Registers an ITK observer on `source` that fires `tgtEvt` on `target`.
3. Stores the `Association*` in both static maps.

Cleanup is **entirely passive**: when either `source` or `target` is destroyed, its ITK `DeleteEvent` fires a callback that removes and `delete`s all related `Association` objects. If an object is never properly destroyed (e.g., the process exits without a full teardown), its Associations remain in the static maps forever.

### The duplicate-registration bug

The class implementation in `Rebroadcaster.cxx` contained this TODO:

```cpp
// TODO: for now, we allow the user to call this method twice with the same
// input without checking if the rebroadcast has already been set up.
```

When any model's `Initialize()` method is called more than once on the same `(source, target)` pair — for example, `ImageLayerTableRowModel::ReloadAsMultiComponent()` and `ReloadAs4D()` both call `this->Initialize(parentModel, layer)` after replacing the image — each call creates a fresh batch of `Association` objects for connections that already exist. The old connections are never removed (because the source/target are not destroyed), so they accumulate in the static maps indefinitely.

**Example:** `AbstractLayerTableRowModel::Initialize()` contains 5 `Rebroadcast()` calls. Each extra `Initialize()` invocation on the same model object adds 5 more `Association` heap allocations that can never be freed.

### The leak detector's view

The static maps are alive for the entire process lifetime. The `Association*` pointers they contain have no back-reference from the heap — the leak tool reports them as **ROOT LEAKs** (heap allocations reachable only from global/static storage that is never freed at exit).

### Fix

Added a **deduplication check** to `Rebroadcaster::Rebroadcast()` that returns early if an identical `(source, sourceEventType, target, targetEventType)` association already exists:

```cpp
// Added to Association struct (Rebroadcaster.h):
const char *m_SourceEventName;  // event name for deduplication

// Added to Rebroadcaster::Rebroadcast() before 'new Association(...)':
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

`itk::EventObject::GetEventName()` returns a static string literal from the vtable, so string comparison is stable and effectively zero-cost at runtime for the common (non-duplicate) path.

### Remaining GUI leaks

After all three fixes, all 5 non-GUI tests pass with 0 leaks. The 15 GUI tests still report leaks because they arise from **application-lifetime objects that are never explicitly destroyed before `exit()`**. The test runner invokes `ITK-SNAP --test <name>` and the process exits without a full teardown; image wrappers, model objects, and their associated `Rebroadcaster` entries are reclaimed by the OS rather than through proper C++ destructors, so `DeleteEvent` callbacks never fire. These are not regressions introduced by this PR — they predate this work and require a dedicated application-lifecycle cleanup pass.

---

---

## Fix 3 — `vtkScalarBarActor` Double-Reference-Count in `Generic3DRenderer`

### Root cause

VTK uses its own reference-counting system independent of ITK's `SmartPtr`. `vtkSmartPointer<T>` manages a VTK object's ref count: it calls `Register()` (increment) on assignment and `UnRegister()` (decrement) on destruction. The VTK factory `T::New()` creates an object with an initial ref count of **1**.

The correct idiom for initialising a `vtkSmartPointer` member is `vtkSmartPointer<T>::New()`, which creates the object and hands its initial reference directly to the smart pointer (ref count stays at 1). Using the raw `T::New()` on the right-hand side of an assignment to a `vtkSmartPointer` causes the smart pointer to call `Register()`, bumping the ref count to **2**. When the smart pointer is later destroyed it decrements to 1 — never to 0 — so the object is never freed.

In `Generic3DRenderer::Generic3DRenderer()` (`Generic3DRenderer.cxx:160`), every other VTK member used the correct form, but `m_ScalarBarActor` was initialised with the raw factory:

```cpp
// Before fix — ref count reaches 2, leaks
m_ScalarBarActor = vtkScalarBarActor::New();
```

The member is declared in the header as `vtkSmartPointer<vtkScalarBarActor> m_ScalarBarActor`, making the inconsistency easy to overlook.

### Fix

```cpp
// After fix — ref count stays at 1, freed when renderer is destroyed
m_ScalarBarActor = vtkSmartPointer<vtkScalarBarActor>::New();
```

### Result

`vtkScalarBarActor` ROOT LEAK eliminated from every GUI test.
`PreferencesDialog`: **2,258 leaks / 297 KB → 599 leaks / 87 KB.**

---

## Files Changed

| File | Change |
|------|--------|
| `Logic/Mesh/ImageMeshLayers.h` | `m_ImageData`: `SmartPtr<GenericImageData>` -> `GenericImageData*` |
| `Logic/Mesh/ImageMeshLayers.cxx` | Remove two `.GetPointer()` calls on the now-raw `m_ImageData` |
| `Common/Rebroadcaster.h` | Add `const char *m_SourceEventName` to `Association` |
| `Common/Rebroadcaster.cxx` | Deduplication check in `Rebroadcast()`; initialize `m_SourceEventName` in constructor |
| `GUI/Renderer/Generic3DRenderer.cxx` | `vtkScalarBarActor::New()` → `vtkSmartPointer<vtkScalarBarActor>::New()` |

---

## Test Methodology

```bash
# Build: plain Debug, no ASan (ASan replaces malloc, making 'leaks' non-functional)
cmake -DCMAKE_BUILD_TYPE=Debug ...
ninja

# Run:
MallocStackLogging=1 leaks --atExit -- <binary> [args]
# exit code 0 = clean, exit code 1 = leaks found
```

Test script: `memory_leak_profiling/run_memory_test.sh`
Logs: `memory_leak_profiling/asan_logs/<TestName>.leaks.log`
