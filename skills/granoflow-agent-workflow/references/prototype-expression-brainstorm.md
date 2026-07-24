# Prototype Expression Brainstorm

Apply this contract whenever the host authors an interactive **prototype option
batch**—including Project Definition **Design Spec** and **App Shell** triads,
and post-Baseline **task/milestone page expressions**. It forces an explicit
**mainstream-reference-first** candidate set before HTML, and prevents splitting
one product surface into incomplete options.

For task option count, required layout families, and final multi-layout
confirmation, also load `responsive-prototype-finalization`.

## Mandatory Load (fail closed if skipped)

Before authoring HTML for any interactive option batch below, the host **Must**
load this reference via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-expression-brainstorm"
)
```

Skipping the load fails closed as `prototype_option_brainstorm_unread`.
Seeing `SKILL.md` or Craft Gate prose alone does **not** count.

Also load `user-visible-copy-boundary` before in-frame product copy (separate
gate). Design Spec Style Guide boards follow Spec artifact rules; still keep
reviewer-only candidate theses outside user-facing Preview Gate jargon.

## Layers And Promote Counts (hard)

Do **not** collapse either Design Spec HTML round or Shell into task-level
duals. Promote count is layer-specific:

| Layer                                | When                                         | Candidate pool                        | Promote (interactive) | Option ids                                         |
| ------------------------------------ | -------------------------------------------- | ------------------------------------- | --------------------- | -------------------------------------------------- |
| **Design direction chooser**         | Project Definition Design Spec Round 1       | Product-fit candidates per dimension  | **4 per dimension**   | User-visible `1a`…`6d`; internal recipe ids hidden |
| **Complete Design Spec**             | Project Definition Design Spec Round 2       | ≥5 (mainstream first; backfill if <5) | **3, justified 2**    | `spec_a`, `spec_b`, optional `spec_c`              |
| **App Shell**                        | Project Definition Round B (after Spec lock) | ≥5 (mainstream first; backfill if <5) | **exactly 3**         | `shell_match`, chrome challenger a/b (deck labels) |
| **Task / milestone page expression** | After Baseline lock                          | ≥5 (mainstream first; backfill if <5) | **2 or justified 3**  | `expr_a`, `expr_b`, optional `expr_c`              |

**Unattended (explicit only):** candidate protocol still runs; promote **one**
faithful option (`spec_match` / `shell_match` / `expr_a`) per that round’s Mode
split.

Fail closed `prototype_option_promote_count_mismatch` when the gallery offers
the wrong count for the layer (e.g. Spec offered as AB-only, or task page
expressions offered as a Design Spec triad).

## Functional Parity (hard)

All promoted options in a batch are **presentations of the same product
surface / same Must set** for that layer.

They **Must** be identical on:

1. **Capabilities / Musts** — every authorized action, navigation Must, recovery
   path, Spec token **role**, or Shell primary-nav Must for that round appears
   in **every** promoted option (or is honestly marked `【增强实现】` in all with
   the same invariants).
2. **Data / content fields** (task page expressions and journey Shell surfaces)
   — the same objects, metrics, labels, and sample domain facts. Presentation
   may reorder, group, or progressively disclose the **same** fields; it may
   not invent, drop, or swap domain facts to create contrast.
3. **Required states** — default / empty / error / success / disabled states
   required by Scope (or Spec/Shell Musts) are covered by **each** promoted
   option (in-frame or via shared scenario controls **outside** product UI).

They **May** differ only on the layer’s allowed contrast:

- **Design Spec:** seed-driven craft (palette, type pairing, density/spacing,
  component emphasis) inside shared product IA Musts—via
  `draw_visual_lots.py --kind spec --count 3`.
- **App Shell:** chrome / nav structure / breakpoint expression **fitted to the
  selected Spec**—via `draw_visual_lots.py --kind shell --count 3`; no second
  visual system.
- **Task page expressions:** Craft Gate whitelist axes inside the locked Design
  System (hierarchy, density, interaction chrome pattern, state emphasis,
  progressive disclosure, task-local secondary nav).

### Illegal “contrast” (feature / logic split)

Fail closed `prototype_option_function_split` when promoted options differ by
omitting or relocating a required capability/Must. Examples:

| Bad split                                                     | Why it fails                                            |
| ------------------------------------------------------------- | ------------------------------------------------------- |
| Spec A covers brand tokens; Spec B omits type scale           | Style Guide Musts must be complete on every Spec option |
| Shell A has primary nav; Shell B hides a required destination | Shell IA Musts are shared                               |
| Task A = edge hot-zones only; B = top/bottom chrome only      | Feature split disguised as presentation                 |
| Task A = TTS playing; B = TTS unavailable grey                | Product **states**, not alternative expressions         |
| Task A = TOC only; B = search only                            | Both capabilities must exist in each expression         |

Fail closed `prototype_option_data_divergence` when sample domain data differs
between frames without a documented scenario switch that applies to **all**
promoted options in the batch.

## Candidate Protocol (before HTML)

**Source strategy (hard): `mainstream_first`.**

Do **not** open with pure invention. Build the candidate pool in this order:

### 1. Scope mode (AI decides; fail-open default)

Before listing products, choose how wide “mainstream” is for **this** surface:

| `scope_mode`       | Meaning                                                               |
| ------------------ | --------------------------------------------------------------------- |
| `same_category`    | Same product category / genre peers                                   |
| `capability_match` | Any mainstream product that exposes the **same capability / surface** |

Rules:

1. AI **May** prefer `same_category` when category peers are rich and comparable.
2. AI **May** prefer `capability_match` when the surface is cross-category (e.g.
   reader chrome vs media player chrome) or category peers are thin.
3. When the host **cannot decide confidently**, set
   `scope_mode: capability_match` and
   `scope_mode_rationale: ambiguous_default_capability_match`
   (or equivalent one-line that states the ambiguous-default).
4. Record a one-line `scope_mode_rationale` either way.
5. Illegal / missing `scope_mode` fails closed
   `prototype_option_scope_mode_invalid`.

Same-category is **not** mandatory. Capability-match peers are first-class when
chosen (or defaulted).

### 2. Mainstream product references (primary)

Collect distinct mainstream products that match `scope_mode`, each mapped to a
**presentation thesis** on layer-legal contrast axes.

Each mainstream reference **Must**:

- name a real, publicly observable product;
- describe the transferable expression pattern (not a feature checklist);
- map to allowed contrast axes for this layer;
- cover the full Must/Scope set (`covers_full_scope: true`) when promoted or
  kept as a live candidate.

Target band for the **combined** pool remains **5–8** candidates. Fewer than 5
total fails closed `prototype_option_brainstorm_incomplete`. More than 8 is
allowed only when the host records why five-to-six was insufficient.

### 3. Brainstorm backfill (only when mainstream < 5)

If fewer than **5** qualified mainstream references exist:

1. Invent presentation candidates **only** to fill the deficit up to ≥5.
2. Record `brainstorm_backfill` entries and a non-empty
   `brainstorm_backfill_reason`.
3. Backfill candidates still obey Functional Parity and layer-legal axes.

If `mainstream_count ≥ 5` and `brainstorm_backfill` is non-empty, fail closed
`prototype_option_mainstream_skip` (pure invention must not pad an already
sufficient mainstream set).

If `mainstream_count < 5` and backfill is missing or still leaves total `< 5`,
fail closed `prototype_option_brainstorm_incomplete`. Missing
`brainstorm_backfill_reason` when backfill is used fails closed
`prototype_option_backfill_unjustified`.

### 4. Candidate principles (all sources)

1. **No capability tax for variety** — every candidate Must cover the full
   Must/Scope set for that layer. Do not drop features to make a candidate
   “cleaner.”
2. **No logic breakage** — candidates Must preserve implementation-valid flows
   (serial gates, confirmation before destructive actions, recovery paths) and
   Spec→Shell convergence (Shell never reopens Spec).
3. **Layer-legal axes only** — Spec/Shell/task each vary only what that round
   allows (see Functional Parity). Product “has feature X / lacks feature Y”
   is **not** a contrast axis.
4. **Honest discard** — candidates that violate parity, product truth, Baseline
   Musts, or high-risk feasibility are discarded with a one-line reason.
5. **States ≠ options** — alternate product states belong inside each candidate
   (or shared scenario controls), never as the sole difference between promoted
   options.

### 5. Selection (AI fit judgment → promote)

1. Record the full pool under `expression_brainstorm` (Project Work for
   Spec/Shell; Task Work `prototype_option_set` for task pages).
2. AI judges fit to locked product truth / Baseline / Spec / Shell / Scope and
   promotes the best candidates to the layer count. Complete Spec defaults to
   three and may use two only with `insufficient_distinct_third`; Shell uses
   three. Task pages default to two and may use three only with a permitted
   `option_count_reason_code`; state `selection_rationale` and why each wins on
   allowed contrast axes.
3. **Design Spec / Shell:** Design Spec draws one true-random master lot and
   derives stable candidate seeds from product fit + selection code; Shell
   still draws three chrome cards with
   `draw_visual_lots.py --kind shell --count 3 --record`. Mainstream analysis
   does **not** replace true-random lot draw.
4. **Unattended:** run the same candidate protocol, then promote exactly **one**
   faithful option.
5. Conditional task `industry_peer_c` remains only for documented Craft Gate
   deadlock (three live peers hard to separate for human review)—not the normal
   path to introduce mainstream references.

Do **not** author option HTML until the candidate record exists and
`expression_brainstorm_ok` (or Project Work equivalent checklist field) can be
set true.

## Required Record

### Task Work (`prototype_option_set`)

```yaml
prototype_option_set:
  expression_brainstorm:
    status: recorded # missing => prototype_option_brainstorm_missing
    layer: task_page_expression # design_spec | app_shell | task_page_expression
    source_strategy: mainstream_first
    scope_mode: capability_match # same_category | capability_match
    scope_mode_rationale: "ambiguous_default_capability_match" # or why category/capability
    mainstream_references:
      - id: r1
        product: "<product name>"
        surface: "<observed surface / pattern>"
        transferable_axes: [density, chrome_pattern] # layer-legal only
        thesis: "<one-line presentation thesis>"
        covers_full_scope: true
        discarded: false
        promote_as: expr_a # optional until selection
    brainstorm_backfill: [] # only when len(mainstream_references) < 5
    brainstorm_backfill_reason: null # required when backfill non-empty
    candidate_count: 6 # mainstream + backfill; band 5–8 default
    promote_count: 2 # 3 for Spec/Shell; task uses 2 or justified 3
    candidates: # unified view (mainstream + backfill); ids may mirror r*/b*
      - id: c1
        source: mainstream # mainstream | brainstorm_backfill
        thesis: "<one-line presentation thesis>"
        covers_full_scope: true
        discarded: true
        discard_reason: "<why not promoted>"
      - id: c2
        source: mainstream
        thesis: "<…>"
        covers_full_scope: true
        discarded: false
        promote_as: expr_a # Spec/Shell: spec_match | ai_challenger_a | …
    selected:
      expr_a: c2
      expr_b: c5
      # Spec example: spec_match / ai_challenger_a / ai_challenger_b
    selection_rationale: "<why these 2–3 fit this product best>"
    parity_check:
      same_capabilities: true
      same_data_fields: true # N/A for pure Style Guide boards → true if token roles complete on all
      same_required_states: true
    loaded_reference_sha256: "<sha from granoflow_bundled_skill_reference>"
  craft_checklist:
    expression_brainstorm_ok: true
