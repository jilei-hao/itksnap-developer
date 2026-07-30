# W2 — Developer docs & governance

**Status:** not started
**Branch:** none yet
**Depends on:** nothing

## Goal

A newcomer can find, in the repo, how the project is governed, how to behave in its spaces, and how
to build/test/contribute a change — without asking anyone.

## Current state

Verified against `upstream/master`, 2026-07-30.

**Does not exist:** `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, any governance document, `CODEOWNERS`,
or a root `LICENSE` file. `git ls-tree -r upstream/master` matches only `GUI/Qt/Resources/license.txt`
and `Utilities/licensetemplate.txt`. Root markdown is exactly `CLAUDE.md`, `README.md`,
`ReleaseNotes.md`.

**Does exist:**

| Path | Added | Content |
|---|---|---|
| `CLAUDE.md` | `9ad06754`, `63ae2293`, `ad5a3892` | Layout, build commands, architecture, header-registration convention, `--url` flag. Written for Claude, but it is the closest thing to a developer guide. |
| `Documentation/Developer/MemoryManagement.md` | `3360b9dd` | Owning vs non-owning pointer patterns |
| `Documentation/Developer/MemoryLeakTestingMacOS.md` | `3360b9dd` | `leaks --atExit` workflow, canary tests, baselines |
| `Documentation/Developer/RemoteURLs.md` | remote-IO series | URL schemes |
| `Documentation/Developer/Cardiac4DCTA_IO.md` | `dec2a2f2` (**unmerged**, W1) | 4D cardiac I/O |

So the three-layer architecture, the property/event system, the coupling pattern, and the build
matrix are documented **only** inside `CLAUDE.md` and this wrapper's `CLAUDE.md`.

## Plan

1. `CODE_OF_CONDUCT.md` — adopt Contributor Covenant 2.1 verbatim; the only real decision is the
   reporting contact.
2. `CONTRIBUTING.md` — build from source, run `ctest`, branch naming, commit style, PR expectations,
   the test-as-ratchet rule, where developer docs go.
3. `GOVERNANCE.md` — who decides, how a maintainer is added, how releases are cut. Needs Paul's input;
   this is the one item that cannot be drafted unilaterally.
4. `Documentation/Developer/Architecture.md` — promote the architecture section out of `CLAUDE.md`
   so it is addressed to humans, and have `CLAUDE.md` link to it rather than restate it.
5. `Documentation/Developer/README.md` — index of the above.
6. Root `LICENSE` mirroring `GUI/Qt/Resources/license.txt`, so GitHub detects it.
7. Optional: `.github/PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`.

## Open questions

1. **Who owns the CoC reporting contact?** A code of conduct with no reachable contact is worse than
   none.
2. **Is governance mine to write?** This is a Yushkevich-lab project with outside contributors
   (x1y9, zhiyong-wang, Matt McCormick this cycle). Draft and propose, don't declare.
3. **Does `CLAUDE.md` stay the source of truth for build instructions,** with `CONTRIBUTING.md`
   linking to it, or does it invert? Duplicating them guarantees drift.
4. **License text confirmation** — GPL vs the current bundled text; check before adding a root file.

## Done-criteria

- All files above exist on `staging/v460` and are linked from `README.md`.
- `CONTRIBUTING.md`'s build instructions have been followed verbatim on a clean checkout, on macOS
  **and** Linux, and both worked. Docs that were never executed are not done.
- No architecture or build content is stated in two places without one linking to the other.
