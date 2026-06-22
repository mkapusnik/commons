# Repository Workflow

This repository uses `master` as the canonical base branch for pull requests.
Do not target `develop` unless the repository later creates and documents that
branching strategy.

## Issue-backed feature or fix flow

1. Start from an up-to-date `master` branch.
2. Create a focused feature or fix branch with a concise kebab-case name.
3. Make the smallest change that addresses the linked issue.
4. Run the relevant lightweight checks for the changed files before committing.
5. Commit only the intended files with a concise message.
6. Push the feature or fix branch.
7. Open a draft pull request with `master` as the base branch.
8. Reference the issue in the draft pull request body without closing syntax,
   for example `Related to #1`.
9. Keep the pull request as a draft while implementation, testing, review, or CI
   feedback is still pending.
10. Mark the pull request ready for review only after the content is accepted and
    required checks are passing.

## Pull request base branch

When creating pull requests manually or with automation, pass the base branch
explicitly:

```sh
gh pr create --draft --base master --head <feature-branch>
```

For existing pull requests, verify that the base branch is `master` before
requesting review or enabling merge-related automation.
