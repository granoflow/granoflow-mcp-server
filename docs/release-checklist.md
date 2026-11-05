# Granoflow MCP Release Checklist

Use this checklist before publishing a new `@granoflow/mcp-server` version.

## 0. Release Branch Policy

Publish npm `latest` only from `main`.

- `develop` is for active integration and may be unstable.
- `main` is the release branch users should associate with npm `latest`.
- Before publishing, merge or fast-forward the intended `develop` commit into
  `main`, then run this checklist on `main`. Push the candidate to remote
  `main` and read back its exact SHA before npm or Registry publication.
- Do not run `npm publish --access public` from `develop` unless the user
  explicitly overrides this policy for an emergency release.

Before invoking a wrapper, check the flags and side effects of every step
against the authorized scope. The MCP write-tool `code: "dry_run"` result
described below does not establish that the release wrapper is read-only.

## 1. Source State

- Confirm the worktree is clean or only contains intended release changes:

  ```bash
  git status --short --branch
  ```

- Confirm the current branch is `main` before publish:

  ```bash
  git branch --show-current
  ```

- Confirm the package version, runtime metadata, and tests agree:

  ```bash
  node -p "require('./package.json').version"
  npm run release:preflight
  node dist/index.js --version
  ```

## 2. Static Gates

Run the project gate:

```bash
npm run release:preflight
```

The preflight includes `npm run check`, so these gates must pass:

- Prettier
- ESLint
- TypeScript build
- Vitest

## 3. Package Contents

Inspect the packed files:

```bash
npm run release:preflight
```

Verify:

- `dist/index.js` is present.
- `dist/index.js` mode is executable, for example `493`.
- `README.md` is present.
- `docs/` files are present when documentation changed.
- no obsolete `dist/cli.*` files are present.
- no local config, token, recovery code, or temporary file is present.

`npm pack --dry-run` does not create a tarball. If a separate packaging step
created an obsolete `.tgz`, move that artifact to the system Trash after confirming
its exact path and retention needs.

## 4. Local MCP Smoke

Start the package through stdio and list tools. The smoke should prove:

- expected tool count is returned.
- `granoflow_health` returns `code: "ok"` when Granoflow is running.
- resource tools such as project, milestone, and structured task tools exist.
- write tools can return `code: "dry_run"` without creating real data.

## 5. App Runtime Evidence

Verify the running Granoflow app:

```bash
curl -s http://127.0.0.1:56789/v1/health
```

For macOS production app verification, `granoflow_setup_status` should show a
process path like:

```text
/Applications/granoflow.app/Contents/MacOS/granoflow
```

## 6. Client Config Examples

Confirm README and docs show the same command shape:

```text
command = "npx"
args = ["-y", "@granoflow/mcp-server"]
```

Cursor and Codex examples should set:

```text
GRANOFLOW_API_BASE_URL=http://127.0.0.1:56789
```

Do not add API tokens to checked-in examples.

Confirm public docs still describe the agent completion workflow:

- `granoflow_task_finish` is preferred over low-level task completion.
- task reviews are for durable decisions, lessons, failure modes, reusable
  process details, and unresolved risks.
- review cards are one durable knowledge point each, not only language-learning
  cards.
- pronunciation, phonetic, translation, and TTS card fields are gated by
  `granoflow_ai_agent_tools` capability discovery and have a plain front/back
  fallback.

## 7. Secret And Drift Checks

Search for obsolete command-wrapper references and secret-like values:

```bash
rg -n "granoflow-cli|GRANOFLOW_CLI|cliPath|granoflow_cli" README.md docs src tests package.json AGENTS.md
rg -n "recovery code|_authToken|secret-token|npm password" README.md docs src tests package.json AGENTS.md
```

Expected result:

- no obsolete command-wrapper dependency.
- no real token, OTP, password, or recovery code.
- test fixtures may use fake values only when they assert redaction.

## 8. Publish

Publish only after all previous checks pass:

```bash
npm publish --access public
```

