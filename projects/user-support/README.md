# user-support — ITK-SNAP user Q&A

A standing log of questions from ITK-SNAP users, and a scratch pad for drafting replies. When a
question turns out to be a bug or a feature request, its thread holds everything a later session
needs to fix it without reading the conversation.

This is **not a sprint**. It has no `SPRINT_PLAN.md` / `NEXT_SESSION_PROMPT.md` and no end date.
[INDEX.md](INDEX.md) is the entry point.

## ⚠️ This repo is public

`itksnap-developer` is public on GitHub, so every committed file here is published. **Committed files
hold no user identity and no user data.**

| Never in a committed file | Instead |
|---|---|
| Names, emails, institutions, GitHub or forum handles | A user handle `U-NNN`. The mapping lives in `users.local.md`. |
| Email bodies pasted verbatim | Paraphrase. Quote only what must be exact, such as error text or steps. |
| Home paths (`/Users/jdoe/…`, `C:\Users\jdoe\…`), hostnames, IPs | `/Users/<user>/…`, `<host>` |
| Patient/subject IDs, DICOM tags, study dates, screenshots of scans | Describe it, e.g. "4D CTA, 20 phases, 512×512×320, NRRD". |
| Images, data files, crash dumps, logs the user sent | `attachments/Q-NNN/`, then refer to them by filename |

`users.local.md` and `attachments/` are gitignored (see the root `.gitignore`).

**A pre-commit hook enforces part of this.**
[`scripts/hooks/wrapper-pre-commit`](../../scripts/hooks/wrapper-pre-commit) blocks a commit that
stages any of the following under this directory:

- an email address (`git@host:` SSH remotes are allowed)
- `users.local.md` or `attachments/`, even when forced with `git add -f`
- any binary file

Install it once per clone. On the Linux box, run this again after pulling:

```bash
scripts/hooks/wrapper-pre-commit --install
```

The hook can't recognize names, institutions or home paths, so those still need a human read of
the diff. If the hook flags something by mistake, rephrase the line. Don't bypass it with
`--no-verify`.

## Layout

| Path | Committed | What it holds |
|---|---|---|
| [INDEX.md](INDEX.md) | yes | One row per thread with its status. **Start here.** |
| [TEMPLATE.md](TEMPLATE.md) | yes | Copy this to start a new thread. |
| `threads/Q-NNN-<slug>.md` | yes | One file per question: the conversation log, investigation notes, the draft reply, and a fix brief if one is needed. |
| [KNOWN_ANSWERS.md](KNOWN_ANSWERS.md) | yes | Reusable explanations taken from closed threads. Check it before drafting. |
| `users.local.md` | **no** | Maps each `U-NNN` handle to a real identity, plus notes on each user. |
| `attachments/Q-NNN/` | **no** | Files the user sent. |

IDs: threads are `Q-001, Q-002, …` and users are `U-001, U-002, …`. Both are assigned in order
and never reused. One user can open several threads.

## Workflows

**A new question arrives**
1. Look the sender up in `users.local.md`. If they aren't there, add them with the next `U-NNN`.
2. Copy `TEMPLATE.md` to `threads/Q-NNN-<slug>.md`, fill in the header, and paraphrase the question.
   Save any attachments to `attachments/Q-NNN/`.
3. Add a row to `INDEX.md` with status `new`.

**Drafting a reply**
1. Check `KNOWN_ANSWERS.md`, then earlier threads with the same tag in `INDEX.md`.
2. Investigate. Put code pointers (`file:line`, with the branch or commit) and repro attempts under
   **Investigation**.
3. Write the reply under **Draft reply**. Jilei sends it. Claude never sends user mail.
4. Once it's sent, move the text into the **Conversation log** as `us (sent)`, clear the draft, and
   update the status.

**It's a bug or a feature request**
1. Fill in **For a fix session** in the thread. It has to stand on its own: repro, expected vs.
   actual, versions, suspected code area, and the test that would fail on regression.
2. Record the work item where work is tracked. For 4.6.0 bugs that means a row in
   [../release-460/workstreams/bugfixes.md](../release-460/workstreams/bugfixes.md) citing `Q-NNN`.
   Features go to the workstream that owns them, or into a new project.
3. Set the status to `escalated` and fill **Escalated to** in both the thread and the index.
4. The fix follows the usual rule: one topic branch off `upstream/master`, never `staging/v460`.
   Mention `Q-NNN` in the commit body so the fix can be traced back to the user.
5. Once the fix ships, draft the "this is fixed in …" reply, then close the thread.

**A fix session picking this up**: read the thread's **For a fix session** section. The conversation
log is background and can be skipped.

**Closing**: set the status to `closed` and write a one-line resolution in the index. If the answer
will come up again, turn it into an entry in `KNOWN_ANSWERS.md`.
