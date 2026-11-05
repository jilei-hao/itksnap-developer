# Scripts for reviews/4dcta-slice-order-test-plan.md

macOS, run from the `itksnap-developer` root. Needs a Python with pydicom and numpy (default: the
`instant3d` miniconda env; set `PYTHON=` otherwise).

| File | Use |
|---|---|
| `compare.sh` | Step 1: runs `TestDicomSeriesDetection` from the before and after builds, writes the reporter's exam (and a control) to `build-4dcta-slice-order/repro/`, and prints the two `ITK-SNAP -g` commands. Override `BEFORE`, `AFTER`, `PYTHON`, `OUT` from the environment. |
| `make_reporter_exam.py` | `upstream/master`'s `make_dicom_ct_exam.py` with the reporter's four lines. `--same-tilt` writes the control. |
