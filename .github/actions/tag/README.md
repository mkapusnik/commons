# Set Git Tag

Creates or updates a lightweight tag in the current repository. This action is retained for backward compatibility with existing workflows; new workflows should prefer `../git-ref` with `ref: refs/tags/<tag-name>`.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `tag` | Yes | None | Tag name to create or update, without the `refs/tags/` prefix. |
| `commit_sha` | No | Current workflow SHA | Commit SHA to tag. Omit it to use `context.sha`. |
| `token` | Yes | None | GitHub token used for ref operations. |

## Outputs

This action declares no outputs.

## Permissions

The token needs `contents: write` in the current repository. Use a PAT or GitHub App token when default `GITHUB_TOKEN` behavior is not sufficient, such as workflows that need tag updates to trigger downstream workflows.

## Example

```yaml
permissions:
  contents: write

steps:
  - name: Move legacy sanity tag
    uses: mkapusnik/commons/.github/actions/tag@v1
    with:
      tag: sanity
      commit_sha: ${{ github.sha }}
      token: ${{ secrets.RELEASE_TOKEN }}
```

For external consumers, pin this shared action to a release tag or immutable commit SHA rather than a moving branch.
