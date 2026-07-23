# Project Artifact Workflows

Read this reference when authoring Design Spec, App Shell, Design Baseline,
`widgets.yaml`, or task/milestone `ui_prototype`. It owns the **Prototype
Preview Gate**, Spec/Shell Mode split, Widget Catalog, and **Task Prototype
Craft Gate And Option Set**. Fail-closed checklist:
`hard-constraints.md`.

## Companion roles (see Project Work map)

Authority and slots align with the **Companion attachments** table in
`granoflow-agent-workflow/project-work-document-template`:

| Artifact                                                           | Role                                                              |
| ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Design Baseline + tokens                                           | Project visual/IA **current** authority                           |
| `widgets.yaml`                                                     | Reusable widget contracts after Baseline confirm                  |
| Task/milestone `ui_prototype`                                      | Task-level clickable UI authority (`derivedFrom` Baseline SHA)    |
| `data-model.md` / `data-contracts.yaml` / `constants-catalog.yaml` | Data/constants current shapes (not embedded in Project Work body) |
| Project Work                                                       | Product/acceptance **current** truth and admission                |
| `project_snapshot.yaml` / `project_rules.yaml`                     | Code status quo / durable boundaries—not product SoT              |

Do not invent a parallel product ledger inside Baseline HTML or widgets.yaml.

## Design-first, product-truth, and high-risk feasibility

**Default order stays design-first.** Confirmed product docs and previewable UI
express user-visible demand; engineering then implements. If a visual commitment
cannot be delivered in time, return to product and **change the design**—do not
fake the capability in code or in the prototype.

Do **not** invert the whole pipeline into “data model / tech design before any
preview.” Do apply the three guardrails below so previews do not invent
unauthorized or undeliverable behavior.

### 1) Product-truth check before Preview Gate wait

Before emitting option links (or a single preview) for interactive wait, or
before ledger/digest notice in unattended mode, check the prototype against
**confirmed product authority** for this project (Project Work sources such as
product UX docs and user stories; conflict rules already in Project Work).

- Previews **must not** introduce capabilities, states, or copy that product
  authority forbids or never authorized (example: shelf chrome that implies the
  App is actively syncing a cloud library when the product only waits on
  system materialization at open-time).
- Fail closed `prototype_product_truth_violation` if the preview shows such
  unauthorized behavior. Fix the prototype (or reopen product docs) before the
  Preview Gate wait / visual confirm.
- This is **fidelity to product**, not a tech-first gate.

### 2) Honest ahead-of-implementation craft

Design may lead implementation. Where the HTML is schematic, or where a platform
API may not deliver the exact visual (for example a precise download percent),
record `【增强实现】` / `implementation_notes` with:

- what the UI **promises** the user will observe;
- what the target stack / OS may only approximate;
- **Must** invariants that remain unchanged if the implementation degrades.

Do not paint a fake precise progress bar (or similar) when product requires
“real progress when available” and the spike has not proven availability—prefer
an honest waiting state plus the enhancement note.

### 3) High-risk screens: spike after preview, conclusion before Readiness

**High-risk** means platform-coupled or otherwise easy-to-overpromise surfaces
(examples: cloud Files On-Demand / SAF hydration, directory authorization,
key migration, import of large trees, OS share sheets). For these:

1. Still author and preview the UI **design-first** under guardrails 1–2.
2. As soon as the preview batch exists (parallel OK), write a short **Tech
   Note** (trigger, system APIs, progress/availability limits, Non-goals,
   degradation). Optionally sketch minimal data fields the UI must not invent
   (for example no shelf-level `download_percent` if product forbids it).
3. Before `readiness_grill_status: passed` / claiming execution-ready, the Tech
   Note must conclude one of: **deliverable as drawn**, **deliverable with
   documented degradation**, or **must revise design/product**. Missing
   conclusion → fail closed `high_risk_feasibility_unresolved`.
4. If the conclusion is “revise design,” do **not** pass Readiness; return to
   product/prototype change. Do not hardcode a fake UI to satisfy the preview.

Ordinary chrome / IA / copy screens that only reuse Baseline + widgets do **not**
require a Tech Note.

## Prototype Preview Gate (every HTML prototype)

Applies to **every** discrete HTML prototype the host authors in this workflow:

- each Design Baseline journey/critical-state screen (or self-contained preview
  unit) as it becomes previewable;
- landscape and portrait App Shell previews when authored as distinct preview
  units;
- every task/milestone `ui_prototype` package.

MCP does not render HTML. The host must expose a **clickable** preview link
(file URL, local static server, or host sidebar/browser open path).

### Mode Gate

Default `executionMode: interactive` unless the user explicitly declared
unattended. Never infer unattended from prototype authoring alone.

### Interactive (default)

When each prototype becomes previewable:

1. Emit the clickable preview link (and a one-line what-to-review hint).
2. **Stop** and wait for the user's visual review decision (accept / revise /
   reject) before packaging with `visualConfirmed=true`, importing Baseline,
   starting the next prototype, or continuing UI implementation.
3. Do not batch several unfinished prototypes into one confirmation when each
   already has its own previewable link—review them one by one.

Skipping the wait fails closed as `prototype_preview_review_required`.

### Unattended (explicit only)

When each prototype becomes previewable:

1. Emit the same clickable preview link as a **non-blocking notice** (does not
   consume the unattended interaction budget; do not wait).
2. Auto-continue solvable packaging/import/next work per
   `unattended-interaction-contract` (Baseline may still use
   `auto_accept_recommendation` only under explicit unattended).
3. Append `{ title, path_or_url, entity, sha_or_pending }` to the run's
   `prototype_link_ledger`.

At **run close** (Project Definition Done, milestone/task batch complete, or
`complete_with_residuals`):

1. Emit a mandatory **Prototype Link Digest** listing every ledger entry with
   clickable links in one place for human audit.
2. Do not omit links that were already shown mid-run.
3. The digest is the unattended closing review surface; it does not reopen
   mid-run waits. Park outstanding visual taste follow-ups in the Residual
   Report when the user must still judge aesthetics offline.
