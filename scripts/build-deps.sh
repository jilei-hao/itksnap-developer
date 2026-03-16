#!/usr/bin/env bash
# build-deps.sh — Build ITK and VTK from source; download Qt via aqtinstall.
# Reads ITK_VERSION, VTK_VERSION, QT_VERSION, TARGET_OSX_VERSION from config.local.sh.
# All dependencies are installed under <devdir>/lib/.
#
# Usage:
#   scripts/build-deps.sh [OPTIONS]
#
# Options:
#   --skip-itk         Skip ITK build
#   --skip-vtk         Skip VTK build
#   --skip-qt          Skip Qt download
#   --force-itk        Rebuild ITK even if already installed
#   --force-vtk        Rebuild VTK even if already installed
#   --force-qt         Re-download Qt even if already present
#   -h, --help         Show this help
#
# Per-dependency full versions can be set in config.local.sh:
#   ITK_FULL_VERSION=5.4.0   (default: ${ITK_VERSION}.0)
#   VTK_FULL_VERSION=9.3.1   (default: ${VTK_VERSION}.1)
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
CONFIG="$DEVDIR/config.local.sh"
[ -f "$CONFIG" ] && source "$CONFIG"

# --- Versions (read from config.local.sh or use defaults) ---
ITK_VERSION="${ITK_VERSION:-5.4}"
VTK_VERSION="${VTK_VERSION:-9.3}"
QT_VERSION="${QT_VERSION:-6.8.3}"
TARGET_OSX_VERSION="${TARGET_OSX_VERSION:-14.0}"

# Full git tag versions — override in config.local.sh if needed
ITK_FULL_VERSION="${ITK_FULL_VERSION:-${ITK_VERSION}.0}"
VTK_FULL_VERSION="${VTK_FULL_VERSION:-${VTK_VERSION}.1}"

# --- Paths ---
LIB_DIR="$DEVDIR/lib"
ITK_SRC="$LIB_DIR/itk/src"
ITK_BUILD="$LIB_DIR/itk/build"
ITK_INSTALL="$LIB_DIR/itk/install"
VTK_SRC="$LIB_DIR/vtk/src"
VTK_BUILD="$LIB_DIR/vtk/build"
VTK_INSTALL="$LIB_DIR/vtk/install"
QT_INSTALL="$LIB_DIR/Qt"

# --- Flags ---
SKIP_ITK=0; SKIP_VTK=0; SKIP_QT=0
FORCE_ITK=0; FORCE_VTK=0; FORCE_QT=0

usage() {
  sed -n '/^# Usage:/,/^set -/{ /^set -/d; s/^# \{0,1\}//; p }' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-itk)   SKIP_ITK=1;  shift ;;
    --skip-vtk)   SKIP_VTK=1;  shift ;;
    --skip-qt)    SKIP_QT=1;   shift ;;
    --force-itk)  FORCE_ITK=1; shift ;;
    --force-vtk)  FORCE_VTK=1; shift ;;
    --force-qt)   FORCE_QT=1;  shift ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ "$(uname)" == "Darwin" ]]; then
  JOBS=$(sysctl -n hw.logicalcpu)
else
  JOBS=$(nproc)
fi
ARCH=$(uname -m)   # arm64 or x86_64

# Portable in-place sed (BSD/macOS requires an explicit backup suffix argument)
sed_inplace() {
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "$@"
  else
    sed -i "$@"
  fi
}

# On Linux, ensure required dev packages are present before attempting to build
if [[ "$(uname)" != "Darwin" ]] && command -v apt-get &>/dev/null; then
  MISSING_PKGS=()
  for pkg in libfreetype-dev zlib1g-dev libpng-dev libtiff-dev liblz4-dev liblzma-dev libssh-dev; do
    dpkg -s "$pkg" &>/dev/null || MISSING_PKGS+=("$pkg")
  done
  if [ "${#MISSING_PKGS[@]}" -gt 0 ]; then
    echo "ERROR: Missing required system packages: ${MISSING_PKGS[*]}" >&2
    echo "       Run: sudo apt-get install -y ${MISSING_PKGS[*]}" >&2
    exit 1
  fi
