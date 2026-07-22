# Integration Test Special Requirements

Project-level contract for **user/project special constraints** on integration
tests—beyond the default Task Integration Test Policy (≤2 authored, campaign
runs later).

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "integration-test-special-requirements"
)
```

## Why this exists

Project Work already lists `required_evidence: integration_test` and named
`integration_check` ids. That does **not** capture durable fixture policy such
as:

- a fixed seed corpus of real EPUB files for multi-book library IT
- “these files are **not** the app production seed”
- “do not substitute randomly generated fake EPUBs on the primary IT path”

Those constraints belong in Project Work so task authoring and the integration
campaign can fail closed when ignored.

## Canonical location

```yaml
engineering:
  quality_gates:
    integration_tests: [] # suite entrypaths / commands (existing)
    integration_test_special_requirements: [] # this contract
```

Empty `integration_test_special_requirements` means no extra constraints.

## Record shape

```yaml
- id: ITR-001
  kind: seed_corpus | fixture_paths | forbidden_substitute | run_constraint | other
  statement: <one durable sentence>
  corpus_paths: [] # required non-empty when kind=seed_corpus
  not_app_seed: true | false
  app_seed_paths: [] # production seed paths to keep distinct when not_app_seed
  forbidden_substitutes: []
  applies_when:
    - multi_book_library_it
    - folder_import_it
    - bookshelf_with_real_books_it
    - campaign_suite
    - all_authored_it
    # or other:<label>
  product_doc_refs: [] # e.g. docs/11-product-V02.md §9.7
  source_refs: [] # SRC-* from requirement_intake
  provenance: user_stated | recommended | inferred
  enforcement: fail_closed | advisory
```

### Kind notes

| kind                   | Meaning                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| `seed_corpus`          | Fixed real fixture files used to seed/import a test library        |
| `fixture_paths`        | Named fixture paths without “corpus as library” semantics          |
| `forbidden_substitute` | Explicit ban on a substitute pattern (also list under forbidden_*) |
| `run_constraint`       | How/where suite may run (device, isolation, no-network, etc.)      |
| `other`                | Free-form; still needs `statement` + `applies_when`                |

### `not_app_seed` (hard semantic)

When `not_app_seed: true`:

- corpus paths are **integration-test fixtures only**
- they **must not** be treated as create-library auto-injected sample books
- they **must not** be added to production app asset bundles as a seed library
- `app_seed_paths` should name the real production seed (when the product has one)

## When to fill (Project Definition / discussion writeback)

During Project Work intake or later discussion accept:

1. If product docs or the user state a durable IT fixture / corpus rule, record
   one or more `ITR-*` rows (`provenance: user_stated`).
2. Recommend defaults only when the product doc already names fixed paths;
   otherwise ask → recommend → wait (interactive).
3. Write back to the App `project_work` slot and reconfirm hash before treating
   the rule as automation-admitted.

Do **not** invent a parallel fixture SSOT outside Project Work + product docs.

## Enforcement — task authoring (write IT, do not run campaign)

Before adding any task-local integration test under Task Integration Test
Policy:

1. Read Project Work `engineering.quality_gates.integration_test_special_requirements`.
2. Select rows whose `applies_when` intersects the task’s IT scope
   (`all_authored_it` always matches; `campaign_suite` alone does **not** force
   task authoring unless the authored case is clearly in that suite path).
3. For each selected row with `enforcement: fail_closed`, apply the constraint
   in the authored test (paths, forbidden substitutes, not_app_seed boundary).
4. Record on Task Work:
   - `integration_test_special_requirements_checked`
   - `integration_test_special_requirements_applied: [ITR-…]`

Fail closed:

| Code                                               | When                                                             |
| -------------------------------------------------- | ---------------------------------------------------------------- |
| `integration_test_special_requirements_unchecked`  | Code-changing task adds IT without checking Project Work rows    |
| `integration_test_special_requirement_ignored`     | Matching `fail_closed` row not applied / substituted away        |
| `integration_test_special_requirement_as_app_seed` | Corpus with `not_app_seed: true` used as create-library app seed |

`advisory` rows must still be checked and either applied or explicitly declined
in Delivery residuals (not silently dropped).

## Enforcement — integration campaign

At campaign start / suite orchestration:

1. Load the same Project Work list.
2. Suite Plan **Must** set:
   - `special_requirements_loaded: true` after the list was read
   - `special_requirements_applied: [ITR-…]` for every `fail_closed` row whose
     `applies_when` includes `campaign_suite` or `all_authored_it`, or otherwise
     matches inventoried cases
3. Prefer shared-session journeys; when a `seed_corpus` applies, seed/import
   from `corpus_paths`—do not rebuild with random fake books for those cases.
4. Apply the same seed_corpus constraints on E2E UI import paths when the E2E
   suite exercises multi-book import (UI entry, not service_path-only).
5. Lint with `lint_integration_campaign_artifacts.py --kind suite_plan` and, when
   Project Work is available, `--project-work <path>`.

Fail closed:

| Code                                                 | When                                                                   |
| ---------------------------------------------------- | ---------------------------------------------------------------------- |
| `integration_campaign_special_requirements_unloaded` | Suite Plan claims ready without loading PW special requirements        |
| `integration_campaign_special_requirement_unapplied` | Matching `fail_closed` ITR missing from `special_requirements_applied` |
| `integration_campaign_seed_corpus_substituted`       | Primary multi-book path uses banned substitutes                        |

## Lint helpers

Validate Project Work rows:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_integration_test_special_requirements.py \
  path/to/project-work.yaml
```

Validate Suite Plan against Project Work:

```text
python3 skills/granoflow-integration-test-campaign/scripts/lint_integration_campaign_artifacts.py \
  --kind suite_plan --project-work path/to/project-work.yaml path/to/suite-plan.json
```

## Compatibility

Older App schemas may not admit this field for automation gates. Per Project
Work compatibility, unknown fields are
`preserve_without_admission_effect` until the App schema catches up. Agents
still **must** honor recorded rows when present in the current Project Work
attachment content (skill-level fail-closed), even if App admission does not
yet key on the path.