4. Omitting the digest fails closed as `prototype_link_digest_required`.

### Option-set exception (interactive choice batches)

**Project Definition — Design Spec / Shell**

When Project Definition is **interactive** and presents a Spec or Shell choice
set:

0. Load `granoflow-agent-workflow/prototype-expression-brainstorm`, run
   **mainstream-reference-first** candidates for **this** round
   (`scope_mode` `same_category`|`capability_match`; default capability when
   unsure; brainstorm backfill only when mainstream `<5`), then **promote
   exactly 3** (Spec triad / Shell triad—not task-level AB). Show a short
   candidate digest above the triad. Wrong promote count →
   `prototype_option_promote_count_mismatch`. Lint
   `lint_prototype_expression_brainstorm.py`.
1. Design Spec triad: author all **three** as **Style Guide / Design Tokens
   boards** after drawing lots with `scripts/draw_visual_lots.py --kind spec
--count 3 --record` (**true random**; never reuse a seed inside the triad;
   never hand-invent `seed-*`; never substitute a full journey-screen gallery).
   Candidate analysis does **not** replace lot draw.
2. Shell triad: after Spec lock, mainstream-first→promote-3, draw chrome cards
   with `draw_visual_lots.py --kind shell --count 3 --record`, then author all
   **three** **fitted to the selected Spec** (**no** independent palette
   seeds; `shell_spec_mismatch` if Spec is broken).
3. Emit **all** clickable links in one batch with **plain-language labels only**
   (no `seed-*`, no `spec_match` / `ai_challenger_*` / chrome-variant ids in
   user-visible copy). Add a one-line human contrast note per option.
4. **One wait** for: pick one / **换新批** / **在某套上改**.
   - 换新批: re-draw with `--dedupe ledger` (machine-local history) + `--record`;
     skipping dedupe → `visual_lot_dedupe_required`.
   - 在某套上改: revise that option in place (no seed/chrome re-draw unless the
     user asks to change structure).
5. After the user picks one, further single-screen refinements of that winner
   again follow the per-prototype rules above.

**Task / milestone `ui_prototype` — interactive dual (default) / conditional
third**

See **Task Prototype Craft Gate And Option Set** below. Default batch size is
**two**; a **third** option is allowed only under the industry-peer exception.

**Contrast Gallery (hard, interactive option batches):** do **not** present only
separate option links. Emit one clickable **side-by-side contrast gallery**
page that shows every option in one viewport (or one scrollable section per
task), with:

1. Plain-language option labels;
2. Per declared contrast axis, one short **visible-diff caption** that names
   what the user should see differ (not only intent prose);
3. Embedded previews (iframe or equivalent) so options can be compared without
   opening many tabs.

Prefer `scripts/build_option_contrast_gallery.py` (or an equivalent host
gallery). Missing gallery → `prototype_option_contrast_gallery_required`.
Missing per-axis visible-diff captions → `prototype_option_diff_unlabeled`.
Then **one wait**. Unattended mode **does not** use Spec/Shell triads or task
dual/triple batches (and therefore does not require a contrast gallery).

## UI Prototype (Task / Milestone Slot)

When a **task changes UI**, a high-fidelity HTML prototype is **mandatory**
(see `granoflow-agent-workflow/task-work-document-workflow` UI Change Prototype
Mandate). Do not treat prototypes as optional suggestions. Enter this branch as
soon as UI change is detected—not only when the user asks.

1. Read the confirmed project Design Baseline first
   (`granoflow_project_design_baseline_read` with exact ids/SHA). Accept against
   contract fidelity (契约级一致): Shell IA, tokens, main-path regions, and
   locked widgets Must match; pixel/motion 1:1 is not required.
2. Declare `derivedFrom` the baseline `prototypeId`, `versionId`, and
   `packageSha256` in Task Work / attachment metadata (document-level gate in
   this release). Missing `derivedFrom` on a UI-changing task fails closed.
3. **Do not** apply a new random visual seed. Task prototypes inherit the
   locked Spec + Shell. Fail closed `task_prototype_seed_forbidden`.
4. Load project `widgets.yaml`; reuse widgets with the same role before
   inventing new chrome/controls (`widget_reuse_required` if skipped).
5. Author options under **Task Prototype Craft Gate And Option Set** (below).
6. Apply the **Prototype Preview Gate** for the option batch (interactive: all
   links + one wait; unattended: single option notice + ledger).
7. Visual confirmation (interactive user accept of the chosen option, or
   unattended auto-accept when explicitly authorized) authorizes only packaging
   that exact source hash. It is not implementation acceptance or execution
   authorization. Craft Gate must pass before `visualConfirmed=true`—else
   `task_prototype_craft_incomplete`. After confirmation, extract any
   new/changed reusable widgets into the same project `widgets` slot.
8. Build a deterministic ZIP: root `index.html`, relative paths only, sorted
   entries, normalized timestamps, no symlinks, no path traversal, and all
   required static resources included. Use
   `scripts/package_prototype.py SOURCE OUTPUT` (or `--dry-run` before writing)
   unless the host already provides an equivalent deterministic packager.
9. Call `granoflow_logical_attachment_replace` with `visualConfirmed=true` to
   replace the target entity's `ui_prototype` logical slot and retain App-owned
   SHA/manifest evidence.
10. Record `【增强实现】` / `implementation_notes` where the HTML is schematic
    and the target stack will use richer third-party widgets, listing Must
    invariants that remain unchanged.

### Task Prototype Craft Gate And Option Set

Applies to every UI-changing task/milestone prototype. **From Shell onward
style is converged**; task options explore only the **authorized UI delta**,
never a new visual system. **After any sibling page in the same chrome family
is visually confirmed**, later pages Must also converge to that confirmed
**control vocabulary** (see
`granoflow-agent-workflow/prototype-confirmed-chrome-lock`)—Baseline tokens
alone are not enough.

**Two layers (do not conflate):**

