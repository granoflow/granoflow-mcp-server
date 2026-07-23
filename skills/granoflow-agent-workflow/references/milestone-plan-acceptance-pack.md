# Milestone Plan Acceptance Pack

Single owner for the **milestone-level Plan closeout artifact**: one Markdown
file that aggregates Plan-phase design products for user acceptance before the
milestone leaves Planning.

Per-task Plan Design Gate content remains in each Task Work Plan
(`plan-design-gate.md`). This pack is the **user-facing acceptance surface** at
the end of a milestone's Plan phase.

## Mandatory Load

Load via MCP before either of:

1. closing a milestone Plan phase (batch Gate confirm / “Plan 环节结束”);
2. starting **Execution** for any in-scope task of that milestone (first code /
   test / build edit, or Delivery that claims Plan outcomes).

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "milestone-plan-acceptance-pack"
)
```

Use the template
`references/milestone-plan-acceptance-pack-template.md` when creating the file.
Skipping the load fails closed as `milestone_plan_acceptance_pack_unread`.

## When It Applies

| Case                                                                                                | Rule                                                                          |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Software milestone finishing Plan Design Gate batch (interactive or unattended)                     | **required**                                                                  |
| Milestone has zero Plan-phase artifacts (no UI copy, no schema change, no diagrams, no test tables) | Still emit a pack with every section marked `present: false` + one-line basis |
| Non-software / no Planning milestone                                                                | `not_applicable`                                                              |

## Copy Language (Plan phase) — hard

When any in-scope task introduces or changes **user-visible copy** (UI strings,
empty/error/success microcopy, a11y labels that users hear/see):

1. **Design that copy in Plan** (not deferred to “whatever the prototype had”).
2. **Locale selection:**
   - If the user **explicitly specified** a product/UI language (or locale) for
     copy → use that locale only in Plan.
   - Else → use the **language of the current user↔AI conversation** as the
     Plan locale (e.g. Chinese chat → `zh-Hans` product copy in the pack).
3. **Multilingual products:** Plan designs and shows **only** the selected
   locale. Other locales are authored in **Execution / development**, not in
   the Plan acceptance pack.
4. Copy still obeys `user-visible-copy-boundary.md` (no reviewer jargon inside
   product strings).

Fail closed:

- `plan_copy_locale_unresolved` — UI copy required but neither explicit locale
  nor conversation language was recorded
- `plan_copy_missing` — UI/user-visible strings are in Scope but Plan has no
  copy inventory for the selected locale
- `plan_copy_extra_locale` — Plan pack includes non-selected locales as if they
  were Plan deliverables

Record in pack frontmatter:

```yaml
copy_locale: zh-Hans # BCP 47 or project id
copy_locale_source: user_explicit | conversation_language
```

## Pack File

### Location And Naming

Preferred local path (repo `temp/` during authoring; promote/write back per
discussion writeback when App slots exist):

```text
temp/milestone-plan-acceptance-<milestoneKey>-v<n>.md
```

Examples: `temp/milestone-plan-acceptance-M1-v1.md`.

One file per milestone Plan closeout version. Do not split copy / schema /
diagrams / tests across multiple acceptance files for the same closeout.

### Single-File Sections (include only what exists)

The pack **May** omit a body section when `present: false` in frontmatter, but
**Must** list every section key with `present: true|false`. When `present:
true`, the Markdown body **Must** contain the corresponding heading and content.

| Section key       | Heading (localize)   | Content                                                             |
| ----------------- | -------------------- | ------------------------------------------------------------------- |
| `user_copy`       | 用户文案 / User copy | Strings for `copy_locale` only; keyed by screen/task/state          |
| `data_structures` | 表结构 / 数据结构    | Tables, JSON shapes, ER/field lists this Plan introduces or extends |
| `flowcharts`      | 流程图               | Mermaid `flowchart` (and only flowcharts) aggregated from tasks     |
| `uml_diagrams`    | UML 图               | State / sequence / class / ER sketches that were authored in Plan   |
| `test_cases`      | 测试用例             | Aggregated verification tables (or links + inlined tables)          |

Rules:

1. **Do not invent** empty decorative sections. If nothing exists, `present:
false` + basis (e.g. `no_user_visible_copy_in_milestone_plan`).
2. **Do not hide** real artifacts in chat-only form; anything used to claim Gate
   completeness for the milestone must appear in this file when present.
3. Task Work Plans remain authoritative for per-task detail; the pack may
   **inline or excerpt** tables/diagrams and cite `task_id` / Plan path.
4. Flowcharts vs UML: Operation Flow Mermaid → `flowcharts`; state/sequence/
   class/ER → `uml_diagrams`. Do not double-count.

## Acceptance Interaction

Load `markdown-html-acceptance-render` and apply its **Plan Acceptance Preview
Gate** (clickable links are mandatory).

| Mode          | Behavior                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interactive` | Write Markdown SoT → run `render_markdown_acceptance_html.py` → emit **Plan Acceptance Link** block with clickable `file://` HTML (when ready) plus Markdown SoT link → prefer host open (`open_resource` / equivalent) → **wait** for explicit pack accept/revise. Missing clickable HTML when `html_render.status: ready` → `plan_acceptance_html_link_required`. Tools missing → clickable Markdown + token-free install hint every time. |
| `unattended`  | Same convert + clickable links as non-blocking notice; ledger + closing **Plan Acceptance Link Digest** (`plan_acceptance_link_digest_required` if omitted). Auto-adopt only under a valid unattended Planning grant (`unattended-interaction-contract.md`).                                                                                                                                                                                 |

