# RESUME — ITK-SNAP Agentic API · post-CAIMI-submission

## Current state (read this paragraph first)

**The CAIMI sprint is over and the submission is in.** SIIM-CAIMI26 AI Builder Showcase,
submission ID **`2480386`**, status **Complete**, preferred presentation **Oral**; notifications
**2026-08-26**; the conference is **Oct 26–27, 2026** at Penn. Authors: Jilei Hao · Alison M.
Pouch · Paul A. Yushkevich. What was built and submitted: ITK-SNAP made callable by an AI agent
over the Model Context Protocol, where every edit — by agent or person — returns a structured
record of what changed and who changed it. Three repos, all pushed and all clone-clean:
**`itksnap`** (C++ audit record + live socket channel, `sprint/caimi`, `daeeb99`),
**`itksnap-dls`** (FastAPI model server, `feature/agentic-api`, `bbaac51`), **`itksnap-mcp`**
(public, `main`, `12286185`). Wrapper `main` is at `9dc1e77` and in sync with origin. The
submitted text lives in `caimi-submission/caimi_submitted.md`, verified field-by-field against
the portal preview; treat it as a record, not a draft. **No deadline is now pending** — the next
session is free work, not a scramble.

## The single next goal

**Decide the post-submission track, then do exactly one of these — do not start all three.**
In rough priority order:

1. **Close the honesty gap the submission names.** Field 10 says the routing decision "is the
   point of the design" and is not implemented: the confidence gate in
   `itksnap-mcp/src/itksnap_mcp/confidence.py` (`agreement_gate`) is unit-tested but **called by
   nothing** — not by `server.py`, not by `demo/run_p2.py`. Wiring it into an MCP tool so a case
   is routed by measurement rather than by a person choosing it is the highest-value next
   increment, and it is what the Q&A will probe.
2. **Prepare the October demo.** The submitted demo description commits to a **live** run in six
   steps, applying into a **running** ITK-SNAP session over the socket — not the headless
   workspace path that `docs/demo_runbook.md` documents as the default. That path needs to be
   rehearsed end to end on the presentation machine, and there is no pinned inference seed.
3. **Explicit commit/discard of a correction** (field 10, item 2): after correcting a proposal
   the operator has no way to accept or reject — the outcome is implied by whether the file is
   saved. This is the most user-visible of the named limitations.

Everything else — OS4LS Goal 1, the pip-shippable Layer-1 binding, batch triage (P3) — is
planning work, not this file's business. See `docs/agentic-prototype-plan.md`.

## Files to read first (in order)

1. **`project_retrospective.md`** — limitations, next steps, and lessons. Start here; it is the
   condensed form of everything below.
2. **`caimi-submission/caimi_submitted.md`** — what was actually submitted, including the
   limitations we committed to in public. Its header lists the edits made in the portal.
3. **`PROGRESS_LOG.md`** — newest entry (2026-07-25) for this session; the two before it for how
   the prototype was built.
4. **`../../SUBMODULE_SYNC.md`** (wrapper root) — which branch each submodule must track, and the
   two checks to run before pushing anything that bumps a pointer.
5. `docs/demo_runbook.md` — the recording/demo runbook. Note §254: the default `apply` is
   headless, so nothing paints into a running window on that path.
6. `docs/agentic-prototype-plan.md` — the authoritative long-range plan (§8 models, §9 distribution).

## Setup (this machine — Linux, RTX 2080 8 GB; a 4090 box is used for full-res)

- **Base env** (DLS server): `source ~/tk/miniconda3/etc/profile.d/conda.sh && conda activate base`.
- **MCP server env** (isolated): `~/.venvs/itksnap-mcp`. Claude Code's registration points at
  `~/.venvs/itksnap-mcp/bin/python -m itksnap_mcp.server`.
- **Tests:** `cd itksnap-mcp && ~/.venvs/itksnap-mcp/bin/python -m pytest tests/ -q` → **12 passed**.
  `PYTHONPATH=src python3 -m pytest tests/ -q` also works. Plain `python3 -m pytest` from the base
  env **fails to collect** (`ModuleNotFoundError: itksnap_mcp` — `src` layout, not installed there).
