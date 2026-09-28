### Summary

Every pull request opened from a fork currently ends with all four build jobs red. This happens for reasons unrelated to the change being reviewed. Separately, test failures never make a run fail, so a green run does not mean the tests passed. `CONTRIBUTING.md` says a pull request "is expected to be green before it is merged". Right now outside contributors cannot get there, and a green result would not say much if they did.

Evidence: #241 and #244, both opened from forks, fail at the same steps. The push builds of `master` (52ee94fa) are green.

| Job | Failing step |
|---|---|
| ubuntu-22.04, windows-2022 | `ITK-SNAP Dashboard -- Gatekeeper` |
| macos-15, macos-15-intel | `Cleanup secrets` |
| `claude-review` | fails before reviewing |

Thanks to @marcoduering, who analysed the first three in #241 and proposed fixes there.

### 1. Ubuntu/Windows: the build never runs on fork PRs

The `Configure and Build` step runs Start, Update, Configure and Build in one bash script. Actions runs bash with `-e`, so the first failing command ends the script:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L273-L282

On fork PRs, `ctest -D ExperimentalUpdate` fails. According to the job logs as read in #241, the failure is in its `git fetch`, and this still needs confirming from a log. Configure and Build then never run, and the Gatekeeper fails the job. Possible fix: skip `ExperimentalUpdate` for `pull_request` events. The checkout step already selects the PR revision. The `Post-checkout fetch` step (L239-L243) could be skipped for PRs too.

### 2. macOS: `Cleanup secrets` deletes a keychain that PR runs never create

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L396-L402

`build.keychain` is created only by `Setup codesign keychain` (L322-L323), which is skipped whenever `SKIP_PACKAGING` is set, as it is for every PR. Possible fix: delete the keychain only if it exists, for example `security delete-keychain build.keychain || true`, or with a file check.

### 3. `claude-review` cannot run on fork PRs

`.github/workflows/claude-code-review.yml` needs `secrets.CLAUDE_CODE_OAUTH_TOKEN` and an OIDC token (`id-token: write`). GitHub gives neither to `pull_request` workflows that run for forks. Possible fix: skip the job for forks, with `if: github.event.pull_request.head.repo.full_name == github.repository`. Maintainers can still request a review through the `@claude` comment workflow. (`pull_request_target` would provide the secrets, but it runs with the repository's secrets and write permissions. Checking out a fork's code inside it needs care.)

### 4. Test results are never gated

The test step has `continue-on-error: true`, and the Gatekeeper checks only the configure/build and submit steps:

https://github.com/pyushkevich/itksnap/blob/52ee94fa5f191a122cda71c2fc5600e1924143b7/.github/workflows/build.yml#L284-L303

So a run is green even when tests fail. The mechanical fix is to add `steps.ctest-test.outcome` to the Gatekeeper condition, after checking that `ctest -D ExperimentalTest` exits non-zero when a test fails. Doing that today would turn CI red, though, because of the remote-image tests (`RemoteImageLoadTest_*`). They are flaky, and `RemoteImageLoadTest_Cache` fails on Windows and Linux. Those need fixing or excluding first, so this item is a decision for the maintainers rather than a one-line change.
