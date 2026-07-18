# Spike: live command channel (Gate 2) — design verdict

**Question (sprint §3 Gate 2 / plan §6.2):** can an external process inject commands into the
**running** ITK-SNAP event loop — driving the same live GUI the human sees — without the `--test`
scaffold that runs canned JS *before* `app.exec()`?

**Verdict: DESIGN GREEN.** No architectural blocker found. Empirical prototype (below) is the next
concrete step; it needs an ITK-SNAP rebuild, so it's booked as a focused task, not done in this note.

## Evidence from the code (branch `sprint/caimi`)

- **"Create before `exec()`, operate during `exec()`" is already the pattern.** In
  `GUI/Qt/main.cxx`, `SNAPTestQt` is constructed and `LaunchTest()` called at **1445–1446**, then
  `app.exec()` runs at **1504**; command-line image loading is deferred *into* the loop via
  `QTimer::singleShot(0, …)` at **1452**. A `QLocalServer` created at the same point and serving
  during `exec()` fits this exactly.
- **The primitives already exist as `public slots` on a main-thread `QObject`** (`SNAPTestQt.h:73–117`):
  `findChild`, `findWidget`, `invoke`, `trigger`, `comboBoxSelect`, `tableItemText`, `postMouseEvent`,
  `postKeyEvent`, plus `Library.js` idioms (`setCursor(x,y,z)` drives the coupled `inCursorX/Y/Z`
  voxel spinboxes). Image-space cursor control (the demo's "focus the uncertain slice") is already
  there and is voxel-based, not pixel-based.
- **Threading is favourable.** Today the JS runs on a `TestWorker` QThread and calls these slots
  cross-thread (with `postKeyEventInternal` marshalling and `QApplication::postEvent` for safety). A
  live channel whose `QLocalServer::readyRead` fires on the **main thread** dispatches directly on the
  GUI thread — **strictly safer** than the current worker-thread model; no marshalling needed.

## Proposed design — `SNAPCommandChannel`

1. **Flag:** add `--agent-listen <socket-name>` in `main.cxx` (parse near the `--test` block at 732).
2. **Object:** before `app.exec()`, if the flag is set, construct `SNAPCommandChannel(mainwin, name)`
   (main-thread `QObject`) owning a `QLocalServer` listening on `name`.
3. **Protocol:** newline-delimited JSON, request/response with an `id`:
   ```
   -> {"id":1,"cmd":"set_cursor","args":{"x":128,"y":96,"z":40}}
   -> {"id":2,"cmd":"trigger","args":{"action":"actionLayerInspector"}}
   -> {"id":3,"cmd":"click","target":"grp4DProperties/btn4DReplay"}
   -> {"id":4,"cmd":"get_state","args":{"keys":["cursor","foreground_label","tool_mode"]}}
   -> {"id":5,"cmd":"screenshot","args":{"path":"/tmp/before.png"}}
   <- {"id":4,"ok":true,"result":{"cursor":[128,96,40],"foreground_label":3,...}}
   ```
4. **Stateless widget addressing** (avoids sending pointers over a socket): each command carries an
   objectName path (`"grp4DProperties/btn4DReplay"`) resolved via `findChild` per call — mirrors how
   JS does `findChild(...).click()`. No handle registry needed.
5. **Dispatch:** reuse the `SNAPTestQt` primitives. Cleanest refactor = extract the slot bodies into a
   shared `SNAPTestCommands` helper that both `SNAPTestQt` (JS) and `SNAPCommandChannel` (socket) call;
   the fast path for the prototype is to instantiate `SNAPTestQt` (without `LaunchTest`) and call its
   public slots directly.
6. **State read-back:** `get_state` via `GlobalUIModel` property models (cursor/label/tool — Qt-free,
   `PropertyModel.h`); `screenshot` via `SliceViewPanel::SaveScreenshot` (exists at `SliceViewPanel.h:58`,
   currently unbound — a ~1-line binding).

## What the empirical prototype must prove (minimal)

Add `--agent-listen`, a `QLocalServer`, and ONE command (`set_cursor`) that moves the crosshair on
receipt; launch ITK-SNAP under Xvfb; from a Python client send `set_cursor` and confirm the live slice
follows (the cursor set fires `CursorUpdateEvent` → the GUI re-renders for free, per plan §2.4).
Success = the running GUI reacts to an external socket command with no `--test` scaffold.

## Risks / open checks
- Confirm `QLocalServer` created pre-`exec()` serves normally once the loop runs (expected: yes).
- Confirm calling `SNAPTestQt` slots from the main-thread channel handler is safe (expected: yes —
  main-thread affine).
- `SaveScreenshot` binding + `get_state` surface are small adds, not blockers.

## Effort & build order
Effort **M**. Order: (1) `set_cursor`-only prototype to close Gate 2 empirically; (2) extract
`SNAPTestCommands`; (3) add `trigger`/`click`/`get_state`/`screenshot`; (4) wire the MCP `live.*` tools
(`itksnap-mcp/server.py`) to the socket. Gated behind Gate 2's empirical pass; P2 floor does not depend on it.
