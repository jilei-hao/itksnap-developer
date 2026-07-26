# SUBMODULE_SYNC.md

**Source of truth for which branch each submodule should track.** When this file and
`.gitmodules` disagree, **this file states the intent** and `.gitmodules` is the thing to fix —
see §6. `CLAUDE.md`'s repository-layout table is a summary and may lag; this file wins.

The contract is **per wrapper branch**. Everything below applies to wrapper branch **`main`**.
If you branch the wrapper for a sprint that needs different submodule branches, add a section
for it rather than editing the `main` table.

Wrapper remote: `https://github.com/jilei-hao/itksnap-developer.git`

---

## 1. Contract for wrapper branch `main`

| Path | Should track | Remote (all `github.com/jilei-hao/…`) | Purpose |
|---|---|---|---|
| `itksnap/` | `sprint/caimi` | `itksnap.git` | Main ITK-SNAP application. `sprint/caimi` = `feature/cardiac-io` + Linux/GCC build patches; the active sprint branch. |
| `itksnap-mcp/` | `main` | `itksnap-mcp.git` | Python agent glue: the Model Context Protocol server and demo driver. |
| `itksnap-dls/` | **`feature/agentic-api`** | `itksnap-dls.git` | Deep-learning segmentation server (TotalSegmentator, nnInteractive, SAM2). **`.gitmodules` wrongly says `main` — see §6.1.** |
| `segflow4d/` | `main` | `segflow4d.git` | 4D segmentation flow. |
| `greedy_python/` | `test/integration` | `greedy_python.git` | Python bindings for Greedy. |
| `convert-mesh/` | `main` | `convert-mesh.git` | ConvertMesh CLI/library. |
| `cmrep/` | `local` | `cmrep.git` | cm-rep; ground-truth parity reference for ConvertMesh. |
| `FireANTs/` | `main` | `FireANTs.git` | Registration project. |

Eight submodules. `itksnap-mcp` is missing from `CLAUDE.md`'s table; this list is complete.

### Nested submodules (inside `itksnap/`)

| Path | Tracking | Upstream |
|---|---|---|
| `itksnap/Submodules/c3d` | none — pinned by commit | `github.com/pyushkevich/c3d.git` |
| `itksnap/Submodules/greedy` | none — pinned by commit | `github.com/pyushkevich/greedy.git` |
| `itksnap/Submodules/digestible` | none — pinned by commit | `github.com/pyushkevich/digestible.git` |

These declare no `branch` in `itksnap/.gitmodules`, so they are pinned by SHA and are **not**
moved by `git submodule update --remote`. All three currently resolve on `origin/master`
upstream. They are upstream repositories, not forks — do not commit into them.

This is why clones must be recursive:

```bash
git clone --recursive git@github.com:jilei-hao/itksnap-developer.git
# after a plain clone, or to fill in newly added submodules:
git submodule update --init --recursive
```

---

## 2. Status as verified 2026-07-25, wrapper `d5c2dcc`

| Path | Declared | Checked out | Pointer reachable from its remote branch? |
|---|---|---|---|
| `itksnap/` | `sprint/caimi` | `sprint/caimi` | ❌ **no — 1 unpushed commit** |
| `itksnap-mcp/` | `main` | `main` | ❌ **no — 1 unpushed commit** |
| `itksnap-dls/` | `main` ⚠️ | `feature/agentic-api` | ✅ on `origin/feature/agentic-api` |
| `segflow4d/` | `main` | `main` (detached at pointer) | ✅ |
| `greedy_python/` | `test/integration` | `test/integration` | ✅ |
| `convert-mesh/` | `main` | `main` | ✅ |
| `cmrep/` | `local` | `local` (detached at pointer) | ✅ |
| `FireANTs/` | `main` | `main` | ✅ |

No submodule has uncommitted working-tree changes.

---

## 3. How to verify

Run from the wrapper root. Prints one line per submodule; anything not `ok` needs attention.

```bash
git config -f .gitmodules --get-regexp '\.path$' | awk '{print $2}' | while read -r p; do
  decl=$(git config -f .gitmodules --get "submodule.$p.branch")
  rec=$(git ls-tree HEAD "$p" | awk '{print $3}')
  cur=$(git -C "$p" rev-parse HEAD 2>/dev/null)
  br=$(git -C "$p" symbolic-ref --quiet --short HEAD 2>/dev/null || echo DETACHED)
  note=""
  [ "$rec" = "$cur" ] || note="$note POINTER!=HEAD"
  git -C "$p" merge-base --is-ancestor "$rec" "origin/$decl" 2>/dev/null || note="$note NOT-ON-origin/$decl"
  [ -z "$(git -C "$p" status --porcelain --ignore-submodules=all)" ] || note="$note DIRTY"
  printf '%-16s decl=%-18s at=%-22s %s\n' "$p" "$decl" "$br" "${note:-ok}"
done
```

