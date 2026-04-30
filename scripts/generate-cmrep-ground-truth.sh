#!/usr/bin/env bash
# generate-cmrep-ground-truth.sh — populate ConvertMesh/Testing/Fixtures/cmrep-truth/
# with reference outputs produced by the cmrep utilities.
#
# Workflow:
#   1. Generate a small synthetic sphere image (sphere.nii.gz) via the
#      MakeSphereImage helper that ships with the ConvertMesh test suite.
#   2. Run cmrep tools (vtklevelset, mesh_image_sample, mesh2img,
#      mesh_merge_arrays, mesh_smooth_curv, mesh_decimate_vcg) against that
#      input, producing reference VTK meshes / NIFTI images.
#   3. Drop everything into Testing/Fixtures/cmrep-truth/ for ConvertMesh's
#      CmrepParityTest to consume.
#
# Run after `scripts/build-cmrep.sh` and `scripts/build-convertmesh.sh`.
# Re-run only when cmrep behaviour changes — the produced files are tiny and
# committed to source control.
set -euo pipefail

DEVDIR="${DEVDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
CMREP_BUILD="${CMREP_BUILD:-$DEVDIR/build-cmrep}"
CMESH_BUILD="${CMESH_BUILD:-$DEVDIR/build-convertmesh}"
TRUTH_DIR="$DEVDIR/ConvertMesh/Testing/Fixtures/cmrep-truth"
MAKE_SPHERE="$CMESH_BUILD/Testing/MakeSphereImage"
ADD_TAG="$CMESH_BUILD/Testing/AddTagArray"

for bin in "$CMREP_BUILD/vtklevelset" \
           "$CMREP_BUILD/mesh_image_sample" \
           "$CMREP_BUILD/mesh2img" \
           "$CMREP_BUILD/mesh_merge_arrays" \
           "$CMREP_BUILD/mesh_smooth_curv" \
           "$CMREP_BUILD/mesh_decimate_vcg"; do
  if [ ! -x "$bin" ]; then
    echo "ERROR: missing cmrep binary $bin — run scripts/build-cmrep.sh first." >&2
    exit 1
  fi
done

for bin in "$MAKE_SPHERE" "$ADD_TAG"; do
  if [ ! -x "$bin" ]; then
    echo "ERROR: missing $bin — run scripts/build-convertmesh.sh first" >&2
    echo "       (or 'ninja MakeSphereImage AddTagArray' inside the build dir)." >&2
    exit 1
  fi
done

mkdir -p "$TRUTH_DIR"

# Step 1: input fixture — a 32^3 binary sphere
echo "==> Generating sphere.nii.gz"
"$MAKE_SPHERE" "$TRUTH_DIR/sphere.nii.gz" 32

# Step 2: vtklevelset → sphere-mesh.vtk (also serves as the input mesh for
# every downstream tool). -k applies the clean filter so cmesh's `-clean`
# matches; -f orients normals outward.
echo "==> vtklevelset → sphere-mesh.vtk"
"$CMREP_BUILD/vtklevelset" -k -f \
    "$TRUTH_DIR/sphere.nii.gz" \
    "$TRUTH_DIR/sphere-mesh.vtk" \
    0.5

# Step 3: mesh_image_sample → sphere-sampled.vtk (linear interpolation;
# array name "Intensity" — same default as cmesh -sample-image)
echo "==> mesh_image_sample → sphere-sampled.vtk"
"$CMREP_BUILD/mesh_image_sample" -i 1 \
    "$TRUTH_DIR/sphere-mesh.vtk" \
    "$TRUTH_DIR/sphere.nii.gz" \
    "$TRUTH_DIR/sphere-sampled.vtk" \
    Intensity

# Step 4: mesh2img → sphere-rasterized.nii.gz (fill interior).
# Use auto-bbox mode rather than `-ref sphere.nii.gz`: cmrep's mesh2img -ref
# code path is broken in this configuration (it produces an empty image when
# the reference geometry doesn't match the cmrep auto-bbox convention of a
# (-1,-1,1) direction matrix). Auto mode with 1mm spacing and 0 margin gives
# the cmrep canonical rasterization of this mesh, which the parity test
# compares against by physical volume rather than voxel-wise.
echo "==> mesh2img → sphere-rasterized.nii.gz (auto-bbox, 4mm margin)"
"$CMREP_BUILD/mesh2img" \
    -i "$TRUTH_DIR/sphere-mesh.vtk" \
    -f \
    -a 1 1 1 4 \
    "$TRUTH_DIR/sphere-rasterized.nii.gz"

# Step 5: mesh_merge_arrays → sphere-merged.vtk
# Build a "tagged" copy that carries an extra "Tag" array, then merge that
# array onto sphere-mesh via mesh_merge_arrays. The output should equal
# sphere-mesh decorated with Tag — mirroring `cmesh -merge-array`.
echo "==> Building sphere-tagged.vtk (helper input for merge)"
"$ADD_TAG" \
    "$TRUTH_DIR/sphere-mesh.vtk" \
    "$TRUTH_DIR/sphere-tagged.vtk" \
    Tag

echo "==> mesh_merge_arrays → sphere-merged.vtk"
# mesh_merge_arrays adds the named array of every input mesh onto the output
# (geometry from -r reference). With one input and the reference set to the
# bare sphere mesh, the output is sphere-mesh + Tag.
"$CMREP_BUILD/mesh_merge_arrays" \
    -r "$TRUTH_DIR/sphere-mesh.vtk" \
    "$TRUTH_DIR/sphere-merged.vtk" \
    Tag \
    "$TRUTH_DIR/sphere-tagged.vtk"

# Step 6: mesh_smooth_curv → sphere-smoothed-vcg.vtk
# Taubin smoothing (mu = -0.51, lambda = 0.5, default 1000 iters is too much
# for a 32^3 sphere — use 50 iters)
echo "==> mesh_smooth_curv → sphere-smoothed-vcg.vtk"
"$CMREP_BUILD/mesh_smooth_curv" -iter 50 -mu -0.51 -lambda 0.5 \
    "$TRUTH_DIR/sphere-mesh.vtk" \
    "$TRUTH_DIR/sphere-smoothed-vcg.vtk"

# Step 7: mesh_decimate_vcg → sphere-decimated-vcg.vtk
# Reduce to 50 % of the original face count.
echo "==> mesh_decimate_vcg → sphere-decimated-vcg.vtk"
"$CMREP_BUILD/mesh_decimate_vcg" \
    "$TRUTH_DIR/sphere-mesh.vtk" \
    "$TRUTH_DIR/sphere-decimated-vcg.vtk" \
    0.5

echo "==> Done. Fixtures written to: $TRUTH_DIR"
ls -lh "$TRUTH_DIR"
