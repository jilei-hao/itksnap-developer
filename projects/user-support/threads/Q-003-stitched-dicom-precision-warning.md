# Q-003 — Stitched DICOM looks bad and shows a "loss of precision" warning; can ITK-SNAP stitch NIfTI?

<!-- Public repo: no names, emails, institutions, home paths, patient IDs, or pasted data.
     Identity → users.local.md. Files → attachments/Q-003/. See README.md. -->

| | |
|---|---|
| Opened | 2026-09-25 |
| User | U-002 |
| Channel | email |
| ITK-SNAP version | 4.2.0 or later, inferred from the warning text (see Investigation 1). Exact version unknown. |
| Platform | Windows (from the screenshots) |
| Type | question + data (plus a warning-message bug on our side) |
| Status | drafting |
| Escalated to | [ISS-001](../confirmed_issues.md) (the false precision warning) |
| Attachments | `user-email-screenshot.webp` (the email with two screenshots). `stitch-tested.sh` (the c3d recipe below, as tested). |

## The question

- **What they did:** a small-animal MRI study, with each brain scanned in two parts. Earlier they
  combined the two parts into one DICOM series to get the whole brain. Jilei's reading is that
  they put the two DICOM series together into one, rather than using a stitching tool.
- **What goes wrong:** when that combined DICOM is opened in ITK-SNAP, the image quality is
  "terrible", and ITK-SNAP shows a warning about possible loss of precision.
- **What they ask:** can ITK-SNAP stitch their NIfTI files instead?

The screenshots show:
- **Warning, verbatim (our own text):** "Warning: Possible Loss of Precision. The file you opened
  represents image data using the 'itk::CommonEnums::IOComponent::DOUBLE' data type, but ITK-SNAP
  only supports 16-bit integer and 32-bit floating point data types…"
- **Combined DICOM:** 238×256×113, spacing 0.1261×0.1172×0.2502 mm, orientation LPI, pixel type
  `double`.
- **One NIfTI stack:** 238×256×64, spacing 0.160067×0.15625×0.26 mm, oblique (closest to LPS),
  pixel type `float`.

## Conversation log

### 2026-09-25 — user

Sent the question and the two screenshots described above.

## Investigation

**1. Would 4.4.0 show the same warning? Yes. What the warning *does* tell us is that the version
is ≥ 4.2.0.**
- `LoadAnatomicImageDelegate::ValidateHeader` (`Logic/Framework/ImageIODelegates.cxx:16-36`) warns
  for any component type other than `uchar`, `char`, `ushort`, `short` and `float`. `56b3d2f9`
  made `double` native but never added it to that list. The check is identical in 4.2.0, 4.2.2,
  4.4.0 (`20f63186`), `upstream/master` and `staging/v460`.
- The message has two wordings, and hers is the newer one:

  | Release (upstream/master version-bump commit) | Warning wording | `double` kept exactly? |
  |---|---|---|
  | 4.0.0 `3bc2bdce` (tag `v4.0.0` = `ca9f5028`), 4.0.1 `797769ee`, 4.0.2 `5770ead5` | "Loss of Precision. You are opening an image with 32-bit or greater precision, but ITK-SNAP only provides 16-bit precision" (everything *was* converted to 16-bit) | no |
  | 4.2.0 `0d798539`, 4.2.2 `9637de7b`, 4.4.0 `20f63186` | **"Possible Loss of Precision … '%s' data type, but ITK-SNAP only supports 16-bit integer and 32-bit floating point"**, as in her screenshot | **yes** |

  The newer wording came from `c58f72bf` (2023-02-09), which was developed on a side branch and
  first shipped in 4.2.0. Upstream never tagged 4.0.1, 4.0.2 or 4.2.0, which is why this table was
  built from the version-bump commits.
- **So every version that can show her exact message already stores `double` exactly.** For her
  the warning is false, whatever made the file `double`. Nothing was lost on load.
- This is the second spot `56b3d2f9` missed. The first is the reload switch in Q-002, and both are
  in Q-002's candidate fix brief.

**2. Why a DICOM series reads as `double`. This is what the code says; her file hasn't been checked.**
- ITK-SNAP takes the pixel type from ITK's GDCM reader. The one exception is echo-Cartesian
  files, which are forced to `uchar` (`GuidedNativeImageIO.cxx:1006`).
- GDCM's pixel reader only reads the standard Pixel Data element `7FE0,0010`
  (`gdcmPixmapReader.cxx:339`). It never reads Float or Double Float Pixel Data (`7FE0,0008/0009`).
- `FLOAT64` can come from two places, and only one applies to a standard DICOM:
  - **Pixel format.** Only for `PixelRepresentation == 4`, a GDCM-internal "secret code" that is
    not a legal DICOM value (`gdcmPixelFormat.cxx:111,188`).
  - **Rescaler.** `Rescaler::ComputeInterceptSlopePixelType()` returns `FLOAT64` whenever Rescale
    Slope (0028,1053) or Rescale Intercept (0028,1052) isn't a whole number
    (`gdcmRescaler.cxx:206`). `itkGDCMImageIO.cxx:576` maps that to `DOUBLE`.
- **Conclusion:** for a standard DICOM, a fractional rescale slope or intercept is the only route
  to `double`.
