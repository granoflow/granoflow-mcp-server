# User-Visible Copy Boundary

Apply this contract whenever Task Work includes UI, a visual Prototype, or
user-visible copy. It prevents an Agent from turning internal quality
requirements, filtering policy, or design rationale into product text.

**Plan-phase locale:** design and show only the selected product locale
(user-explicit language, else the language of the user↔AI conversation).
Other locales are Execution work. See `milestone-plan-acceptance-pack.md`.

## Mandatory Load (fail closed if skipped)

Before authoring or revising any user-visible string in:

- a Task `ui_prototype` / Contrast Gallery frame;
- product UI copy in Scope, Plan, or Delivery;
- empty / error / success / helper microcopy;

the host **Must** load this reference via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "user-visible-copy-boundary"
)
```

Skipping the load and shipping product UI fails closed as
`user_visible_copy_boundary_unread`.

Seeing `SKILL.md` alone does **not** count as loading this contract.

## Admission Test

Every visible string **inside the simulated product UI** must help the user
answer at least one question:

1. What object or content is this?
2. What user-understandable state is it in?
3. What can the user do now?
4. What important consequence follows from the action?
5. How must the user distinguish two otherwise ambiguous valid choices?

If deleting the string does not change the user's understanding of the object,
state, action, consequence, or choice, delete it by default.

Errors, permissions, destructive actions, overwrites, and recovery remain
explicit about user-understandable facts and consequences. Brevity must not
hide safety-critical information.

## Internal Information Stays Outside Product UI

Do not expose implementation strategy, filtering policy, confidence, internal
tiers, result limits, architecture, data-source guarantees, test conclusions,
acceptance language, developer intent, or **design rationale** as ordinary
product copy.

**Design rationale** means any sentence whose audience is the reviewer/agent
(why we chose a layout, what we omit, how the pipeline works) rather than the
end user acting in the product.

Examples that fail this gate (`user_visible_copy_boundary_violation`):

| Leak class                | Bad product copy (examples)                                              |
| ------------------------- | ------------------------------------------------------------------------ |
| Filtering / scan policy   | “0 本的类型不显示”; “仅按后缀统计”; “不在导入前计算 MD5”                 |
| Reviewer pedagogy         | “本批不会在确认页列出文件名”; “便于排查”; “两组分栏查看·不混在同一列表”  |
| Confidence / quality      | “only reliable results”; “high-confidence candidate”; “passed filtering” |
| Architecture / acceptance | “local database decision”; “up to three matches”; “验收 A6 通过”         |
| Design thesis in-frame    | “hierarchy：续读置顶”; “expr_a vs expr_b 差异轴”                         |

Reliability and craft are proven by behavior and acceptance evidence, not by a
UI claim.

Recommendation and candidate rows default to the object name, a necessary
user-domain state or time, and the required action. A domain fact is visible
only when removing it would prevent the user from distinguishing valid choices
or deciding the next action. A field used internally is not automatically a
user-facing reason.

## Prototype Separation

A Prototype may include scenario controls and reviewer explanations **only**
when they are clearly marked and visually **outside** the simulated product UI
(e.g. gallery thesis above the phone, captions beside iframes, elements with
`data-reviewer-only`).

Inside product chrome (`.phone`, `[data-product-ui]`, device frames, or—when
no frame is marked—the whole `body`):

- no design rationale;
- no craft/contrast-axis narration;
- no “we don’t show X because…” policy notes.

Review product copy and Prototype-only annotations separately.

Do not add product empty states, degradation explanations, helper labels, or
quality promises merely to explain behavior to a reviewer. Follow the confirmed
product visibility contract.

## Craft Gate Hook (hard)

For every UI prototype option, `prototype_option_set.craft_checklist` Must
include:

```yaml
user_visible_copy_boundary_ok: true
```

Set it to `true` only after **all** of:

1. This reference was loaded via `granoflow_bundled_skill_reference`.
2. Every in-frame string passed the Admission Test.
3. Host ran
   `skills/granoflow-agent-workflow/scripts/lint_prototype_user_copy.py`
   on each option HTML (or packaged source) and got `ok: true`.

Otherwise keep `user_visible_copy_boundary_ok: false`, keep
`craft_status: incomplete`, and fail closed
`task_prototype_craft_incomplete` /
`user_visible_copy_boundary_violation` before `visualConfirmed=true`.

Interactive confirm surfaces Must not ask the user to “confirm craft” while
this checklist item is false.

## Pre-Confirm Inspection

Before visual confirmation, inspect visible body copy, headings, badges,
helper text, buttons, links, tooltips, and accessibility labels **inside**
product UI. Any internal-requirement leak returns the Prototype for revision.

Validate copy through visual/copy review plus the lint script—not through fixed
natural-language literal unit tests of marketing prose.

## Copy-Only Work: No Automated Tests

User-visible copy changes and **文字验证 / copy verification** are frequent and
must stay lightweight.

When a task's authorized Scope is **copy-only** (string/copy/i18n text changes
and review, with no behavior, layout structure, navigation, API, schema, or
state-logic change):

1. Set `copy_change_only: true` (and keep
   `unit_test_sufficiency` / `integration_test_requirement` /
   `integration_test_execution` as `not_applicable`).
2. **Do not** add, require, or run unit tests, integration tests, widget tests,
   snapshot/golden tests, e2e, or any other automated test for that copy work.
3. Evidence is visual/copy review (and Prototype copy admission when UI is
   shown)—not a green test suite. Still run
   `lint_prototype_user_copy.py` when a Prototype is shown.
4. Adding or executing automated tests for copy-only Scope fails closed as
   `copy_change_tests_forbidden`.

If the same task also changes behavior or non-copy surfaces, it is **not**
copy-only: apply ordinary software test policy to the non-copy delta only, and
still do not invent string-literal tests whose sole job is to lock marketing or
UI prose.
