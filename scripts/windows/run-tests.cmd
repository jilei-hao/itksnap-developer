@echo off
rem run-tests.cmd - Run ctest in build-release\ with Qt's DLLs on PATH.
rem Extra arguments go to ctest, e.g.:  scripts\windows\run-tests.cmd -R SegAnchor
rem
rem The GUI tests open real ITK-SNAP windows on the desktop (about 13 minutes for
rem the full suite); leave the mouse and keyboard alone while they run.

setlocal
call "%~dp0vsenv.cmd" || exit /b 1
set "PATH=%QT_DIR%\bin;%PATH%"
cd /d "%DEVDIR%\build-release" || exit /b 1
ctest --output-on-failure %*
