Hi @marcoduering, thank you for this PR, and for your patience while it waited. I've added it to the 4.6.0 milestone.

I built it on Windows 11 (system code page 1252, MSVC 2022, Qt 6.9.3, ITK 5.4.0), both on its own and merged on top of our 4.6 staging branch. Then I ran it with `%APPDATA%` pointing at a folder named `…\Müller_日本`:

- **Before:** ITK-SNAP refuses to start with the old "non-ASCII characters in user names" message.
- **With your PR:** it starts and writes `UserPreferences.xml`, `ImageAssociations` and `Thumbnails` under the correct Unicode path.
- **Full test suite with that `%APPDATA%`:** 40/42. Both failures are remote-image tests that also fail or flake on Windows without your change.

Your write-up made this easy to check. Comparing against the wide-character API in the test was what let me see what was going on at each step.

While testing, I found that the fix works slightly differently than the description says. It also turns out to fix more than the title suggests. I stripped the manifest from copies of the built binaries (`mt.exe -outputresource`) to separate the two parts of the change:

**1. Removing the guard is what fixes the user-name case.**
ITK builds its kwsys with `KWSYS_ENCODING_DEFAULT_CODEPAGE=CP_UTF8` ([`Modules/ThirdParty/KWSys/CMakeLists.txt` in 5.4.0](https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4.0/Modules/ThirdParty/KWSys/CMakeLists.txt#L11)), and VTK does the same, so itksys already decodes UTF-8. That is probably the ITK 4.5 change the original 2014 commit was waiting for. The CRT side is covered by the `setlocale(LC_ALL, ".UTF8")` in `main.cxx`, as you pointed out. With the manifest removed, `ITK-SNAP.exe` still starts with the non-ASCII `%APPDATA%` and saves its preferences in the right place. A nice consequence: this part should also work on Windows builds older than 1903, where the manifest is ignored. The stripped binary simulates that case.

**2. The manifest fixes non-ASCII paths on the command line.**
This is the effect you mentioned in your follow-up comment, and it matters more than it first appears. Without the manifest, `argv` arrives in the legacy code page, so `日本` becomes `??`. `DecodeFilename()` (`main.cxx:439`) then fails in `GetLongPathNameA`, and `ITK-SNAP.exe -g …\Brücke_日本.gipl.gz` exits during startup. With the manifest, the same command opens the image, and the recent-files history stores the path correctly. This should also cover opening such files by double-clicking them in Explorer.

**What I changed**

To get this merged without another round trip, I pushed four small commits on top of your branch (thank you for allowing maintainer edits). Your change itself is untouched:

1. **`DOC:` Explain what the UTF-8 process code page is needed for.** The comments in `SystemInterface.cxx`, `itksnap.manifest` and `CMakeLists.txt` now describe the two parts above. Comments only.
2. **`BUG:` Report the APPDATA length without the terminating null.** On overflow, `GetEnvironmentVariableW` returns the size including the null, so the "too long" message counted one extra character.
3. **`ENH:` Test APPDATA, the command line and the code page in `NonAsciiPathTest`.**
   - The test now calls `setlocale(LC_ALL, ".UTF8")` as `main()` does, so its Registry checks match what `ITK-SNAP.exe` does.
   - On Windows it adds a check that `SystemInterface` starts with a non-ASCII `%APPDATA%`. This check fails if the old guard is put back.
   - It adds three checks for what the manifest provides: `GetACP() == CP_UTF8`; `GetLongPathNameA` on the UTF-8 path; and a child process that receives the path on its command line and checks its `argv`. All three fail with the manifest stripped.
   - I ran both of those negative controls to confirm that each check fails for the right reason.
4. **`ENH:` Give `itksnap-wt` the UTF-8 process code page manifest**, as you offered. Before, `itksnap-wt -i …\Müller_日本\mricrop.itksnap` reported that the file does not exist; now it reads the workspace. c3d and greedy live in their own repositories, so they can follow separately.

Thanks as well for the detailed CI analysis. Those failures come from the workflow, not from your change, and we'll look at them separately. And a heads-up so it doesn't surprise you: ITK-SNAP also exits on Windows when `-g` points to a file that doesn't exist, because `DecodeFilename()` throws before `main()`'s `try`. That problem predates your PR, and we'll fix it on our side.
