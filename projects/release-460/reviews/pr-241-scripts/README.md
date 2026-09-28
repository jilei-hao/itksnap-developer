# Scripts for reviews/pr-241.md

These are Windows-only and run from PowerShell. They assume the layout used on 2026-09-25: the
worktree is at `C:\dev\snapwt\pr241` and the build at `C:\dev\snapwt\build-pr241`.

| File | Test | Use |
|---|---|---|
| `build-pr241.cmd` | build | `scripts\windows\build-release.cmd` with a different source and build directory |
| `acp-probe.cmd`, `acp.cpp` | T3 | prints `GetACP()` without and with the PR's manifest |
| `noutf8.manifest` | T2, T8c/d | the linker's default manifest. `mt.exe -nologo -manifest noutf8.manifest "-outputresource:copy.exe;#1"` strips the UTF-8 code page from a **copy** of a binary. `mt.exe` is in `C:\Program Files (x86)\Windows Kits\10\bin\<ver>\x64`. |
| `appdata-console.ps1` | T5 | `-Exe <logic_api_test.exe> -Label x`: runs a console exe that constructs `SystemInterface` with a non-ASCII `APPDATA`, then lists what was created, by code point |
| `e2e-appdata.ps1` | T8 | `-Exe <ITK-SNAP.exe> -Label x [-OpenImage]`: launches the GUI with a non-ASCII `APPDATA` (and a non-ASCII `-g` image), declines first-run prompts, closes normally, and reports what landed on disk. Opens a real window for about 25 s. |

Non-ASCII names are built from code points inside the scripts. That keeps them pure ASCII, which
Windows PowerShell 5.1 needs.
