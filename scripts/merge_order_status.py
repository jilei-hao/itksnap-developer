#!/usr/bin/env python3
"""Regenerate the Status section of the release merge-order doc from live git state.

The doc (projects/release-460/MERGE_ORDER.md) has two curated, machine-read parts:

  * the QUEUE block  -- one topic branch per line, in merge order:
        <branch>  <verified-at sha | ->  <why this position ...>
  * the ordering-constraints table -- rows whose first two cells are `before` and
    `after` branch names in backticks.

This script reads both, inspects the itksnap repo, and rewrites only the text between
<!-- AUTO:BEGIN --> and <!-- AUTO:END -->. It never touches refs, so it is safe to run
from the itksnap reference-transaction hook (see --install-hook).

Usage:
  scripts/merge_order_status.py                 # refresh the doc
  scripts/merge_order_status.py --check         # refresh, exit 1 if anything needs attention
  scripts/merge_order_status.py --install-hook  # symlink the itksnap reference-transaction hook
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

WRAPPER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REPO = os.path.join(WRAPPER, "itksnap")
DOC = os.path.join(WRAPPER, "projects", "release-460", "MERGE_ORDER.md")
HOOK_SRC = os.path.join(WRAPPER, "scripts", "hooks", "itksnap-reference-transaction")
BASE = "upstream/master"
STAGING = "staging/v460"

# Hooks run with GIT_DIR, GIT_INDEX_FILE, ... pointing at the invoking operation.
# Strip them so every call below sees the itksnap repo exactly as a shell would.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, env=ENV)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def rev(ref):
    r = git("rev-parse", "--verify", "-q", ref + "^{commit}", check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def short(sha):
    return sha[:8] if sha else "—"


def is_ancestor(a, b):
    return git("merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def merges_clean(a, b):
    """(clean?, conflicted paths) for merging a and b, without touching any ref."""
    r = git("merge-tree", "--write-tree", "--name-only", a, b, check=False)
    if r.returncode == 0:
        return True, []
    lines = r.stdout.splitlines()
    # Output: <tree oid>, then conflicted paths, then a blank line and informational messages.
    paths = []
    for line in lines[1:]:
        if not line.strip():
            break
        paths.append(line.strip())
    return False, paths


def between(text, begin, end):
    i, j = text.find(begin), text.find(end)
    if i < 0 or j < 0 or j < i:
        raise SystemExit(f"{DOC}: missing or misordered markers {begin} / {end}")
    return i + len(begin), j


def read_queue(text):
    i, j = between(text, "<!-- QUEUE:BEGIN -->", "<!-- QUEUE:END -->")
    queue = []
    for line in text[i:j].splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("```"):
            continue
        parts = s.split(None, 2)
        branch = parts[0]
        verified = parts[1] if len(parts) > 1 else "-"
        why = parts[2] if len(parts) > 2 else ""
        queue.append((branch, verified, why))
    return queue


def read_constraints(text):
    """Ordering edges from table rows of the form | `before` | `after` | ... |."""
    edges = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            edges.append((m.group(1), m.group(2)))
    return edges


def build_status(queue, edges):
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    base = rev(BASE)
    if not base:
        return [f"_Generated {now}: `{BASE}` not found — fetch upstream first._"], True
    base_date = git("log", "-1", "--format=%cs", base).stdout.strip()
    attention = []
    out = [
        f"_Generated {now} by `scripts/merge_order_status.py` — do not edit by hand._",
        "",
        f"`{BASE}` = `{short(base)}` ({base_date}).",
        "",
        "| # | Branch | Tip | Ahead | Base | On `origin` | Verified | Why this position |",
        "|---:|---|---|---:|---|---|---|---|",
    ]
    tips = {}
    for n, (branch, verified, why) in enumerate(queue, 1):
        tip = rev(branch)
        if not tip:
            out.append(f"| {n} | `{branch}` | **missing** | | | | | {why} |")
            attention.append(f"`{branch}` is in the queue but has no local branch")
            continue
        tips[branch] = tip
        ahead = git("rev-list", "--count", f"{BASE}..{branch}").stdout.strip()

        if is_ancestor(base, tip):
            base_cell = "current"
        else:
            clean, paths = merges_clean(base, tip)
            mb = git("merge-base", base, tip).stdout.strip()
            base_cell = f"⚠️ old (`{short(mb)}`) — rebase" + ("" if clean else ", **conflicts**")
            attention.append(f"`{branch}` is not on the current `{BASE}`")

        remote = rev(f"origin/{branch}")
        if remote is None:
            pushed = "not pushed"
        elif remote == tip:
            pushed = "✅ in sync"
        elif is_ancestor(remote, tip):
            pushed = "⚠️ local ahead"
        elif is_ancestor(tip, remote):
            pushed = "⚠️ local behind"
        else:
            pushed = "⚠️ diverged"
        if remote != tip:
            attention.append(f"`{branch}` differs from `origin/{branch}`")

        if verified in ("-", ""):
            ver = "⚠️ never"
            attention.append(f"`{branch}` has never been verified")
        elif tip.startswith(verified):
            ver = f"✅ `{verified[:8]}`"
        else:
            ver = f"⚠️ moved since `{verified[:8]}` — re-verify"
            attention.append(f"`{branch}` moved since it was last verified")

        out.append(f"| {n} | `{branch}` | `{short(tip)}` | {ahead} | {base_cell} | {pushed} | {ver} | {why} |")

    # Pairwise mergeability: every subset must merge in any order.
    names = list(tips)
    conflicts = []
    for a_i, a in enumerate(names):
        for b in names[a_i + 1:]:
            clean, paths = merges_clean(tips[a], tips[b])
            if not clean:
                conflicts.append((a, b, paths))
    npairs = len(names) * (len(names) - 1) // 2
    out.append("")
    if conflicts:
        out.append(f"**Pairwise merges: {len(conflicts)} of {npairs} pairs conflict.**")
        for a, b, paths in conflicts:
            out.append(f"- `{a}` + `{b}`: {', '.join(f'`{p}`' for p in paths) or 'conflict'}")
            attention.append(f"`{a}` and `{b}` conflict")
    else:
        out.append(f"**Pairwise merges:** all {npairs} pairs merge cleanly.")

    # Ordering constraints must be respected by the queue order.
    pos = {b: i for i, (b, _, _) in enumerate(queue)}
    bad = [(a, b) for a, b in edges if a in pos and b in pos and pos[a] > pos[b]]
    live = [(a, b) for a, b in edges if a in pos and b in pos]
    if bad:
        out.append(f"**Ordering constraints: {len(bad)} violated by the queue order.**")
        for a, b in bad:
            out.append(f"- `{a}` must come before `{b}`")
            attention.append(f"queue puts `{b}` before `{a}`")
    else:
        out.append(f"**Ordering constraints:** queue order satisfies {len(live)} of {len(live)}.")

    # Staging must contain the base and every queue tip.
    st = rev(STAGING)
    if st is None:
        out.append(f"**`{STAGING}`:** missing.")
    else:
        missing = [b for b, t in tips.items() if not is_ancestor(t, st)]
        stale_base = not is_ancestor(base, st)
        extra = git("rev-list", "--count", "--no-merges", f"{BASE}..{STAGING}", *[f"^{t}" for t in tips.values()]).stdout.strip()
        ok = not missing and not stale_base and extra == "0"
        if ok:
            out.append(f"**`{STAGING}`** (`{short(st)}`): contains `{BASE}` and every queue tip, and nothing else. ✅")
        else:
            why = []
            if stale_base:
                why.append(f"not on the current `{BASE}`")
            if missing:
                why.append("missing " + ", ".join(f"`{b}`" for b in missing))
            if extra != "0":
                why.append(f"{extra} commit(s) not on any queue branch")
            out.append(f"**`{STAGING}`** (`{short(st)}`): ⚠️ rebuild — {'; '.join(why)} (SPRINT_PLAN §7).")
            attention.append(f"`{STAGING}` needs a rebuild")

    out.append("")
    if attention:
        out.append("**Needs attention:** " + "; ".join(dict.fromkeys(attention)) + ".")
    else:
        out.append("**Needs attention:** nothing.")
    return out, bool(attention)


def install_hook():
    hooks = git("rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout.strip()
    dst = os.path.join(hooks, "reference-transaction")
    if os.path.lexists(dst):
        if os.path.islink(dst) and os.path.realpath(dst) == os.path.realpath(HOOK_SRC):
            print(f"already installed: {dst}")
            return
        raise SystemExit(f"{dst} exists and is not our hook; not overwriting")
    os.makedirs(hooks, exist_ok=True)
    os.symlink(HOOK_SRC, dst)
    print(f"installed: {dst} -> {HOOK_SRC}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if anything needs attention")
    ap.add_argument("--install-hook", action="store_true", help="install the itksnap reference-transaction hook")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--doc", default=None, help="operate on another copy of the doc (for testing)")
    args = ap.parse_args()
    global DOC
    if args.doc:
        DOC = os.path.abspath(args.doc)
    if args.install_hook:
        install_hook()
        return 0

    text = open(DOC, encoding="utf-8").read()
    status, attention = build_status(read_queue(text), read_constraints(text))
    i, j = between(text, "<!-- AUTO:BEGIN -->", "<!-- AUTO:END -->")
    # The first line is the timestamp. Rewrite only when something else changed, so a ref
    # update that changes nothing (a fetch, a no-op rebase) leaves the wrapper clean.
    old = text[i:j].strip("\n").splitlines()
    if old[1:] == status[1:]:
        status[0] = old[0] if old else status[0]
    new = text[:i] + "\n" + "\n".join(status) + "\n" + text[j:]
    if new != text:
        tmp = DOC + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, DOC)
    if not args.quiet:
        print("\n".join(status))
    return 1 if (args.check and attention) else 0


if __name__ == "__main__":
    sys.exit(main())
