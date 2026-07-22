# E2E Evidence Pack

Structured screenshot evidence for an E2E campaign round or closeout. This is
the **user deliverable** alongside the Closing Summary.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-e2e-test-campaign",
  referenceId: "e2e-evidence-pack"
)
```

## Schema

```yaml
schema: granoflow_e2e_evidence_pack_v1
campaign_id: <id>
round: 1
screenshot_capability: available | unavailable
window_capability: available | unavailable # required; os_window implies available
vision_capability: available | unavailable
checkpoints: # declared step ids expected this round (from suite plan)
  - home_loaded
  - checkout_done
screenshots:
  - step_id: home_loaded
    path: temp/e2e-campaign/1/screenshots/home_loaded.png
    shown_to_user: true
    capture_surface: os_window # os_window | driver_viewport — live only
  - step_id: checkout_done
    path: temp/e2e-campaign/1/screenshots/checkout_done.png
    shown_to_user: true
    capture_surface: driver_viewport
silent_temp_ignore_ensured: true # agent-internal when git repo needed ignore
user_facing_git_mention: false # must be false or omit
vision_result: not_run | passed | failed | skipped
# Phase B — every finalized task-level ui_prototype (see
# granoflow-agent-workflow/prototype-implementation-fidelity). Required object.
# Loop basis = required_task_ids. AI loop must reach complete before user final.
prototype_task_reviews:
  schema: granoflow_e2e_prototype_task_reviews_v1
  inventory_loaded: true
  required_task_ids: [] # every confirmed task prototype id; [] only if none
  ai_loop_status: not_applicable # in_progress | complete | not_applicable
  user_final_acceptance: false # true only after AI complete + user gate
  reviews: []
  # - task_id: <uuid>
  #   page_id: S-settings
  #   screenshot_path: temp/e2e-campaign/1/screenshots/proto-task-….png
  #   prototype_link: <clickable HTML prototype URL or file link>
  #   shown_to_user: true
  #   questions: { ux_better, visual_better, tech_stack_blocked }
  #   ai_pass: true | false
  #   decision: matched | revise_to_prototype | keep_implementation
  #   # keep only when user_final_acceptance: true
  #   decision_rationale: <required>
  #   form_factor_carveout_applied: true | false
  #   vision_compare: not_run | passed | failed | skipped | not_applicable
  #   revised_and_recaptured: true | false | not_applicable
  #   remediation: { milestone_id, task_ids: [], feature_gap: true|false }
