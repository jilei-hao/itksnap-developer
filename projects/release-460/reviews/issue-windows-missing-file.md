### What happens

On Windows, if a file named on the command line does not exist, ITK-SNAP prints `Launching ITK-SNAP` and exits immediately with code `0xC0000409`. It shows no window and no error message. For example:

```
ITK-SNAP.exe -g C:\no\such\file.nii.gz
ITK-SNAP.exe C:\no\such\file.nii.gz          (a bare argument, which is how Explorer passes a double-clicked file)
ITK-SNAP.exe -w C:\no\such\workspace.itksnap
```

A user sees this when opening a file that has been moved or renamed since, for example through a shortcut or "Open with", or when a path on the command line has a typo.

**Expected:** the usual "Image IO Error: Failed to load image …" dialog, which is what `main()` shows when loading fails. On macOS and Linux, where `DecodeFilename()` does nothing, the missing file reaches that code.

Reproduced on Windows 11 (MSVC 2022, Qt 6.9.3, ITK 5.4.0) in two builds: one of `master` @ 52ee94fa plus our pending 4.6 branches, none of which touch `main.cxx`, and one of the head of #241. The Windows Application event log records a fail-fast in `ucrtbase.dll`.

### Cause

Every local path given on the command line (`-g`, `-s`, `-o`, `-m`, `-l`, `-w`, `--url`, `--testdir`, and a bare file argument) goes through `DecodeFileOrUrl()` → `DecodeFilename()`. On Windows, that function expands the path with `GetLongPathNameA`, which fails for a path that does not exist. It then throws:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/GUI/Qt/main.cxx#L439-L456

The exception is thrown inside `parse()`, which `main()` calls here:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/GUI/Qt/main.cxx#L1072

That call is before `main()`'s `try` block (line 1287), so nothing catches the exception and the C runtime aborts the process. The function also leaks `buffer` (`new char[]`, never deleted).

(Before #241, the same crash also hit files that **do** exist when their path contained non-ASCII characters. The command line was decoded in the legacy code page, so `GetLongPathNameA` could not find them. #241's UTF-8 manifest fixed that part.)

### Suggested fix

In `DecodeFilename()`, if `GetLongPathNameA` fails, return the path unchanged instead of throwing. The normal loading code then reports the missing file with the usual dialog. The fix should also use a `std::string` or `std::vector<char>` for the buffer so that it cannot leak.
