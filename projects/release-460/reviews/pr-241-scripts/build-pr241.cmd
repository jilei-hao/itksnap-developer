@echo off
rem Review build of staging/v460 + upstream PR 241, mirroring scripts\windows\build-release.cmd
rem Source: C:\dev\snapwt\pr241   Build: C:\dev\snapwt\build-pr241
setlocal
call "C:\dev\itksnap-developer\scripts\windows\vsenv.cmd" || exit /b 1
set "L=%LIBDIR:\=/%"
set "V=%L%/vcpkg/installed/x64-windows-release"
if not exist "C:\dev\snapwt\build-pr241\CMakeCache.txt" (
  cmake -G Ninja -S "C:/dev/snapwt/pr241" -B "C:/dev/snapwt/build-pr241" -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_TOOLCHAIN_FILE="%L%/vcpkg/scripts/buildsystems/vcpkg.cmake" ^
    -DVCPKG_TARGET_TRIPLET=x64-windows-release ^
    -DCMAKE_PREFIX_PATH="%QT_DIR:\=/%" ^
    -DITK_DIR="%L%/itk/build" -DVTK_DIR="%L%/vtk/install/lib/cmake/vtk-9.5" ^
    -DCURL_LIBRARY="%V%/lib/libcurl.lib" -DCURL_INCLUDE_DIR="%V%/include" ^
    "-DCMAKE_EXE_LINKER_FLAGS=/FORCE:MULTIPLE" || exit /b 1
)
cmake --build "C:/dev/snapwt/build-pr241" -j %JOBS% %* || exit /b 1