| Layer                     | When                       | Brainstorm → promote | What the batch chooses                                                               |
| ------------------------- | -------------------------- | -------------------- | ------------------------------------------------------------------------------------ |
| **Design Spec triad**     | Project definition Round A | 6 → **3**            | Design System / Style Guide (`spec_match` + `ai_challenger_*`)                       |
| **App Shell triad**       | Project definition Round B | 6 → **3**            | Chrome / nav fitted to selected Spec (`shell_match` + challengers)                   |
| **Task page expressions** | After Baseline locked      | 6 → **2**            | Per-task / per-page layout & interaction detail **within** that locked Design System |

Task-level dual options are **not** a second Design Spec vote, and Spec/Shell
remain **triads of three**—never collapse them to task AB. After the user locks
Spec/Shell/Baseline, re-labeling task options as `delta_match` vs
`ai_challenger` (or any design-system reopen) fails closed
`prototype_option_design_system_reopened`. Offering Spec/Shell as dual-only
fails closed `prototype_option_promote_count_mismatch`.

**Why side-by-side still matters:** page-expression galleries exist to force
visible, page-local choices and to surface agent misunderstandings of product
behavior early. Exposing those errors is a successful gate—not a reason to
collapse back to a single frame or to reopen the Design System.

#### Craft Gate (fail closed before `visualConfirmed=true`)

Every option in the batch Must pass all of:

1. **Intent:** state the authorized UI delta (what changes / what must not
   change vs Baseline). Whole-page redesign only when Scope explicitly
   authorizes it.
2. **Fidelity / Baseline fit (hard):** `derivedFrom` exact Baseline; no random
   visual seed; reuse `widgets.yaml` for the same role; **both** options share
   the locked Design System (`design_system_locked`). Load
   `granoflow-agent-workflow/prototype-baseline-fit` via
   `granoflow_bundled_skill_reference`. Embed/link locked Spec tokens with
   `data-baseline-tokens="locked"`; match Shell chrome language (immersive
   screens may omit primary nav only when Baseline/product already allow it).
   Run `lint_prototype_baseline_fit.py` (prefer `--baseline-tokens`). Set
   `craft_checklist.baseline_fit_ok: true` only when load + lint pass. Fail
   closed `prototype_baseline_fit_*` /
   `prototype_spec_tokens_not_loaded` /
   `prototype_spec_tokens_drift` /
   `prototype_shell_chrome_mismatch` /
   `prototype_generic_phone_frame`.
   2b. **Confirmed chrome lock (hard when siblings exist):** After any sibling
   screen in the same product chrome family is `visualConfirmed`, load
   `granoflow-agent-workflow/prototype-confirmed-chrome-lock`, record
   `chrome_lock.authorities` (exact package SHAs), and **reuse that confirmed
   control vocabulary** (title-ico / tbtn / chip selected tint / pref-ico)—do
   not invent a parallel dialect that only shares Baseline tokens. A/B May
   change layout only. Run
   `lint_prototype_confirmed_chrome_lock.py --authority …`. Set
   `craft_checklist.confirmed_chrome_lock_ok: true` only when load + lint
   pass (or `chrome_lock.status: not_applicable` when no sibling is confirmed
   yet). Fail closed `prototype_confirmed_chrome_lock_*`.
3. **Product truth:** no unauthorized capability, state, or copy vs confirmed
   product docs / Project Work (see **Design-first, product-truth, and
   high-risk feasibility**). Fail closed `prototype_product_truth_violation`.
4. **Craft:** real project/domain copy (no lorem ipsum, fake data walls, or
   generic AI feature grids); cover Scope-required default / empty / error /
   success states; schematic or platform-uncertain regions carry `【增强实现】`
   with Must invariants and honest degradation (do not fake undeliverable
   precision). Prefer **page-specific** controls and states over generic
   skeleton phones that skip Baseline fit.
5. **User-visible copy boundary (hard):** load
   `granoflow-agent-workflow/user-visible-copy-boundary` via
   `granoflow_bundled_skill_reference` **before** authoring in-frame copy.
   Keep design rationale / filtering policy / reviewer pedagogy **outside**
   the simulated product UI. Run
   `granoflow-agent-workflow/scripts/lint_prototype_user_copy.py` on each
   option HTML and require `ok: true`. Record
   `craft_checklist.user_visible_copy_boundary_ok: true` only after both the
   load and lint succeed. Fail closed
   `user_visible_copy_boundary_unread` /
   `user_visible_copy_boundary_violation` (also keeps
   `task_prototype_craft_incomplete`).
6. **Expression candidates (hard for interactive dual/triple):** load
   `prototype-expression-brainstorm`, run mainstream-reference-first (≥5;
   backfill only when mainstream `<5`), promote parity-safe A/B, lint with
   `lint_prototype_expression_brainstorm.py`, set
   `expression_brainstorm_ok: true`. Every candidate Must assume Baseline fit
   (no “escape Spec” options). Fail closed `prototype_option_brainstorm_*` /
   `prototype_option_mainstream_skip` / `prototype_option_scope_mode_invalid` /
   `prototype_option_function_split` / `prototype_option_data_divergence`.
7. **Confirm surface:** interactive shows Baseline-fit digest (Spec id + Shell
   chrome variant + sha short) + **confirmed-chrome-lock digest** (family id +
   authority SHA shorts + vocabulary) when applicable + candidate digest +
   craft checklist + **per-page/per-task** Contrast Gallery before wait;
   unattended records the same checklist into the run digest for the single
   option. Do **not** ask for `visualConfirmed` while `baseline_fit_ok`,
   `confirmed_chrome_lock_ok` (when applicable),
   `user_visible_copy_boundary_ok`, or (interactive dual)
   `expression_brainstorm_ok` is false.

Fail closed `task_prototype_craft_incomplete` if any item is missing. Do not
treat packaging or upload as craft completion.

#### Expression candidates → functional-parity A/B (hard)

Before authoring dual HTML, run **Prototype Expression Brainstorm**
(`granoflow-agent-workflow/prototype-expression-brainstorm`):

1. Load the reference via `granoflow_bundled_skill_reference` (else
   `prototype_option_brainstorm_unread`).
