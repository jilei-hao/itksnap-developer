# Demo cohort (10 studies)

Synthetic cohort for the manual-vs-agent comparison. Images are copies of
`itksnap/Testing/TestData/*` (anatomy is irrelevant — this exercises the
*workflow*, not segmentation accuracy). One subject per folder; a shared
label-description file at `data/labels.label`.

## Contents

| Subject  | images present | notes |
|----------|----------------|-------|
| subj001  | T1 | T1-only |
| subj002  | T1, FLAIR | overlay |
| subj003  | T1, seg | segmentation |
| subj004  | T1 | T1-only |
| subj005  | T1, FLAIR | overlay |
| subj006  | T1 | T1-only |
| subj007  | T1, FLAIR, seg | overlay + seg |
| subj008  | T1 | T1-only |
| subj009  | T1, FLAIR | overlay |
| subj010  | T1 | T1-only |
| subj011  | T1, FLAIR, **PET** | **two overlays** (picked-layer ordering footgun) |
| subj012  | T1, **T2** | **main-selection footgun** (T2 sorts first; must NOT become main) |
| subj013  | T1, **CT**, seg | overlay + seg, non-T1 modality |

subj011–013 are *footgun* cases that punish a cold agent: multiple overlays
needing per-layer nicknames, and a subject where the alphabetically-first image
(`T2`) must not be chosen as the main.

## Target workspace spec (same for both methods)

For each subject, produce `<subject>.itksnap` following this **convention**:

- **main** = `T1.nii.gz` (always), nickname **`T1`**
- **overlays** = every *other* anatomical image (`FLAIR`/`T2`/`PET`/`CT`),
  nickname = its modality (filename stem)
- **segmentation** = `seg.nii.gz` (if present)
- **labels** loaded from `data/labels.label`
- **tags** on the main image: `cohort:demo`, `status:needs-review`

(This same convention is encoded in the `itksnap-workspace-builder` skill, and
checked by `experiment/verify.py`.)

## The experiment

See `../experiment/EXPERIMENT.md`. Two arms of the **same agent**: one with no
itksnap-wt context (`output/no-mcp/`), one with the MCP server + skill
(`output/with-mcp/`). Score each with `experiment/verify.py`.

> Generated `.itksnap` files in `output/` are git-ignored. **Note:** this
> `data/README.md` *is* the spec — for the "no-spec / vague-prompt" protocol
> (Protocol B) keep it out of both scratch dirs so neither agent can read it.
