# Lifecycle Tag Gate

## Purpose

`Lifecycle Tag Gate` decides whether a lifecycle workflow should run by comparing a source tag with a target tag. It reads tags from a Git remote and emits a decision instead of mutating repository state.

## User scenario

Use this action before a promotion job. For example, a production promotion should run when the `staging` tag exists and the `production` tag is missing or points at a different commit. It should skip when `staging` is missing or `production` already matches `staging`.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `source_tag` | Yes | None | Source lifecycle tag name that must exist before the workflow should run. Do not include `refs/tags/`. |
| `target_tag` | Yes | None | Target lifecycle tag name that is current when it points at the same SHA as `source_tag`. Do not include `refs/tags/`. |
| `repository` | No | Current workflow repository | Repository in `owner/repo` form. Used for validation and log messages. |
| `remote` | No | `origin` | Git remote name or URL used with `git ls-remote` to read tags. |

## Outputs

| Output | Description |
| --- | --- |
| `should_run` | `true` only when `reason=pending`; otherwise `false`. |
| `source_sha` | Commit SHA currently referenced by `source_tag`, or an empty string when `source_tag` is missing. |
| `target_sha` | Commit SHA currently referenced by `target_tag`, or an empty string when `target_tag` is missing. |
| `short_sha` | First 12 characters of `source_sha`, or an empty string when `source_tag` is missing. |
| `reason` | Decision reason: `source-missing`, `already-current`, or `pending`. |

## Permissions

The action reads refs with `git ls-remote` and does not call the GitHub API. Same-repository workflows using `actions/checkout` need only `contents: read`. Private or cross-repository remotes need credentials in the configured remote URL or checkout configuration so `git ls-remote` can read the tags.

## Success behavior

- Missing `source_tag`: succeeds with `should_run=false`, empty SHA outputs, and `reason=source-missing`.
- Existing `source_tag` and missing `target_tag`: succeeds with `should_run=true` and `reason=pending`.
- Existing tags with different SHAs: succeeds with `should_run=true` and `reason=pending`.
- Existing tags with the same SHA: succeeds with `should_run=false` and `reason=already-current`.

Annotated tags are peeled to the referenced commit SHA before comparison.

## No-op behavior

The action never mutates repository state. The no-op decisions are `source-missing` and `already-current`, both of which set `should_run=false` so downstream jobs can skip safely.

## Failure behavior

The action fails when required inputs are empty, `repository` is not in `owner/repo` form, `source_tag` or `target_tag` includes `refs/`, a tag name is invalid according to Git ref-name rules, a tag or remote value starts with `-`, `GITHUB_OUTPUT` is unavailable, or `git ls-remote` fails for a reason other than a missing tag.

## Notable edge cases

- A missing target tag is a pending lifecycle state, not a failure.
- A missing source tag is also not a failure because the upstream lifecycle step may not have produced a candidate yet.
- Without a prior checkout, pass an explicit `remote` URL instead of relying on `origin`.
- External consumers should pin the action to a release tag or immutable commit SHA.
