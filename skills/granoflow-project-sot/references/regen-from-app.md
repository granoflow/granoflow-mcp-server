# Regen Project SoT from App

Rebuild `temp/project-sot.yaml` from Granoflow Local HTTP API entities when the
file is missing, `temp/` was wiped, or the operator requests a refresh.

## Command

```bash
python3 skills/granoflow-project-sot/scripts/regen_project_sot_from_app.py \
  --project-id <uuid> \
  --repo-root <absolute-or-cwd-relative-path> \
  --force
```

Optional:

| Flag                | Meaning                                                                              |
| ------------------- | ------------------------------------------------------------------------------------ |
| `--base-url URL`    | Override `GRANOFLOW_API_BASE_URL` (default `http://127.0.0.1:56789`)                 |
| `--token TOKEN`     | Override `GRANOFLOW_API_TOKEN`                                                       |
| `--output PATH`     | Default `<repo-root>/temp/project-sot.yaml`                                          |
| `--force`           | Overwrite existing SoT                                                               |
| `--probe-workspace` | Record analyze/test pointer notes under stages when local cmds exist                 |
| `--migrate-legacy`  | Prefer fields from `temp/project-e2e-sot-v*.md` when present (still emit new schema) |

Stdout is a JSON envelope (`ok` / `code` / `path` / details). Exit `0` only when
write + structural projection succeeded.

## Inputs read from App

1. `GET /v1/projects/{id}` — title, description hints
2. `GET /v1/projects/{id}/attachments` — `logicalSlot: project_work` →
   `contentSha256` / `confirmedContentSha256` for `source_digests.project_work`
3. `GET /v1/milestones` (or list filtered by `projectId`) — milestone titles /
   status / ids
4. `GET /v1/tasks` filtered by `projectId` — task status for coarse stage /
   work_item inference

Does **not** require full Project Work YAML body. Large PW is hash-only.

## Local evidence (optional, honest)

When `--probe-workspace` or when scanning `temp/`:

| Path                                             | Effect                                                                                       |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `temp/integration-campaign/closing-summary.json` | Pointer on `integration_campaign.evidence_ref`                                               |
| `temp/e2e-campaign/**/closing-summary.json`      | Pointer on `e2e_campaign.evidence_ref`                                                       |
| Missing dirs                                     | Leave thin gates `not_applicable` / stages not greenwashed; may set `evidence_missing: true` |

Regen **never** invents screenshot files or green coverage. Missing evidence →
honest incomplete fields.

## Projection rules (coarse)

1. Project exists → stage `project_init` at least `in_progress`; with PW hash →
   prefer `done`.
2. ≥1 milestone → `milestones_created` `done`.
3. Feature milestones with all child tasks `done` → treat implement black box as
   progressed; otherwise leave implement unfinished.
4. Campaign milestone titles matching `/integration/i` or `/e2e/i` plus local
   closing-summary → mark corresponding campaign stages when evidence_ref
   non-empty.
5. `next_step`: earliest unfinished legal work_item, or `DONE` when
   `status: completed` and `project_complete` stage is `done`.
6. Always emit `doc_type: project_sot` / `schema: granoflow_project_sot_v1` and
   `bound_sot_path: temp/project-sot.yaml`.

After regen, always lint:

```bash
python3 skills/granoflow-project-sot/scripts/lint_project_sot.py \
  temp/project-sot.yaml
```

## Failure codes

| Code                       | Meaning                                          |
| -------------------------- | ------------------------------------------------ |
| `project_sot_regen_failed` | API unreachable, project missing, or write error |
| `project_sot_exists`       | Output exists and `--force` not set              |
| `project_sot_lint_failed`  | Caller must fix after regen if lint fails        |

## Explicit non-goals

- Does not run Flutter E2E inside the App
- Does not recover deleted screenshots
- Does not replace host-wake arming; continuity still owns wake protocol
