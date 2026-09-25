@echo off
rem build-deps.cmd - Build ITK-SNAP's dependencies on Windows into lib\ (gitignored).
rem
rem   vcpkg  curl, libssh, zlib  -> lib\vcpkg\installed\x64-windows-release
rem   ITK    v5.4.0 (static)     -> lib\itk\build     (used as ITK_DIR, like CI)
rem   VTK    v9.5.2 (static, Qt) -> lib\vtk\install
rem
rem Mirrors the windows-2022 job in itksnap/.github/workflows/build.yml. Qt is not
rem built here: install Qt >= 6.9.3 (msvc2022_64) with the Qt Maintenance Tool and
rem set QT_DIR if it is not C:\tk\Qt\6.9.3\msvc2022_64. Each step is skipped when
rem its output already exists, so the script is safe to re-run; delete lib\itk\build
rem or lib\vtk\build-9.5 + lib\vtk\install to force a rebuild.
rem
rem Usage (cmd or PowerShell):  scripts\windows\build-deps.cmd

setlocal
call "%~dp0vsenv.cmd" || exit /b 1
set "L=%LIBDIR:\=/%"
set "Q=%QT_DIR:\=/%"

rem --- vcpkg ------------------------------------------------------------------
if not exist "%LIBDIR%\vcpkg\.git" (
  git clone --depth 1 https://github.com/microsoft/vcpkg.git "%LIBDIR%\vcpkg" || exit /b 1
)
pushd "%LIBDIR%\vcpkg" || exit /b 1
rem Explicit .\ paths: with NoDefaultCurrentDirectoryInExePath set (Claude Code
rem sets it), cmd will not run a bare "bootstrap-vcpkg.bat" from the current dir.
if not exist vcpkg.exe call .\bootstrap-vcpkg.bat -disableMetrics || exit /b 1
set "X_VCPKG_ASSET_SOURCES=x-script,powershell -NoProfile -ExecutionPolicy Bypass -File %~dp0vcpkg-fetch.ps1 -Url {url} -Dst {dst}"
.\vcpkg.exe install curl libssh zlib --triplet x64-windows-release || exit /b 1
popd

rem vcpkg has now downloaded CMake and Ninja; put them on PATH.
call "%~dp0vsenv.cmd" || exit /b 1

rem --- ITK --------------------------------------------------------------------
if exist "%LIBDIR%\itk\build\lib\ITKCommon-5.4.lib" (
  echo ==^> ITK already built - skipping.
  goto :vtk
)
if not exist "%LIBDIR%\itk\src\.git" (
  git clone --depth 1 --branch v5.4.0 https://github.com/InsightSoftwareConsortium/ITK.git "%LIBDIR%\itk\src" || exit /b 1
)
if not exist "%LIBDIR%\itk\build\CMakeCache.txt" (
  rem /FORCE:MULTIPLE: CI's workaround for duplicate symbols in ITK 5.4.0 on MSVC.
  cmake -G Ninja -S "%L%/itk/src" -B "%L%/itk/build" -DCMAKE_BUILD_TYPE=Release ^
    -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF ^
    -DModule_MorphologicalContourInterpolation=ON ^
    -DCMAKE_INSTALL_PREFIX="%L%/itk/install" ^
    "-DCMAKE_EXE_LINKER_FLAGS=/FORCE:MULTIPLE" || exit /b 1
)
cmake --build "%L%/itk/build" -j %JOBS% || exit /b 1

rem --- VTK --------------------------------------------------------------------
:vtk
if exist "%LIBDIR%\vtk\install\lib\cmake\vtk-9.5\vtk-config.cmake" (
  echo ==^> VTK already installed - skipping.
  goto :done
)
if not exist "%LIBDIR%\vtk\src\.git" (
  git clone --depth 1 --branch v9.5.2 https://github.com/Kitware/VTK.git "%LIBDIR%\vtk\src" || exit /b 1
)
if not exist "%LIBDIR%\vtk\build-9.5\CMakeCache.txt" (
  rem RenderingExternal is required by the 3D view: vtkExternalOpenGLRenderWindow.
  rem No parentheses in comments inside this block - cmd would end the block there.
  cmake -G Ninja -S "%L%/vtk/src" -B "%L%/vtk/build-9.5" -DCMAKE_BUILD_TYPE=Release ^
    -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF -DBUILD_SHARED_LIBS=OFF ^
    -DVTK_QT_VERSION=6 -DVTK_GROUP_ENABLE_Qt=YES ^
    -DVTK_MODULE_ENABLE_VTK_GUISupportQtQuick=NO -DVTK_MODULE_ENABLE_VTK_GUISupportQtSQL=NO ^
    -DVTK_MODULE_ENABLE_VTK_RenderingExternal=YES -DVTK_SMP_ENABLE_STDTHREAD=OFF ^
    -DCMAKE_PREFIX_PATH="%Q%" -DCMAKE_INSTALL_PREFIX="%L%/vtk/install" || exit /b 1
)
cmake --build "%L%/vtk/build-9.5" -j %JOBS% --target install || exit /b 1

:done
echo.
echo ==^> Dependencies ready. Next: scripts\windows\build-release.cmd
