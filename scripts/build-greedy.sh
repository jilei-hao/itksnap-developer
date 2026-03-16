#!/usr/bin/env bash
# build-greedy.sh — Build standalone Greedy from itksnap's submodule.
# Produces a GreedyConfig.cmake in build-greedy/ so that greedy_python
# can find it via -DGreedy_DIR.
#
# Run from itksnap-developer/ root.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
GREEDY_SRC="$DEVDIR/itksnap/Submodules/greedy"
BUILD_DIR="$DEVDIR/build-greedy"
INSTALL_DIR="$DEVDIR/build-greedy/install"

# Source local config for ITK_DIR, VTK_DIR
CONFIG="$DEVDIR/config.local.sh"
if [ -f "$CONFIG" ]; then
  source "$CONFIG"
fi

ITK_DIR="${ITK_DIR:-}"
VTK_DIR="${VTK_DIR:-}"

if [ -z "$ITK_DIR" ] || [ -z "$VTK_DIR" ]; then
  echo "ERROR: ITK_DIR and VTK_DIR must be set (via config.local.sh or env)." >&2
  exit 1
fi

echo "==> Configuring standalone Greedy..."
echo "    Source:  $GREEDY_SRC"
echo "    Build:   $BUILD_DIR"
echo "    Install: $INSTALL_DIR"
echo "    ITK_DIR: $ITK_DIR"
echo "    VTK_DIR: $VTK_DIR"

cmake -G Ninja \
  -S "$GREEDY_SRC" \
  -B "$BUILD_DIR" \
  -DCMAKE_BUILD_TYPE=Release \
  -DITK_DIR="$ITK_DIR" \
  -DVTK_DIR="$VTK_DIR" \
  -DGREEDY_BUILD_LMSHOOT=ON \
  -DGREEDY_BUILD_AS_SUBPROJECT=OFF \
  -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
  -DEigen3_DIR=/opt/homebrew/Cellar/eigen@3/3.4.1/share/eigen3/cmake

echo "==> Building Greedy..."
cmake --build "$BUILD_DIR" -- -j$(sysctl -n hw.logicalcpu)

echo "==> Installing Greedy..."
cmake --install "$BUILD_DIR"

# The propagation subdirectory headers are not installed by greedy's CMakeLists.
# Copy them manually so greedy_python can find PropagationParameters.hxx.
PROP_SRC="$GREEDY_SRC/src/propagation"
cp "$PROP_SRC"/*.h "$INSTALL_DIR/include/" 2>/dev/null || true
cp "$PROP_SRC"/*.hxx "$INSTALL_DIR/include/" 2>/dev/null || true

# propagationapi is not exported by greedy's install rules.
# Copy the library and append its target definition to GreedyTargets.cmake.
PROP_LIB="$BUILD_DIR/propagation/libpropagationapi.a"
GREEDY_TARGETS="$INSTALL_DIR/lib/cmake/Greedy/GreedyTargets.cmake"
if [ -f "$PROP_LIB" ]; then
    cp "$PROP_LIB" "$INSTALL_DIR/lib/"
    cat >> "$GREEDY_TARGETS" <<'EOF'

# propagationapi — added by build-greedy.sh (not exported by upstream CMakeLists)
if(NOT TARGET propagationapi)
    add_library(propagationapi STATIC IMPORTED)
    get_filename_component(_GREEDY_SELF "${CMAKE_CURRENT_LIST_FILE}" PATH)
    get_filename_component(_GREEDY_SELF "${_GREEDY_SELF}" PATH)
    get_filename_component(_GREEDY_SELF "${_GREEDY_SELF}" PATH)
    get_filename_component(_GREEDY_SELF "${_GREEDY_SELF}" PATH)
    set_target_properties(propagationapi PROPERTIES
        IMPORTED_LOCATION "${_GREEDY_SELF}/lib/libpropagationapi.a"
        INTERFACE_LINK_LIBRARIES "greedyapi"
    )
endif()
EOF
fi

echo "==> Done. GreedyConfig.cmake at: $INSTALL_DIR/lib/cmake/Greedy/GreedyConfig.cmake"
