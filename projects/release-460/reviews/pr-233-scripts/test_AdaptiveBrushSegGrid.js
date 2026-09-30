// Repro for #233 / #222 on current master (seg_anchor): an adaptive-brush click
// when the segmentation has its own grid. The 0.4 mm segmentation (82x135x92)
// is larger than the 1 mm MRIcrop image (78x110x64) in voxel count, so a click
// on axial slice 85 asks the watershed for image voxels that do not exist.
//   master 52ee94fa:      ITK-SNAP aborts (uncaught itk::InvalidRequestedRegionError)
//   master + #233:        no crash; the click is refused
// Register in TestingScripts.qrc and GUI_TESTS to run it (see README.md).
include("Library");

openMainImage("MRIcrop-orig.gipl.gz");
openSegmentation("MRIcrop-seg-hippoL-04mm.nii.gz");

engine.clickChild(mainwin, "btnAxial");
var panel0 = engine.findChild(mainwin, "panel0");
var canvas = engine.findChild(panel0, "sliceViewCanvas");
if (!canvas)
    engine.testFailed("The axial slice view canvas was not found");

//=== Adaptive paintbrush. A mouse press is needed: the Space key paints with
//=== dragging = true, which never runs the adaptive (watershed) code.
engine.trigger("actionPaintbrush");
engine.sleep(500);
var btnW = engine.findChild(mainwin, "btnWatershed");
if (!btnW)
    engine.testFailed("The adaptive brush button was not found");
engine.click(btnW);
engine.sleep(300);
engine.validateValue(engine.getProperty(btnW, "checked"), true);
setForegroundLabel("Label 1");

//=== Click on a slice inside both grids
setCursor(49, 67, 30);
engine.postMouseEvent(canvas, 0.5, 0.5, "click", "left");
engine.sleep(1500);

//=== Click on a slice the main image does not cover in voxel terms
setCursor(40, 125, 85);
engine.postMouseEvent(canvas, 0.5, 0.5, "click", "left");
engine.sleep(1500);
engine.print("Still running after the adaptive-brush clicks");
