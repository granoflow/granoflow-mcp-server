# Prototype Baseline Fit (Spec + Shell)

Apply this contract whenever the host authors a **task or milestone**
`ui_prototype` / page expression **after** the project Design Baseline (Design
Spec + App Shell) is locked. It prevents “same-ish colors in a generic phone
frame” from passing as Spec/Shell fidelity.

Design Spec Round A and App Shell Round B **define** the system; they do not
consume this gate. After Baseline confirm, every downstream screen Does.

## Mandatory Load (fail closed if skipped)

Before authoring HTML for any post-Baseline task/milestone option batch, load:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-baseline-fit"
)
```

Skipping fails closed as `prototype_baseline_fit_unread`.
Seeing Craft Gate prose or `derivedFrom` YAML alone does **not** count.

Also load `user-visible-copy-boundary` and (interactive dual)
`prototype-expression-brainstorm` per their own gates.

## Strict Fit (hard)

Post-Baseline prototypes Must be **fitted into** the locked Baseline—not merely
inspired by it.

### 1. Spec tokens (hard)

1. Read the confirmed Baseline package (`prototypeId` / `versionId` /
   `packageSha256`) and its token sources (`token_sources` / packaged tokens
   CSS or JSON).
2. Every option HTML Must **load or embed that locked token set** (CSS
   custom properties for color roles, type roles, radius, spacing density).
   Mark the token root with `data-baseline-tokens="locked"`.
3. Do **not** hand-roll a parallel palette, type stack, or radius system that
   only “looks similar.” Re-declaring the same variable names with different
   values fails closed `prototype_spec_tokens_drift`.
4. Fonts, primary/surface/ink/muted/reader roles, and radius Must match the
   locked Spec (contract fidelity). Pixel-perfect Baseline screenshots are not
   required; **token and role identity** is.

### 2. Shell chrome language (hard)

1. Read the locked Shell selection (`shell_selection` / chrome variant id, e.g.
   icons+labels rail/tabbar) and project `widgets.yaml`.
2. Screens that sit **inside** primary navigation Must reuse Shell widgets for
   the same role (`shell.primary_nav_*`, brand strip, etc.)—
   `widget_reuse_required` if skipped without rationale.
3. Screens that are **fullscreen / immersive** (e.g. reader) May omit primary
   nav **only when** Baseline/Shell/product docs already declare that
   exception. They Must still use:
   - the same Spec tokens; and
   - the Shell’s **chrome language** for overlays (icon+label vs text-only,
     glass-on-chrome-only, control radius/type roles, selected/primary tint).
4. Inventing a second chrome dialect (text-only top actions while Shell is
   icons+labels; new glass body treatments; foreign component chrome) fails
   closed `prototype_shell_chrome_mismatch`.

### 3. No generic parallel phone (hard)

Fail closed `prototype_generic_phone_frame` when an option is a simplified
device mock that:

- does not carry locked tokens (`data-baseline-tokens` missing); or
- restyles the page as a new mini design system; or
- ignores Shell overlay/nav language while claiming `ai_challenger` / Spec id
  only in reviewer copy.

Reviewer thesis may say “ai_challenger”; product frames Must **look and
behave** as Baseline children.

### 4. derivedFrom + checklist (hard)

Record exact Baseline ids/SHA on every option package and in Task Work
`prototype_inputs` / `design_baseline_derived_from`. Set:

```yaml
craft_checklist:
  baseline_fit_ok: true # only after load + token embed + Shell language check + lint
```

Run
`skills/granoflow-agent-workflow/scripts/lint_prototype_baseline_fit.py`
on each option HTML (pass `--baseline-tokens` when a Baseline tokens CSS/JSON
path is available). Require `ok: true`.

## Immersive / no-primary-nav screens

When product + Shell say the screen has no primary nav:

| Allowed                                                 | Forbidden                                              |
| ------------------------------------------------------- | ------------------------------------------------------ |
| Full-bleed content using Spec reader/surface tokens     | Dropping Spec fonts/colors for a “cleaner” mock        |
| Transient overlays using Shell chrome language          | Text-only action chrome when Shell locked icons+labels |
| Glass/blur on overlay chrome only (if Spec/Shell allow) | Full-bleed glass body fighting reading surfaces        |

Document the no-primary-nav exception under the option’s reviewer thesis
(`data-reviewer-only`), not as product copy.

## Gallery / confirm surface

Interactive galleries Must state in the digest (reviewer-only):

- Baseline `packageSha256` (short);
- Spec option id + Shell chrome variant id;
- whether primary nav is reused or immersively omitted (with product cite).

Missing digest line → `prototype_baseline_fit_digest_required`.

## Fail-closed codes

| Code                                     | When                                                                 |
| ---------------------------------------- | -------------------------------------------------------------------- |
| `prototype_baseline_fit_unread`          | Reference not loaded via MCP                                         |
| `prototype_spec_tokens_not_loaded`       | Option HTML missing locked token embed/link / `data-baseline-tokens` |
| `prototype_spec_tokens_drift`            | Token roles present but values diverge from Baseline                 |
| `prototype_shell_chrome_mismatch`        | Overlay/nav chrome language ≠ locked Shell                           |
| `prototype_generic_phone_frame`          | Parallel simplified mock without Baseline fit                        |
| `prototype_baseline_fit_digest_required` | Gallery missing Baseline fit digest                                  |
| `prototype_baseline_fit_lint_failed`     | `lint_prototype_baseline_fit.py` ≠ ok                                |

Any of the above keeps `baseline_fit_ok: false` and
`task_prototype_craft_incomplete` until fixed. Do **not** ask for
`visualConfirmed` while `baseline_fit_ok` is false.

## Relationship To Other Gates

- **Brainstorm / functional parity** still apply; every candidate Must assume
  Baseline fit—do not invent “escape Spec” candidate options.
- **Copy boundary** still applies inside product UI.
- **Contract fidelity** (契约级一致) remains the acceptance bar—not pixel
  parity with Baseline screenshots.
- **Confirmed chrome lock** (`prototype-confirmed-chrome-lock`) applies after
  sibling pages in the same chrome family are visually confirmed; Baseline fit
  alone does not authorize a parallel control dialect.
- Reopening Design Spec labels as task options remains
  `prototype_option_design_system_reopened`.

## Admission Test (host self-check)

1. Did we load this reference via MCP?
2. Does every option HTML embed/link the **same** locked Spec tokens with
   `data-baseline-tokens="locked"`?
3. Does chrome match Shell language (or a documented immersive exception)?
4. Would a reviewer who knows the Shell say “this is the same app,” not “a
   cousin mock”?

If any answer is no, revise before wait-for-confirm.
