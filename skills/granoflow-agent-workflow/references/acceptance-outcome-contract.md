# Acceptance Outcome Contract

Stack-agnostic gate: **user-required real operation results** are part of what
“green” means. A thinner path (service double, in-memory store, skipped host
capability) must not be reported as the full user result.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "acceptance-outcome-contract"
)
```

## Why this exists

Integration and E2E campaigns can turn green on a **substitute path** while the
user-facing path still fails (classic gap: domain I/O tested; Keychain /
Keystore / entitlement / session restore never exercised).

This contract forces an explicit **Acceptance Outcome (AO)** matrix:

1. State the real-world result the user / product requires.
2. Name which **layer** proves that result.
3. Close only layers actually observed with **real side effects**.
4. Defer or residual the rest—never silently upgrade a partial proof.

## Layers

| `layer`                 | What must be observed                                             | Typical closer              |
| ----------------------- | ----------------------------------------------------------------- | --------------------------- |
| `domain_io`             | Durable domain data (files, DB rows, encrypted blobs, catalogs)   | `integration_campaign`      |
| `platform_secure_store` | OS secure storage write/read (Keychain / Keystore / equivalent)   | `e2e_campaign` + host probe |
| `os_capability`         | Entitlement, sandbox, permission, or other OS capability required | `e2e_campaign` + host probe |
| `ui_human_path`         | User-visible controls driven on a real window (not service-only)  | `e2e_campaign`              |
| `session_recovery`      | Cold start / relaunch still reaches the claimed post-condition    | `e2e_campaign`              |

## Evidence kinds

| `evidence_kind`    | Meaning                                                        |
| ------------------ | -------------------------------------------------------------- |
| `real_side_effect` | Production-like persistence or host API observed               |
| `host_probe`       | Capability probe (read/write once, entitlement present, etc.)  |
| `test_double`      | In-memory / fake / injected store—**cannot** close an AO alone |

## Record shape (Suite Plan + Closing Summary)

```yaml
acceptance_outcomes_loaded: true
acceptance_outcomes:
  - id: AO-001
    statement: <one user-facing sentence: the world after the operation>
    layer: domain_io # one layer per row; split multi-layer results into rows
    evidence_kind: real_side_effect | host_probe | test_double
    status: closed | open | deferred_e2e | residual
    residual_code: null | <code>
    case_ids: [] # optional links to suite case ids
user_path_claim: service_layers_only | full_user_path
```

`user_path_claim`:

- `service_layers_only` — default for `integration_campaign`. Closing Summary
  must not imply the full UI / secure-session user journey is done.
- `full_user_path` — only when every required AO for that journey is `closed`
  with non-`test_double` evidence (normally after E2E).

## Hard rules

1. **Green has two dimensions.** Suite technical green (tests passed) is not
   enough; every in-scope AO must be `closed`, or explicitly
   `deferred_e2e` / `residual` with Closing Summary leftovers.
2. **No layer overclaim.** A campaign may close only layers it is allowed to
   close (see campaign rules below). Closing a forbidden layer fails closed as
   `acceptance_outcome_layer_overclaim`.
3. **No test-double claim.** `status: closed` requires
   `evidence_kind: real_side_effect` or `host_probe`—never `test_double`
   (`acceptance_outcome_test_double_claim`).
4. **Deferred blocks plain green.** Any `deferred_e2e` or `residual` AO forces
   campaign `outcome: green_with_residuals` or `blocked_external`, never bare
   `green` (`acceptance_outcome_overclaim_green`).
5. **Omit ≠ absolve.** When the production path needs
   `platform_secure_store` / `os_capability` / `session_recovery` /
   `ui_human_path`, those AOs **Must** appear (closed or deferred). Agents
   judge presence from Project Work + production wiring; lint enforces shape
   and overclaim once rows exist.
6. **Plain language honesty.** `plain.what_we_checked` may only describe layers
   marked `closed`. Deferred AOs belong in `plain.leftovers` / residuals.

## Campaign rules

### `integration_campaign` (service_path)

- **May close:** `domain_io` only.
- **Must not close:** `platform_secure_store`, `os_capability`, `ui_human_path`,
  `session_recovery` → use `deferred_e2e` (preferred) or `residual`.
- `user_path_claim` **Must** be `service_layers_only`.
- Closing Summary next step still points at E2E when any AO is deferred.

### `e2e_campaign` (human_path)

- **May close:** all layers, with real window / host evidence as required by
  `e2e-host-capabilities`.
- Closing `platform_secure_store` **Must** have
  `secure_storage_capability: available` (or equivalent host probe residual).
- Closing `os_capability` **Must** cite a host probe or real failure absence
  after the entitled path ran.
- `user_path_claim: full_user_path` only when no in-scope AO remains open /
  deferred for that claim.

## Host probe (secure storage)

Mirror window/screenshot probing. Before claiming
`platform_secure_store` closed:

1. Probe once: production secure-storage write + read (or documented host
   entitlement check) on the verification host.
2. Record `secure_storage_capability: available | unavailable` on E2E campaign
   state / host capabilities write-back.
3. `unavailable` → cannot close the AO; residual
   `e2e_campaign_secure_storage_unavailable` (or product fix for missing
   entitlement). Do not substitute `Memory*` / fake stores for the claim.

## Fail-closed codes

| Code                                      | When                                               |
| ----------------------------------------- | -------------------------------------------------- |
| `acceptance_outcomes_unloaded`            | Matrix missing / `acceptance_outcomes_loaded≠true` |
| `acceptance_outcomes_incomplete`          | Empty or malformed AO rows                         |
| `acceptance_outcome_layer_overclaim`      | Campaign closed a layer it must not close          |
| `acceptance_outcome_test_double_claim`    | `closed` with `evidence_kind: test_double`         |
| `acceptance_outcome_overclaim_green`      | Bare `green` while deferred/residual AOs remain    |
| `acceptance_outcome_user_path_overclaim`  | IT claims `full_user_path`                         |
| `e2e_campaign_secure_storage_unprobed`    | Closed secure-store AO without capability probe    |
| `e2e_campaign_secure_storage_unavailable` | Probe failed / entitlement missing                 |

## Relationship

| Concern                       | Owner                                   |
| ----------------------------- | --------------------------------------- |
| Seed corpora / IT fixtures    | `integration-test-special-requirements` |
| IT suite order                | `integration-suite-orchestration`       |
| E2E journey coverage          | `e2e-user-flow-coverage`                |
| Window / screenshot / vision  | `e2e-host-capabilities`                 |
| Host signing scheme selection | `code-signing-strategy`                 |
| Lifecycle stage 6→7 honesty   | `project-lifecycle-progress-board`      |

## Worked pattern (generic)

User result: “After create, I can enter and later reopen the private library.”

| AO id  | statement (plain)                     | layer                   | IT status      | E2E status |
| ------ | ------------------------------------- | ----------------------- | -------------- | ---------- |
| AO-lib | Encrypted library exists on disk      | `domain_io`             | `closed`       | (reuse)    |
| AO-key | Secret persisted in OS secure storage | `platform_secure_store` | `deferred_e2e` | `closed`   |
| AO-ui  | Create control reaches bookshelf      | `ui_human_path`         | `deferred_e2e` | `closed`   |
| AO-re  | Relaunch opens the same library       | `session_recovery`      | `deferred_e2e` | `closed`   |

IT may report technical suite green + `green_with_residuals` for deferred AOs.
Only after E2E closes AO-key / AO-ui / AO-re may anyone claim the full user
result.