The acceptance sequence is fixed: create the pack candidate with
`ai_decomposition_review_ref` and `ai_decomposition_plan_sha256` → run
`grill-finalizer` → persist the temporary candidate → run `grill-me` → accept
the same digest → promote and read back the App hash.

Interactive `grill-me` asks one question at a time and waits; record
`grill_me_status: shared_understanding_confirmed` and
`final_acceptance_status: user_accepted`. Unattended `grill-me` still states
each question, recommendation, and reason one at a time, then auto-adopts the
recommendation; record `grill_me_status: recommendations_auto_adopted`,
`final_acceptance_status: unattended_auto_adopted`, and
`accepted_by: unattended_grant`. Never present unattended adoption as user
acceptance. In both modes `authorization_effect: none`.

Pack frontmatter **Must** include `html_render` (with `html_file_url` /
`markdown_file_url` / `link_emitted`) per `markdown-html-acceptance-render.md`.

Setting every in-scope task `plan_design_gate_status: passed` without emitting /
accepting this pack (interactive) fails closed as
`milestone_plan_acceptance_pack_missing`.

## Relationship To Plan Design Gate

| Concern                                                                                 | Owner                                                                                 |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Per-task minimal Plan package (TC table, flow, disposition, libs, forecast, UI binding) | `plan-design-gate.md`                                                                 |
| Plan-phase copy locale + milestone acceptance surface                                   | **this file**                                                                         |
| Product-doc writeback of accepted copy                                                  | `prototype-product-truth-writeback` / discussion writeback when product truth changes |

Per-task Gate `passed` for all children is **necessary but not sufficient** to
leave milestone Planning: the acceptance pack must be shown (and interactively
accepted).

For UI milestones, load `responsive-prototype-finalization`. The pack records
the current Project platform matrix digest and every in-scope task's accepted
responsive Prototype Bundle digest plus required layout families. Missing or
stale Bundle coverage blocks pack acceptance.

## Implementation And Delivery Reference — hard

After a milestone Plan pack is accepted (interactive) or validly auto-adopted
(unattended), that pack is the **primary milestone-level alignment reference**
for Execution and Delivery of in-scope tasks.

| Layer                                                                                   | Authority                                                    |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Milestone alignment (accepted copy locale, schema intent, flows, UML, TC inventory)     | **Acceptance pack** (`status: accepted` or unattended grant) |
| Per-task Execution Plan steps, Structural Change Forecast, libraries, UI binding detail | Task Work Plan (`plan-design-gate.md`)                       |

Rules:

1. **Before the first edit** in a milestone implement wave, open the current
   accepted pack path (frontmatter `status: accepted`, or the closeout version
   named by orchestration) and keep `present: true` sections in working
   context. Do not rely on chat memory alone.
2. **Implement against the pack** for user-visible copy (`copy_locale` only),
   data shapes, Operation Flow / UML behavior, and verification cases that
   appear in the pack. Task Work supplies how to execute; the pack supplies
   what the user already accepted.
3. **Delivery** for software tasks in that milestone **Must** reconcile against
   pack sections that are `present: true`:
   - tick pack test-case rows (or cite the same Case IDs from Task Work) with
     `passed` / `failed` / `blocked_by_dependency`;
   - confirm shipped copy matches the pack inventory for `copy_locale` (other
     locales remain Execution extras, not silent Plan drift);
   - note schema / flow / UML deviations via `implementation-design-fidelity`
     (kept divergences require better_rationale **and** pack/Task Work/data
     attachment writeback in the same batch).
