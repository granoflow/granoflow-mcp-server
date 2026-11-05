# AGENTS

## Project Role

This repository is the public Granoflow MCP server. It exposes Granoflow's
Local HTTP API to AI agents.

On the maintainer workbench, use the shared global rules and the topics they
select for the task. Keep public project documentation in `docs/` and local
task records in the ignored `docs-temp/`. Exclude private material from
commits and package contents.

## Hard Rules

- Keep the MCP server thin. Do not reimplement Granoflow business logic here.
- Call the Granoflow Local HTTP API directly. Do not add an execution dependency
  on external command-line wrappers.
- Do not print API tokens or secrets in logs, tool results, test snapshots, or
  documentation.
- For npm publish 2FA, check repo-local private `.npm*.txt` files before asking
  the user for an OTP. Read codes only into shell-local variables, never print
  them, and never include them in docs, commits, screenshots, logs, or chat.
- Keep tool results structured and predictable for Cursor, Codex, Claude Code,
  and OpenCode/OpenClaw-compatible MCP clients.
- Do not add direct SQLite, Drift, app build, app run, screenshot, or release
  orchestration logic.

For changes to the MCP or Local HTTP protocol boundary, read
`workspace/cross-language-interfaces.md` in the shared rules checkout.
Start with the tool registration and
schemas under [src/](src/) and the [Local HTTP client](src/api.ts), then trace
the Granoflow endpoint and the affected MCP caller. Validate the affected
boundary through the real caller and endpoint when required; fixture evidence
covers only the behavior exercised by the fixture.

## Bundled Skills

Before changing a bundled Skill, check its callers, the
[MCP resource allowlist](src/workflow-resources.ts), and the npm `files`
configuration in [package.json](package.json). Package inclusion and MCP
resource discovery are separate. Use `workspace/document-content-quality.md`
in the shared rules checkout for authoring; use the project Skill testing
policy below for structure, script behavior, and agent behavior checks.

For Granoflow task Analysis, Plan, and execution handoff, start at the bundled
[task orchestrator](skills/granoflow-task-orchestrator/SKILL.md). Shared
workbench handoff guidance covers workbench queue records; the bundled
workflow owns Granoflow task states, tool names, and confirmation gates.

## Skill Testing

Follow popular Agent Skills practice (structure + script tests; behavior via evals):

- **Allowed in CI**: `SKILL.md` frontmatter structure (`tests/skills-structure.test.ts`); real `skills/*/scripts` tests under `tests/python/`; MCP skill tools asserting `ok` / `path` / non-empty body / reference ids only.
- **Forbidden**: reading `skills/**/SKILL.md` or `references/**` and locking prose, gate copy, or activation phrases with `toContain` / `toMatch`. That is not conventional skill testing and must not be reintroduced.
- **Behavior**: validate agent compliance with LLM evals when needed. This repository does not require an eval harness in CI today — do not replace evals with markdown snapshot locks.

See `.cursor/rules/skill-testing.mdc`.

## Quality Gate

Run before handoff after code changes:

```text
npm run check
```

The gate includes Prettier, ESLint, TypeScript, Vitest, and Python skill-script checks.

See the [Change Quality Gate](.cursor/rules/change-quality-gate.mdc) for checks by
change type.

## Release

For a release, follow the [Granoflow MCP Release Checklist](docs/release-checklist.md).
Before using a release wrapper, apply the preview guidance in
`workspace/engineering-principles.md` in the shared rules checkout. Check
the wrapper's actual behavior against the authorized release scope.
