# Review — six outside PRs: #243 and #251–#255

| | |
|---|---|
| Reviewed | 2026-09-29, on macOS arm64 (Apple Clang, Homebrew Qt 6.9.3, ITK 5.4, VTK 9.5.2) |
| Base | `upstream/master` @ `52ee94fa`. #251–#255 are cut from it. #243 is cut from `679ba76a`, so it was merged onto `52ee94fa` locally for testing (clean) |
| Method | An independent review agent read each PR (read-only), judging it against the linked issue before reading the PR text. I then built each PR, ran its test, and **undid the fix on purpose to see whether the test fails**. Each claim is marked **measured** (I ran it), **read** (I checked the code) or **agent** (the agent's reading, not re-checked) |
| Meeting page | https://claude.ai/artifact/KjsGnpqcBdf2P1G2RyGbCs (private). A rendered copy of this file as of 2026-09-29; this file stays the source of truth |
| Status | **Nothing is posted to GitHub.** The draft comment in each section needs Jilei's OK. Merges happen only at the planning meeting |
| On GitHub | All six were assigned to Jilei on 2026-09-25, and none has a milestone. CI has not run on any of them: each waits for a maintainer's "Approve and run", and would be red anyway (#259) |
| Scratch | Worktree `worktrees/pr-review` (detached; local merge commits only) and build `build-pr-review`. Probe programs are in the session scratchpad; none is committed anywhere |

## Summary

| PR | Fixes | Verdict | The one thing to know |
|---|---|---|---|
| [#251](https://github.com/pyushkevich/itksnap/pull/251) | `RLEImage::CleanUp()` would not compile if anyone called it (#216) | **Merge** | Nothing in the app calls it yet, so the risk is close to zero |
| [#252](https://github.com/pyushkevich/itksnap/pull/252) | Layer Inspector shows one orientation for every layer (#185) | **Merge** | Its GUI test really runs and fails without the fix. It also exposed an upstream Reorient bug (below) |
| [#253](https://github.com/pyushkevich/itksnap/pull/253) | Dropped label files with Windows line endings or no header open as images (#154) | **Merge** (two optional tidy-ups) | No false positives: of 49 test-data files, only the real `.label` file is accepted |
| [#254](https://github.com/pyushkevich/itksnap/pull/254) | Crash when a drop carries no file (#212) | **Merge after one wording change** | It stops the crash, but the reporter's drop will now do nothing. Say "Refs #212", not "Fixes" |
| [#255](https://github.com/pyushkevich/itksnap/pull/255) | UI language follows the region, not the language (#210) | **Needs Paul's decision** | Paul disagreed with the diagnosis in #210. On macOS with Qt 6.9.3, upstream already picks the right language in the reported setup. The Windows and Linux code has never been built |
| [#243](https://github.com/pyushkevich/itksnap/pull/243) | Strongly oblique images are refused: "invalid orientation (code IRI)" (#69) | **Merge after one small change** | It changes the displayed orientation of images tilted at exactly 45°, which load fine today (144 of 576 test matrices). A 5-line fallback avoids that |

**All six together** (measured: local merge on `52ee94fa`, full `ctest`): **38/39**.
- The only failure is `RemoteImageLoadTest_WorkspaceWithMesh`, on the p25 quantile: the rotating
  remote flake (W8 3b).
- The six new tests pass, and no existing test changed.
- Caveat: on this base, `RandomForestBailOut` (1.6 s) and `4DContinuousRenderingD` (1.4 s) are still
  upstream's two false passes. So those two cover nothing here, as on plain `upstream/master`.

**Collisions with our branches:** only in `CMakeLists.txt`, where everyone registers tests next to each
other (measured with `git merge-tree`):
- #251 with `bug/full-extent-off-by-one`;
- #253 and #255 with `bug/seg3d-into-4d-check`, and with each other;
- #243 with `test/seg-anchor-4d`, and with #241.

Each is trivial: keep both blocks. Whoever merges second rebases.

## Found on the way: Reorient Image no longer changes the main image (upstream)

**Measured on `upstream/master` `52ee94fa`** (probe `reorient_probe.cxx`):
1. Load `MRIcrop-orig.gipl.gz` (RAI).
2. Call `IRISApplication::ReorientImage(LAS)`, which is what Tools › Reorient Image does.

Result:
- the segmentation and the display geometry become LAS;
- **the main image stays RAI, and saving it writes RAI**.

**Read:**
- `ImageWrapper::SetDirectionMatrix` sets the direction on `m_ReferenceSpace`, not on the layer's own
  image. That code has not changed since `679ba76a`.
- What changed with seg_anchor is what `m_ReferenceSpace` points to: now the active segmentation.
- **Inferred:** a seg_anchor regression. A user who reorients and saves the image loses the change.
  I have not built a pre-seg_anchor tree to prove the "before".

Recorded as **W8 45**, for Paul, since it is his seg_anchor code. #252's reviewer spotted it, because
after #252 the Info tab shows the main image's real (unchanged) orientation.

---

## #251 — `RLEImage::CleanUp()` (aycibatuhan, fixes #216)

**Verdict: merge.**

- **Measured:**
  - the test passes, fragmenting 12 lines into 144 runs, then cleaning them to 34;
  - with upstream's `RLEImage.txx` restored, the test no longer compiles (`no member named 'size'
    in itk::SmartPointer<…>`). So the guard is a build failure rather than a failing test, which is
    loud enough.
- **Read / agent:**
  - the new loop walks the pixel container, so it works for any dimension, and for the per-time-point
    views of 4D images;
  - nothing in the app or the submodules calls `CleanUp` or `SetOnTheFlyCleanup`, so no app
    behaviour changes;
  - the test's four checks each catch a different mistake, and none is vacuous.
- **Optional follow-ups (agent, not blocking):**
  - `CleanUpLine` reserves the full line width and keeps it. A future caller would get lines *bigger*
    than uncompressed ones. Use `shrink_to_fit`.
  - A null pixel container would crash `->Size()`. No code path produces one.

**Draft comment:**
> Thank you. We built this on macOS and ran `RLECleanUpTest`: it passes. With the old `RLEImage.txx`
> the test no longer compiles, so it guards the fix. Nothing in ITK-SNAP calls `CleanUp()` yet, so this
> changes no behaviour today. One thing for later, not for this PR: `CleanUpLine()` reserves the full
> line width, so a cleaned line keeps that capacity. A `shrink_to_fit()` would stop a future caller from
> using more memory than an uncompressed image.

## #252 — orientation of the selected layer (aycibatuhan, fixes #185)

**Verdict: merge.**

- **Measured:**
  - the new GUI test `LayerOrientation` really runs (19.1 s) and passes: main `RPI`, overlay
    `Oblique (closest to RIA)`, main `RPI` again;
  - with upstream's `ImageInfoModel.cxx` restored, the overlay reads `RPI` and the test fails.
- **Read / agent:**
  - since seg_anchor, the old code showed the *reference space's* orientation, which is now the
    active segmentation, for every layer;
  - the fix reads each layer's own direction;
  - for meshes and for no selection, the `dynamic_cast` fails and the field is blank, like the other
    fields on the tab;
  - the test survives the harness's silent-lookup traps (W8 22/23/31–34). A missing row leaves `RPI`
    on screen, which the oblique check catches.
- **Small asks (optional):**
  - Check the exact string `Oblique (closest to RIA)`, not just the prefix.
  - The PR text says `GetImageGeometry()` is "the main image's geometry". Since seg_anchor it is the
    active segmentation's.
- **Side effect:** after Reorient Image, the main row now shows its real, unchanged orientation. That is
  the Reorient bug above, not this PR's.

**Draft comment:**
> Thank you. We built this and ran `LayerOrientation`: it passes, and with the old `ImageInfoModel.cxx`
> it fails, so the test guards the fix. Two small suggestions: compare the overlay's text exactly
> (`"Oblique (closest to RIA)"`) instead of its prefix, and note in the description that since the
> seg_anchor change the old code showed the active segmentation's orientation rather than the main
> image's.

## #253 — label files with CRLF or no header (aycibatuhan, fixes #154)

**Verdict: merge.** Two optional tidy-ups.

- **Measured:**
  - `TestColorLabelTableFile` passes;
  - with upstream's `ColorLabelTable.cxx` restored, 3 checks fail: CRLF validate, CRLF load and
    headerless validate;
  - **no false positives:** `ValidateFile` run on all 49 files in `Testing/TestData` (images, meshes,
    workspaces, DICOM, HTML) accepts only `MRIcrop-seg.label`.
- **Read / agent:**
  - the crash in #154's title was already fixed upstream in 4.2.2 (`02ecbeee` catches drop
    exceptions);
  - this PR fixes the remaining misdetection;
  - a file that passes the check but is broken further down fails with "Syntax error on line N"
    and leaves the label table unchanged.
- **Tidy-ups (agent, low):**
  - `ValidateFile` trims spaces, tabs and `\r`, but `LoadFromFile` trims only `\r`. So a headerless
    file with a blank line of spaces is accepted and then fails to load.
  - The test leaves six files in `Testing/Temporary`.

**Draft comment:**
> Thank you. We built this and ran `TestColorLabelTableFile`: it passes, and with the old
> `ColorLabelTable.cxx` three checks fail. We also ran the new `ValidateFile()` on every file in
> `Testing/TestData`; only the `.label` file is accepted, so dropped images are not mistaken for label
> files. Two optional tidy-ups: `LoadFromFile()` could trim spaces and tabs the same way `ValidateFile()`
> does, and the test could remove its temporary files, as `TestLargeImageCheck` does.

## #254 — drop event with no URLs (aycibatuhan, fixes #212)

**Verdict: merge after one wording change.**

- **Measured:** builds clean. There is no test.
- **Read / agent:**
  - the guard is correct, and the normal drop path is unchanged;
  - #212's stack trace shows the crash in the `QUrl` copy under `dropEvent`, so the URL list was
    empty.
  - After this PR, the reporter's drop does nothing, silently. The crash is gone, but the file still
    does not load.
- **Asks:**
  - Write "Refs #212", not "Fixes #212", and ask the reporter to try a build.
  - Optionally, use the same test as `dragEnterEvent` (exactly one local file), so that an `http://` URL
    or a two-file drop is refused cleanly.
- **Test:** practical but not trivial. It needs a small `SNAPTestQt` slot that sends a synthetic
  `QDropEvent`. Not worth holding the PR for.

**Draft comment:**
> Thank you, the guard is right and we confirmed it builds. One suggestion: the stack trace suggests the
> reporter's drops arrive with no file URLs at all, so after this change those drops will do nothing
> rather than load the file. Could you change "Fixes #212" to "Refs #212", so the issue stays open until
> the reporter confirms? Optionally, `dropEvent` could use the same condition as `dragEnterEvent`
> (exactly one local file).

## #255 — UI language from preferred languages (aycibatuhan, fixes #210)

**Verdict: needs Paul's decision.** It is not a code-quality problem.

- **Read (checked on GitHub):** in #210, Paul answered "I don't think the code is wrong", and that
  `LANG` should not be set if German is not wanted. A later comment reports the same effect on Windows,
  with Spanish.
- **Measured, macOS, Qt 6.9.3:**
  - `TestTranslationLocale` passes.
  - A probe runs upstream's own call, `QTranslator::load(QLocale(), "itksnap", …)`, against the built
    `.qm` files. It uses per-process `-AppleLocale` / `-AppleLanguages` overrides, so no system setting
    changed. In all four setups, **upstream already picks what the PR picks**:

    | Region | Preferred languages | Result (upstream and the PR) |
    |---|---|---|
    | de_DE | en-US | English (#210's setup) |
    | en_GB | en-GB, de-DE | English |
    | es_ES | en-US, es-ES | English |
    | de_DE | de-DE | German |

  - `LANG=de_DE.UTF-8` alone does not change what Qt picks on macOS.
  - So on the Qt that 4.6 requires (≥ 6.9.3), the macOS report does not reproduce. The author could not
    reproduce it either.
- **Agent:**
  - The Windows and Linux branches of `GetPreferredUILanguages()` have never been compiled or run.
  - The unit test covers the selection rules, but not the platform lists or the `main.cxx` wiring,
    which is where the bug was.
  - It is a behavior change for users who today get their region's language on purpose: for example a
    Spanish speaker in Spain on English Windows would switch to English. There is no in-app language
    setting to switch back, only `--lang`.
- **Suggestion for the meeting:** if Paul wants it, build and test it on the Windows box first, using
  the Spanish-on-Windows case from #210. It could also be narrowed to Windows and Linux, since macOS
  looks fine on current Qt.

**Draft comment (only after Paul decides):**
> Thank you for the careful analysis. We tested on macOS with Qt 6.9.3, which 4.6 requires: with English
> as the language and Germany as the region, the current code already loads the English translation, and
> so does this PR. So on macOS the change is not visible with current Qt. We have not yet been able to
> build the Windows and Linux paths. Paul will decide whether to change how the language is chosen; see
> his comments in #210.

## #243 — oblique orientation codes (duchenhe, #69)

**Verdict: merge after one small change.**

- **Measured** (probe `orient_probe.cxx`, which compares the PR's function with a copy of upstream's):
  - **200,000 random rotations:** 30,232 (15%) are refused by upstream today, and 0 are refused with the
    PR. None of the 169,768 that load today changes its code.
  - **Rotations of exactly 45°** (3 axes × 4 angles × 48 signed axis orders = 576 matrices, all of which
    load today): **144 change their code**. Examples: `Rx(135°)` goes from `RIP` to `RPS`, and columns
    (0,0,1), (c,c,0), (−c,c,0) go from `IAL` to `IRA`.
    - The cause is ties. The old code broke ties column by column, trying the diagonal first. The new
      code keeps the first of several equal permutations.
    - At 45°, `cos` and `sin` differ only in the last bit, and that difference is lost in the sum.
  - The PR's test passes. With upstream's `.cxx` restored, 4 checks fail, including the #69 `IRI` case.
- **Read / agent:**
  - everything that computes an orientation code calls this one function (loading, the Info tab, the
    wizard, reorient), so there is no inconsistency;
  - upstream has not touched the file since the PR's base.
- **Asks:**
  1. Run the old per-column logic first, and use the global assignment only when the old result is
     invalid. Every image that loads in 4.4 then keeps its layout, by construction.
  2. Add a test that the old and new results agree whenever the old one is valid, over a grid that
     includes multiples of 45°.
  3. Optional: reject a direction matrix containing NaN. According to the agent, such an image now
     loads with a made-up valid code (such as `LPS`), where it used to be refused.
  4. Retitle with `BUG:`.

**Draft comment:**
> Thank you, this fixes #69 and we confirmed it on current master: of 200,000 random rotations, 15% are
> refused today and none with this PR, and none of the random ones that load today changes its code.
> One case does change: images tilted by exactly 45°, where two axes tie. For example `Rx(135°)` shows as `RPS` instead
> of `RIP`; 144 of 576 such matrices change, and all of them load fine in 4.4. Could the function first
> compute the old per-column code and return it when it is valid, and only use the global assignment
> otherwise? That keeps every image that loads today exactly as it was. A test comparing old and new over
> a grid of angles including multiples of 45° would lock that in.
