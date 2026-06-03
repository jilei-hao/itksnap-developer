# Demo cohort (10 studies)

Synthetic cohort for the manual-vs-agent comparison. Images are copies of
`itksnap/Testing/TestData/*` (anatomy is irrelevant — this exercises the
*workflow*, not segmentation accuracy). One subject per folder; a shared
label-description file at `data/labels.label`.

## Contents

| Subject  | T1 (main) | FLAIR (overlay) | seg | labels |
|----------|:---------:|:---------------:|:---:|:------:|
| subj001  | ✓ | – | – | ✓ |
| subj002  | ✓ | ✓ | – | ✓ |
| subj003  | ✓ | – | ✓ | ✓ |
| subj004  | ✓ | – | – | ✓ |
| subj005  | ✓ | ✓ | – | ✓ |
| subj006  | ✓ | – | – | ✓ |
| subj007  | ✓ | ✓ | ✓ | ✓ |
| subj008  | ✓ | – | – | ✓ |
| subj009  | ✓ | ✓ | – | ✓ |
| subj010  | ✓ | – | – | ✓ |

(4 have a FLAIR overlay; 2 have a segmentation; all share `labels.label`.)

## Target workspace spec (same for both methods)

For each subject, produce `<subject>.itksnap` containing:

- **main** = `T1.nii.gz`, nickname **`T1`**
- **overlay** = `FLAIR.nii.gz` (if present), nickname **`FLAIR`**
- **segmentation** = `seg.nii.gz` (if present)
- **labels** loaded from `data/labels.label`
- **tags** on the main image: `cohort:demo`, `status:needs-review`

## The experiment

- **`output/no-mcp/`** — build the 10 workspaces by hand (raw `itksnap-wt`
  invocations, one per subject, reasoning about which optional layers each has).
- **`output/with-mcp/`** — point an agent at this folder with the
  `itksnap-workspace-builder` skill + the `itksnap-wt` MCP server, and ask it to
  build review-ready workspaces for the whole cohort.

Compare effort, error rate, and consistency between the two.

> Generated `.itksnap` files in `output/` are git-ignored.
