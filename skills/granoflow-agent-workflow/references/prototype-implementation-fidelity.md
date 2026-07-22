# Prototype Implementation Fidelity

Single owner for comparing a task's **current implementation design** to its
confirmed HTML `ui_prototype` **before unit tests**, recording divergences, and
requiring **task-complete** E2E visual review (screenshot + prototype link +
three-question decision) for every finalized task-level prototype—no omissions.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-implementation-fidelity"
)
```

Seeing `SKILL.md` alone does **not** count. Skipping the load when the gate
applies fails closed as `prototype_impl_compare_unread`.

## When It Applies

Applies when the task has a required / ready `ui_prototype` (or an equivalent
confirmed HTML prototype reference used as the implementation authority for a
UI change).

`not_applicable` when:

- `prototype_requirement: not_required`; or
- the task has no UI / no prototype authority.

## Phase A — Implement (before unit tests)

After code for the UI change is authored (or substantially updated) and
**before** running unit tests:

1. Compare implementation to the HTML prototype by **code reading / design
   inference** (`method: code_review_guess` only).
2. **Do not** use screenshots, vision OCR, integration captures, or image
   diffs for this phase (`prototype_impl_compare_wrong_method`).
3. Answer **all three** fidelity questions (even when `matched`) and emit an
   **explicit declaration** (non-question notice) with status, answers,
   decision, and rationale.
4. Persist the ledger on Task Work / run evidence:

```yaml
prototype_impl_compare:
  status: not_applicable | matched | diverged
  method: code_review_guess # only; never screenshot/vision
  declaration_emitted: true | false
  questions:
    # Required whenever status is matched or diverged
    ux_better: true | false | unknown
    visual_better: true | false | unknown
    tech_stack_blocked: true | false | unknown
  decision: keep_implementation | revise_to_prototype | not_applicable
  # matched ⇒ keep_implementation; diverged ⇒ keep or revise (task-local keep OK)
  decision_rationale: <plain-language why>
  diffs: [] # required when diverged: [{ page_id, summary, prototype_ref, impl_ref }]
```

### Form-factor carve-out (not a fidelity diff)

Prototypes usually show **one** screen shape (e.g. one phone portrait frame).
Do **not** treat the following as prototype/implementation differences:

- landscape vs portrait (横屏 / 竖屏)
- desktop vs mobile (or other form-factor) layout reflow that is expected for
  the target host

Judge fidelity only on content, hierarchy, chrome intent, and interaction that
remain after ignoring those adaptations. If the only visible gap is form-factor
/ orientation adaptation → status `matched` (not `diverged`).

### Three questions (required when matched or diverged)

Answer all three without waiting for the user:

1. **ux_better** — Is the current implementation UX better than the prototype?
2. **visual_better** — Is the current visual result better?
3. **tech_stack_blocked** — Can the current stack not achieve the prototype
   effect with acceptable fidelity?

Then choose `keep_implementation` or `revise_to_prototype` from those answers
and apply the decision (revise **code** when deciding to match the prototype).
Task-local `keep_implementation` remains allowed when the three answers support
it and rationale is non-empty. This is **distinct** from E2E Phase B AI loop,
where `keep` is forbidden until user final acceptance.

Human intervention is **not** required for Phase A, but the declaration **is**.

### Fail-closed (Phase A)

| Code                                                | When                                                        |
| --------------------------------------------------- | ----------------------------------------------------------- |
| `prototype_impl_compare_unread`                     | Gate applies; reference not loaded                          |
| `prototype_impl_compare_undeclared`                 | `declaration_emitted` is not true when applicable           |
| `prototype_impl_compare_three_questions_incomplete` | Questions missing when matched/diverged                     |
| `prototype_diff_ledger_incomplete`                  | `diverged` but `diffs` empty or missing page_id             |
| `prototype_impl_compare_lint_failed`                | lint script structural failure                              |
| `prototype_impl_compare_wrong_method`               | method is not `code_review_guess` (incl. screenshot/vision) |

## Phase B — E2E campaign (every finalized task prototype)

Phase B is **not** limited to Phase A `diverged` rows. At E2E campaign time the
agent **Must** treat **every finalized / confirmed** task-level prototype as the
**loop basis** (not optional sampling).

### Hard loop (agent_auto — no user confirm mid-loop)

1. **Inventory** every project task that has a finalized / confirmed task-level
   `ui_prototype` (or equivalent HTML authority). Sources: Granoflow task list +
   `ui_prototype` attachments / prototype import readbacks / Delivery
   `prototype_inputs`. Empty inventory is allowed only when truly none exist—
   and must still be declared (`required_task_ids: []`).
2. For **each** inventoried `task_id`, emit a **user-visible compare row** that
   **Must** include all of:
   - clickable `prototype_link` (opens in embedded or external browser)
   - corresponding live-window `screenshot_path` under `temp/`
   - three-question answers + `ai_pass` + `decision`
     Missing screenshot while a prototype exists is a **process error**
     (`e2e_prototype_diff_screenshot_missing`)—do not proceed to user final
     acceptance.
3. Apply the **form-factor carve-out**; then answer the three questions. Set:
   - `decision: matched` and `ai_pass: true` only when remaining gaps are none
     (including form-factor-only → matched).
   - `decision: revise_to_prototype` and `ai_pass: false` when UX/visual still
     better in the prototype, or when the screen/feature is **missing /
     incomplete**.
4. **`keep_implementation` is forbidden in the AI loop**
   (`e2e_prototype_ai_keep_forbidden`). Do not soft-pass incomplete UI as
   “manual later”. Keep is allowed **only** after
   `user_final_acceptance: true` (user explicitly retains a material diff).
5. If **any** row has `ai_pass: false` after a round:
   - Do **not** ask the user whether to fix.
   - Open / continue an **E2E fidelity fix milestone**.
   - Create GF task(s) for the gap(s). **Feature missing / incomplete** **Must**
     re-enter task Analysis + Plan per
     `task-analysis-profile-software-development` /
     `task-delivery-profile-software-development`, and author follow-on tests
     per those rules.
   - Set `ai_loop_status: in_progress` + per-row `remediation` refs
     (`milestone_id`, `task_ids`).
   - After fixes, run the **next E2E campaign round** and repeat the **full**
     inventory compare loop (every required prototype again).
6. Repeat until **every** row is `matched` / `ai_pass: true` → set
   `ai_loop_status: complete`.
7. **Only then** enter **user final acceptance**: show the full compare loop
   (link + screenshot + AI pass) and ask for user opinion. Do **not** suggest
   「项目收尾」 until the user accepts (or explicitly keeps a diff under
   `user_final_acceptance`).

```yaml
prototype_task_reviews:
  schema: granoflow_e2e_prototype_task_reviews_v1
  inventory_loaded: true
  required_task_ids: [<uuid>, ...] # may be []; this list IS the loop basis
  ai_loop_status: in_progress | complete | not_applicable # [] inventory → not_applicable
  user_final_acceptance: false # true only after AI loop complete + user gate
  reviews:
    - task_id: <uuid> # Must be in required_task_ids
      page_id: <screen or primary page>
      screenshot_path: temp/e2e-campaign/<round>/screenshots/proto-task-<task_id>-<page_id>.png
      prototype_link: <clickable HTML prototype URL or file link>
      shown_to_user: true
      questions:
        ux_better: true | false | unknown
        visual_better: true | false | unknown
        tech_stack_blocked: true | false | unknown
      ai_pass: true | false # true iff decision=matched under AI loop rules
      decision: matched | revise_to_prototype | keep_implementation
      # keep_implementation only when user_final_acceptance: true
      decision_rationale: <plain-language; required>
      form_factor_carveout_applied: true | false
      vision_compare: not_run | passed | failed | skipped | not_applicable
      revised_and_recaptured: true | false | not_applicable
      remediation: # required when ai_pass=false
        milestone_id: <uuid or null>
        task_ids: [<uuid>, ...] # non-empty when ai_pass=false
        feature_gap: true | false # true ⇒ Analysis+Plan re-entry required
