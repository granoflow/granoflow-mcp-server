---
name: granoflow-release-all-platforms
description: Use when releasing Granoflow MCP to npm and validating cross-platform MCP directory surfaces.
---

# Granoflow Release All Platforms

Maintainer entrypoint for releasing `@granoflow/mcp-server` and verifying
cross-platform MCP directory listings. The
[release checklist](../../docs/release-checklist.md) owns the release policy,
preflight gates, and 2FA procedure.

## Keyword

- `#release-platforms`
- `#npm-release`
- `#mcp-directory-release`

## When to use

- Publishing a new `@granoflow/mcp-server` version to npm.
- Running the standard `develop` → `main` merge-and-release pipeline.
- Dry-run or partial release (`--dry-run`, `--skip-publish`, `--skip-push`, `--open-platforms`).
- Maintainer needs the cross-platform MCP directory checklist after npm publish.

## Before a release

Read the [release checklist](../../docs/release-checklist.md) and confirm the
authorized candidate, release scope, and intended remote. Verify the clean
worktree and version. The required sequence is push `main`, read back its exact
candidate SHA, then publish npm, then verify or update the Registry.

## Release wrapper behavior

`npm run release:platforms` invokes `scripts/release-all-platforms.mjs`.

- The default path fetches, checks out the source branch, fast-forwards `main`,
  and runs preflight. It reads the remote SHA, pushes only if needed, then
  requires an exact remote SHA readback before any npm operation.
- It reads the exact npm version before publishing; an existing version skips
  publication. Unknown remote/npm state stops retries. After npm success it
  reads back that version and requires npm `latest` to match the candidate.
  The checklist also covers fresh npx and published-package verification.
- `--dry-run` retains branch switching and restoration. A missing local branch
  can cause remote lookup and local branch creation. It skips fetch, merge,
  preflight, push and npm publish. `--open-platforms` can still open pages.
  This is an execution preview with side effects; review scope before use.
- `--skip-publish` leaves Git updates and preflight enabled.
- `--skip-push` requires the candidate already exists on remote `main` before
  npm can proceed; it does not bypass the SHA readback.
- The original branch is restored on success and failure when Git permits.
  An interrupted process or restoration failure requires local inspection.
- The wrapper prints manual Registry/directory follow-up; it does not publish
  Registry metadata. Before retrying that stage, read back the exact version,
  active/latest state and npm package identity, and skip it when already current.

## `.env` contract

Create `.env` at repo root (local only — never commit):

- `NPM_TOKEN`
- `NPM_PACKAGE_NAME`
- `RELEASE_SOURCE_BRANCH`
- `RELEASE_TARGET_BRANCH`
- `RELEASE_REMOTE`
- `NPM_OTP` (optional wrapper input; follow the release checklist for 2FA)

## Release scope

The wrapper publishes to npm and prints directory follow-up steps. Use the
release checklist to determine which directory updates are authorized and
what to verify on each platform.

## Success Criteria

- `develop` merged to `main` per release branch policy.
- npm package published unless explicitly skipped.
- Cross-platform checklist surfaced for manual follow-up.
- Maintainer returned to the expected branch with an observable release outcome.
