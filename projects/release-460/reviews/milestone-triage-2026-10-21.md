# v4.6.0 milestone triage — 2026-10-21

Fetched from GitHub (unauthenticated API: `gh` here has an invalid token and fails TLS) and
`git fetch upstream` on 2026-10-21. Nothing in this file has been posted. Each close or comment
needs Jilei's OK, and `gh` must be logged in again first (`gh auth refresh -h github.com`).

## What happened upstream

`upstream/master` moved from `41a1e0a6` (2026-10-05) to **`8868dc2e`** (2026-10-21): 169 commits,
most of them Paul's "4.6 cleanup" PRs #267–#290, plus CI work (#275–#293) and the version bump to
**4.6.0-alpha.5** with 4.6 release notes (#289).

Merged outside or old PRs: **#241** (non-ASCII Windows user names, with Jilei's 4 commits), **#196**
(zh_CN), **#253** (CRLF label files), **#280** (macOS launcher paths), **#284** (Flywheel URLs),
**#114** (old contour interpolator removed).

Paul closed as already fixed, today: **#233** (by `0e310d2a` + #296), **#251** and **#254** (by #290),
and with them issues #222, #212, #216, #154, #256, #257.

## The milestone now

74 items: **14 open**, 60 closed.

| # | Kind | Title (short) | State | What to do |
|---|---|---|---|---|
| [#69](https://github.com/pyushkevich/itksnap/issues/69) | issue | invalid orientation code for oblique images | open | Fixed by #243 when it merges. **#20 is a duplicate** (below) |
| [#128](https://github.com/pyushkevich/itksnap/pull/128) | PR (2024, a-a-danilov) | workaround for malformed 4D CTA DICOM | open, merges clean; assigned to Jilei | Not reviewed yet. Touches the same two files as `feature/cardiac-io`, but merges cleanly with it |
| [#182](https://github.com/pyushkevich/itksnap/pull/182) | PR | MSVC build speed (+1 line) | open, merges clean | Approved by dzenanz; not reviewed here |
| [#185](https://github.com/pyushkevich/itksnap/issues/185) | issue | orientation code doesn't follow the selected layer | open | Fixed by #252 when it merges |
| [#210](https://github.com/pyushkevich/itksnap/issues/210) | issue | "ITK-SNAP is suddenly German" | open | One decision closes it: #255 (follow preferred languages) or #260 (a Language preference) or both |
| [#229](https://github.com/pyushkevich/itksnap/issues/229) | issue | free rotation vs the 3D mesh | open | Our `bug/free-rotation-3d-sync`, no PR yet |
| [#234](https://github.com/pyushkevich/itksnap/issues/234) | issue | nnInteractive backend v2 | open | itksnap-dls work. **#236 is the same break** (below) |
| [#243](https://github.com/pyushkevich/itksnap/pull/243) | PR | orientation codes for oblique images | open, **conflicts with master** | Master merged in locally: `pr-merge/243` (below) |
| [#252](https://github.com/pyushkevich/itksnap/pull/252) | PR | orientation of the selected layer | open, **conflicts with master** | Master merged in locally: `pr-merge/252` |
| [#255](https://github.com/pyushkevich/itksnap/pull/255) | PR | UI language from preferred languages | open, **conflicts with master** | Master merged in locally: `pr-merge/255`; Paul's decision |
| [#258](https://github.com/pyushkevich/itksnap/issues/258) | issue (ours) | `RemoteImageLoadTest_Cache` on Windows/Linux | open | **Fixed upstream** — close (below) |
| [#259](https://github.com/pyushkevich/itksnap/issues/259) | issue (ours) | CI: PR builds fail; failing tests never fail a run | open | **Part 1 fixed, part 2 declined by design** — close (below) |
| [#260](https://github.com/pyushkevich/itksnap/issues/260) | issue (ours) | Language preference | open | Our `feature/ui-language-setting`, rebased today |
| [#291](https://github.com/pyushkevich/itksnap/issues/291) | issue (new, venkmurthy) | Windows installer registers CPack placeholders | open, assigned to Paul | Real and **not fixed**. Cause seen in `CMakeLists.txt`: `CPACK_NSIS_DISPLAY_NAME` (line ~2106) uses `CPACK_PACKAGE_INSTALL_DIRECTORY` before it is set (~2118), hence the leading space; `CPACK_PACKAGE_VERSION` and `CPACK_PACKAGE_VENDOR` are never set, hence CPack's defaults 0.1.1 and "Humanity" |

## Can be closed

### Fixed upstream (our own issues)

**#258 — fixed by `60bc0f60`** (#271), extended in #272. `RemoteImageLoadTest_Cache` now asks the
application for its data directory, and CMake gives `_Cache` and `_URLKeys` their own data
directory through `APPDATA` / `HOME` / the working directory. That is the same fix as our
`bug/remote-cache-test-datadir`. What is left: the other five remote tests (`_SingleImage`,
`_EncodedURL`, `_WorkspaceWithMesh`, `_SaveWorkspace`, `_Cancel`) still download through the
user's real cache on Windows and Linux. They add files there but never clear it.

Draft comment:

> Fixed on master by 60bc0f60 (#271): `RemoteImageLoadTest_Cache` now asks the application for
> its data directory, and CMake points `APPDATA`/`HOME` at a folder in the build tree, so it passes
> on Windows and Linux and no longer clears the real cache. #272 gave `_URLKeys` the same treatment.
> The other remote tests still download through the real cache on Windows and Linux, but they only
> add to it. Closing; thanks!

```bash
gh issue close 258 -R pyushkevich/itksnap -c "<comment above>"
```

**#259 — part 1 fixed, part 2 a deliberate choice.** `5e21fa0b` ("make pull-request builds
actually build and test") lets `ExperimentalUpdate` fail without stopping the build, and
`4f96672f` fails the job on compile errors. On test failures the workflow now says: "Failing tests
don't stop the job (some are allowed to fail); they are reported on CDash." That is item 4 of the
issue, decided.

Draft comment:

> Thanks for the CI work in #275–#293. Pull-request builds now build and test (5e21fa0b), and a
> compile error fails the job (4f96672f), which was the main point here. Failing tests are reported
> on CDash rather than failing the job, as the workflow now says. Closing.

```bash
gh issue close 259 -R pyushkevich/itksnap -c "<comment above>"
```

### Duplicates

| Close | Duplicate of | Why | Confidence |
|---|---|---|---|
| [#20](https://github.com/pyushkevich/itksnap/issues/20) (2020) | [#69](https://github.com/pyushkevich/itksnap/issues/69) | Same error, "Image has an invalid orientation", for a direction matrix with non-axis-aligned values. #243 explains the cause: `ConvertDirectionMatrixToClosestRAICode` maps two image axes to the same anatomical axis. #69 has the repro and the fix PR, so it is the one to keep | high on the symptom; #20 has no data file, so not reproduced |
| [#236](https://github.com/pyushkevich/itksnap/issues/236) | [#234](https://github.com/pyushkevich/itksnap/issues/234) | #236 is the concrete nnInteractive 2.x break (`use_pinned_memory` removed); #234 is the v2 support request. itksnap-dls `main` already dropped the argument (`7270f8a`, 2026-06-11). Close #236 once a release with it is on PyPI | high |
| [#202](https://github.com/pyushkevich/itksnap/issues/202) | [#58](https://github.com/pyushkevich/itksnap/issues/58) | Both "Exception: vector too long" while loading images on Windows | low: no data in either, so the cause may differ. Ask before closing |
| [#92](https://github.com/pyushkevich/itksnap/issues/92) | [#5](https://github.com/pyushkevich/itksnap/issues/5) | Both "libpng12 missing" with the 3.8 Linux binary. Both obsolete after 4.6: the Linux x64 package is now built on Rocky Linux 8 (glibc 2.28, `85f10a2b`), which also answers #92's glibc part | medium: close both when 4.6 ships |

Draft comment for #20:

> This looks like the same problem as #69: a direction matrix that is far from the axes gives an
> invalid orientation code. #243 has a fix. Closing as a duplicate of #69; please reopen if your
> image still fails to load once that is merged.

```bash
gh issue close 20 -R pyushkevich/itksnap --reason "not planned" -c "<comment above>"
```

### Fixed upstream, not on the milestone (close when 4.6.0 ships)

| Issue | Fixed by |
|---|---|
| [#242](https://github.com/pyushkevich/itksnap/issues/242) Windows on ARM build | ARM64 builds in CI (`2fdcc1c7`, `cf0cddee`) |
| [#113](https://github.com/pyushkevich/itksnap/issues/113) CMP0080 deprecation warning | `661cd08d` removed the OLD-policy workaround (2026-05-07) |
| [#16](https://github.com/pyushkevich/itksnap/issues/16) `VTK_USE_FILE` deprecation warning | gone from the CMake files since 2021 |
| [#169](https://github.com/pyushkevich/itksnap/issues/169) c3d fails with ITK 5.4.2 | c3d updated (`dbf814c4`); CI builds on ITK 5.4.7. Likely, not checked |

### Not duplicates (checked)

- #228 (free rotation does not turn the additional images) and #176 (2D segmentation mapping after a
  loaded transform) are free-rotation bugs, but not #229.
- #291 is new; nothing else reports the installer metadata.

## Outside PRs that conflict with master

All three conflicts are in test registration lists only. Master is merged into each PR head
locally, in the same way as #196, so the contributors' commits stay as they are. **Not built and not
pushed.** Pushing needs Jilei's OK and "maintainers can modify" on each fork.

| PR | Local branch | Resolution |
|---|---|---|
| #243 | `pr-merge/243` | kept both test blocks in `CMakeLists.txt` |
| #252 | `pr-merge/252` | appended `LayerOrientation` after upstream's new GUI tests (`CMakeLists.txt`, `TestingScripts.qrc`) |
| #255 | `pr-merge/255` | upstream replaced the GUI-test `FOREACH` with `ADD_SNAP_GUI_TEST()`; kept upstream's version and added the PR's `TestTranslationLocale` block before it. The PR's `main.cxx` hunk merged cleanly and still sits right before the translator load |
