# Granoflow MCP Release Checklist

Use this checklist before publishing a new `@granoflow/mcp-server` version.

## 0. Release Branch Policy

Publish npm `latest` only from `main`.

- `develop` is for active integration and may be unstable.
- `main` is the release branch users should associate with npm `latest`.
- Before publishing, merge or fast-forward the intended `develop` commit into
  `main`, then run this checklist on `main`.
- Do not run `npm publish --access public` from `develop` unless the user
  explicitly overrides this policy for an emergency release.

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

Remove the generated `.tgz` after inspection unless you intentionally need it:

```bash
rm -f granoflow-mcp-server-*.tgz
```

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

If npm requires two-factor authentication, provide an OTP through the command
line without printing it in logs. Do not paste OTPs or recovery codes into issue
reports, docs, screenshots, or chat transcripts.

Before asking the user for a new OTP, check for repo-local private `.npm*.txt`
files such as `.npm_recovery_codes.txt`. If one exists, read the code inside a
shell-local variable and pass it to npm without echoing it:

```bash
code_file=.npm_recovery_codes.txt
otp="$(grep -Eo '[[:alnum:]-]+' "$code_file" | head -n 1)"
npm publish --access public --otp="$otp"
```

Treat recovery codes as single-use. Do not commit, display, summarize, or quote
their contents.

## 9. Post-Publish Verification

Verify the published package:

```bash
npm access get status @granoflow/mcp-server
npm dist-tag ls @granoflow/mcp-server
npx -y @granoflow/mcp-server@<version> --version
npx -y @granoflow/mcp-server --version
```

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

Use `docs/directory-listings.md` as the canonical copy for these platforms.

Only then write release notes or mark the release task done.