fi

mkdir -p "$LIB_DIR"

echo "==> Dependency build configuration"
echo "    ITK:              ${ITK_FULL_VERSION}  -> $ITK_INSTALL"
echo "    VTK:              ${VTK_FULL_VERSION}  -> $VTK_INSTALL"
echo "    Qt:               ${QT_VERSION} (clang_64 universal) -> $QT_INSTALL"
echo "    macOS target:     ${TARGET_OSX_VERSION}"
echo "    Parallel jobs:    ${JOBS}"
echo ""

# --- Helper: resolve a Qt kit root from a path that may point to the kit root,
#     lib/cmake, or lib/cmake/Qt6.  Prints the kit root and returns 0 on success.
qt_find_root() {
  local p="$1"
  [ -d "$p" ] || return 1
  if   [ -f "$p/lib/cmake/Qt6/Qt6Config.cmake" ]; then echo "$p"; return 0
  elif [ -f "$p/Qt6/Qt6Config.cmake" ];            then echo "$(cd "$p/../.." && pwd)"; return 0
  elif [ -f "$p/Qt6Config.cmake" ];                then echo "$(cd "$p/../../.." && pwd)"; return 0
  fi
  return 1
}

# --- Helper: set or update a key=value line in config.local.sh ---
update_config() {
  local key="$1" val="$2"
  touch "$CONFIG"
  if grep -q "^${key}=" "$CONFIG"; then
    sed_inplace "s|^${key}=.*|${key}=${val}|" "$CONFIG"
  else
    # Ensure the file ends with a newline before appending
    if [[ -s "$CONFIG" ]] && [[ "$(tail -c1 "$CONFIG" | wc -l)" -eq 0 ]]; then
      echo "" >> "$CONFIG"
    fi
    echo "${key}=${val}" >> "$CONFIG"
  fi
}

# ============================================================
# Detect already-installed deps and validate QT_PREFIX
# Updates config.local.sh with any paths found.
# ============================================================
detect_installed() {
  echo "==> Detecting already-installed dependencies..."
  local found_any=0

  # ITK — check ITK_DIR from config first, then the default install path
  local itk_cfg="${ITK_DIR:-}"
  local itk_default="$ITK_INSTALL/lib/cmake/ITK-${ITK_VERSION}"
  if [ -n "$itk_cfg" ] && [ -f "$itk_cfg/ITKConfig.cmake" ]; then
    echo "    ITK: found at $itk_cfg (from config)"
    update_config "ITK_DIR" "$itk_cfg"
    found_any=1
  elif [ -f "$itk_default/ITKConfig.cmake" ]; then
    echo "    ITK: found at $itk_default (default install)"
    update_config "ITK_DIR" "$itk_default"
    found_any=1
  else
    echo "    ITK: not detected"
  fi

  # VTK — same pattern
  local vtk_cfg="${VTK_DIR:-}"
  local vtk_default="$VTK_INSTALL/lib/cmake/vtk-${VTK_VERSION}"
  if [ -n "$vtk_cfg" ] && [ -d "$vtk_cfg" ]; then
    echo "    VTK: found at $vtk_cfg (from config)"
    update_config "VTK_DIR" "$vtk_cfg"
    found_any=1
  elif [ -d "$vtk_default" ]; then
    echo "    VTK: found at $vtk_default (default install)"
    update_config "VTK_DIR" "$vtk_default"
    found_any=1
  else
    echo "    VTK: not detected"
  fi

  # Qt — try to find a valid kit root from several sources.
  # Also try resolving the kit root from a qmake binary
  qt_root_from_qmake() {
    local qmake_bin="$1"
    command -v "$qmake_bin" &>/dev/null || return 1
    local prefix
    prefix=$("$qmake_bin" -query QT_INSTALL_PREFIX 2>/dev/null) || return 1
    [ -d "$prefix" ] && echo "$prefix"
  }

  local qt_valid=0
  local qt_root=""
  if [ -n "${QT_PREFIX:-}" ]; then
    if qt_root=$(qt_find_root "$QT_PREFIX"); then
      echo "    Qt: QT_PREFIX valid — kit root at $qt_root"
      qt_valid=1
    elif [ ! -d "$QT_PREFIX" ]; then
      echo "    Qt: WARNING — QT_PREFIX='$QT_PREFIX' does not exist"
    else
      echo "    Qt: WARNING — QT_PREFIX='$QT_PREFIX' exists but Qt6Config.cmake not found"
    fi
  fi
  if [ "$qt_valid" -eq 0 ]; then
    # Try qmake6 / qmake on PATH
    for qmake in qmake6 qmake; do
      if qt_root=$(qt_root_from_qmake "$qmake"); then
        echo "    Qt: found via $qmake at $qt_root"
        qt_valid=1; break
      fi
    done
  fi
  if [ "$qt_valid" -eq 0 ]; then
    # Check the aqt-downloaded location
    local aqt_prefix
    if [[ "$(uname)" == "Darwin" ]]; then
      aqt_prefix="$QT_INSTALL/${QT_VERSION}/macos"
    else
      aqt_prefix="$QT_INSTALL/${QT_VERSION}/gcc_64"
    fi
    if qt_root=$(qt_find_root "$aqt_prefix"); then
      echo "    Qt: found aqt install at $qt_root"
      qt_valid=1
    fi
  fi
  if [ "$qt_valid" -eq 1 ]; then
    update_config "QT_PREFIX" "$qt_root"
  else
    echo "    Qt: not detected"
  fi

  [ "$found_any" -eq 1 ] || true
  echo ""
}

