### Summary

Every pull request currently ends with all four build jobs red, whether it comes from a fork or from a branch in this repository. This happens for reasons unrelated to the change being reviewed. Separately, test failures never make a run fail, so a green run does not mean the tests passed. `CONTRIBUTING.md` says a pull request "is expected to be green before it is merged". Right now nobody can get there, and a green result would not say much if they did.

Evidence: #241 and #244, opened from forks, and #247, opened from the `seg_anchor` branch here, all fail at the same steps. The manual (`workflow_dispatch`) build of `master` at 52ee94fa is green.

| Job | Failing step | Affects |
|---|---|---|
| ubuntu-22.04, windows-2022 | `ITK-SNAP Dashboard -- Gatekeeper` | every PR |
| macos-15, macos-15-intel | `Cleanup secrets` | every PR |
| `claude-review` | fails before reviewing | fork PRs (see 3) |

Thanks to @marcoduering, who analysed the first three in #241 and proposed fixes there.

### 1. Ubuntu/Windows: the build never runs on pull requests

The `Configure and Build` step runs Start, Update, Configure and Build in one bash script. Actions runs bash with `-e`, so the first failing command ends the script:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L273-L282

On pull requests, `ctest -D ExperimentalUpdate` fails with `Update command failed: "/usr/bin/git" "fetch"`. Configure and Build then never run, and the Gatekeeper fails the job.

The underlying error is in the greedy submodule:

```
Fetching submodule Submodules/greedy
fatal: remote error: upload-pack: not our ref a88a4f3e01d1f59ff43e4a6c3e673e5c9c5571ac
```

`git fetch` fetches, on demand, the submodule commits that the newly fetched superproject commits point to. 7ee09def ("Added baseline code for 2d mesh rendering", 2025-03-18), which is in `master`'s history, points `Submodules/greedy` at a88a4f3e, and that commit no longer exists in pyushkevich/greedy. So a fresh `git fetch` fails.

`master` builds hit the same error. That is what the `Post-checkout fetch` step works around; its comment mentions "some bizarre git error with greedy submodule":

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L237-L243

On `master`, that first fetch fails (the step is `continue-on-error`) and the second fetch, inside `ExperimentalUpdate`, then succeeds. On pull requests the second fetch fails too, on every runner:

- On Ubuntu and Windows, `ctest -D ExperimentalUpdate` then exits with code 1, so the script stops and nothing is built. In #241 all 34 tests then fail.
- On macOS, `ctest` logs the same `Update command failed` but exits with code 0, so the build and tests still run. In #241, 33 of 34 tests passed there, and the macOS jobs failed only because of item 2.

We have not worked out why the second fetch passes on `master`, or why `ctest` exits differently on the two kinds of runner. The fixes below do not depend on it, because each one stops this fetch from reaching the greedy submodule.

Possible fixes:
- Stop the submodule recursion in CI: `git config fetch.recurseSubmodules false` in the `Post-checkout fetch` step. The checkout step already checks the submodules out at the right commits.
- Or skip `ExperimentalUpdate` for `pull_request` events. The checkout step already selects the PR revision.
- If a88a4f3e still exists in someone's local greedy clone, pushing it to a branch or tag of pyushkevich/greedy would remove the error at its source.

### 2. macOS: `Cleanup secrets` deletes a keychain that PR runs never create

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L396-L402

`build.keychain` is created only by `Setup codesign keychain` (L322-L323), which is skipped whenever `SKIP_PACKAGING` is set. `SKIP_PACKAGING` is set for every `pull_request` event (L50). Possible fix: delete the keychain only if it exists, for example `security delete-keychain build.keychain || true`, or with a file check.

### 3. `claude-review` cannot run on fork PRs

`.github/workflows/claude-code-review.yml` needs `secrets.CLAUDE_CODE_OAUTH_TOKEN` and an OIDC token (`id-token: write`). GitHub gives neither to `pull_request` workflows that run for forks. Possible fix: skip the job for forks, with `if: github.event.pull_request.head.repo.full_name == github.repository`. Maintainers can still request a review through the `@claude` comment workflow. (`pull_request_target` would provide the secrets, but it runs with the repository's secrets and write permissions. Checking out a fork's code inside it needs care.)

`claude-review` also failed on #249, a same-repository PR that does get the secrets. There it failed inside the `Run Claude Code Review` step, for a reason we have not looked into.

### 4. Test results are never gated

The test step has `continue-on-error: true`, and the Gatekeeper checks only the configure/build and submit steps:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L284-L303

So a run is green even when tests fail. The manual build of `master` at 52ee94fa is an example: on Ubuntu, 3 of 34 tests failed (the three `RemoteImageLoadTest_*`), and the test step exited with code 8, yet the run is green. That also shows `ctest -D ExperimentalTest` already exits non-zero when a test fails, so the mechanical fix is to add `steps.ctest-test.outcome` to the Gatekeeper condition. Doing that today would turn CI red, though, because of the remote-image tests (`RemoteImageLoadTest_*`). They are flaky, and `RemoteImageLoadTest_Cache` fails on Windows and Linux (#258, which has a fix ready). Those need fixing or excluding first, so this item is a decision for the maintainers rather than a one-line change.

One way to exclude them already exists. The three remote tests carry the CTest label `Remote`, which `CMakeLists.txt` added "so CI can skip them easily":

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/CMakeLists.txt#L1460-L1467

So the gate could check a test run with `-LE Remote`, which leaves out tests with that label, while the remote tests keep running and reporting to CDash without failing the job.