```

Rules:

- **No silent skip.** Omitting a `required_task_ids` entry from `reviews` fails
  closed as `e2e_prototype_task_review_missing`.
- **Inventory must be loaded.** Missing
  `prototype_task_reviews.inventory_loaded: true` fails closed as
  `e2e_prototype_task_inventory_unloaded`.
- Phase A `matched` does **not** waive Phase B—still capture, show, and judge.
- Form-factor / orientation-only gaps → `decision: matched`, never keep.
- `ai_loop_status: complete` requires every review `ai_pass: true` and
  `decision: matched`. Campaign green / 「项目收尾」 requires AI loop complete
  **and** user final acceptance.

### Fail-closed (Phase B)

| Code                                       | When                                                                |
| ------------------------------------------ | ------------------------------------------------------------------- |
| `e2e_prototype_task_inventory_unloaded`    | Evidence pack lacks loaded task-prototype inventory                 |
| `e2e_prototype_task_review_missing`        | A `required_task_ids` entry has no review row                       |
| `e2e_prototype_three_questions_incomplete` | Review lacks all three question answers                             |
| `e2e_prototype_ai_pass_missing`            | Review lacks boolean `ai_pass`                                      |
| `e2e_prototype_ai_pass_inconsistent`       | `ai_pass` disagrees with `decision` under AI-loop rules             |
| `e2e_prototype_ai_keep_forbidden`          | `keep_implementation` while `user_final_acceptance` is not true     |
| `e2e_prototype_ai_loop_incomplete`         | Close/green while any `ai_pass: false` or status not `complete`     |
| `e2e_prototype_remediation_missing`        | `ai_pass: false` without non-empty `remediation.task_ids`           |
| `e2e_prototype_keep_rationale_missing`     | `keep_implementation` (user-final only) without rationale           |
| `e2e_prototype_revise_not_recaptured`      | Claiming done revise without `revised_and_recaptured` when required |
| `e2e_prototype_diff_screenshot_missing`    | Review lacks `screenshot_path` under `temp/`                        |
| `e2e_prototype_diff_link_missing`          | Review lacks non-empty `prototype_link`                             |
| `e2e_prototype_diff_not_shown`             | `shown_to_user` is not true                                         |
| `e2e_prototype_user_final_before_ai`       | `user_final_acceptance: true` while AI loop not complete            |
| `e2e_campaign_closing_summary_ai_loop`     | Closing suggests 「项目收尾」 before user final acceptance          |

## Lint

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_implementation_fidelity.py \
  path/to/compare-ledger.yaml

python3 skills/granoflow-e2e-test-campaign/scripts/lint_e2e_campaign_artifacts.py \
  --kind evidence_pack path/to/evidence-pack.json
```

## MCP Thin Boundary

Agents capture/show screenshots using host tools. The MCP server remains thin
and does not embed screenshot or vision orchestration as Local HTTP API
business logic.
