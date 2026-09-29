### What happens

`RemoteImageLoadTest_Cache` fails on Windows and Linux. It passes only on macOS:

```
FAIL: CacheMetadata.xml not created after first download
```

The download cache itself works. The test is looking for it in the wrong folder.

There is also a side effect. On Windows and Linux, every `ctest` run writes remote-image cache files into the developer's real ITK-SNAP settings folder: `%APPDATA%\itksnap.org\ITK-SNAP` on Windows, `~/.itksnap.org/ITK-SNAP` on Linux. All three `RemoteImageLoadTest_*` tests do this, not just `_Cache`.

### Cause

The test tells ITK-SNAP to keep its data in a scratch folder, `.itksnap_test`. It does this through its own `SystemInfoDelegate`, and `TestCache()` then looks for `CacheMetadata.xml` in that same folder:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/Testing/Logic/RemoteImageLoadTest.cxx#L332-L335

But `SystemInterface::GetApplicationDataDirectory()` decides where the cache goes, and it asks the delegate only on macOS. On Windows it builds the path from `%APPDATA%`, and on Linux from `$HOME`:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/Common/SystemInterface.cxx#L88-L154

So on Windows and Linux the cache is written to the real settings folder, and the test never finds it. Its "clear the cache" step clears a folder that does not exist.

### Fix

The fix changes the test only; ITK-SNAP itself is untouched. It is ready on the `bug/remote-cache-test-datadir` branch of jilei-hao/itksnap (6ff7a582), and we will open a pull request for it.

- The test asks ITK-SNAP where its data folder is, instead of assuming.
- At startup, the test points `%APPDATA%` (Windows) or `$HOME` (macOS and Linux) at `.itksnap_test` inside the build folder. So all three remote-image tests keep their files there on every platform.
- Before clearing a cache, the test checks that the folder really is inside `.itksnap_test`. If a future change broke the redirect, the test would fail instead of deleting someone's real cache.

We chose not to make `GetApplicationDataDirectory()` ask the delegate on every platform. That would move where the real application keeps its data. On Linux, the Qt delegate returns `~/.local/share/itksnap.org/ITK-SNAP`, so existing users would lose their preferences and recent files on upgrade.

### Tested

- **Windows 11:** before the fix, `_Cache` failed on 5 of 5 runs. After it, it passed 6 of 6, including the check that the second download is answered from the cache. The real settings folder was not touched. We also checked that the test still catches problems: breaking the cache write makes it fail, and removing the redirect makes the safety check stop it before anything is cleared.
- **macOS:** the full test suite passes. The only failures were single runs of the other two remote-image tests, which also fail now and then without this change and passed when run again. `_Cache` passes with its files inside the build folder, and the real settings folder is unchanged.
- **Linux:** not run yet.
