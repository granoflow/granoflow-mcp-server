# E2E Campaign Closing Summary

Mandatory **user-facing** closing digest when an E2E campaign reaches
`phase: complete` (or stops with only external residuals). Screenshots are part
of the story—not an engineer-only artifact.

## Mandatory Load

Before writing or showing the closing summary:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-e2e-test-campaign",
  referenceId: "e2e-campaign-closing-summary"
)
granoflow_bundled_skill_reference(
  skillId: "granoflow-e2e-test-campaign",
  referenceId: "e2e-campaign-closing-summary-template"
)
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "workflow-jargon-plain-language"
)
```

Also follow `project-interaction-style.md`: durable records are
`beginner_detailed`.

## Hard Output Rules

1. **Lead with plain language.** `plain.*` and user sections in `markdown_body`
   are primary. Workflow tokens may appear once in parentheses after a gloss.
2. **Screenshots for humans.** When `screenshot_capability: available`, include
   section 「关键步骤截图」 in `markdown_body` and fill `plain.screenshots_note`.
   When Evidence Pack `prototype_task_reviews.required_task_ids` is non-empty,
   also include 「原型对照」 listing **every** required prototype: clickable
   link + live screenshot + AI three-question pass/fail. Closing without that
   full loop is forbidden. Screenshots **Must** come from a live visible window.
   If `screenshot_capability: unavailable`, do **not** close as `green` /
   `green_with_residuals`—fail closed as `e2e_campaign_window_required`.
3. **AI loop before user final.** Embedded `prototype_task_reviews` **Must**
   have `ai_loop_status: complete` (or `not_applicable` when inventory empty)
   before suggesting 「项目收尾」. While AI loop is complete but
   `user_final_acceptance` is false, `plain.next_step` **Must** ask for user
   prototype acceptance—not project close
   (`e2e_campaign_closing_summary_ai_loop`).
4. **Never mention git** to the user about temp/ or ignore rules.
5. **Embed or reference evidence pack** (`evidence_pack` or `evidence_pack_ref`).
6. **`plain.next_step`** may suggest 「项目收尾」 only after
   `user_final_acceptance: true`.
7. **Manual-test leftovers.** When any residual uses
   `e2e_campaign_manual_test_required` / `e2e_campaign_automation_too_hard`
   (or short aliases), `outcome` **Must** be `green_with_residuals` (or
   `blocked_external`), each residual **Must** name `feature`, and
   `plain.leftovers` **Must** explicitly ask the user to **手工/手动** test
   that named feature. Silent skips are forbidden. Do **not** use manual
   leftovers to waive Phase B AI fails—those go through remediation + next
   round.

## Required Artifact

Schema: `granoflow_e2e_campaign_closing_summary_v1`  
Copy structure from `e2e-campaign-closing-summary-template.md`.

Required `plain` keys (zh locale must use Chinese):

| Key                    | Meaning                                      |
| ---------------------- | -------------------------------------------- |
| `headline`             | One-sentence outcome                         |
| `what_we_checked`      | UI flows exercised in everyday words         |
| `result`               | Pass / pass-with-leftovers                   |
| `what_changed_for_you` | User-visible difference                      |
| `leftovers`            | Unfinished items or 「没有未完成事项」       |
| `next_step`            | 用户终验邀请；「项目收尾」仅在 user_final 后 |

Required `markdown_body` headings when `screenshot_capability: available`:

1. `一句话结论`
2. `这次查了什么`
3. `结果如何`
4. `对你有什么影响`
5. `关键步骤截图`
6. `还剩什么没做完`
7. `下一步你可以做什么`

When `prototype_task_reviews.required_task_ids` is non-empty,
`markdown_body` **Must** also contain heading `原型对照` (as section or under
screenshots).

When `screenshot_capability: unavailable`, do **not** omit 「关键步骤截图」 to
claim a green close—the campaign **Must** fail closed as
`e2e_campaign_window_required` (residuals cannot waive).

When `code_changed: true`, embed `change_report` or set `change_report_ref`.

## Validation

```text
python3 skills/granoflow-e2e-test-campaign/scripts/lint_e2e_campaign_artifacts.py \
  --kind closing_summary --campaign-complete path/to/closing-summary.json
```

Fail-closed codes include:

- `e2e_campaign_closing_summary_missing`
- `e2e_campaign_closing_summary_incomplete`
- `e2e_campaign_closing_summary_not_plain`
- `e2e_campaign_closing_summary_screenshots_missing`
- `e2e_campaign_closing_summary_residual_unexplained`
- `e2e_campaign_closing_summary_ai_loop`
- `e2e_campaign_manual_test_reminder_missing`
- `e2e_campaign_change_report_missing`
- `e2e_campaign_window_required`
- `e2e_prototype_ai_loop_incomplete`
- `e2e_prototype_ai_keep_forbidden`
- `e2e_prototype_user_final_before_ai`
- `e2e_campaign_headless_ui_forbidden`
- `e2e_campaign_screenshot_not_from_live_window`