detect_installed

# ============================================================
# Qt  (downloaded first — VTK needs it)
# ============================================================
download_qt() {
  local qt_prefix="$QT_INSTALL/$QT_VERSION/macos"
  local sentinel="$qt_prefix/lib/cmake/Qt6/Qt6Config.cmake"

  # If QT_PREFIX from config already points to a valid Qt installation, skip download
  local existing_root
  if [ "$FORCE_QT" -eq 0 ] && existing_root=$(qt_find_root "${QT_PREFIX:-}"); then
    echo "==> Qt already present via QT_PREFIX — skipping aqt download. (use --force-qt to re-download)"
    update_config "QT_PREFIX" "$existing_root"
    return
  fi

  if [ -f "$sentinel" ] && [ "$FORCE_QT" -eq 0 ]; then
    echo "==> Qt ${QT_VERSION} already present — skipping. (use --force-qt to re-download)"
    update_config "QT_PREFIX" "$qt_prefix"
    return
  fi

  if ! command -v aqt &>/dev/null; then
    echo "==> aqtinstall not found — installing via pip3..."
    pip3 install -q aqtinstall
  fi

  # macOS Qt builds are universal (arm64+x86_64) and always published as clang_64
  local qt_arch="clang_64"

  # Discover available modules so we only request ones that exist
  local extra_modules=""
  if aqt list-qt mac desktop --modules "$QT_VERSION" "$qt_arch" 2>/dev/null | grep -q "qtlinguisttools"; then
    extra_modules="qtlinguisttools"
  fi

  echo "==> Downloading Qt ${QT_VERSION} (${qt_arch})..."
  if [ -n "$extra_modules" ]; then
    aqt install-qt mac desktop "$QT_VERSION" "$qt_arch" \
      --modules $extra_modules \
      --outputdir "$QT_INSTALL"
  else
    aqt install-qt mac desktop "$QT_VERSION" "$qt_arch" \
      --outputdir "$QT_INSTALL"
  fi

  echo "==> Qt installed at $qt_prefix"
}