2. Choose `scope_mode` (`same_category`|`capability_match`; default
   `capability_match` when unsure). Collect mainstream product references
   first; brainstorm backfill **only** when mainstream `<5`. Combined pool
   band **5–8**. Every candidate Must cover the **full** authorized
   Outcome/Scope—do not omit capabilities or break serial/recovery logic to
   manufacture variety.
3. Promote the host's best **two** as `expr_a` / `expr_b`. They Must be
   **functionally identical** and show the **same domain data fields**; only
   presentation (whitelist contrast axes) may differ.
4. Product **states** (empty / error / TTS unavailable / limit reached) are
   covered **inside** each expression or via shared scenario controls—not as
   the A-vs-B difference (`prototype_option_function_split` /
   `prototype_option_data_divergence`).
5. Record `expression_brainstorm`, run
   `lint_prototype_expression_brainstorm.py`, and set
   `craft_checklist.expression_brainstorm_ok: true`. Interactive galleries
   Must show a short candidate digest above the frames.

Fail closed: `prototype_option_brainstorm_missing` /
`prototype_option_brainstorm_incomplete` /
`prototype_option_mainstream_skip` /
`prototype_option_scope_mode_invalid` /
`prototype_option_backfill_unjustified` /
`prototype_option_brainstorm_digest_required`.

#### Interactive option set (default dual; conditional third)

**Default (hard):** after the candidate protocol, author exactly **two**
complete **page expressions** for each UI-changing task (or each distinct
screen the task owns). Both share the locked Design System and pass
**functional parity**:

| Label    | Role                                                                                                                                           |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `expr_a` | Page expression A — a complete, craft-ready treatment of the authorized delta                                                                  |
| `expr_b` | Page expression B — an equally complete **presentation** alternative on the declared contrast axes (same capabilities, same data, same tokens) |

Record `prototype_option_set.design_system_locked` to the confirmed Spec /
Baseline option id (e.g. `ai_challenger_a` / project-local label). Selection is
**mix-and-match by task (and by page when a task owns multiple screens)** —
the user may pick `expr_a` for import and `expr_b` for bookshelf; do **not**
require one expression id for the whole milestone.

Both options Must fully satisfy the Craft Gate (not a sketch + a finished
pair). Emit a **side-by-side Contrast Gallery** (see Preview Gate option-set
exception) plus optional per-option deep links; **one wait** for per-page
select / revise / request-more. Separate links alone are insufficient.

**Contrast axes (hard):** declare **at least two** axes from this whitelist and
make the options diverge on those axes in a user-visible, defendable way.
Axes describe **page-local** hierarchy/interaction/disclosure—not a new Spec:

- `information_hierarchy`
- `density`
- `interaction_pattern`
- `state_emphasis`
- `progressive_disclosure`
- `secondary_nav_within_delta` (task-local only; must not rewrite global Shell)

**Visible-diff bar (hard):** for each declared axis, the gallery Must show a
one-line caption the reviewer can verify in the frames (e.g. “续读顶栏条卡 vs
续读英雄大卡”, “确认对话框+checklist vs 新旧对比卡”). Captions that only
restate axis names without a screen-checkable difference fail
`prototype_option_diff_unlabeled`.

**Not valid contrast:** new palette/typography/material seed; spacing/radius/
shadow-only tweaks; restyling a locked widget for the same role; unauthorized
Shell IA change; reopening Design Spec (`delta_match` / `ai_challenger` /
`spec_match` as task option ids); **prose-only** differences where the two
frames look the same to a careful reviewer.

Fail closed:

- `prototype_option_design_system_reopened` — task options re-offer Design
  Spec / Design System choice after Baseline lock;
- `prototype_option_brainstorm_unread` /
  `prototype_option_brainstorm_missing` /
  `prototype_option_brainstorm_incomplete` /
  `prototype_option_brainstorm_digest_required` — brainstorm contract skipped
  or incomplete (see `prototype-expression-brainstorm`);
- `prototype_option_function_split` — A/B differ in capabilities or omit
  Scope actions (feature-split disguised as presentation contrast);
- `prototype_option_data_divergence` — A/B show different domain data without
  shared scenario controls;
- `prototype_option_contrast_insufficient` — fewer than two whitelist axes, or
  either expression lacks a defendable page-local contrast thesis;
- `prototype_option_near_duplicate` — options are the same skeleton with only
  cosmetic deltas, **or** the frames are not distinguishable on the declared
  axes without reading captions;
- `prototype_option_contrast_gallery_required` — interactive batch presented
  without a side-by-side contrast gallery;
- `prototype_option_diff_unlabeled` — gallery missing per-axis visible-diff
  captions.

**Conditional third option:** add `industry_peer_c` **only when** all of the
following hold (record under `prototype_option_set.third_option_rationale`):

1. The industry has **three** peer interaction/IA patterns in active use for
   this problem class;
2. All three are suitable for **this** app given Baseline Musts and Outcome
   **and** stay inside the locked Design System;
3. The host **cannot honestly prefer** one of the three on evidence (not taste
   laziness)—document the three industry references and why preference is
   blocked.

Otherwise stay at two. A gratuitous third option without that rationale fails
closed as `prototype_option_third_unjustified`.

**Request-more:** a new batch must again meet Craft Gate + contrast rules and
must not near-duplicate the prior batch (`prototype_option_near_duplicate`).

#### Unattended (explicit only)

Author **one** option only: `expr_a`, full Craft Gate, no dual/triple
exploration, no random seed, no Design System reopen. Link notice + ledger;
closing digest includes the craft checklist summary.

## Project Design Baseline Package

The project Design Baseline is not the mutable `ui_prototype` logical slot. It
is a versioned App-owned Prototype linked to the project and referenced exactly
from Project Work. It is the authoritative visual/IA reference for later
milestones, task prototypes, and code acceptance.

A complete initialization package **must** include:

1. High-fidelity HTML screens for primary journeys and critical states;
2. Companion Design Tokens (DTCG-oriented JSON or equivalent), referenced from
   Project Work `token_sources`—do not dump the full token graph into YAML;
