# User-support thread index

Newest at the top. Keep each row short: the details belong in the thread file. Before committing,
read the privacy rules in [README.md](README.md).

## Status legend

| Status | Meaning | Whose move |
|---|---|---|
| `new` | Logged, nobody has looked yet | us |
| `drafting` | We're investigating or writing a reply | us |
| `waiting-user` | Reply sent, waiting on the user for data, a repro, or confirmation | user |
| `escalated` | Became a bug or feature item. See **Escalated to**. | fix session |
| `closed` | Resolved. The resolution is in the last column. | — |

**Type**: `question` · `how-to` · `bug` · `feature` · `build` (compiling ITK-SNAP or its deps) · `data` (a file won't load or loads wrong)

## Open

| ID | Opened | User | Type | Topic | Status | Escalated to |
|---|---|---|---|---|---|---|
| [Q-003](threads/Q-003-stitched-dicom-precision-warning.md) | 2026-09-25 | U-002 | data | Combined DICOM looks bad and shows a precision warning; can ITK-SNAP stitch NIfTI? (No, but the bundled c3d can; recipe tested.) | drafting | [ISS-001](confirmed_issues.md) |
| [Q-002](threads/Q-002-double-precision-images.md) | 2026-09-25 | — | question | Double-precision image support (yes, since 4.2.0). Candidate bugs: reload fails, false precision warning (Q-003). | drafting | [ISS-001](confirmed_issues.md) (warning); reload bug is still a candidate |

## Closed

| ID | Opened | Closed | User | Type | Topic | Resolution |
|---|---|---|---|---|---|---|
| [Q-001](threads/Q-001-gpu-recommendation.md) | 2026-09-24 | 2026-09-24 | U-001 | question | Recommended GPU for itksnap-dls (nnInteractive + SAM2) | Answered: any recent NVIDIA GPU, ≥ 12 GB VRAM. Now in KNOWN_ANSWERS. |

Next IDs: **Q-004**, **U-003**
