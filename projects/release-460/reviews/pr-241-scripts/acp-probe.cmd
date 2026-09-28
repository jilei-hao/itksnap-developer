@echo off
rem acp-probe.cmd - T3 of reviews/pr-241.md: does the PR's manifest switch GetACP() to 65001?
rem Builds acp.cpp twice (plain / with the PR's manifest) and runs both. Output goes next to this file.
call "C:\dev\itksnap-developer\scripts\windows\vsenv.cmd" || exit /b 1
cd /d "%~dp0"
if not exist itksnap.manifest git -C C:\dev\itksnap-developer\itksnap show pr/241:Utilities/Win32/itksnap.manifest > itksnap.manifest
cl /nologo /EHsc acp.cpp /Fe:acp_plain.exe >nul || exit /b 1
cl /nologo /EHsc acp.cpp /Fe:acp_manifest.exe /link /MANIFEST:EMBED /MANIFESTINPUT:itksnap.manifest >nul || exit /b 1
.\acp_plain.exe
.\acp_manifest.exe