Before publishing or retrying, read back remote `main` and the exact npm version:

```bash
git rev-parse HEAD
git ls-remote --exit-code --heads origin refs/heads/main
npm view @granoflow/mcp-server@<version> version --json
```

Require the remote SHA to match the candidate. An existing exact npm version
means skip publication and continue verification. Only `E404` establishes an
absent version; authentication, connection or malformed responses require
inspection before retrying. Before resuming Registry publication, read back its
exact version, active/latest state and npm identity, then skip already-current
metadata. The wrapper does not automate Registry publication.

On actual npm `EOTP`, check repo-local private `.npm*.txt` files before asking
for an OTP. Recovery files use one code per line; blank lines and `#` comments
are ignored. Read a code only into a shell-local variable and pass it through
the child environment without printing it. Mark that line `# USED` only after
npm confirms success. A failed publish preserves it; if its result is ambiguous,
read back npm before retrying. Missing usable codes require a user OTP. Never
paste codes, tokens or child error output into logs, docs, screenshots or chat.

The wrapper implements this through `scripts/release-npm-publish.sh` and injects
the token through npm's config environment without writing project npm config.
`NPM_OTP` is an optional explicitly supplied OTP; it is used only after `EOTP`
and only when no usable private recovery code is available.

`--dry-run` can switch/create local branches, query a remote when a local branch
is missing, and open pages with `--open-platforms`. It skips fetch, merge,
preflight, push and npm publication. `--skip-push` still requires the exact
candidate SHA on remote `main`.

## 9. Post-Publish Verification

Verify the published package:

```bash
npm access get status @granoflow/mcp-server
npm dist-tag ls @granoflow/mcp-server
fresh_cwd="$(mktemp -d -t granoflow-npx-cwd)"
fresh_cache="$(mktemp -d -t granoflow-npx-cache)"
cd "$fresh_cwd"
npm_config_cache="$fresh_cache" npx --yes --package=@granoflow/mcp-server@<version> granoflow-mcp-server --version
npm_config_cache="$fresh_cache" npx --yes --package=@granoflow/mcp-server@latest granoflow-mcp-server --version
npm_config_cache="$fresh_cache" npx --yes --package=@granoflow/mcp-server@<version> granoflow-mcp-server gfmcp-runner --help
```

Use both a fresh cache and a directory outside the source repository. Running
`npx` from the package worktree can resolve a local `node_modules/.bin` entry
and falsely report an older build even when the public tarball is correct.

Run one MCP stdio smoke against the published version:

- list tools
- call `granoflow_health`
- call one dry-run write tool

## 10. Directory Platform Closure

After npm and the official MCP Registry are current, verify the directory
platforms that users may discover from:

- `Glama`: open or search the Granoflow listing and confirm the repository,
  install command, description, and source-code metadata are still accurate. If
  any of those changed, submit the listing update and wait for the review state
  to prove the update was accepted or queued.
- `mcp.so`: open or search the Granoflow listing and confirm the repository,
  install command, server config, short description, and privacy positioning are
  still accurate. If any of those changed, submit the listing update and record
  the platform state before closing the release.
- `mcpservers.org`: open or search the Granoflow listing and confirm the
  repository, category, and short description are still accurate. If any of
  those changed, submit the listing update and wait for the review state to
  prove the update was accepted or queued.
- `Awesome MCP Servers`: confirm the Granoflow row or pull request still points
  to `https://github.com/granoflow/granoflow-mcp-server` and uses current
  positioning. If the project name, repository, category, or run command changed,
  open or update the pull request and wait for checks to pass.

For a platform where no Granoflow listing or pull request exists, record
`absent` rather than claiming freshness. A routine package release does not
silently create a previously deferred third-party submission; creation needs
the corresponding distribution task or explicit release scope. Existing
listings must still be checked whenever the install command, repository,
description, privacy boundary, or public capability set changes.

Use `docs/directory-listings.md` as the canonical copy for these platforms.

Only then write release notes or mark the release task done.
