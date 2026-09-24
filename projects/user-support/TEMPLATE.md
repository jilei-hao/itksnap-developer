# Q-NNN — <one-line topic>

<!-- Public repo: no names, emails, institutions, home paths, patient IDs, or pasted data.
     Identity → users.local.md. Files → attachments/Q-NNN/. See README.md. -->

| | |
|---|---|
| Opened | YYYY-MM-DD |
| User | U-NNN |
| Channel | email · GitHub issue #N · forum · in person |
| ITK-SNAP version | e.g. 4.4.0, 4.6.0-alpha.3, a nightly build, or unknown |
| Platform | e.g. macOS 15 arm64, Windows 11, Ubuntu 24.04 |
| Type | question · how-to · bug · feature · build · data |
| Status | new |
| Escalated to | — |
| Attachments | — (or the filenames in `attachments/Q-NNN/`) |

## The question

What the user is asking, paraphrased. Quote only what has to be exact: error text, menu paths,
or the steps they took.

## Conversation log

Append-only, oldest first. Add one entry for each message, in either direction.

### YYYY-MM-DD — user

### YYYY-MM-DD — us (sent)

## Investigation

Scratch notes: what was checked and what was found. Give code pointers as `path/file.cxx:line`
with the branch or commit, since line numbers drift. For each repro attempt, record the version,
the data used, and the outcome.

## Draft reply

The working draft. Once it's sent, move it into the conversation log and clear this section.

## For a fix session

<!-- Fill in only when Type is bug or feature and we'll act on it. Assume the reader has not read
     anything above. -->

- **Symptom:**
- **Repro:** numbered steps, plus the data. Prefer a file in `itksnap/Testing/TestData/`, or say which attachment reproduces it.
- **Expected vs. actual:**
- **Affects:** version(s) and platform(s). Is it confirmed on our build?
- **Suspected area:** `file:line` @ commit
- **Done when:** the test that fails today and passes after the fix
- **Tracked at:** the workstream row or branch
