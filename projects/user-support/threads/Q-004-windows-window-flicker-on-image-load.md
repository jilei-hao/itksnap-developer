# Q-004 — Window flickers between normal and garbled once an image is opened (Windows 11)

<!-- Public repo: no names, emails, institutions, home paths, patient IDs, or pasted data.
     Identity → users.local.md. Files → attachments/Q-004/. See README.md. -->

| | |
|---|---|
| Opened | 2026-09-29 |
| User | U-003 |
| Channel | not recorded. The first message reads like a post to a mailing list or forum ("has anybody else experienced…"). |
| ITK-SNAP version | 4.4.0 |
| Platform | Windows 11 Enterprise 24H2, x64. Dell Pro Max Slim FCS1250, Intel Core Ultra 7 265, 64 GB RAM. **Graphics card not stated** (see Investigation 3). |
| Type | bug (display). Most likely a graphics-driver problem on the user's machine, not an ITK-SNAP defect. |
| Status | drafting |
| Escalated to | — |
| Attachments | `screenshot-glitched-window.png`, `screenshot-normal-window.png` |

## The question

- **Symptom:** as soon as any image is opened, the ITK-SNAP window keeps switching back and forth
  between the normal view and a garbled one. The user says it didn't use to happen.
- **Already tried:** uninstalling and reinstalling the newest version. That didn't help.
- **Data:** it happens with every file. They first saw it with their own compressed NIfTI brain
  MRIs, then reproduced it with our sample data: "Multi-modal brain tumor MRI" from the Downloads →
  Data page, file `BRATS_HG0015_FLAIR.mha`. So the data is ruled out.
- **Asked:** does anyone else see this, and how do they fix it? They also couldn't find a support
  phone number.

**Screenshots** (`attachments/Q-004/`):
- `screenshot-normal-window.png` — the normal layout. Three slice views of the BRATS FLAIR image,
  an empty 3D view, the toolbox, and the menu bar all look correct.
- `screenshot-glitched-window.png` — the same window a moment later.
  - The Windows title bar is intact.
  - **Everything below the title bar is garbled:**
    - The menu bar is gone.
    - Large light-grey triangles cross the window. That grey is the Qt window background colour.
    - The toolbox panel is drawn as a thin, sheared sliver.
    - The three slice views are drawn small, skewed, and in the wrong places.

## Conversation log

### 2026-09-29 — user

First message: describes the glitch and attaches photos of it. Says it started recently and that
reinstalling the newest version didn't help. Asks for tips.

### 2026-09-29 — user

Follow-up with the details (version, hardware, OS, sample file, as in the header) and the two
screenshots above.

## Investigation

**1. What the garbled screenshot shows: a failure in the final step, where the graphics card
assembles the window.** This is inferred from the screenshot plus the code; it hasn't been
reproduced.

- **In 4.4.0 every image view is an OpenGL widget.** The 2D and 3D views are
  `QVTKOpenGLNativeWidget`, a `QOpenGLWidget` subclass (`GUI/Qt/View/QtVTKRenderWindowBox.cxx` @
  `20f63186`, the 4.4.0 release commit). The Windows build uses Qt 6.8.1
  (`.github/workflows/build.yml` @ `20f63186`).
- **How Qt 6 draws such a window.** Once a top-level window contains a `QOpenGLWidget`, Qt 6
  composites the whole window through OpenGL.
  - The ordinary widgets (menus, toolbox, grey background) are painted into one image.
  - Each OpenGL view renders into its own offscreen texture.
  - Qt then draws all of these onto the window with the graphics card: one textured rectangle per
    piece.
- **The screenshot matches that step going wrong.**
  - Every piece Qt composites is distorted: the background, the toolbox, and each view texture.
    The pieces' *content* is intact (the slices are recognisable), but the geometry they're drawn
    with is wrong.
  - The title bar is fine. Windows draws it, not the app.
  - The display flips between good frames and bad ones. That fits an intermittent failure in
    compositing, not a stable bug in ITK-SNAP's own drawing.
- **Why it starts only when an image opens.** Before that, the welcome page is showing and the
  OpenGL views aren't in use.

**2. Why the driver is the prime suspect, not ITK-SNAP or the data.**
- It happens with any file, including our sample data.
- A clean reinstall of the same 4.4.0 didn't change it.
- The user says it used to work. ITK-SNAP didn't change, so something on the machine did. A driver
  update pushed by Windows Update or the IT department is the usual trigger.
- Intel driver updates breaking Qt OpenGL apps is a known, recurring pattern. VTK has also tracked
  Intel-driver breakage of its Qt widget before. Neither is evidence about this exact driver.
- Not ruled out: an ITK-SNAP, VTK or Qt OpenGL state bug that only this driver exposes. The user
  can't tell those apart, and the advice to them would be the same.

**3. The graphics card is unknown, and the advice depends on it.**
- Dell configures the FCS1250 with either Intel integrated graphics only, or a separate card:
  NVIDIA A400, A1000, RTX 2000 Ada, RTX 4000 SFF Ada, or RTX PRO 2000/4000 Blackwell; or AMD Radeon
  Pro W7400. (Source: Dell's and resellers' spec pages, 2026-09-29.)
- The Core Ultra 7 265 (Arrow Lake-S) always has Intel graphics built in. So a machine with a
  separate card has two GPUs, and cross-GPU display is another known source of OpenGL glitches.
