# Q-002 — Does ITK-SNAP support double-precision images?

<!-- Public repo: no names, emails, institutions, home paths, patient IDs, or pasted data.
     Identity → users.local.md. Files → attachments/Q-002/. See README.md. -->

| | |
|---|---|
| Opened | 2026-09-25 |
| User | not recorded (fill in a U-NNN handle if this came from a user) |
| Channel | not recorded |
| ITK-SNAP version | not stated. Answer checked against 4.4.0 (`20f63186`), `upstream/master` and `staging/v460` (`d02236c3`) |
| Platform | not stated |
| Type | question (a reload bug turned up during the investigation; see below) |
| Status | drafting |
| Escalated to | ISS-001 (the warning). The reload bug is still a candidate. |
| Attachments | — |

## The question

Does ITK-SNAP currently support images stored with double-precision (64-bit float) pixels?

## Conversation log

### 2026-09-25 — user

Asked whether ITK-SNAP supports double-precision images.

## Investigation

**Short version: yes, since 4.2.0.** Paul's commit `56b3d2f9` (2024-01-03, "Enabled native loading
of double format images") added the support, while the version read `4.2.0-alpha.2`.

**Correction (2026-09-25):** this first said "since 4.2.2", because `v4.2.2` is the only 4.2 tag
upstream. Upstream never tagged 4.0.1, 4.0.2 or 4.2.0. The version-bump commits on
`upstream/master` show it: 4.2.0 is `0d798539` (2024-04-17), which contains `56b3d2f9`, and 4.0.2
(`5770ead5`) does not. The commit is also in `v4.2.2`, the 4.4.0 release commit
`20f63186`, `upstream/master`, and `staging/v460`.

**Pipeline, followed through the code on `staging/v460` @ `d02236c3`:**
- **Read.** The reader dispatches on the file's component type. `DOUBLE` is read as native `double`
  (`Logic/ImageWrapper/GuidedNativeImageIO.cxx:1051`).
- **Wrapper type.** `GenericImageData::CreateAnatomicWrapper` has an explicit `DOUBLE` case that
  creates a `double` wrapper (`Logic/Framework/GenericImageData.cxx:340`). The wrapper templates
  are instantiated for `double` (`ImageWrapperInstantiateMacro(double)` and
  `ScalarImageWrapperInstantiateMacro(double)`, both added by `56b3d2f9`). Every type without its
  own case falls back to `float` (the switch's `default:`): that covers `uint`, `int`, `long` and
  `ulong`.
- **No rescaling.** `RescaleNativeImageToIntegralType::DoCast` only computes a scale and shift when
  the output type differs from the native type *and* is an integer type
  (`GuidedNativeImageIO.cxx:2374`). `double`→`double` is therefore an exact copy, and the
  intensities shown are the file's values.
- **Save.** `GuidedNativeImageIO::SaveImage<TImageType>` writes the wrapper's own pixel type, and
  it's instantiated for `double` (`GuidedNativeImageIO.cxx:3068`). A `double` layer is saved as
  `double`.
- **Memory.** 8 bytes per voxel, twice what `float` uses.

**Bug found while checking. Not reproduced yet.** Reloading a `double` image from file should fail:
- `ReloadAnatomicWrapperDelegate` (`Logic/Framework/ImageIODelegates.cxx:470-478`) says
  "this logic tracks GenericImageData::CreateAnatomicWrapper". But its switch has no `DOUBLE` case,
  so `double` falls to `default: UpdateWrapperInternal<float>()`.
- `UpdateWrapperWithTraits` then `dynamic_cast`s the existing wrapper to the `float` wrapper type.
  For a `double` wrapper that cast returns null, which throws
  `"Error reloading image from file: Cannot cast wrapper to …"` (`ImageIODelegates.cxx:513`).
- **History.** The reload switch came from `c5bd72f0` (2023-11-17), seven weeks before double
  support landed. `56b3d2f9` updated the load switch and missed this one. The gap is present in
  4.4.0, `upstream/master` and `staging/v460`.
- **How users reach it.** The layer's "Reload from file" action, via
  `ImageLayerTableRowModel::ReloadWrapperFromFile` (`GUI/Model/LayerTableRowModel.cxx:697`), for any
  non-segmentation layer.

This conclusion comes from reading the code. The GUI has not been run to confirm it.

## Draft reply

> Yes. ITK-SNAP has supported double-precision images since version 4.2.0, and that includes the
> current 4.4.0 release. A double image is loaded and kept in double precision in memory. Nothing
> is rounded or converted to a smaller type, so the intensity values ITK-SNAP shows are the values
> in your file. Saving the image writes it back as double.
>
> One practical note: a double image takes twice the memory of the same image stored as float. If
> you run short on memory with very large images, such as long 4D series, converting them to float
> first will help.

The reload bug is deliberately left out of the reply until it's reproduced. If it's confirmed and
the user reloads images, add: "Reloading a double image from file currently fails. As a
workaround, close the image and open it again."

## For a fix session

<!-- CANDIDATE: found by code reading while answering Q-002. Not reproduced, so it isn't in
     confirmed_issues.md yet. Once reproduced, add it there as its own ISS entry. -->

**Root cause:** `56b3d2f9` (4.2.0) made `double` a natively stored type by adding a case to
`GenericImageData::CreateAnatomicWrapper`. Two other component-type switches that should have
changed with it did not.

**Symptom 2 — false "Possible Loss of Precision" warning.** This one is confirmed and tracked as
**[ISS-001](../confirmed_issues.md)**, which has the full brief. It's no longer duplicated here.

**Symptom 1 — reload fails.** Found for Q-002; not yet reproduced. It is listed as "Related" under ISS-001, so a session fixing that issue will reproduce it.
- **Symptom:** "Reload from file" on an anatomical layer that was loaded from a `double` image
  fails. The expected error is `Error reloading image from file: Cannot cast wrapper to: "…"`.
- **Repro:**
  1. Make a double image from any test image:
     `c3d itksnap/Testing/TestData/MRIcrop-orig.gipl.gz -type double -o /tmp/dbl.nii.gz`
     (the input is in the repo's test data).
  2. Open `/tmp/dbl.nii.gz` in ITK-SNAP.
  3. In the Layer Inspector, choose "Reload from file" on the layer.
- **Expected vs. actual:** the image should reload in place. Instead, code reading predicts the
  exception above.
- **Affects:** every version since 4.2.0 (`56b3d2f9`), on all platforms. Confirmed on no build yet.
- **Suspected area:**
  - `Logic/Framework/ImageIODelegates.cxx:471-478` @ `d02236c3`. Add
    `case itk::IOComponentEnum::DOUBLE: UpdateWrapperInternal<double>(); break;`
  - A sturdier fix is to share one component-type→pixel-type mapping between this switch and
    `GenericImageData::CreateAnatomicWrapper` (`GenericImageData.cxx:~325-345`). The "tracks"
    comment has already drifted once.
- **Done when:** a GUI test loads a `double` image, reloads it, and checks that the layer still has
  `double` values. That test must fail on the current code.
- **Tracked at:** — (not escalated)