- **Assumptions left:**
  - Her ITK/GDCM matches the ITK 5.4.5 source read here. That logic has been stable for years.
  - The file is standard DICOM, and whatever combined the series didn't write something exotic.
  - The file itself hasn't been seen. The tags (0028,1052/1053) would settle it.
- **An earlier draft stated the scaling factor as fact. That overstated it.** The short reply
  doesn't depend on it.

**3. The warning doesn't explain the poor quality.** Per item 1, her version keeps `double`
values exactly. (The previous draft said "older versions round to float". That was wrong on two
counts: 4.0.x converted to 16-bit, and 4.0.x can't show her wording anyway.)

**4. The more likely cause of the poor quality is how the two series were combined.** This is a
hypothesis; neither file has been seen.
- Merging two overlapping series makes the slice positions interleave or become unevenly spaced.
  ITK sorts slices by position and assumes one uniform spacing, so the volume comes out
  jagged-looking and geometrically wrong.
- The headers fit this: 113 slices where two 64-slice stacks would give 128, and a z spacing of
  0.2502 mm against the NIfTI's 0.26 mm.
- **The in-plane spacing differs too** (0.126 vs 0.160 mm, with the same 238×256 matrix). Merging
  doesn't change that. Either the screenshots show different scans, or the combining step rewrote
  the geometry. So the reply speaks only generally about the header mismatch.

**5. Can ITK-SNAP stitch? No, but the c3d it ships with can.**
- ITK-SNAP has no stitching or mosaicking tool. Loading the second stack as an extra layer doesn't
  help either: every layer is shown on the main image's grid, so the part of stack 2 beyond stack
  1's extent isn't visible.
- **c3d ships with ITK-SNAP.** The top-level `CMakeLists.txt:1198-1204` installs Convert3D's
  command-line tools into `SNAP_CLI_INSTALL_PATH`: `bin` on Windows and Linux, `../bin` inside the
  macOS app (`CMakeLists.txt:69-74`). It's been bundled since 3.8.0 (`2ae99e23`). Verified in the
  local 4.4.0 app: `Contents/bin/c3d` is Convert3D 1.4.2.

**The c3d recipe and how it was tested** (2026-09-25):
- **How it works:** stack 1's voxel grid is padded with empty slices at both ends. Stack 2 and a
  mask of ones are resliced onto that grid with the identity transform (scanner coordinates). The
  two are averaged in the overlap as (A+B)/(maskA+maskB), and the empty slices are trimmed away.
- **Test data:** `MRIcrop-orig.gipl.gz` from TestData, given the user's voxel size, and tested
  both axis-aligned and oblique (12° about x, 7° about y). It was cut into two 40-slice stacks with
  16 slices of overlap, then stitched back together.
- **Result:** the geometry matches the original exactly.
  - Max voxel error, axis-aligned: 8.5e-13.
  - Max voxel error, oblique: 1.6e-3 on a 0–269 range, from floating-point round-off in the
    oblique coordinates.
  - Max voxel error, with stack 2 as the base: 8.3e-4.
- **Environment:** run with both `/usr/local/bin/c3d` and the 4.4.0 app's bundled c3d (both 1.4.2).
  The output is `float32`, so the user won't see the precision warning.
- **Gotcha hit while testing:** c3d's `-divide` computes **last ÷ second-to-last**. Pushing 6 then
  2 gives 0.333. The recipe pushes the mask sum first.
- **Limits:**
  - It assumes both stacks come from one session, so their scanner coordinates agree, and differ
    mainly along the slice axis.
  - Stack 2 is cut to stack 1's in-plane field of view.
  - If the animal moved between the two parts, the stacks need registering first; greedy is also
    bundled.
  - `-trim 0vox` crops on the mask, so it only removes the padding.

## Draft reply

The short version, per Jilei (2026-09-25). It explains the warning and asks how the series were
combined. The tested c3d recipe (Investigation 5) is held back until we know more about the data.

> Thanks for the screenshots, they help.
>
> **About the warning:** it only means the combined file stores its intensities as 64-bit
> ("double") numbers. The version of ITK-SNAP you're using keeps those values exactly, so nothing
> is lost, and the warning isn't what makes the image look bad. The message is out of date, and
> we'll fix it.
>
> To work out the quality problem, could you tell us a bit more about how you combined the two
> DICOM series?
> - What software or steps did you use?
> - Do the two sets of images overlap?
> - Which version of ITK-SNAP are you using (Help → About)?
>
> If you can share the combined DICOM, or the two original series, we can also take a look
> directly.
>
> **On stitching the NIfTI files:** ITK-SNAP itself doesn't have a stitching tool, but it comes
> with a command-line tool, Convert3D, that can do it. Once we know a bit more about your images,
> we can send you step-by-step instructions.

**Notes:**
- "The version of ITK-SNAP you're using keeps those values exactly" is safe because it rests on
  the warning wording (item 1), not on the scaling-factor inference.
- Jilei decides whether to keep the file-sharing request.

## For a fix session

Tracked as **[ISS-001](../confirmed_issues.md)**: the false "Possible Loss of Precision" warning
for `double`, confirmed from this thread's screenshot. When ISS-001 reaches `released`, tell this
user it's fixed.
