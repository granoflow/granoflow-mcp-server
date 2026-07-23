# Engineering Acceptance Pack

Single owner for the **Project Definition Step 1 user-facing acceptance
surface**: one Markdown file (HTML preferred) that projects engineering locks
from Project Work for **browse-and-confirm**. It is **not** a second product
SoT and **not** a substitute for Design Spec / Shell selection.

## Acceptance Division Of Labor (hard)

| Deliverable                                    | Who accepts                        | Rule                                                                                        |
| ---------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------- |
| Project Work YAML + companion attachment slots | **AI self-check only**             | Structured checklist before pack emit; never present raw YAML as the user's acceptance page |
| Engineering Acceptance Pack (this file)        | **User browse-and-confirm**        | Explicit accept / revise (interactive) or valid unattended grant                            |
| Design Spec HTML / App Shell HTML              | **User selection** (when required) | Existing triad Preview Gate after `granoflow_project_work_confirm`                          |

Calling `granoflow_project_work_confirm` before interactive pack acceptance
(or valid unattended adopt) fails closed as
`engineering_acceptance_pack_unconfirmed`.

## Mandatory Load

Load via MCP before either of:

1. emitting / presenting the Engineering Acceptance Pack during Project
   Definition Step 1;
2. calling `granoflow_project_work_confirm` for a software Project Definition
   run.

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "engineering-acceptance-pack"
)
```

Use the template
`references/engineering-acceptance-pack-template.md` when creating the file.
Skipping the load fails closed as `engineering_acceptance_pack_unread`.

Also load `markdown-html-acceptance-render` for convert + Preview Gate.

## When It Applies

| Case                                             | Rule                                                                              |
| ------------------------------------------------ | --------------------------------------------------------------------------------- |
| Software Project Definition Step 1 (interactive) | **required** before `granoflow_project_work_confirm`                              |
| Software Project Definition Step 1 (unattended)  | **required** emit + link digest; auto-adopt only under valid unattended Mode Gate |
| Non-software / no engineering locks              | `not_applicable` with basis                                                       |

## Pack File

### Location And Naming

Preferred local path (repo `temp/` during authoring):

```text
temp/engineering-acceptance-<projectKey>-v<n>.md
```

Examples: `temp/engineering-acceptance-granoreader-v1.md`.

One file per Project Work confirmation version. Do not split frameworks /
directory / data / diagrams across multiple acceptance files for the same
confirm wave.

### Authority

| Layer                                                          | Authority                                                                |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Product / engineering locks, companion SHA registry            | **Project Work YAML** + App companion slots                              |
| User-facing browse surface for Step 1 engineering confirmation | **This pack** (Markdown SoT for acceptance identity; HTML is derivative) |

Rules:

1. Pack body **Must project** from filled Project Work / companions. Do not
   invent a parallel stack, dependency list, or directory tree.
2. When pack content and YAML disagree, fix YAML (or companions) first, then
   regenerate the pack. Do not “accept” chat-only engineering claims.
3. After interactive accept (or unattended adopt), record pack `status:
accepted`, path, content hash, and `html_render` into Project Work fields
   described in `project-work-document-template.md`, then call
   `granoflow_project_work_confirm`.

### Single-File Sections

The pack **Must** list every section key with `present: true|false`. When
`present: true`, the Markdown body **Must** contain the corresponding heading
and content.

| Section key            | Software rule                                     | Content                                                                                         |
| ---------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `frameworks_and_libs`  | **Must** `present: true`                          | Project from `engineering.stack` + `dependencies.approved` (or explicit none declaration)       |
| `directory_structure`  | **Must** `present: true`                          | Project from `engineering.directory_structure` + `architecture.modules` summary                 |
| `data_structures`      | true when DB / JSON / constants apply; else false | Project or link registered `data-model` / `data-contracts` / `constants-catalog`; basis if none |
| `flowcharts`           | true when authored; else false                    | Mermaid flowcharts from `workflows.md` (or init-authored flows)                                 |
| `uml_diagrams`         | true when authored; else false                    | State / sequence / class / ER when present; PlantUML optional                                   |
| `visual_baseline_plan` | **Must** `present: true`                          | `required` or `not_applicable` + basis (CLI / library / no UI chrome)                           |

Fail closed when software pack omits required `present: true` sections or
leaves `directory_structure.roots` empty in the projected source:
`directory_structure_unselected` /
`engineering_acceptance_pack_incomplete`.

## AI Self-Check (before pack emit)

Before writing or showing the pack, the Agent **Must** complete an AI-only
self-check of Project Work + companions and record
`init_ai_self_check` (see template / Project Work fields). **Do not** ask the
user to read YAML as acceptance.

Checklist (all must pass for software init):

1. `product_spec_coverage.status: ready`
2. `engineering.stack` / `stack_capability_profile` locked; capability-critical
   libraries selected or explicit `no_capability_dependency_declaration`
3. `data_persistence` set; required data companions registered or explicit
   `not_applicable` / `no_database_declaration`
4. `engineering.directory_structure.roots` non-empty; at least one
   `architecture.modules[]` entry with non-null `id` and `responsibility`
5. Pack projection would not contradict YAML / companion SHA intent
6. `visual_baseline.applicability` is `required` or `not_applicable` with basis

Any failure → `init_ai_self_check_failed` (and the more specific code when
known). Do not emit the pack or call confirm while self-check fails.

## Acceptance Interaction

Reuse the Preview Gate pattern from `markdown-html-acceptance-render.md`
(**Engineering Acceptance Preview Gate** — same clickable-link bar as Plan
Acceptance).

| Mode          | Behavior                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `interactive` | AI self-check pass → write Markdown pack → run `render_markdown_acceptance_html.py` → emit **Engineering Acceptance Link** block (clickable HTML when ready + Markdown SoT) → prefer host open → **wait** for explicit accept / revise. Missing clickable HTML when `html_render.status: ready` → `plan_acceptance_html_link_required` (shared render code). Tools missing → clickable Markdown + token-free install hint; **still wait** for confirm. |
| `unattended`  | Same convert + clickable links as non-blocking notice; ledger + closing **Engineering Acceptance Link Digest** (`engineering_acceptance_link_digest_required` if omitted). Auto-adopt only under valid unattended Mode Gate.                                                                                                                                                                                                                           |

Pack frontmatter **Must** include `html_render` per
`markdown-html-acceptance-render.md`.

### Required user-visible block (interactive)

```markdown
## 工程验收链接 · <projectKey> v<n>