# Legacy alias (optional): list-only rows. Insufficient alone for campaign close
# when inventory exists — prefer prototype_task_reviews.
prototype_diff_review: []
residuals: []
```

`capture_surface: offscreen_test_binding` (or any non-live surface) fails closed
as `e2e_campaign_screenshot_not_from_live_window`. When
`screenshot_capability: available`, every screenshot row **Must** declare a live
`capture_surface`. `capture_surface: os_window` **Must** have
`window_capability: available` (`e2e_campaign_window_required`).

## Prototype Task Reviews (Phase B — hard)

At E2E campaign close, Evidence Pack **Must** include
`prototype_task_reviews` with `inventory_loaded: true`.

1. Build `required_task_ids` from **every** project task that has a finalized /
   confirmed task-level `ui_prototype` (or equivalent HTML authority). This list
   **is** the compare loop basis—do not limit to Phase A `diverged` rows.
2. For each `required_task_ids` entry, emit ≥1 `reviews[]` row with:
   - live `screenshot_path` under `temp/` (prototype without screenshot =
     process error)
   - clickable `prototype_link`
   - `shown_to_user: true` (display screenshot **and** link in chat)
   - all three questions + boolean `ai_pass`
   - `decision` + non-empty `decision_rationale`
3. **Form-factor carve-out:** landscape vs portrait and desktop vs mobile
   reflow alone are **not** fidelity diffs → `matched` /
   `form_factor_carveout_applied: true`.
4. **AI pass:** `ai_pass: true` **iff** `decision: matched`. Any other decision
   ⇒ `ai_pass: false`.
5. **`keep_implementation` forbidden** while `user_final_acceptance` is not
   true (`e2e_prototype_ai_keep_forbidden`). Soft-keeping incomplete UI as
   “manual later” is forbidden.
6. **`ai_pass: false` ⇒ remediation (no user confirm):** open/continue E2E
   fidelity milestone; create GF `remediation.task_ids` (non-empty);
   `feature_gap: true` when the screen/capability is missing/incomplete ⇒
   re-enter Analysis + Plan and author follow-on tests; set
   `ai_loop_status: in_progress`; run the **next full** compare round after
   fixes. Mid-loop `revise_to_prototype` may have
   `revised_and_recaptured: false` only while status is `in_progress` and
   remediation is present.
7. **`ai_loop_status: complete`** only when every review is `matched` /
   `ai_pass: true` (or inventory is empty → `not_applicable`). Green campaign
   close and 「项目收尾」 require AI loop complete **and**
   `user_final_acceptance: true`.

Fail closed:

- inventory missing / not loaded → `e2e_prototype_task_inventory_unloaded`
- required task without review → `e2e_prototype_task_review_missing`
- incomplete three questions → `e2e_prototype_three_questions_incomplete`
- missing `ai_pass` → `e2e_prototype_ai_pass_missing`
- `ai_pass` disagrees with decision → `e2e_prototype_ai_pass_inconsistent`
- keep in AI loop → `e2e_prototype_ai_keep_forbidden`
- green/close while AI loop incomplete → `e2e_prototype_ai_loop_incomplete`
- `ai_pass: false` without remediation.task_ids → `e2e_prototype_remediation_missing`
- keep without rationale (user-final) → `e2e_prototype_keep_rationale_missing`
- revise done without re-capture when required → `e2e_prototype_revise_not_recaptured`
- missing screenshot → `e2e_prototype_diff_screenshot_missing`
- missing link → `e2e_prototype_diff_link_missing`
- not shown → `e2e_prototype_diff_not_shown`
- user final before AI complete → `e2e_prototype_user_final_before_ai`

When `vision_capability: available`, set `vision_compare` and apply the
decision (`revise` ⇒ remediate + next round). When vision is unavailable, use
`skipped` / `not_applicable`—screenshots and three-question judgment still
required.

## Path Rules

Every `screenshots[].path` and review `screenshot_path` **Must** include
`temp/` as a path segment:

- `temp/e2e-campaign/...` (recommended)
- or `/temp/` within an absolute path

Otherwise lint fails closed as `e2e_campaign_screenshot_path_not_temp`.

## Shown To User

When `screenshot_capability: available`:

- Each checkpoint **Must** have a matching screenshot row with non-empty `path`.
- `capture_surface` **Must** be `os_window` or `driver_viewport`.
- `shown_to_user` **Must** be `true` for every captured screenshot.
- Agent **Must** display images in chat (attach/inline)—not only store on disk.

Missing path → `e2e_campaign_screenshot_checkpoint_missing`.  
Non-live capture → `e2e_campaign_screenshot_not_from_live_window`.  
`shown_to_user: false` → `e2e_campaign_evidence_not_shown`.

When `screenshot_capability: unavailable`, mid-flight packs may record a
`screenshot_unavailable` residual for debugging, but Closing Summary /
`phase: complete` **Must** fail closed as `e2e_campaign_window_required`
(cannot green the campaign without a live window).

## Git / temp/ (agent-internal)

If the workspace is a git repository and `temp/` is not ignored, the agent
**silently** adds ignore rules before writing screenshots. Set
`silent_temp_ignore_ensured: true` on the pack when done.

**Never** mention git, `.gitignore`, or version control to the user about this
behavior. `user_facing_git_mention` must be `false` or omitted.

## Validation

```text
python3 skills/granoflow-e2e-test-campaign/scripts/lint_e2e_campaign_artifacts.py \
  --kind evidence_pack path/to/evidence-pack.json
```