- If it's a Blackwell card, this may be related to upstream
  [pyushkevich/itksnap#240](https://github.com/pyushkevich/itksnap/issues/240). There, 4.4.0
  crashes on image load with an RTX 5090 on Windows 11. That's a different symptom, and it's
  still open.

**4. Related upstream reports.** Neither is the same bug.
- [pyushkevich/itksnap#165](https://github.com/pyushkevich/itksnap/issues/165) — window flickering
  on Ubuntu 24.04 with an NVIDIA RTX 4090. It started after XRDP (remote desktop) was set up. Open,
  no replies from us.
- [pyushkevich/itksnap#240](https://github.com/pyushkevich/itksnap/issues/240) — see item 3.

**5. No workaround inside ITK-SNAP.**
- 4.4.0 has no preference for switching rendering mode or turning off multisampling. The 4×
  multisampling is hard-coded (`GUI/Qt/main.cxx:799` @ `20f63186`).
- The `--testgl` command-line option only opens a test dialog; it doesn't change how the main
  window draws. It could still serve as a diagnostic later.
- `QT_OPENGL=software` is not recommended to the user.
  - The #240 reporter tried it and it didn't help.
  - Untested, but likely: VTK loads its OpenGL functions from the system `opengl32.dll`. That
    would clash with Qt's software renderer `opengl32sw.dll`.
- So the fixes all sit at the driver or Windows level.

**6. Default install path** (for the Windows graphics-settings step). The installer defaults to
`C:\Program Files\ITK-SNAP 4.4\bin\ITK-SNAP.exe` (`CPACK_PACKAGE_INSTALL_DIRECTORY` and
`CPACK_NSIS_INSTALL_ROOT` in `CMakeLists.txt` @ `20f63186`).

**Not done:** no reproduction. We have no Arrow Lake or FCS1250 machine. The Penn Windows build
box's GPU hasn't been recorded; if it's Intel Arc-class, a 4.4.0 run there would be worth trying.

## Draft reply

> Thanks for the detailed report and the screenshots. They make the problem clear.
>
> **The short answer:** this looks like a problem with your computer's graphics driver, not with
> your images or your ITK-SNAP installation.
>
> **Why we think so:** in the garbled screenshot, the window's title bar is fine, but everything
> below it is scrambled. Windows draws the title bar itself. ITK-SNAP hands everything below it to
> the graphics card to assemble. In your screenshot, the pieces themselves (the brain slices, the
> toolbox) are all there, but they are put together in the wrong shapes and places. That points to
> the graphics card's software, the driver. It also fits what you've seen: it happens with every
> file, including our sample data, reinstalling didn't help, and it started without any change to
> ITK-SNAP. A common cause is a driver update installed automatically by Windows Update.
>
> **Things to try, in this order:**
>
> 1. **Find out which graphics card(s) you have.** Open Device Manager and expand "Display
>    adapters". Your Dell model always has Intel graphics built into the processor, and many are
>    also fitted with a separate NVIDIA card, so you may see two entries.
> 2. **Update the graphics driver.** Get it from Dell's support page for your model, or directly
>    from Intel or NVIDIA. Windows Update is often behind. Your computer runs Windows Enterprise,
>    so it's probably managed by your IT department, and they may need to do this for you.
> 3. **If you see two graphics entries, choose which one ITK-SNAP uses.** Go to Settings → System
>    → Display → Graphics, add `C:\Program Files\ITK-SNAP 4.4\bin\ITK-SNAP.exe`, click it, then
>    Options, and choose "High performance". Restart ITK-SNAP. If that doesn't help, try "Power
>    saving" instead. Also check that your monitor cable is plugged into the NVIDIA card, not into
>    the computer's built-in display ports.
> 4. **If the problem began right after a driver update**, and a newer driver doesn't fix it,
>    rolling back usually will. In Device Manager, right-click the display adapter → Properties →
>    Driver tab → Roll Back Driver.
>
> If none of these helps, please send us:
> - the name of each entry under "Display adapters", and its driver version (on the Driver tab),
> - whether you use ITK-SNAP directly at that computer or over Remote Desktop,
> - how many monitors you use.
>
> With that we can try to reproduce it on our side.

**Notes for Jilei:**
- Step 3's cable check matters because a monitor on the built-in ports makes Windows draw on the
  Intel GPU and hand frames across to the NVIDIA one, or the reverse. That cross-GPU path is a
  known source of OpenGL glitches.
- The reply doesn't mention the upstream issues (#165, #240). Add a link if you'd like the user to
  follow one.
- Since the first message was addressed to "all", you may want the reply to go to the same list or
  forum, so others with the problem find it.
- If the user comes back with an NVIDIA Blackwell card (RTX PRO 2000/4000), link it to #240.

## For a fix session

Not escalated. Nothing points to an ITK-SNAP defect yet: the evidence fits a driver problem, and it
hasn't been reproduced.

**Reopen as a candidate if** any of these happens:
- The user's reply shows it persists on a current driver, with only one GPU, locally rather than
  over Remote Desktop.
- A second user reports the same symptom on a different machine.

At that point the brief would be: reproduce on Intel Arrow Lake graphics with 4.4.0 and with
`staging/v460` (Qt ≥ 6.9.3, VTK 9.5.2). Then check whether VTK leaves OpenGL state that Qt's
compositor relies on (bound VAO, buffers, program) after `QVTKOpenGLNativeWidget::paintGL`.
