# AGENTS

## Project Role

This repository is the public Granoflow MCP server. It exposes Granoflow's
Local HTTP API to AI agents.

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
