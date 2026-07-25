# Durable Run Plan Template

**Superseded for project-bound long / unattended runs.**

Use the Project SoT YAML skeleton:

```text
skills/granoflow-project-sot/references/project-sot-template.yaml
```

Copy to:

```text
temp/project-sot.yaml
```

Owner: `granoflow-project-sot` / `project-sot`. Continuity mechanics:
`long-task-run-continuity.md`.

Do not create a parallel `temp/run-plan-*.md` for the same project orchestration
scope — that splits the source of truth. Legacy `temp/project-e2e-sot-v*.md` is
read-only compatibility only.
