@echo off
rem build-release.cmd - Configure and build ITK-SNAP (all targets) into build-release\.
rem Needs scripts\windows\build-deps.cmd to have run. Configures only on the first
rem run; after that it just builds. Delete build-release\ after changing Qt, VTK or
rem ITK.
rem
rem Usage (cmd or PowerShell):  scripts\windows\build-release.cmd

setlocal
call "%~dp0vsenv.cmd" || exit /b 1
set "D=%DEVDIR:\=/%"
set "L=%LIBDIR:\=/%"
set "V=%L%/vcpkg/installed/x64-windows-release"

if not exist "%DEVDIR%\build-release\CMakeCache.txt" (
  rem The vcpkg toolchain file also copies the curl/ssh/zlib DLLs next to each
  rem executable, which the GUI tests need: their PATH is set to Qt's bin only.
  cmake -G Ninja -S "%D%/itksnap" -B "%D%/build-release" -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_TOOLCHAIN_FILE="%L%/vcpkg/scripts/buildsystems/vcpkg.cmake" ^
    -DVCPKG_TARGET_TRIPLET=x64-windows-release ^
    -DCMAKE_PREFIX_PATH="%QT_DIR:\=/%" ^
    -DITK_DIR="%L%/itk/build" -DVTK_DIR="%L%/vtk/install/lib/cmake/vtk-9.5" ^
    -DCURL_LIBRARY="%V%/lib/libcurl.lib" -DCURL_INCLUDE_DIR="%V%/include" ^
    "-DCMAKE_EXE_LINKER_FLAGS=/FORCE:MULTIPLE" || exit /b 1
)
cmake --build "%D%/build-release" -j %JOBS% || exit /b 1