- **Build FOREGROUND** if C++ changes: `cmake --build build-release --target ITK-SNAP -j`. Never
  `nohup &` — it reports success instantly while `ninja` is still linking. Confirm the binary mtime
  advanced before testing.
- **Live agent-directed run:**
  1. base env: `cd itksnap-dls && python -m itksnap_dls --port 8911 --device cuda` (poll `/status`).
  2. `ITK-SNAP -g /tmp/ct3d_bavcta028.nii.gz --agent-listen /tmp/snap-agent.sock` on a real display.
  3. Start a **fresh** `claude` session in this repo (MCP tools load at session start).
  4. GPU-free retake: `apply_file /tmp/p2_proposal_10.nii.gz` (label 1).
  5. Stop the server by port: `lsof -ti:8911 | xargs -r kill`.
- **Rebuild the submission docs** (only if the record must change — it should not):
  `python3 docs/build_caimi_submission.py caimi-submission/caimi_submitted.md caimi-submission/caimi_submitted.docx`

## Known traps

- **Never `pip install mcp` into the DLS base env.** It upgrades `starlette` past FastAPI's pin and
  breaks `itksnap_dls` (`on_startup` TypeError). The two cannot share one environment.
- **Never `pkill -f "<string>"` from your own shell** — the pattern matches the tool shell's own
  command line and kills it. Servers by port, GUIs by `setsid` + `kill -TERM -<pid>`, builds by
  `pgrep -x ninja`.
- **Push submodules BEFORE recording the pointer in the wrapper.** This was broken for five wrapper
  commits this sprint: `git clone --recursive` failed because two pointers referenced commits that
  existed only locally. It is invisible on the machine that made them. Run the reachability check in
  `SUBMODULE_SYNC.md` §3 before pushing a pointer bump.
- **Do not "simplify" that check to `git ls-remote | grep <sha>`** — `ls-remote` lists only ref
  **tips**, so it reports healthy ancestor pointers as missing. Use `git branch -r --contains` after
  a fetch.
- **`.docx` output is not byte-reproducible.** `zipfile` stamps entry mtimes, so a rebuild dirties
  git even when content is identical. Either don't rebuild before committing, or `git checkout --`
  the file after verifying content. A fixed `ZipInfo.date_time` would fix this properly.
- **Word comments do not survive regeneration.** The `.docx` is a build artifact of the `.md`. A
  review round is: comment → save in Word → extract → apply to the `.md` → rebuild → archive the
  commented copy. Note Word holds the file open; unsaved comments are not on disk.
- **`.gitmodules` drifts silently.** It declared `itksnap-dls` on `main` for most of the sprint while
  the work was on `feature/agentic-api`; a bare `git submodule update --remote` would have discarded
  it. Fixed at `9dc1e77`, but the failure mode recurs whenever a submodule is switched with
  `git switch` and `.gitmodules` is not updated.
- **Local body CTs are 4D cardiac CTA** — extract a 3D frame first (`/tmp/ct3d_bavcta028.nii.gz`).
- **DLS upload drops geometry** — `write_label_mask` restores it via `CopyInformation`. If the
  proposal and image do not share a grid, `apply` silently reports `changed_voxels: 0`.
- **The demo depends on one machine and one dataset.** Everything traces to `/tmp` paths and a
  hardcoded MCP config; nothing has run on a second dataset, scanner, modality, or machine.

## How to work

The deadline pressure is gone; the failure mode now is drift, not haste. Prefer one finished
increment over three started ones. The submitted text is a public commitment — when the code and
`caimi_submitted.md` disagree, that is a bug in the code or a note for the Q&A, never a silent edit
to the record. Commit and **push** inside a submodule first, then bump the wrapper pointer, then run
the `SUBMODULE_SYNC.md` §3 checks. Run `/handoff` at the end of the session rather than improvising it.
