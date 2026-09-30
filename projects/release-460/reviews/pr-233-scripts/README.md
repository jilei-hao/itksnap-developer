# #233 repro

`test_AdaptiveBrushSegGrid.js` crashes ITK-SNAP on `upstream/master` `52ee94fa`, and runs cleanly
with #233 merged (measured 2026-09-30, macOS).

To run it:
1. Copy the script to `Testing/GUI/Qt/Scripts/`.
2. Add `<file>Scripts/test_AdaptiveBrushSegGrid.js</file>` to `Testing/GUI/Qt/TestingScripts.qrc`.
3. Add `AdaptiveBrushSegGrid` to `GUI_TESTS` in `CMakeLists.txt`.
4. Rebuild `ITK-SNAP`, then run `ctest -R AdaptiveBrushSegGrid -V`.

On master it ends in `Subprocess aborted`, with `terminating due to uncaught exception of type
itk::InvalidRequestedRegionError`. It uses only files already in `Testing/TestData`.
