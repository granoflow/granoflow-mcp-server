# User-Visible Copy Boundary

Apply this contract whenever Task Work includes UI, a visual Prototype, or user-visible copy. It prevents an Agent from turning internal quality requirements into product text.

## Admission Test

Every visible string must help the user answer at least one question:

1. What object or content is this?
2. What user-understandable state is it in?
3. What can the user do now?
4. What important consequence follows from the action?
5. How must the user distinguish two otherwise ambiguous valid choices?

If deleting the string does not change the user's understanding of the object, state, action, consequence, or choice, delete it by default.

Errors, permissions, destructive actions, overwrites, and recovery remain explicit about user-understandable facts and consequences. Brevity must not hide safety-critical information.

## Internal Information Stays Outside Product UI

Do not expose implementation strategy, filtering policy, confidence, internal tiers, result limits, architecture, data-source guarantees, test conclusions, acceptance language, or developer intent as ordinary product copy.

Examples that fail this gate include “only reliable results,” “up to three matches,” “high-confidence candidate,” “passed filtering,” “local database decision,” and “title and description are highly similar.” Reliability is proven by behavior and acceptance evidence, not by a UI claim.

Recommendation and candidate rows default to the object name, a necessary user-domain state or time, and the required action. A domain fact is visible only when removing it would prevent the user from distinguishing valid choices or deciding the next action. A field used internally is not automatically a user-facing reason.

## Prototype Separation

A Prototype may include scenario controls and reviewer explanations only when they are clearly marked and visually outside the simulated product UI. Review product copy and Prototype-only annotations separately.

Do not add product empty states, degradation explanations, helper labels, or quality promises merely to explain behavior to a reviewer. Follow the confirmed product visibility contract.

Before visual confirmation, inspect visible body copy, headings, badges, helper text, buttons, links, tooltips, and accessibility labels. Any internal-requirement leak returns the Prototype for revision. Validate copy through visual/copy review rather than fixed natural-language literal tests.

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
   shown)—not a green test suite.
4. Adding or executing automated tests for copy-only Scope fails closed as
   `copy_change_tests_forbidden`.

If the same task also changes behavior or non-copy surfaces, it is **not**
copy-only: apply ordinary software test policy to the non-copy delta only, and
still do not invent string-literal tests whose sole job is to lock marketing or
UI prose.