3. Landscape App Shell (primary navigation + chrome + breakpoints);
4. Portrait App Shell (or an explicit responsive Shell that covers both modes
   with documented breakpoints).

Missing App Shell fails Done and fails visual confirmation for initialization.

### Design Spec then Shell (mode-split rounds)

Project Definition **must not** jump to an unlabeled locked Baseline+Shell.
Run Design Spec first, then Shell. **Design Spec** may explore with random
visual seeds (`impeccable` / matching `skill_routing` Skills).
**From Shell onward, design style converges**: every Shell candidate Must
perfectly fit the **already selected** Design Spec (tokens, typography, color
roles, IA Musts). Do not invent a second visual system at Shell time.

#### What a Design Spec artifact is (hard)

A Design Spec option is a **Style Guide / Design Tokens board**, not a product
screen mockup set. The HTML preview Must read like a design-system sheet:

| Required panels         | Purpose                                                                                                                                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Colors**              | Text / Neutrals ramp / Primary / Secondary (or accent) / System (error, success, semantic flags when product-defined) — include light and dark roles when the product has App modes                                               |
| **Typescale**           | Named roles (e.g. H1–H4, body, caption, button) with size / weight / line-height / letter-spacing; note responsive tiers when used; separate **reading body** vs **App chrome UI** type roles when the product distinguishes them |
| **Spacing**             | Named 4pt/8pt (or equivalent) scale with labels (e.g. 4XS→XXXL)                                                                                                                                                                   |
| **Grid & Breakpoints**  | Column counts / gutters / margins and Shell-relevant breakpoints (e.g. narrow bottom bar vs wide side rail)                                                                                                                       |
| **Components (states)** | At least Button and Input/Field across Default / Hover / Active / Disabled / Error (add product-critical controls when known)                                                                                                     |
| **Shadows & Radius**    | Elevation and corner-radius tokens                                                                                                                                                                                                |

Optional: a one-page **token summary** card (Colors / Typography / Spacing /
Shadows&Radius). Real product copy for labels is required; no lorem ipsum.

**Forbidden as Design Spec content** (fail closed
`design_spec_wrong_artifact_type`):

- Completing every `product_spec_coverage` journey/critical screen as full-page
  UI mockups inside the Spec triad;
- Treating Spec preview as an app walkthrough / phone gallery of all screens;
- Shipping Spec as marketing landing grids instead of token/component boards.

Journey/screen high-fidelity belongs in **App Shell + Baseline package** (and
later task `ui_prototype`), always **fitted to** the selected Spec tokens.
`product_spec_coverage.screen_coverage` still gates Baseline completeness—not
the Spec artifact shape.

#### Mode split (hard)

| Mode                           | Design Spec                                                                                                                                                                                                                                                                                                                                                                                    | Shell                                                                                                                                                                                                                                                            |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Interactive (default)**      | Mainstream-first ≥5→**promote 3**, then **Triad**: exactly three options from `draw_visual_lots.py --kind spec` (**true random**, `--record`)—one `spec_match` (faithful to user requirements) + two `ai_challenger_*`. Hand-invented seeds → `design_spec_seed_not_drawn`. User picks one, **换新批** (`--dedupe ledger` against machine-local history), or **在某套上改** (in-place revise). | After Spec selection: mainstream-first ≥5→**promote 3**, then **Triad** from `draw_visual_lots.py --kind shell` (chrome deck, `--record`); all reuse the selected Spec—one `shell_match` + two chrome challengers. Same pick / 换新批(强去重) / 在某套上改 gate. |
| **Unattended (explicit only)** | **Single** Design Spec: faithful `spec_match` only, true-random draw + `--record`. No challengers, no triad wait. Emit link notice + ledger.                                                                                                                                                                                                                                                   | **Single** Shell: faithful `shell_match` only, derived from that Spec—**no independent palette seed**. Emit link notice + ledger. Auto-accept package when explicitly unattended.                                                                                |

Contract-fidelity Musts (journeys, IA, acceptance behavior, primary nav, Shell
modes) stay intact on every option. Spec-round challengers may vary craft
presentation within those Musts. Shell-round challengers may only vary chrome
density, nav structure, and breakpoint expression **inside** the selected Spec.

#### Round A — Design Spec

**Interactive**

1. Load `prototype-expression-brainstorm`; run mainstream-reference-first
   Style Guide candidates that each cover full Spec Musts (backfill only when
   mainstream `<5`); **promote exactly 3** (never task-style AB-only). Lint
   `lint_prototype_expression_brainstorm.py`. Record digest +
   `expression_brainstorm` beside `design_spec_selection`.
2. Produce exactly those three Design Spec options as **Style Guide / Design
   Tokens boards** (see “What a Design Spec artifact is”). All three share the
   same product IA Musts and token _roles_; they differ by seed-driven craft
   (palette, type pairing, density/spacing expression)—not by inventing new
   primary navigation (`prototype_option_function_split` if a board omits Must
   token roles).
3. Draw lots with `scripts/draw_visual_lots.py --kind spec --count 3 --record`
   (**true random** only). Do **not** invent `seed-*` ids and do **not** pass
   classroom salt / `--from` (`visual_lot_classroom_salt_forbidden`). Reusing a
   seed inside the triad fails closed as `design_spec_seed_collision`. Skipping
   the script → `design_spec_seed_not_drawn`. Compose palettes from drawn seeds
   (invoke `impeccable` / `palette.mjs --id <drawn>` when available).
   Brainstorm does **not** replace lot draw.
4. Label: `spec_match` | `ai_challenger_a` | `ai_challenger_b` with contrast
   rationale on challengers (valid axes include color strategy, typography
   pairing, spacing density, component emphasis—not full-page IA rewrites).
