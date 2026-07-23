# Recommendation Taxonomy

Produced by `scripts/mcp_skill_orchestrate.py` for each skill directory.

## Buckets

| Recommendation     | Meaning                                                           | Default next action                          |
| ------------------ | ----------------------------------------------------------------- | -------------------------------------------- |
| `keep`             | Structure healthy; no draft smells                                | None                                         |
| `steward_audit`    | Minor section-hint gaps; optional memory/registry audit           | Optional `skill-steward`                     |
| `manual_review`    | Draft smells without design lock, or long body + missing sections | Discuss; supply design or fix smells by hand |
| `polish_candidate` | Draft smells **and** design lock under `temp/`                    | Confirm → `skill-polish` → `skill-validate`  |
| `fix_structure`    | Frontmatter / broken reference link errors                        | Fix structure first                          |

## Polish eligibility (hard)

`polish_allowed: true` only when:

1. Recommendation is `polish_candidate`; and
2. A design lock file was found (or the human later attaches a confirmed
   design); and
3. Human confirms that skill id in the apply scope.

Otherwise polish is forbidden even if the body is long.

## Finding codes (audit)

| Code                    | Severity | Typical bucket impact     |
| ----------------------- | -------- | ------------------------- |
| `frontmatter_*`         | error    | `fix_structure`           |
| `broken_reference_link` | error    | `fix_structure`           |
| `draft_smell`           | warn     | `manual_review` or polish |
| `section_hint_missing`  | warn     | `steward_audit` / review  |
| `skill_md_long`         | info     | informational only        |

## Confirmed plan shape (future apply)

```yaml
schema: granoflow_mcp_skill_orchestrate_plan_v1
status: confirmed # required for any apply attempt
confirmed_at: <ISO8601>
confirmed_by: user
skill_ids: [] # explicit allow-list
actions:
  - skill_id: granoflow-example
    recommendation: polish_candidate
    design_file: temp/example-design-lock-v1.json
```

Until apply is implemented in the script, the agent executes this plan
manually under the orchestration contract.
