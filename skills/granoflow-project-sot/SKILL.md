---
name: granoflow-project-sot
description: >-
  Own the single project-local orchestration SoT at temp/project-sot.yaml.
  Create, lint, and regenerate it from the Granoflow App when missing, wiped,
  or intentionally refreshed. Use on long/unattended runs, host-wake resume,
  and when the user asks to rebuild Project SoT. Not an E2E test runner.
---

# Granoflow Project SoT

Single owner for the **mutable project orchestration SoT** in the target repo:

```text
temp/project-sot.yaml
```

It records lifecycle stages, coarse `work_items`, `next_step`, thin campaign
gates, and **evidence pointers only**. Skill-internal Grill / suite-merge
details stay out of this file.

## Keyword

- `#project-sot`
- `#重生SoT`
- `#regen-project-sot`

## When to use

- Starting or resuming a long / unattended project run.
- Host-wake ticks that must load Layer A continuity.
- `temp/` wiped or `temp/project-sot.yaml` missing → **regen before continue**.
- User asks to refresh SoT to match App / workspace verify status.
- Closing IT/E2E / final delivery when updating campaign thin gates on the SoT.

## Not this Skill

| Concern | Owner |
| --- | --- |
| Running Flutter UI E2E | `granoflow-e2e-test-campaign` |
| Portfolio IT loop | `granoflow-integration-test-campaign` |
| Project Work intake | `granoflow-project-definition` |
| Wake protocol details | `granoflow-agent-workflow` → `long-task-run-continuity` |

## Mandatory loads

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-project-sot",
  referenceId: "project-sot"
)
```

On regen:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-project-sot",
  referenceId: "regen-from-app"
)
```

Also load `long-task-run-continuity` when arming or consuming host wake
(Layer A = this SoT).

## Hard rules

1. **One file owns `next_step`:** only `temp/project-sot.yaml`.
2. **Forbidden as orchestration SoT:** `unattended-run-ledger.yaml`,
   `residual-report.*`, `project-lifecycle-progress-board.md`,
   `campaign-state.json`, coverage-matrix / closing-summary bodies.
   Those may exist as **evidence**; they must not pin `next_step`.
3. **New writes are YAML only** (`doc_type: project_sot`,
   `schema: granoflow_project_sot_v1`).
4. Legacy `temp/project-e2e-sot-v*.md` is read-only compatibility; migrate to
   `temp/project-sot.yaml` before claiming stage progress.
5. Missing SoT on unattended resume → run regen, then lint, then continue.
   Skipping fails closed as `project_sot_missing`.

## Commands

Lint:

```bash
python3 skills/granoflow-project-sot/scripts/lint_project_sot.py \
  temp/project-sot.yaml
```

Regen from App:

```bash
python3 skills/granoflow-project-sot/scripts/regen_project_sot_from_app.py \
  --project-id <uuid> \
  --repo-root <path> \
  --force
```

Optional workspace probe (analyze/test pointers only):

```bash
python3 skills/granoflow-project-sot/scripts/regen_project_sot_from_app.py \
  --project-id <uuid> --repo-root <path> --force --probe-workspace
```

## Fail-closed codes

| Code | Meaning |
| --- | --- |
| `project_sot_unread` | Contract reference not loaded |
| `project_sot_missing` | Required run without active SoT |
| `project_sot_stale` | Digests / next_step stale or digest match failed |
| `project_sot_lint_failed` | Lint aggregate failure |
| `project_sot_legacy_path` | Using deprecated e2e-named SoT path |
| `project_sot_regen_failed` | App API / projection failed |

Legacy codes `project_e2e_sot_*` may still appear from old wrappers; treat as
aliases of `project_sot_*`.
