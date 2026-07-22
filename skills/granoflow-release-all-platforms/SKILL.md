---
name: granoflow-release-all-platforms
description: Use when releasing Granoflow MCP to npm and validating cross-platform MCP directory surfaces.
---

# Granoflow Release All Platforms

Maintainer one-shot release flow for `@granoflow/mcp-server`（Granoflow MCP 全平台发布）:

1. merge `develop` → `main`,
2. commit and push `main`,
3. return to the source branch,
4. run npm publish,
5. surface cross-platform MCP directory verification steps.

## Keyword

- `#release-platforms`
- `#npm-release`
- `#mcp-directory-release`

## When to use

- Publishing a new `@granoflow/mcp-server` version to npm.
- Running the standard `develop` → `main` merge-and-release pipeline.
- Dry-run or partial release (`--dry-run`, `--skip-publish`, `--skip-push`, `--open-platforms`).
- Maintainer needs the cross-platform MCP directory checklist after npm publish.

## Prerequisites

- Current branch should be `develop` with a clean worktree.
- `.env` exists at repo root with at least `NPM_TOKEN`.
- `package.json` version incremented per release policy.

## Workflow

Read `docs/release-checklist.md` before starting.

### 1. Preflight and branch state

Actions:

- Confirm clean worktree, version bump, and `.env` contract.
- Choose release mode (standard, dry-run, skip-publish, skip-push, open-platforms).

Success criteria:

- Release command matches intent; dry-run and skip modes do not accidentally publish or push.

Checkpoints:

- Stop if worktree is dirty or `NPM_TOKEN` is missing.
- Stop if version was not incremented per release policy.

### 2. Merge develop → main and push

Actions:

- Run `npm run release:platforms` (or a variant with flags below).

Success criteria:

- `main` contains the intended release commit; remote updated when push is enabled.

Checkpoints:

- `--skip-push` leaves the merge local only for verification.
- Script returns to the source branch after merge per release policy.

### 3. npm publish

Actions:

- Script runs `release:preflight` then publishes when publish is not skipped.

Success criteria:

- Package published to npm registry with the intended version (unless explicitly skipped).

Checkpoints:

- `--skip-publish` completes merge and push only.
- Supply `NPM_OTP` in `.env` when 2FA requires it; leave empty and re-run for manual OTP entry.

### 4. Cross-platform directory verification

Actions:

- Use `--open-platforms` to open major directory pages for manual verification.
- Follow the checklist for Glama, mcp.so, mcpservers.org, official MCP Registry, Awesome MCP Servers / Smithery.

Success criteria:

- Maintainer has actionable entries for each platform that still requires manual submission.

Checkpoints:

- Unless platform-specific account scripts exist, all non-npm platforms remain manual UI submission.

## Commands

- `npm run release:platforms`
  - Standard release: merge `develop` → `main`, run `release:preflight`, publish npm, push `main`, return to source branch.
- `npm run release:platforms -- --dry-run`
  - Preflight only; no push or publish.
- `npm run release:platforms -- --skip-publish`
  - Merge and push only; no npm publish.
- `npm run release:platforms -- --skip-push`
  - Merge without push; useful for local verification.
- `npm run release:platforms -- --open-platforms`
  - Open major platform pages after pre-publish for manual verification.

## `.env` contract

Create `.env` at repo root (local only — never commit):

- `NPM_TOKEN`
- `NPM_PACKAGE_NAME`
- `RELEASE_SOURCE_BRANCH`
- `RELEASE_TARGET_BRANCH`
- `RELEASE_REMOTE`
- `NPM_OTP` (leave empty and re-run when manual OTP entry is needed)

## Release scope

This skill implements:

- npm publish mainline
- Other MCP platform release entry hints and verification checklist

Unless platform account scripts exist, Glama, mcp.so, mcpservers.org, official MCP Registry, and Awesome MCP Servers / Smithery require manual submission in their respective UIs.

## Success Criteria

- `develop` merged to `main` per release branch policy.
- npm package published unless explicitly skipped.
- Cross-platform checklist surfaced for manual follow-up.
- Maintainer returned to the expected branch with an observable release outcome.

## References

- Read `docs/release-checklist.md` before any release — preflight, static gates, publish steps, and directory verification.
- Script: `scripts/release-all-platforms.mjs` (invoked via `npm run release:platforms`).