5. Option-set Preview Gate: brainstorm digest + three Style Guide links; wait
   for pick / **换新批** / **在某套上改**. **User-visible labels must be plain
   language** (no `seed-*`, no `spec_match` / `ai_challenger_*` in the table or
   hub). Record internal option id + seed only in Project Work / ledger
   (`design_spec_user_facing_jargon` if leaked to the user).
   - 换新批: `draw_visual_lots.py --kind spec --count 3 --dedupe ledger --record`
     (machine-local `~/.granoflow/visual-lot-ledger.json` by default). Skipping
     dedupe → `visual_lot_dedupe_required`. Exhausted pool →
     `visual_lot_exhausted`.
   - 在某套上改: revise that Style Guide in place; do not re-draw its seed
     unless the user asks for a new visual direction.
6. Record selection under
   `engineering.theme_and_design_system.design_spec_selection` (option id,
   seed, provenance: `user_selected`, plus brainstorm digest reference).

Fail closed `design_spec_triad_required` if fewer than three distinct-seed
options were offered before selection. Fail closed
`prototype_option_promote_count_mismatch` if Spec was offered as dual-only.
Fail closed `design_spec_wrong_artifact_type` if an option is a full-screen
journey gallery instead of a Style Guide / Tokens board. Fail closed
`design_spec_user_facing_jargon` if Preview Gate copy exposes seeds or internal
option enums to the user.

**Unattended (explicit only)**

1. Produce **one** Design Spec Style Guide: `spec_match` only (faithful to user
   requirements), via `draw_visual_lots.py --kind spec --count 1 --record`.
2. Preview Gate: link notice + ledger (no wait, no triad).
3. Record `design_spec_selection` with provenance
   `unattended_spec_match_random_seed`.

#### Round B — App Shell (after Spec selection)

**Convergence rule (hard):** every Shell option Must perfectly fit the selected
Design Spec. Reusing Spec tokens/IA is mandatory. Introducing a new palette /
typography / material seed that breaks Spec → fail closed `shell_spec_mismatch`.

#### What an App Shell artifact is (hard)

An App Shell option is a **product-near chrome + primary-surface preview** that
already **embeds the selected Design Spec**—not a grey wireframe of nav alone.

| Must                         | Detail                                                                                                                                                                                                                                                                     |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Consume selected Spec**    | Load the locked Spec tokens (CSS variables / linked `token_sources` JSON / Spec stylesheet). Colors, type roles, spacing density, radius, and elevation Must match the chosen Spec.                                                                                        |
| **Declare provenance**       | Each Shell HTML/`meta` records `fitted_to_design_spec_option_id`, Spec `seed`, and token source path/SHA when available.                                                                                                                                                   |
| **Portrait + landscape**     | Show both modes (or one responsive frame with documented breakpoints) with primary navigation chrome.                                                                                                                                                                      |
| **Product-near surfaces**    | Render at least one primary in-Shell surface (e.g. bookshelf / home) using Spec tokens and **real product copy**—covers, titles, progress, empty/error cues as applicable. Aim for **as close as practical to final product effect** under contract fidelity (契约级一致). |
| **Chrome is the triad axis** | Across the three interactive options, only nav structure / density / chrome expression may diverge. Tokens and type system stay identical.                                                                                                                                 |

**Forbidden as App Shell content** (fail closed):

- `shell_spec_tokens_missing` — Shell does not load/apply the selected Spec
  tokens (generic grey UI, invents a new palette, or ignores `token_sources`);
- `shell_wireframe_only` — Shell is only low-fidelity grey boxes / unlabeled
  placeholders with no Spec craft (no real type, color roles, or product-like
  primary surface);
- `shell_spec_mismatch` — new palette/typography/material seed or broken Spec
  IA Musts.

Glass/blur materials (when Spec/platform allows) may appear on **navigation
chrome only**, never as a full-bleed body treatment that fights reading
surfaces.

Schematic notes (`【增强实现】`) are allowed for platform-native controls, but
the overall Shell Must still read as a credible product frame—not a UX
wireframe deck.

**Interactive**

1. Load `prototype-expression-brainstorm`; run mainstream-reference-first
   Shell candidates that each cover full Shell Musts under the **selected**
   Spec (backfill only when mainstream `<5`); **promote exactly 3** (never
   task-style AB-only). Lint `lint_prototype_expression_brainstorm.py`.
   Record digest beside `shell_selection`.
2. Produce exactly those three Shell options (landscape + portrait) that
   **each** embed the **selected** Design Spec tokens and meet “What an App
   Shell artifact is”.
3. Draw chrome lots with
   `scripts/draw_visual_lots.py --kind shell --count 3 --record` (deck in
   `references/shell-chrome-deck.json`). Do **not** invent chrome ids and do
   **not** assign independent palette seeds. Duplicate chrome-variant ids →
   `shell_seed_collision`. Skipping the script → `design_spec_seed_not_drawn`
   (same “lots must be drawn” rule). Candidate analysis does **not** replace
   lot draw.
4. Label: `shell_match` | two `ai_challenger_*` with rationale (chrome only).
   User-facing Preview Gate copy stays plain language (no `seed-*` / internal
   option enums)—same rule as Spec (`design_spec_user_facing_jargon`).
5. Option-set Preview Gate: candidate digest + triad links; wait for pick /
   **换新批** / **在某套上改**.
   - 换新批: `--dedupe ledger --record` (machine-local history). Skipping
     dedupe → `visual_lot_dedupe_required`.
   - 在某套上改: revise that Shell in place; do not swap chrome primary axis
     unless the user asks.
6. Record `shell_selection` with `user_selected` and the Spec selection id/SHA
   it was fitted to.

Fail closed `shell_triad_required` if the interactive Shell triad is skipped.
Fail closed `prototype_option_promote_count_mismatch` if Shell was offered as
dual-only. Fail closed `shell_spec_tokens_missing` / `shell_wireframe_only` if
any option violates the Shell artifact rules above.

**Unattended (explicit only)**

1. Produce **one** Shell: `shell_match` only, fitted to the unattended Spec
   (draw one chrome lot or the faithful default card; no independent palette
   seed), still meeting the product-near Shell bar.
2. Link notice + ledger; record `shell_selection` with
   `unattended_shell_match_fitted_to_spec`.

#### After Spec + Shell are chosen