请打开验收页（本地转换，不耗 token）：

- [打开 HTML 验收页](file:///…/engineering-acceptance-….html) # when ready
- [打开 Markdown](file:///…/engineering-acceptance-….md)

看完后回复「确认工程验收」或指出要改的章节。
```

Do **not** paste the full Project Work YAML into the user-facing ask.

## Relationship To Later Steps

| Concern                                     | Owner                                                                          |
| ------------------------------------------- | ------------------------------------------------------------------------------ |
| Step 1 engineering browse confirm           | **this pack**                                                                  |
| App Project Work confirmation hash          | `granoflow_project_work_confirm` after pack accepted / adopted                 |
| Design Spec / Shell user selection          | `project-artifact-workflows.md` when `visual_baseline.applicability: required` |
| Directory ownership during later code edits | Confirmed `directory_structure` + `software-structural-budget.md`              |

When `visual_baseline.applicability: not_applicable`, skip Spec / Shell /
`widgets.yaml` for initialization Done.

## Fail-Closed Codes

| Code                                          | When                                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------------------- |
| `engineering_acceptance_pack_unread`          | Reference not loaded                                                                  |
| `engineering_acceptance_pack_missing`         | Software Step 1 confirm / Done without an emitted pack                                |
| `engineering_acceptance_pack_incomplete`      | Required section `present: true` missing body, or required frontmatter absent         |
| `engineering_acceptance_pack_unconfirmed`     | `granoflow_project_work_confirm` without interactive accept or valid unattended adopt |
| `engineering_acceptance_pack_drift`           | Pack content contradicts Project Work / companions without regenerate                 |
| `engineering_acceptance_link_digest_required` | Unattended run omitted closing link digest                                            |
| `directory_structure_unselected`              | Software init with empty `directory_structure.roots` or no valid module row           |
| `init_ai_self_check_failed`                   | Self-check incomplete or failed before pack emit                                      |
| `visual_baseline_applicability_unresolved`    | Neither `required` nor `not_applicable` recorded with basis                           |
| `plan_acceptance_html_link_required`          | HTML ready but no clickable/open HTML link before acceptance ask (shared render gate) |

## Admission Test

1. Was this reference loaded via MCP?
2. Did AI self-check pass and get recorded before pack emit?
3. Is there exactly one pack Markdown for this confirm version?
4. Are all section keys listed with `present`, and are
   `frameworks_and_libs`, `directory_structure`, and `visual_baseline_plan`
   `present: true` for software?
5. Was `render_markdown_acceptance_html.py` run, and does frontmatter
   `html_render` record paths / file URLs / `link_emitted`?
6. Interactive: did the user get a clickable HTML (when ready) or Markdown
   link **before** the acceptance question, and did we wait?
7. Was `granoflow_project_work_confirm` called only after pack
   `status: accepted` (or valid unattended adopt)?