```

### Project Work (Design Spec / Shell rounds)

Record the same shape under the round’s selection block (e.g. beside
`design_spec_selection` / `shell_selection`), with
`layer: design_spec | app_shell` and `promote_count: 3`. Interactive Preview
Gate Must show the candidate digest **above** the triad links.

Interactive confirm surfaces Must show a short digest (mainstream products +
backfill count if any + which options were promoted + parity / Must statement)
**above** the Contrast Gallery or Spec/Shell triad. Omitting the digest fails
closed `prototype_option_brainstorm_digest_required`.

## Lint

Prefer machine check before `expression_brainstorm_ok: true`:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_expression_brainstorm.py PATH
```

`PATH` is YAML/JSON containing `expression_brainstorm` (or a bare record).
Require `ok: true`. Lint failure keeps craft / Spec / Shell gates incomplete.

## Fail-Closed Codes

| Code                                          | When                                                                              |
| --------------------------------------------- | --------------------------------------------------------------------------------- |
| `prototype_option_brainstorm_unread`          | Reference not loaded via MCP before option authoring                              |
| `prototype_option_brainstorm_missing`         | No candidate record before HTML / gallery                                         |
| `prototype_option_brainstorm_incomplete`      | Fewer than 5 candidates, or any promoted candidate has `covers_full_scope: false` |
| `prototype_option_scope_mode_invalid`         | Missing / illegal `scope_mode`                                                    |
| `prototype_option_mainstream_skip`            | `mainstream_count ≥ 5` but non-empty `brainstorm_backfill`                        |
| `prototype_option_backfill_unjustified`       | Backfill used without `brainstorm_backfill_reason`                                |
| `prototype_option_promote_count_mismatch`     | Promoted/offered count ≠ layer require (Spec/Shell=3, task page=2)                |
| `prototype_option_function_split`             | Promoted options differ in capabilities/Musts                                     |
| `prototype_option_data_divergence`            | Promoted options show different domain data without shared scenario controls      |
| `prototype_option_brainstorm_digest_required` | Interactive gallery/triad missing candidate digest                                |

