# Stack Realization Notes (Task / Milestone UI)

Apply this contract whenever the host authors a post-Baseline task or milestone
`ui_prototype`. It forces an explicit map from **what the HTML shows** to **how
the user's chosen tech stack will realize or degrade it**, so prototypes stay
inside the deliverable surface instead of Web-only showcase.

HTML can usually draw anything another stack can draw—and more. The limit is
the **selected stack**, not HTML. Notes live **outside** the simulated product
UI (see `user-visible-copy-boundary`).

## Mandatory Load (fail closed if skipped)

Before authoring draft-1 HTML (after `ui_component_effect_matrix` is lint-clean):

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "stack-realization-notes"
)
```

Skipping fails closed as `stack_realization_notes_unread`.
Seeing Craft Gate or effect-matrix prose alone does **not** count.

Also load `ui-component-effect-matrix` and keep that record green
(`component_effect_matrix_ok: true`).

## Authority Split

| Artifact                               | Role                                                |
| -------------------------------------- | --------------------------------------------------- |
| `ui_component_effect_matrix_v1`        | Eligibility / ranking / forbidden / fallbacks       |
| `granoflow_stack_realization_notes_v1` | Human-readable stack mapping for each selected role |
| HTML `ui_prototype`                    | Visual preview of the **deliverable** target        |
| `【增强实现】` in-frame markers        | Schematic only; must match `enhancement_schematic`  |

## Hard Rules

1. **Matrix first:** do not author HTML while effect-matrix lint ≠ ok, or while
   any selected candidate is `forbidden`, or any behavior-changing replacement
   is still `pending_user_decision`.
2. **Selected coverage:** every matrix candidate with `decision: selected` Must
   have **exactly one** notes row keyed by `role` (or `candidate_id` when roles
   collide). Extra notes rows without a selected candidate fail closed.
3. **No showcase-by-default:** main-path controls, navigation, and effects in
   HTML Must be `native_supported` or `adapted_fallback` (or
   `user_accepted_degrade` after explicit accept). `enhancement_schematic` is
   allowed only for marked schematic regions and is **not** the default
   acceptance look.
4. **Outside product UI:** notes, stack API names, and degrade policy Must not
   appear as in-frame product copy.
5. **Serial revision binding:** each draft on
   `granoflow_prototype_revision_ledger_v1` Must record
   `component_effect_matrix_sha256` and `stack_realization_notes_sha256`
   (exact 64-hex of the records used for that draft).

## Schema

```yaml
stack_realization_notes:
  schema: granoflow_stack_realization_notes_v1
  contract_loaded: true
  stack_id: "<project stack id, e.g. flutter>"
  platform_matrix_sha256: "<64 hex>"
  component_effect_matrix_sha256: "<64 hex>"
  rows:
    - role: bottom_nav # or stable role from matrix
      candidate_id: null # optional; required when role alone is ambiguous
      html_surface: "<what the prototype shows>"
      stack_realization: "<stack API / Widget / pattern>"
      disposition: native_supported # native_supported | adapted_fallback | enhancement_schematic | user_accepted_degrade
      fallback_or_schematic_note: null # required non-empty for adapted_fallback | enhancement_schematic | user_accepted_degrade
  notes_sha256: null # optional canonical digest of notes body excluding this field
```

### Disposition meanings

| Disposition             | Meaning                                                            |
| ----------------------- | ------------------------------------------------------------------ |
| `native_supported`      | Stack can ship the shown treatment with named API/Widget           |
| `adapted_fallback`      | Same role/behavior via a documented stack-native adaptation        |
| `enhancement_schematic` | HTML is schematic (`【增强实现】`); not default acceptance look    |
| `user_accepted_degrade` | User (or unattended grant) accepted a weaker look/behavior vs HTML |

## Lint

```text
python3 skills/granoflow-agent-workflow/scripts/lint_stack_realization_notes.py \
  path/to/notes.yaml \
  --matrix path/to/ui_component_effect_matrix.yaml
```

When `--matrix` is omitted, only structural checks run; serial revision /
`visualConfirmed` require matrix-bound coverage (`ok` with selected-role match).

Fail closed:

- `stack_realization_notes_unread`
- `stack_realization_notes_required`
- `stack_realization_notes_incomplete`
- `stack_realization_notes_matrix_mismatch`
- `stack_realization_notes_coverage_incomplete`
- `stack_realization_notes_disposition_invalid`
- `stack_realization_notes_lint_failed`

Set `craft_checklist.stack_realization_notes_ok: true` only after lint ok.
Missing notes blocks draft-1 and `visualConfirmed`
(`prototype_revision_stack_gates_incomplete` when ledger SHAs are absent).

## Admission Test (host self-check)

1. Loaded this reference + effect-matrix via MCP?
2. Effect-matrix lint green; no selected `forbidden` / open user decisions?
3. Every selected matrix role has one notes row with stack realization text?
4. Schematic HTML regions marked `【增强实现】` and disposition
   `enhancement_schematic`?
5. Notes kept outside product UI?
6. Each serial draft binds matrix + notes SHA?