The check that matters most, because it is the one that breaks other people's clones —
**is every recorded pointer actually on a remote branch?** This fetches, so it is the slower
of the two.

```bash
git config -f .gitmodules --get-regexp '\.path$' | awk '{print $2}' | while read -r p; do
  rec=$(git ls-tree HEAD "$p" | awk '{print $3}')
  git -C "$p" fetch -q origin 2>/dev/null
  on=$(git -C "$p" branch -r --contains "$rec" 2>/dev/null | sed 's/^[ *]*//' | grep -v '\->' | tr '\n' ' ')
  if [ -n "$on" ]; then printf 'ok      %-16s on: %s\n' "$p" "$on"
  else printf 'MISSING %-16s %s is on no remote branch — recursive clone will fail\n' "$p" "${rec:0:12}"; fi
done
```

Run this **before** pushing a wrapper commit that bumps any pointer.

> Do not substitute `git ls-remote <url> | grep <sha>` here. `ls-remote` lists only ref
> **tips**, so any pointer that is a legitimate ancestor of a branch tip — the normal case for
> a submodule pinned below the tip — is reported as missing. That check flags `segflow4d`,
> which is fine. `branch -r --contains` tests reachability, which is the actual question.

---

## 4. Procedures

### Record work you did inside a submodule

Commit **and push inside the submodule first**, then record the pointer in the wrapper.
Pushing first is not a style preference: the wrapper stores a bare SHA, so a pointer to an
unpushed commit is unresolvable for everyone else, and `git clone --recursive` fails outright.

```bash
cd <submodule>
git push                      # <- must come first
cd ..
git add <submodule>
git commit -m "Bump <submodule> to <sha> (<what changed>)"
```

### Bump a submodule to the latest of its tracked branch

```bash
git submodule update --remote <path>   # moves to the tip of the branch in .gitmodules
git add <path> && git commit -m "Bump <path> to <sha> (<why>)"
```

> ⚠️ **Do not run bare `git submodule update --remote`** (no path) while §6.1 is unfixed.
> It reads the branch from `.gitmodules`, so it would move `itksnap-dls` onto `main` and
> silently discard the agentic-API work, including the TotalSegmentator wrapper this
> project depends on.

### Change which branch a submodule tracks

Update **both** this file and `.gitmodules`, in the same commit:

```bash
git config -f .gitmodules submodule.<path>.branch <new-branch>
git -C <path> switch <new-branch>
git add .gitmodules <path> SUBMODULE_SYNC.md
git commit -m "Track <new-branch> for <path>"
```

### Restore everything to the recorded pointers

```bash
git submodule update --init --recursive     # note: no --remote
```

---

## 5. Why submodules show as "detached HEAD"

`git submodule update` checks out the recorded **commit**, not the branch, so a healthy
submodule often sits on a detached HEAD (`cmrep` and `segflow4d` do right now). That is normal
and is not drift. Before committing *into* a submodule, attach to its branch first:

```bash
git -C <path> switch <branch-from-the-table-in-§1>
```

Otherwise the commit lands on no branch and is easy to lose.

---

## 6. Known drift — open items

### 6.1 `itksnap-dls` tracks the wrong branch in `.gitmodules` (medium)

`.gitmodules` declares `branch = main`, but all the work — and the pointer recorded at
wrapper `3689ba8` — is on `feature/agentic-api`. `bbaac51` exists only on that branch.

Consequence: `git submodule update --remote` regresses the submodule to `main` and drops
the agentic API and the TotalSegmentator wrapper.

```bash
git config -f .gitmodules submodule.itksnap-dls.branch feature/agentic-api
git add .gitmodules && git commit -m "Track feature/agentic-api for itksnap-dls"
```

### 6.2 Two recorded pointers are not on their remotes (high — breaks fresh clones)

| Path | Pointer | Unpushed commit |
|---|---|---|
| `itksnap/` | `daeeb99` | `agentic-api: report the whole correction session, not just its last edit` |
| `itksnap-mcp/` | `12286185` | `Add read_audit_log + persist live audit records into the workspace` |

Both are one commit ahead of their upstream, and both SHAs were confirmed to be on no remote
branch after fetching. **`git clone --recursive` of this wrapper fails today**, and
`git submodule update --init` fails for these two on any machine but this one. This predates
the current wrapper commit — the pointers were first recorded at `acaaaa6`.

Fix — push each submodule; no wrapper commit is needed afterwards, because the SHAs the
wrapper already records become valid as soon as they exist on the remote:

```bash
git -C itksnap push origin sprint/caimi
git -C itksnap-mcp push origin main
```

Then re-run the reachability check in §3.

---

## 7. Maintaining this file

Update it in the same commit as any change to submodule branch tracking. Re-run §3 and
refresh §2 whenever pointers are bumped, and state the date and wrapper SHA the status was
verified at, so a stale table is visibly stale rather than quietly wrong.
