# Project E2E SoT — migrated

**Deprecated name.** The orchestration SoT is now **Project SoT**.

Canonical skill and path:

```text
temp/project-sot.yaml
```

```text
granoflow_project_sot_skill
granoflow_bundled_skill_reference(
  skillId: "granoflow-project-sot",
  referenceId: "project-sot"
)
```

Lint / regen:

```text
python3 skills/granoflow-project-sot/scripts/lint_project_sot.py temp/project-sot.yaml
python3 skills/granoflow-project-sot/scripts/regen_project_sot_from_app.py \
  --project-id <uuid> --repo-root <path> --force
```

Legacy `temp/project-e2e-sot-v*.md` is read-only compatibility. New writes must
use `temp/project-sot.yaml` (`doc_type: project_sot`).

Do not treat this stub as contract SoT. Load `granoflow-project-sot` /
`project-sot` before long or unattended runs.