# Returns the Qt prefix dir usable as CMAKE_PREFIX_PATH.
# QT_PREFIX (from config.local.sh) takes priority when explicitly set,
# so you can point at Homebrew Qt or any other installation to override
# the aqt-downloaded Qt (which may link against removed frameworks like AGL).
qt_prefix_for_cmake() {
  # QT_PREFIX from config takes priority; re-use the same multi-layout resolver
  if [ -n "${QT_PREFIX:-}" ]; then
    local root
    if root=$(qt_find_root "$QT_PREFIX" 2>/dev/null); then
      echo "$root"; return
    fi
  fi
  local aqt_prefix
  if [[ "$(uname)" == "Darwin" ]]; then
    aqt_prefix="$QT_INSTALL/$QT_VERSION/macos"
  else
    aqt_prefix="$QT_INSTALL/$QT_VERSION/gcc_64"
  fi
  if [ -f "$aqt_prefix/lib/cmake/Qt6/Qt6Config.cmake" ]; then
    echo "$aqt_prefix"
  else
    echo ""
  fi
}

# ============================================================
# ITK
# ============================================================
build_itk() {
  local sentinel="$ITK_INSTALL/lib/cmake/ITK-${ITK_VERSION}/ITKConfig.cmake"

  if [ -f "$sentinel" ] && [ "$FORCE_ITK" -eq 0 ]; then
    echo "==> ITK ${ITK_FULL_VERSION} already installed — skipping. (use --force-itk to rebuild)"
    update_config "ITK_DIR" "$ITK_INSTALL/lib/cmake/ITK-${ITK_VERSION}"
    return
  fi

  echo "==> ITK ${ITK_FULL_VERSION}: cloning from GitHub..."
  if [ ! -d "$ITK_SRC/.git" ]; then
    git clone --depth 1 --branch "v${ITK_FULL_VERSION}" \
      https://github.com/InsightSoftwareConsortium/ITK.git "$ITK_SRC"
  else
    echo "    Source already present at $ITK_SRC — skipping clone."
  fi

  echo "==> ITK: configuring..."
  cmake -G Ninja \
    -S "$ITK_SRC" \
    -B "$ITK_BUILD" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="${TARGET_OSX_VERSION}" \
    -DCMAKE_INSTALL_PREFIX="$ITK_INSTALL" \
    -DBUILD_TESTING=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DITK_BUILD_DEFAULT_MODULES=ON \
    -DITK_USE_GPU=OFF \
    -DModule_MorphologicalContourInterpolation=ON \
    -DModule_ITKIOMINC=ON

  echo "==> ITK: building (${JOBS} jobs)..."
  cmake --build "$ITK_BUILD" --parallel "$JOBS"

  echo "==> ITK: installing..."
  cmake --install "$ITK_BUILD"

  echo "==> ITK ${ITK_FULL_VERSION} installed at $ITK_INSTALL"
}