Any of the above also keeps craft / Spec / Shell gates incomplete until fixed
(`task_prototype_craft_incomplete` for task pages;
`design_spec_triad_required` / Shell Preview Gate blockers when Spec/Shell
batches are malformed).

## Relationship To Other Gates

- **Design Spec / Shell Mode split** still applies: interactive triad of three;
  true-random `draw_visual_lots`; Shell fitted to selected Spec; no Spec
  reopen at Shell or task time.
- **Baseline fit** (`prototype-baseline-fit`) still applies to every
  post-Baseline task candidate: presentation variety **inside** locked Spec
  tokens + Shell chrome language—never “escape Spec” mocks.
- **Craft Gate / Contrast Gallery** still apply to task page expressions.
- **Product truth** still applies: candidates cannot invent unauthorized
  capabilities to pad count.
- **User-visible copy boundary** still applies for product UI frames.
- **Mix-and-match** (task pages only): each page runs its own candidate
  protocol → promote-2 pair; Spec/Shell are project-level locks, not
  mix-and-match.
- **`industry_peer_c`:** optional deadlock exception only; mainstream references
  are already the default candidate source.

## Admission Test (host self-check)

Before wait-for-confirm, answer yes to all:

1. Did we choose `scope_mode` (or default `capability_match` when unsure)?
2. Did we list mainstream references first, and brainstorm only if `<5`?
3. Is the combined pool ≥5 full-scope candidates for **this** layer?
4. Did we promote the **correct count** (Spec/Shell=3, task page=2)?
5. Do all promoted options expose the same Musts/actions and the same data
   fields (or complete token roles for Spec boards)?
6. Are empty/error/disabled states shown per option (or via shared scenario
   controls), rather than as the only difference between options?
7. Would a careful reviewer describe the difference as “how it looks/flows /
   which craft seed / which mainstream pattern we adapted” rather than “what
   the product can do”?

If any answer is no, revise before confirm.
