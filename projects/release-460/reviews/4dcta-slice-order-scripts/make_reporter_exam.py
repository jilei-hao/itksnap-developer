"""
The reporter's version of the synthetic CT exam (#128 comment, 2026-11-03).

This is Testing/TestData/make_dicom_ct_exam.py from upstream/master (a16d5c3e)
with the four lines from the report: slices written in reverse order, and the
first file of the 4D series ("Dynamic CTA") writing SliceThickness "2.000000"
and GantryDetectorTilt "0.000000" while every other file writes "2.0" and "0.0".

  python make_reporter_exam.py <out_dir>               the reporter's exam
  python make_reporter_exam.py <out_dir> --same-tilt   control: every file "0.0"

The 4D series has 5 slices at Z = 10, 8, 6, 4, 2 mm and 3 time points. Voxel
intensity is 100 * (time point - 1) + n, where n is 0 at Z = 10 mm and 4 at
Z = 2 mm. So in a correct load, the intensity of a voxel goes up by exactly
100 from one time point to the next.
"""
import os, sys, numpy as np
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid, CTImageStorage

out = sys.argv[1]
same_tilt = "--same-tilt" in sys.argv[2:]
os.makedirs(out, exist_ok=True)

# Fixed UIDs, so that the files only change when this script does
def uid(*key):
    return generate_uid(entropy_srcs=["itksnap-dicom-ct-exam"] + [str(k) for k in key])

study = uid("study")

def write_series(number, desc, n_pos, n_frames, base, size=16):
    inst = 0
    for f in range(n_frames):
        for z in range(n_pos):
            inst += 1
            meta = FileMetaDataset()
            meta.MediaStorageSOPClassUID = CTImageStorage
            meta.MediaStorageSOPInstanceUID = uid(number, inst)
            meta.TransferSyntaxUID = ExplicitVRLittleEndian
            ds = Dataset(); ds.file_meta = meta
            ds.SOPClassUID = CTImageStorage
            ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
            ds.Modality = "CT"; ds.Manufacturer = "GE MEDICAL SYSTEMS"
            ds.PatientName = "Synthetic^Test"; ds.PatientID = "0"
            ds.StudyInstanceUID = study; ds.SeriesInstanceUID = uid(number)
            ds.SeriesNumber = number; ds.SeriesDescription = desc
            ds.InstanceNumber = inst
            # --- the reporter's four lines ---
            ds.ImagePositionPatient = [0.0, 0.0, float(n_pos-z) * 2.0]
            ds.SliceLocation = float(n_pos-z) * 2.0
            ds.SliceThickness = "2.000000" if (number == 4 and inst == 1) else "2.0"
            ds.GantryDetectorTilt = "0.000000" if (number == 4 and inst == 1 and not same_tilt) else "0.0"
            # ---------------------------------
            ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
            ds.PixelSpacing = [1.0, 1.0]
            ds.Rows = size; ds.Columns = size
            ds.SamplesPerPixel = 1; ds.PhotometricInterpretation = "MONOCHROME2"
            ds.BitsAllocated = 16; ds.BitsStored = 16; ds.HighBit = 15
            ds.PixelRepresentation = 1
            ds.RescaleIntercept = 0; ds.RescaleSlope = 1
            ds.PixelData = np.full((size, size), base + 100 * f + z, dtype=np.int16).tobytes()
            ds.save_as(os.path.join(out, f"s{number}_{inst:04d}.dcm"), enforce_file_format=True)

write_series(2, "Axial 3D A", 8, 1, 1000)
write_series(3, "Axial 3D B", 6, 1, 2000)
write_series(4, "Dynamic CTA", 5, 3, 0)
