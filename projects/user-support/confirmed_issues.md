# Confirmed issues

Bugs in ITK-SNAP and its companion tools that were **confirmed** while answering users. Each entry
is a self-contained brief a fix session can work from without reading the user threads.

An issue only goes here once its evidence is solid: reproduced, or observed in the field and
explained by the code. Suspected issues stay in their thread's **For a fix session** section until
then.

## For a session that fixes one of these

This file lives in the **wrapper repo** (`itksnap-developer`), not in `itksnap/`. It's the tracker
for where each issue stands, so **update it whenever an issue's state changes**. Each change takes
three edits:

1. The **Status** cell in the index table below.
2. The **Status** line in the issue's entry.
3. A new dated line at the bottom of the entry's **History**, with the branch, commit, or PR that
   justifies the change.

Commit that change in the wrapper, next to the pointer bump if there is one. Mention the `ISS-NNN`
id in the itksnap commit body as well, so the fix can be traced back to the users.

## Status values

| Status | Meaning | Record in History |
|---|---|---|
| `open` | Confirmed. Nobody is working on it. | how it was confirmed |
| `in-progress` | A session has started a fix. | the topic branch name |
| `in-review` | The fix is committed on its topic branch and awaiting review or merge. | branch, commit(s), PR or `branches.md` row |
| `merged` | In `upstream/master`. | the merge commit |
| `released` | Shipped in a release, so users can be told. | the version |
| `wontfix` | Deliberately not fixing. | the reason and who decided |

When an issue reaches `released`, draft a "fixed in …" reply for every thread under **Users to
notify**. Then the threads can close.

## Index

| ID | Title | Status | Severity | Found via | Updated |
|---|---|---|---|---|---|
| [ISS-001](#iss-001--false-possible-loss-of-precision-warning-for-double-images) | False "Possible Loss of Precision" warning for `double` images | `open` | low (misleading, no data affected) | Q-003 (and Q-002) | 2026-09-25 |

Next ID: **ISS-002**

---

## ISS-001 — False "Possible Loss of Precision" warning for `double` images

**Status:** `open`

| | |
|---|---|
| Component | ITK-SNAP, `Logic/Framework/ImageIODelegates.cxx` |
| Severity | low. The message is false and data is never altered, but it misled a user into blaming it for poor image quality (Q-003). |
| Affects | every release from **4.2.0** onward: 4.2.0 `0d798539`, 4.2.2 `9637de7b`, 4.4.0 `20f63186`. Also `upstream/master` @ `52ee94fa` and `staging/v460` @ `d02236c3`. All platforms. |
| Found via | [Q-003](threads/Q-003-stitched-dicom-precision-warning.md): a user on ≥ 4.2.0 got the warning. Code analysis came from Q-002 and Q-003. |
| Users to notify | Q-003 |
| Tracked at | — (not yet a W8 item; Jilei decides) |

**Symptom.** Opening a `double` image as an anatomical layer shows this in the Open Image wizard:

> Warning: Possible Loss of Precision. The file you opened represents image data using the
> 'itk::CommonEnums::IOComponent::DOUBLE' data type, but ITK-SNAP only supports 16-bit integer and
> 32-bit floating point data types. Intensity values reported in ITK-SNAP may differ from the
> actual values in the image.

Both claims in it are false for `double` since 4.2.0. ITK-SNAP stores `double` natively and exactly,
and it also supports 8-bit types.

**Why it matters more than it looks.** The warning also fires for **DICOM files that contain no
floating-point data**. ITK's GDCM reader reports a series as `DOUBLE` whenever its Rescale Slope or
Intercept isn't a whole number (`gdcmRescaler.cxx:206`), which is common for MR. So users can meet
this warning on ordinary scans.

**Evidence that it's confirmed.**
- **Field:** Q-003's screenshot shows this exact wording for `DOUBLE`. That wording only exists in
  4.2.0 and later, and every one of those releases keeps `double` exactly. The table is in Q-003,
  Investigation 1.
- **Code:** `LoadAnatomicImageDelegate::ValidateHeader` (`ImageIODelegates.cxx:15-36`) warns for
  any component type outside `{UCHAR, CHAR, USHORT, SHORT, FLOAT}`. `DOUBLE` is missing from that
  set at every commit listed under **Affects**.
- `GenericImageData::CreateAnatomicWrapper` creates a `double` wrapper for `DOUBLE`
  (`GenericImageData.cxx:340` on staging). `RescaleNativeImageToIntegralType::DoCast` doesn't
  rescale `double`→`double` (`GuidedNativeImageIO.cxx:2374`).

**Root cause.** Paul's commit `56b3d2f9` (2024-01-03, first in 4.2.0) made `double` a native type by
adding a case to `CreateAnatomicWrapper`. It didn't update the warning's allow-list, which still
describes the older behaviour where everything became `float`.

**Fix.**
1. Add `IOB::DOUBLE` to the allow-list in `ValidateHeader`.
2. Correct the message text. The types that are still converted are `uint`, `int`, `ulong` and
   `long`, which go to `float` through the `default:` case. For those the warning is true. For
   32-bit and 64-bit integers above 2²⁴ it's even a real loss, so keep it for them.
3. Consider deriving the allow-list from the same component-type→pixel-type mapping that
   `CreateAnatomicWrapper` uses. This allow-list, the `CreateAnatomicWrapper` switch and the reload
   switch (see **Related**) have already drifted apart once.

**Done when.**
- A test opens a `double` image (e.g. `c3d itksnap/Testing/TestData/MRIcrop-orig.gipl.gz -type
  double -o dbl.nii.gz`) through the anatomic-image load path and asserts that **no** precision
  warning is raised.
- The same test asserts that an `int32` image **still** raises one.
- The first assertion must fail on the current code.

**Related (suspected, not yet reproduced): "Reload from file" probably fails for `double` images.**
- The same commit also missed the switch in `ReloadAnatomicWrapperDelegate`
  (`ImageIODelegates.cxx:471-478` @ `d02236c3`). `DOUBLE` falls through to
  `UpdateWrapperInternal<float>()`, and the `dynamic_cast` to the `float` wrapper should then throw
  `"Cannot cast wrapper to …"`.
- A session fixing ISS-001 should reproduce this. The repro steps are in Q-002's
  **For a fix session**. If it's confirmed, fix it in the same branch and add it here as its own
  issue.

**History**
- 2026-09-25 — `open`. Confirmed from Q-003's screenshot plus the code reading above. Pinned at
  `upstream/master` @ `52ee94fa` and `staging/v460` @ `d02236c3`.