4. **Conflict / drift:** if implementation discovers the pack or Task Work is
   wrong, revise Task Work (discussion writeback), update the pack to a new
   `v<n+1>` when milestone-accepted content changes, and (interactive) re-seek
   acceptance for material deltas. Do not invent a parallel design only in
   chat (`milestone_plan_acceptance_pack_drift`).
5. **Missing pack at implement time:** fail closed
   `milestone_plan_acceptance_pack_missing` — do not start code edits for that
   milestone's software tasks.
6. Pack does **not** replace execution authorization (允许真正开工), Structural
   Forecast notice, prototype confirmation, or Delivery Card Checkpoint. When
   telling the user the next step after pack acceptance, gloss those tokens per
   `workflow-jargon-plain-language.md` (e.g. 「可以说『开始实施』」)—do not end
   on bare `execution_authorization` / `run`.

Fail closed:

- `milestone_plan_acceptance_pack_not_used` — Execution/Delivery for an
  in-scope software task without loading this reference and the accepted pack
  file
- `milestone_plan_acceptance_pack_drift` — material deviation from accepted
  pack with no Task Work + pack revision
- `milestone_plan_acceptance_pack_delivery_unreconciled` — Delivery claims done
  without reconciling `present: true` pack test cases / copy / schema / flows

## Fail-Closed Codes

| Code                                                   | When                                                                 |
| ------------------------------------------------------ | -------------------------------------------------------------------- |
| `milestone_plan_acceptance_pack_unread`                | Reference not loaded                                                 |
| `milestone_plan_acceptance_pack_missing`               | Milestone Plan closeout without pack, or implement without a pack    |
| `milestone_plan_acceptance_pack_incomplete`            | `present: true` section missing body, or required frontmatter absent |
| `milestone_plan_acceptance_pack_not_used`              | Implement/Delivery skipped the accepted pack as working reference    |
| `milestone_plan_acceptance_pack_drift`                 | Shipped work contradicts accepted pack without revision              |
| `milestone_plan_acceptance_pack_delivery_unreconciled` | Delivery omitted pack reconciliation                                 |
| `plan_copy_locale_unresolved`                          | Copy needed; locale not resolved                                     |
| `plan_copy_missing`                                    | Copy needed; no inventory                                            |
| `plan_copy_extra_locale`                               | Non-selected locales treated as Plan deliverables                    |
| `plan_acceptance_html_link_required`                   | HTML ready but no clickable/open HTML link before acceptance ask     |
| `plan_acceptance_link_digest_required`                 | Unattended run authored HTML packs but omitted closing link digest   |
| `milestone_ai_review_required`                         | Schema v2 review, provider evidence, or review pass is missing       |
| `milestone_ai_review_blocking_findings`                | Review retains an open blocking finding                              |
| `milestone_ai_review_verifier_failed`                  | Independent Final Verifier did not pass                              |
| `milestone_ai_review_plan_digest_mismatch`             | Current task plan differs from reviewed digest                       |
| `milestone_final_grill_me_required`                    | Final Grill Me was skipped                                           |
| `milestone_final_acceptance_required`                  | Final acceptance state is missing or invalid                         |
| `milestone_final_acceptance_digest_mismatch`           | Accepted digest differs from reviewed plan                           |

Additional UI fail-closed codes:

- `responsive_prototype_bundle_required`
- `analysis_technical_package_required`
- `contract_prototype_semantic_review_required`
- `contract_prototype_semantic_mismatch`
- `analysis_technical_package_digest_mismatch`
- `analysis_behavior_acceptance_required`
- `responsive_prototype_layout_missing`
- `responsive_prototype_digest_mismatch`

## Admission Test

1. Was this reference loaded via MCP?
2. Is there exactly one pack Markdown for this closeout version?
3. Are all five section keys listed with `present`?
4. If any task has user-visible copy: is `copy_locale` set and only that locale
   shown?
5. Was `render_markdown_acceptance_html.py` run, and does frontmatter
   `html_render` record paths / file URLs / `link_emitted`?
6. Interactive: did the user get a clickable HTML link (when ready) or
   Markdown link (fallback) **before** the acceptance question, and did we wait?
7. Before implement: is the accepted pack path in context, and will Delivery
   reconcile `present: true` sections?
8. Did `grill-finalizer` and `grill-me` complete for the reviewed digest, with
   unattended adoption labeled as unattended rather than user acceptance?