Merge the **selected** (or sole unattended) Design Spec + Shell into one
deterministic Baseline package, import/readback exact ids/SHA, and lock
`prototype_template` / `visual_confirmation` / `token_sources`. Do not import a
non-selected interactive triad candidate as the project authority. After the
Baseline package is visually confirmed, run the **first mandatory Widget
Catalog extract** (see below) from that confirmed Baseline prototype.

### Authoring Steps

1. Lock `stack_capability_profile` first. Do not draw `forbidden` patterns.
2. Require `product_spec_coverage.status: ready` before Spec/Shell HTML.
3. Run **Round A** under the Mode split above. Invoke `skill_routing` Skills
   with `phase: baseline` (include `impeccable` when available to compose
   palettes from seeds drawn by `draw_visual_lots.py`). Author **Style Guide /
   Design Tokens boards only**—never a full
   journey-screen gallery as Spec (`design_spec_wrong_artifact_type`).
4. Use real project/domain labels on the Style Guide (color role names, type
   role names, component labels). Lorem ipsum or a generic marketing feature
   grid fails the Spec quality gate.
5. After Design Spec selection (or sole unattended Spec), emit/refine Design
   Tokens for that Spec (`tokens/*.json`, DTCG-oriented) under
   `engineering.theme_and_design_system.token_sources`. The selected Spec HTML
   and token JSON Must agree on roles and values.
6. Run **Round B** under the Mode split above (`phase: shell`). Every Shell
   option Must embed the selected Spec tokens and meet the product-near Shell
   bar (`shell_spec_mismatch` / `shell_spec_tokens_missing` /
   `shell_wireframe_only` if not). Shell is where landscape/portrait chrome,
   primary navigation, and Spec-styled primary surfaces appear—not Round A.
7. When merging Spec+Shell into the Baseline package, extend to high-fidelity
   journey/critical screens that map 1:1 (or documented many-to-one) onto
   adopted `product_spec_coverage.screen_coverage` rows with
   `baseline_required: true`. Unmapped Baseline screens fail closed as
   `product_spec_coverage_incomplete`. Screens Must consume locked Spec tokens.
   Prefer evolving the chosen Shell’s product-near surfaces rather than
   redrawing from a disconnected wireframe.
8. Add `implementation_notes` / `【增强实现】` where HTML is schematic.
9. Package the chosen Spec+Shell with `scripts/package_prototype.py`.
10. Call `granoflow_project_design_baseline_import`; then
    `granoflow_project_design_baseline_read` with exact
    `prototypeId`, `versionId`, and `packageSha256`.
11. Confirm the imported package hash (interactive: after triad picks / final
    confirm as needed; unattended explicit only:
    `auto_accept_recommendation`). Never auto-accept in interactive mode.
12. Store `prototype_template`, `visual_confirmation.template_package_sha256`,
    `token_sources`, `design_spec_selection`, and `shell_selection`.
13. After Baseline visual confirmation, extract chrome/shared widgets into the
    project `widgets` attachment (`widgets.yaml`)—first mandatory catalog
    write.
14. Later revisions reopen the mode-appropriate Spec/Shell rounds.
    Never resolve "current" or "latest".
15. Closing Prototype Link Digest lists every candidate offered (all triad
    links in interactive; the single Spec + single Shell in unattended).

### Contract Fidelity For Downstream Work

Downstream prototypes and code Must preserve Shell mode, primary navigation IA,
token roles, main-journey layout regions, and **locked widgets** from
`widgets.yaml`. They Should stay visually close. They Won't be judged on pixel
or spring-feel parity.

**Task / milestone `ui_prototype` (hard):**

- Must `derivedFrom` the exact Baseline `prototypeId` / `versionId` /
  `packageSha256`.
- Must **not** apply a new random visual seed (no impeccable palette re-roll,
  no Spec re-exploration). Fail closed `task_prototype_seed_forbidden`.
- Before inventing a new chrome/control/pattern, check `widgets.yaml` and
  reuse when the same role exists (`reuse_policy: must_reuse_when_same_role`).
  Skipping reuse without rationale → `widget_reuse_required`.
- Pass **Task Prototype Craft Gate** before `visualConfirmed=true` else
  `task_prototype_craft_incomplete` (includes **Baseline fit** →
  `prototype_baseline_fit_*` / `prototype_generic_phone_frame` and product
  truth → `prototype_product_truth_violation`).
- Keep design-first; high-risk platform-coupled UI needs Tech Note conclusion
  before Readiness (`high_risk_feasibility_unresolved`).
- Interactive: **strict Spec token embed + Shell chrome language**,
  mainstream-reference-first (≥5; backfill only when mainstream `<5`) then
  dual **page expressions** (`expr_a` + `expr_b`) with functional parity
  inside the locked Design System; mix-and-match per task/page; ≥2 whitelist
  contrast axes; **side-by-side Contrast Gallery** with Baseline-fit
  - candidate digests + per-axis visible-diff captions; conditional third
    only for documented industry-peer deadlock. Fail closed
    `prototype_option_design_system_reopened` /
    `prototype_baseline_fit_*` /
    `prototype_spec_tokens_not_loaded` /
    `prototype_shell_chrome_mismatch` /
    `prototype_option_brainstorm_*` /
    `prototype_option_mainstream_skip` /
    `prototype_option_scope_mode_invalid` /
    `prototype_option_function_split` /
    `prototype_option_data_divergence` /
    `prototype_option_contrast_insufficient` /
    `prototype_option_near_duplicate` /
    `prototype_option_contrast_gallery_required` /
    `prototype_option_diff_unlabeled` / `prototype_option_third_unjustified`.
- Unattended: mainstream-first protocol then single Baseline-fitted `expr_a`
  only.
- Material Shell/token/widget catalog changes require a new Baseline version
  and catalog update—not silent drift in a task prototype.

## Widget Catalog (project `widgets.yaml`)

YAML expresses the **contract** of reusable UI modules—not full visual
geometry, motion, or platform chrome. Visual truth remains in confirmed HTML
prototypes; the catalog records identity, props, token bindings, states,
composition, reuse policy, and anchors into those prototypes.

### Slot and ownership

