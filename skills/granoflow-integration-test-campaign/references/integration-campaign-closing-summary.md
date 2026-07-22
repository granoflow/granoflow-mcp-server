# Integration Campaign Closing Summary

Mandatory **user-facing** closing digest when an integration-test campaign
reaches `phase: complete` (or stops with only external residuals). The durable
record **Must** stay beginner-readable even if the live chat is concise.

## Mandatory Load

Before writing or showing the closing summary:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-integration-test-campaign",
  referenceId: "integration-campaign-closing-summary"
)
granoflow_bundled_skill_reference(
  skillId: "granoflow-integration-test-campaign",
  referenceId: "integration-campaign-closing-summary-template"
)
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "workflow-jargon-plain-language"
)
```

Also load Acceptance Outcomes:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "acceptance-outcome-contract"
)
```

Also follow `project-interaction-style.md`: durable records are
`beginner_detailed`. Skipping the loads and dumping bare workflow tokens fails
closed as `integration_campaign_closing_summary_not_plain` /
`workflow_jargon_unexplained`.

## Why This Exists

Personal developers are often **not** full-time QA/engineers. The closing
summary answers, in everyday language:

1. Did the app pass the module-collaboration checks?
2. What flows were exercised (service/data path—not UI clicks)?
3. If something was fixed—what will **feel** different for the user?
4. Is anything still unfinished (and is that OK)?
5. What can I say next? (usually「开始 E2E 战役」, not project closeout)

Machine paths, fail-closed codes, and file lists belong under **给开发者看的细节**,
never as the only explanation.

## Hard Output Rules (non-programmer first)

1. **Lead with plain language.** `plain.*` fields and the six user sections in
   `markdown_body` are the primary surface. English workflow tokens may appear
   once in parentheses after a gloss—not alone.
2. **Describe user-visible impact, not filenames.**  
   Bad: `lib/comments/delete.dart`  
   Good: `删除评论前会多一步确认，避免误删。`
3. **Explain leftovers in human terms.** If residuals exist, `plain.leftovers`
   must say what is unfinished and whether the user must act (e.g. 需要你提供
   登录验证码). Never claim「没有未完成事项」while residuals remain.
4. **Always give a next phrase.** `plain.next_step` suggests what the user can
   reply (e.g. 「项目收尾」).
5. **Audience is beginner** on the durable record (`audience: beginner`),
   regardless of interactive/unattended mode.
6. Chat may show a short digest, but **Must** still attach/upload the full
   closing summary artifact before claiming campaign complete.

## Required Artifact

Schema: `granoflow_integration_campaign_closing_summary_v1`  
Copy structure from `integration-campaign-closing-summary-template.md`.

Required `plain` keys (everyday language; zh locale must use Chinese):

| Key                    | Meaning                                   |
| ---------------------- | ----------------------------------------- |
| `headline`             | One-sentence outcome                      |
| `what_we_checked`      | What integration flows were exercised     |
| `result`               | Pass / pass-with-leftovers in plain words |
| `what_changed_for_you` | User-visible difference, or “对你没变化…” |
| `leftovers`            | Unfinished items or “没有未完成事项”      |
| `next_step`            | Usually 「开始 E2E 战役」                 |

Required `markdown_body` headings (exact Chinese titles):

1. `一句话结论`
2. `这次查了什么`
3. `结果如何`
4. `对你有什么影响`
5. `还剩什么没做完`
6. `下一步你可以做什么`

Optional seventh heading for engineers: `给开发者看的细节` (paths, commands,
change report). Lint does not require this heading; humans may omit it when
`code_changed: false` and there is nothing useful.

When `code_changed: true`, embed `change_report` or set `change_report_ref`.
Missing either fails closed as `integration_campaign_change_report_missing`.

### Acceptance Outcomes (required)

Closing Summary **Must** repeat the AO matrix (`acceptance_outcomes_loaded`,
`acceptance_outcomes`, `user_path_claim: service_layers_only`). Rules:

- `plain.what_we_checked` may only describe AOs with `status: closed`.
- Any `deferred_e2e` / `residual` AO forces `outcome: green_with_residuals`
  (or `blocked_external`) and honest `plain.leftovers`—never bare `green`.
- Do not imply the full UI / secure-session user journey finished at IT.

## Validation

```text
python3 skills/granoflow-integration-test-campaign/scripts/lint_integration_campaign_artifacts.py \
  --kind closing_summary --campaign-complete path/to/closing-summary.json
```

Fail-closed codes:

- `integration_campaign_closing_summary_missing`
- `integration_campaign_closing_summary_incomplete`
- `integration_campaign_closing_summary_not_plain`
- `integration_campaign_closing_summary_residual_unexplained`
- `integration_campaign_change_report_missing`
- `acceptance_outcomes_unloaded`
- `acceptance_outcomes_incomplete`
- `acceptance_outcome_layer_overclaim`
- `acceptance_outcome_test_double_claim`
- `acceptance_outcome_overclaim_green`
- `acceptance_outcome_user_path_overclaim`

## Relationship

| Concern                  | Owner                                |
| ------------------------ | ------------------------------------ |
| Structured edit ledger   | change report (may be embedded)      |
| Stage strip              | `project-lifecycle-progress-board`   |
| Chat jargon gloss        | `workflow-jargon-plain-language`     |
| Suite order / human path | `integration-suite-orchestration`    |
| Campaign loop            | `integration-test-campaign-contract` |
