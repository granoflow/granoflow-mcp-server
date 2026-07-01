# Granoflow MCP Release Checklist

Use this checklist before publishing a new `@granoflow/mcp-server` version.

## 1. Source State

- Confirm the worktree is clean or only contains intended release changes:

  ```bash
  git status --short --branch
  ```

- Confirm the package version, runtime metadata, and tests agree:

  ```bash
  node -p "require('./package.json').version"
  npm run check
  node dist/index.js --version
  ```

## 2. Static Gates

Run the project gate:

```bash
npm run check
```

The gate must pass:

- Prettier
- ESLint
- TypeScript build
- Vitest

## 3. Package Contents

Inspect the packed files:

```bash
npm pack --json
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

Only then write release notes or mark the release task done.
