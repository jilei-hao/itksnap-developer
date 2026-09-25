# Known answers

Explanations that come up more than once, taken from closed threads. Check here before drafting a
reply. Each entry cites the thread(s) it came from and the version it was last checked against,
because answers go stale as the code changes.

<!-- Entry format:

## <Question as a user would phrase it>

**Short answer:** one or two sentences, ready to paste.

**Detail:** the mechanism, the menu path, or the workaround.

**Source:** Q-NNN, Q-NNN · **Verified against:** 4.x.y (YYYY-MM-DD)
-->

## Which graphics card (GPU) do I need for the deep-learning server?

**Short answer:** For the current ITK-SNAP deep-learning server, which runs nnInteractive and SAM2
(will be released with itksnap 4.6), we recommend any recent NVIDIA GPU with at least 12 GB of
memory (VRAM).

**Detail:**
- **Memory matters more than speed.** nnInteractive is the more demanding model. Its developers
  recommend 10 GB of VRAM, and small structures work with less than 6 GB. SAM2 needs less.
  - 12 GB is the first common card size above 10 GB.
  - 16 GB or more gives headroom for very large images.
  - ITK-SNAP only ever has one model loaded on the server at a time.
- **Examples:** GeForce RTX 3060 (12 GB version), RTX 4070 (12 GB), RTX 4060 Ti (16 GB version),
  RTX A4000 (16 GB).
- **NVIDIA only (CUDA).** AMD cards and Apple Silicon aren't supported.
- **Shared server:** each ITK-SNAP connected at the same time loads its own copy of the model. Plan
  memory per simultaneous user.
- **No suitable GPU:** use remote mode instead, with a GPU machine on the network or Google Colab.
  The steps are at https://itksnap-dls.readthedocs.io.

**Goes stale when** `itksnap-dls` adds a model (check `get_model_listing()` in `segment.py`) or
changes the SAM2 variant or dtype.

**Source:** Q-001 · **Verified against:** itksnap-dls 0.1.3 and 0.1.4 (2026-09-24). This is based
on code reading and the nnInteractive README. VRAM was not measured.
