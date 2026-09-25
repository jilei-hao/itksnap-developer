@echo off
rem vsenv.cmd - MSVC x64 toolchain + CMake/Ninja for the Windows build scripts.
rem Called by the other scripts in this directory; not meant to be run on its own.
rem
rem Sets DEVDIR (the wrapper root), LIBDIR, QT_DIR (override before calling),
rem and JOBS (default: NUMBER_OF_PROCESSORS).

rem Only once per shell: vcvars64.bat prepends to PATH on every call, and a second
rem call can push PATH past cmd's line-length limit. VSCMD_VER is set by it.
if defined VSCMD_VER goto :tools
rem vcvars64.bat looks up vswhere.exe on PATH; without the Installer directory it
rem prints "'vswhere.exe' is not recognized" - harmless, but noisy.
set "PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer;%PATH%"
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1

:tools

for %%I in ("%~dp0..\..") do set "DEVDIR=%%~fI"
set "LIBDIR=%DEVDIR%\lib"
if not defined QT_DIR set "QT_DIR=C:\tk\Qt\6.9.3\msvc2022_64"
if not defined JOBS set "JOBS=%NUMBER_OF_PROCESSORS%"

rem CMake and Ninja: use the ones vcpkg downloads (build-deps.cmd runs vcpkg first).
rem Versions change when vcpkg is updated, hence the globs.
set "CMAKE_BIN="
set "NINJA_BIN="
for /d %%D in ("%LIBDIR%\vcpkg\downloads\tools\cmake-*-windows") do (
  for /d %%E in ("%%D\cmake-*") do set "CMAKE_BIN=%%E\bin"
)
for /d %%D in ("%LIBDIR%\vcpkg\downloads\tools\ninja-*-windows") do set "NINJA_BIN=%%D"
if defined CMAKE_BIN set "PATH=%CMAKE_BIN%;%PATH%"
if defined NINJA_BIN set "PATH=%NINJA_BIN%;%PATH%"
exit /b 0