- Owner: project only. Logical slot: `widgets`. Default file: `widgets.yaml`.
- One current attachment. Any later extract updates this **same** slot.
- Record `widgets_attachment` (exact file name) and registry SHA/readback in
  Project Work. Missing catalog after confirmed Baseline Shell →
  `widget_catalog_required`. Stale SHA vs App readback →
  `widget_catalog_stale`.

### When to extract

1. **First mandatory extract:** after the Design Baseline package (selected
   Spec + Shell) is visually confirmed—example source is that confirmed
   Baseline prototype (`prototype_template` ids/SHA).
2. **Incremental extracts:** after every later confirmed Baseline revision or
   task/milestone `ui_prototype` that introduces or changes a reusable
   chrome/control/pattern.
3. Do not invent widgets from unconfirmed drafts.

### Example shape (Baseline prototype as source)

```yaml
# widgets.yaml — contract catalog; visuals live in confirmed prototypes
schema: granoflow.widgets
schema_version: 1
widgets:
  - id: shell.top_nav
    kind: chrome # chrome | control | pattern | page_region
    status: locked # proposed | locked | deprecated
    derived_from:
      # Example: the confirmed Design Baseline prototype (previous Spec+Shell)
      prototype_id: "<prototype_template.prototype_id>"
      version_id: "<prototype_template.version_id>"
      package_sha256: "<prototype_template.package_sha256>"
      region_id: top_nav
    tokens: [color.surface, type.body, space.s2]
    variants: [landscape, portrait]
    props:
      title: string
      selected_tab: enum
    states: [default, selected, disabled]
    composition: [shell.tab_item]
    reuse_policy: must_reuse_when_same_role
    implementation_notes: []
```

### Reuse gate

Hosts authoring any UI prototype after the first catalog write Must:

1. Load current `widgets.yaml` (App readback).
2. Prefer existing widget ids for the same role.
3. Add new rows only for new roles; lock them after that prototype is
   confirmed.
4. Never replace a locked widget's visual system via task-local random seed.

## Capability-Critical Dependencies

Established in Project Definition **Step 1** immediately after stack lock.
Record chosen packages in Project Work `engineering.dependencies.approved`
(not a separate attachment). Each critical row needs `name`, `capability`,
`capability_critical: true`, `alternatives_considered`, and
`selection_rationale`. Framework-only selection without required capability
packages fails closed as `capability_dependency_unselected`. Later tasks may
challenge and revise the same Project Work list; they must not silently swap
critical libraries in code.

For **user-visible** capabilities (TTS, push, camera, …), also maintain
`engineering.third_party_capabilities` per
`granoflow-agent-workflow/third-party-capability-matrix`: `required_platforms`,
`probe_method`, `fallback`, `in_ship_bar`, and later `probe_by_platform`.
Selection ≠ probed. Claiming full-platform support without probes fails closed
as `third_party_capability_overclaim`.

## Data Persistence And Structured Contracts

Established in Project Definition **Step 1**. Project Work records
`data_persistence`, attachment file names, and artifact registry rows. Full
shapes never live in the Project Work body YAML.

### No business database

When `data_persistence: none`, set `no_database_declaration` to an explicit
statement (for example: 本项目无业务数据库，无需设计表结构). Do not create a
table schema in `data-model.md`. Set `data_model_attachment: not_applicable`.

### Data Model (tables)

- Owner: project only. Slot: `data_model`. Default file: `data-model.md`.
- Required when `data_persistence` implies a business database
  (`embedded_db`, `server_db`, or `mixed` with DB). Record the exact file name
  in `data_and_migrations.data_model_attachment`.
- Every table uses a two-dimensional Markdown table covering field, type,
  nullability, default, keys/indexes/constraints, relations, ownership,
  retention, migration/backfill, sync/conflict, and notes.
- Include detailed prose for invariants, write owners, lifecycle, privacy,
  deletion/archive, compatibility, rollback, and unresolved decisions.
- Any later change updates this **same** project slot. Never create a second
  current data model attachment.

### JSON / structured file contracts

- Owner: project only. Slot: `json_contracts`. Default file:
  `data-contracts.yaml`.
- Required when the project defines JSON or other structured files as a
  contract. Use YAML (or Markdown embedding YAML) for shapes and field
  semantics. Record `json_contracts_attachment`.
- Do not dump full contract graphs into Project Work YAML.

### Constants catalog

- Owner: project only. Slot: `constants_catalog`. Default file:
  `constants-catalog.yaml`.
- Required when the project defines shared constants. List constant names,
  values or types, owners, and purpose in YAML. Record
  `constants_catalog_attachment`.

### Code must match attachments

Tasks that change database schema, JSON/structured file shapes, or shared
constants **must** update the corresponding project attachment and refresh
registry SHA/readback in the same task before Delivery. Code that drifts from
these attachments fails closed with `data_artifact_stale`.

## Workflows

- Owner: the entity whose scope the process describes.
- Slot: `workflows` on project, milestone, or task.
- Filename: `workflows.md`.
- One entity has one current workflows attachment. Multiple diagrams live in
  that same file.
- Every diagram has a stable id, Mermaid source, trigger, actors, preconditions,
  happy path, alternate/error paths, state/data changes, downstream handoff,
  observability, and detailed prose. A diagram without explanation is
  incomplete.

## Artifact Registry And Consistency

Project Work records the current entity, slot, attachment id, SHA, status,
source decision, and relations for every governed artifact. Before automation
or completion, verify:

- registry SHA matches App readback;
- Design Baseline package SHA matches `prototype_template` and
  `visual_confirmation`;
- referenced screen/menu/state ids exist in the baseline or are marked
  planned;
- App Shell landscape and portrait coverage is present for initialization Done;
- `widgets.yaml` exists after Baseline confirmation with registry SHA readback;
- data entities used by workflows exist in `data-model.md`;
- workflow acceptance and failure paths map to Project Work acceptance ids;
- implementation evidence does not claim completion beyond confirmed artifacts;
- stale, conflicting, missing, or unconfirmed artifacts fail closed with all
  findings returned together.
