# Orchestration Contract

Owner for **how** the MCP skill orchestrator uses the external skill-polish
family without weakening bundled Granoflow contracts.

## Family map (external)

| Stage            | Skill             | When MCP orchestrator may invoke                          |
| ---------------- | ----------------- | --------------------------------------------------------- |
| Design/interview | `skillify`        | Only for **new** skills — not bulk MCP rewrite            |
| Scaffold         | `skill-scaffold`  | Only with confirmed design for new skills                 |
| Polish           | `skill-polish`    | Only `polish_candidate` after human confirm + design lock |
| Validate         | `skill-validate`  | After polish, or targeted quality check when requested    |
| Full pipeline    | `skill-authoring` | New skill end-to-end — not default for mature MCP skills  |
| Memory/registry  | `skill-steward`   | Optional for `steward_audit` bucket                       |

Paths are typically under `~/.codex/skills/…`. The audit script **probes**
presence only; it never invokes them.

## Preview → confirm → write

1. Audit script writes report under `temp/` (write of report ≠ write of skills).
2. Agent presents report (prefer clickable HTML/MD links).
3. Human confirms buckets / exceptions.
4. Only then may the agent edit skills or call polish/validate CLIs.

Skipping step 3 fails closed as `skill_orchestrate_unconfirmed`.

## Preserve effectiveness

When applying polish to a candidate:

- Keep Hard Gates, fail-closed codes, Mode Gate, and App admission language.
- Move detail to `references/` rather than deleting constraints.
- Do not invent parallel product SoT.
- Run `npm run check` after MCP surface wiring or skill script changes.

## Fail-closed codes

| Code                              | When                                          |
| --------------------------------- | --------------------------------------------- |
| `skill_orchestrate_unconfirmed`   | Mutate/polish without human confirm           |
| `skill_orchestrate_polish_guess`  | Polish without design lock / confirmed design |
| `skill_orchestrate_apply_refused` | `--apply-plan` without `status: confirmed`    |
| `skill_orchestrate_scope_drift`   | Edits outside confirmed skill id list         |