# ============================================================
# VTK
# ============================================================
build_vtk() {
  local sentinel="$VTK_INSTALL/lib/cmake/vtk-${VTK_VERSION}"

  if [ -d "$sentinel" ] && [ "$FORCE_VTK" -eq 0 ]; then
    echo "==> VTK ${VTK_FULL_VERSION} already installed — skipping. (use --force-vtk to rebuild)"
    update_config "VTK_DIR" "$VTK_INSTALL/lib/cmake/vtk-${VTK_VERSION}"
    return
  fi

  local qt_prefix
  qt_prefix="$(qt_prefix_for_cmake)"
  if [ -z "$qt_prefix" ]; then
    echo "ERROR: Qt not found. Run without --skip-qt or set QT_PREFIX in config.local.sh." >&2
    exit 1
  fi

  echo "==> VTK ${VTK_FULL_VERSION}: cloning from GitHub mirror..."
  if [ ! -d "$VTK_SRC/.git" ]; then
    git clone --depth 1 --branch "v${VTK_FULL_VERSION}" \
      https://github.com/Kitware/VTK.git "$VTK_SRC"
  else
    echo "    Source already present at $VTK_SRC — skipping clone."
  fi

  # Patch typo in octree_node.txx (_M_chilren -> m_children)
  local octree_node="$VTK_SRC/Utilities/octree/octree/octree_node.txx"
  if grep -q "_M_chilren" "$octree_node" 2>/dev/null; then
    echo "==> Patching octree_node.txx typo (_M_chilren -> m_children)..."
    sed_inplace 's/_M_chilren/m_children/g' "$octree_node"
  fi

  echo "==> VTK: configuring (Qt prefix: $qt_prefix)..."
  cmake -G Ninja \
    -S "$VTK_SRC" \
    -B "$VTK_BUILD" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="${TARGET_OSX_VERSION}" \
    -DCMAKE_INSTALL_PREFIX="$VTK_INSTALL" \
    -DCMAKE_PREFIX_PATH="${qt_prefix};/opt/homebrew" \
    -DBUILD_TESTING=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DVTK_BUILD_ALL_MODULES=OFF \
    -DVTK_QT_VERSION=6 \
    -DVTK_MODULE_USE_EXTERNAL_VTK_zlib=ON \
    -DVTK_MODULE_USE_EXTERNAL_VTK_png=ON \
    -DVTK_MODULE_USE_EXTERNAL_VTK_tiff=ON \
    -DVTK_MODULE_USE_EXTERNAL_VTK_freetype=ON \
    -DVTK_MODULE_USE_EXTERNAL_VTK_lz4=ON \
    -DVTK_MODULE_USE_EXTERNAL_VTK_lzma=ON \
    -DVTK_MODULE_ENABLE_VTK_ChartsCore=YES \
    -DVTK_MODULE_ENABLE_VTK_GUISupportQt=YES \
    -DVTK_MODULE_ENABLE_VTK_IOExport=YES \
    -DVTK_MODULE_ENABLE_VTK_IOGeometry=YES \
    -DVTK_MODULE_ENABLE_VTK_IOImage=YES \
    -DVTK_MODULE_ENABLE_VTK_IOLegacy=YES \
    -DVTK_MODULE_ENABLE_VTK_IOPLY=YES \
    -DVTK_MODULE_ENABLE_VTK_ImagingCore=YES \
    -DVTK_MODULE_ENABLE_VTK_ImagingGeneral=YES \
    -DVTK_MODULE_ENABLE_VTK_InteractionStyle=YES \
    -DVTK_MODULE_ENABLE_VTK_InteractionWidgets=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingAnnotation=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingContext2D=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingContextOpenGL2=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingExternal=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingLOD=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingOpenGL2=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingUI=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingVolume=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingVolumeOpenGL2=YES \
    -DVTK_MODULE_ENABLE_VTK_RenderingGL2PSOpenGL2=YES \
    -DVTK_MODULE_ENABLE_VTK_ViewsContext2D=YES

  echo "==> VTK: building (${JOBS} jobs)..."
  cmake --build "$VTK_BUILD" --parallel "$JOBS"

  echo "==> VTK: installing..."
  cmake --install "$VTK_BUILD"

  echo "==> VTK ${VTK_FULL_VERSION} installed at $VTK_INSTALL"
}

# ============================================================
# Main
# ============================================================

[ "$SKIP_QT"  -eq 0 ] && download_qt
[ "$SKIP_ITK" -eq 0 ] && build_itk
[ "$SKIP_VTK" -eq 0 ] && build_vtk

echo ""
echo "==> All done."
[ "$SKIP_ITK" -eq 0 ] && echo "    ITK: $ITK_INSTALL"
[ "$SKIP_VTK" -eq 0 ] && echo "    VTK: $VTK_INSTALL"
[ "$SKIP_QT"  -eq 0 ] && echo "    Qt:  $QT_INSTALL/${QT_VERSION}/macos"
echo ""
echo "    Run scripts/build-debug.sh to build ITK-SNAP."
