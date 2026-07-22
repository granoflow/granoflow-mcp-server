# Prototype Confirmed Chrome Lock

Apply this contract when authoring a **new** post-Baseline task/milestone
`ui_prototype` / page expression **after** one or more **sibling screens in the
same product chrome family** already have `visualConfirmed=true` (or equivalent
App `ui_prototype` confirmation).

Baseline fit (`prototype-baseline-fit`) locks Spec tokens + Shell language.
This lock goes one step further: **confirmed sibling pages become the chrome
vocabulary authority** for later pages. Hosts Must not redesign a parallel
control dialect once the family has a confirmed look.

Typical family: immersive reader chrome (TOC / TTS / quick comment / reading
settings / annotation overlays that share `ReaderBottomSheet` or the same
overlay language). Other products use the same rule for their own confirmed
chrome family (e.g. shelf + import sheets).

## Mandatory Load (fail closed if skipped)

When **any** sibling in the chrome family is already visually confirmed, load
**before** authoring the new option HTML:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-confirmed-chrome-lock"
)
```

Skipping fails closed as `prototype_confirmed_chrome_lock_unread`.
Baseline-fit prose alone does **not** count.

If **no** sibling is confirmed yet, this gate is `not_applicable` for the
batch (still run Baseline fit). The **first** confirmed page in the family
becomes authority for all later pages.

## Hard Rules

### 1. Resolve chrome authorities

1. List project/milestone tasks that share the same **chrome family** (same
   product surface + shared overlay/sheet widget language; cite product docs
   or Project Work journeys/screens).
2. Collect every sibling with confirmed `ui_prototype` / Task Work
   `ui_prototype_confirmed` / `visualConfirmed=true` (exact
   `prototype_id` / `version_id` / `package_sha256`).
3. Record them in Task Work:

```yaml
chrome_lock:
  status: applicable # or not_applicable when no sibling confirmed yet
  family_id: reader_bottom_sheet # host-chosen stable id
  authorities:
    - task_id: ...
      option_id: expr_a
      prototype_id: ...
      version_id: ...
      package_sha256: ...
  vocabulary: [sheet-title-ico, tbtn, pref-ico, tchip-seg] # from authorities
```

Empty `authorities` while a sibling is known-confirmed →
`prototype_confirmed_chrome_lock_authority_missing`.

### 2. Reuse confirmed control vocabulary (hard)

New options Must **reuse** the confirmed siblings’ control vocabulary for the
same roles—not invent a second dialect that only shares Baseline tokens.

| Role                           | Reuse from authority                                                  | Forbidden parallel dialect                                                                   |
| ------------------------------ | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Sheet / overlay header mark    | Same title-icon treatment (`sheet-title-ico` or authority equivalent) | Floating icon-only / plain `h2` chrome when authority uses boxed title-ico                   |
| Primary / secondary actions    | Same button language (`tbtn` / `tbtn.play` or authority equivalent)   | Legacy filled text CTAs (e.g. `.btn.bp` / “发布” text buttons) when authority is icon `tbtn` |
| Segment / chip selection       | Same selected treatment (border + primary tint)                       | Full-bleed filled primary tabs when authority uses tinted chips                              |
| Small icon actions             | `pref-ico` (or authority equivalent)                                  | Ad-hoc icon buttons with a new radius/border system                                          |
| Bottom / rail chrome highlight | Same selected/primary act language                                    | Unrelated highlight dialect                                                                  |

Contrast across `expr_a` / `expr_b` May change **layout / hierarchy /
progressive disclosure** only. It Must **not** change the chrome dialect.

### 3. Gallery digest (hard)

Interactive galleries Must state (reviewer-only):

- chrome family id;
- authority package SHA shorts;
- vocabulary list being reused.

Missing → `prototype_confirmed_chrome_lock_digest_required`.

### 4. Lint + checklist (hard)

When authorities exist, run:

```text
skills/granoflow-agent-workflow/scripts/lint_prototype_confirmed_chrome_lock.py \
  CANDIDATE.html --authority AUTHORITY.html [--authority OTHER.html ...]
```

Require `ok: true`. Set:

```yaml
craft_checklist:
  confirmed_chrome_lock_ok: true # only after load + authorities recorded + lint
```

Do **not** ask for `visualConfirmed` while `confirmed_chrome_lock_ok` is false
and `chrome_lock.status` is `applicable`.

## Fail-closed codes

| Code                                                | When                                                            |
| --------------------------------------------------- | --------------------------------------------------------------- |
| `prototype_confirmed_chrome_lock_unread`            | Reference not loaded via MCP when authorities exist             |
| `prototype_confirmed_chrome_lock_authority_missing` | Sibling confirmed but Task Work `chrome_lock.authorities` empty |
| `prototype_confirmed_chrome_lock_drift`             | Candidate invents parallel chrome dialect vs authorities        |
| `prototype_confirmed_chrome_lock_digest_required`   | Gallery missing chrome-lock digest                              |
| `prototype_confirmed_chrome_lock_lint_failed`       | Lint ≠ ok                                                       |

Any of the above keeps `confirmed_chrome_lock_ok: false` and
`task_prototype_craft_incomplete` until fixed.

## Relationship To Other Gates

- **Baseline fit** still required (tokens + Shell). This lock does not replace
  it.
- **Expression candidates / functional parity** still apply; candidates Must
  assume the confirmed chrome dialect—do not invent “escape sibling look”
  options.
- **Product truth / copy boundary** still apply.
- First page in a family has no sibling authority → `not_applicable`; after it
  is confirmed, later pages Must lock.

## Admission Test (host self-check)

1. Did we load this reference when siblings are confirmed?
2. Are authority package SHAs recorded on Task Work?
3. Would a reviewer who just confirmed TTS/settings say “same app chrome,” not
   “older parallel mock”?
4. Do A/B options diverge in layout only, not in button/chip/title dialect?

If any answer is no, revise before wait-for-confirm.
