---
name: granoflow-skill-orchestrator
description: >-
  Audit and recommend optimizations for bundled Granoflow MCP skills using the
  skill-polish family safely: default is read-only report + human confirm before
  any polish/validate apply. Activate with "orchestrate MCP skills", "audit
  granoflow skills", or "skill polish plan for this MCP". Not a product task
  orchestrator and not Initialize Granoflow.
---

# Granoflow Skill Orchestrator

Coordinates **read-only** quality inventory of `skills/*` in this MCP server,
then proposes a recommendation plan. Uses `skill-polish` / `skill-validate` /
`skill-steward` / `skill-authoring` **only when appropriate and after human
confirmation**. Default: report only — no skill rewrites.

## Keyword

- `#mcp-skill-orchestrate`
- `#skill-audit`
- `#polish-plan`

## When to use

- User wants to optimize / audit **all or selected** bundled MCP skills.
- User asks to apply `skill-polish` series to this repo without breaking
  contracts.
- Need a recommendation bucket (`keep` / `steward_audit` / `polish_candidate`
  / …) before any write.

## Not this Skill

| Concern                        | Owner                                    |
| ------------------------------ | ---------------------------------------- |
| Product task Analysis/Plan/run | `granoflow-task-orchestrator`            |
| New skill from interview       | external `skill-authoring` full pipeline |
| Project definition / Baseline  | `granoflow-project-definition`           |

## Hard Gates

1. **Report first.** Run the audit script; show Markdown report; wait for
   human accept / revise of recommendation buckets.
2. **No silent polish.** Mature skills default to `keep`. `polish_candidate`
   requires draft smells **and** a design lock (or explicit user-supplied
   design). Never polish by guessing.
3. **Preserve effect.** Hard Gates, fail-closed codes, and App admission rules
   must survive any later apply step.
4. **Apply is gated.** `--apply-plan` refuses unless `status: confirmed`; this
   release still does not auto-mutate — confirmed apply is agent-executed
   skill-by-skill after human approval.

## Workflow

### 1. Inventory + audit (read-only)

```bash
python3 skills/granoflow-skill-orchestrator/scripts/mcp_skill_orchestrate.py
```

Optional: `--skill <id>` (repeatable), `--json-out`, `--md-out`.

Success criteria:

- `temp/mcp-skill-orchestrate-report.json` and `.md` written.
- stdout JSON has `awaiting_human_confirmation: true`.

Checkpoints:

- Do not edit `skills/**` in this step.
- Load [orchestration-contract.md](references/orchestration-contract.md).

### 2. Present recommendations and wait

Show the Markdown report buckets and hard rules. Interactive: **wait** for
accept / revise. Unattended: do not auto-apply; residual that confirmation is
required.

Success criteria:

- User has a clear recommended plan.
- No polish/validate write claimed yet.

Checkpoints:

- Preview Gate: clickable `file://` links to the report when possible.

### 3. After human confirmation — execute narrowly

Only after explicit confirmation of buckets / skill ids:

| Bucket             | Allowed action                                           |
| ------------------ | -------------------------------------------------------- |
| `keep`             | None                                                     |
| `fix_structure`    | Fix frontmatter / broken links only                      |
| `steward_audit`    | Optional `skill-steward` 8-point audit (memory/registry) |
| `manual_review`    | Human + agent discuss; no polish without design          |
| `polish_candidate` | `skill-polish` with design lock; then `skill-validate`   |

Success criteria:

- Changes match the confirmed scope only.
- `npm run check` after any skill/MCP surface edit.

Checkpoints:

- Re-run audit script after edits to show delta.
- Refuse broad “polish everything”.

## Script

`scripts/mcp_skill_orchestrate.py` — owner of machine audit. See
[recommendation-taxonomy.md](references/recommendation-taxonomy.md).

## Success Criteria

- One audit report per run with per-skill rationale.
- Human confirmation before any polish-family write.
- Mature skills remain effective (no unsolicited SKILL.md compression).

## References

1. [orchestration-contract.md](references/orchestration-contract.md)
2. [recommendation-taxonomy.md](references/recommendation-taxonomy.md)
