# Code Signing Strategy

Cross-platform contract: when an app needs signing, **probe local host
configuration**, **auto-select** a signing scheme that matches reality (prefer
free / local paths for inexperienced users), and **declare** the choice
explicitly. **Do not ask the user to confirm** the scheme.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "code-signing-strategy"
)
```

## Why this exists

Paid developer subscriptions (e.g. Apple Developer Program) are for **store /
notarized distribution**, not for “can I build and run on my own machine?”.
Agents must not push beginners into paid signing to fix a local-run bug, and
must not silently add entitlements that require development certificates under
ad-hoc / free local signing.

Complements `acceptance-outcome-contract.md` (what user result was proven) and
platform secure-store residuals: signing is how those host capabilities become
buildable.

## Default goal

| Source                                                        | Effective `goal`    |
| ------------------------------------------------------------- | ------------------- |
| Project Work `engineering.quality_gates.default_signing_goal` | that value          |
| Field omitted                                                 | **`local_dev_run`** |

Raise to `distribute_store` / `distribute_direct` only when Project Work (or an
explicit product distribution requirement) already says so—not because a plugin
README mentioned Keychain Sharing.

## When this contract applies

Trigger before editing or when failing on any of:

- entitlements / Info.plist capabilities / sandbox keys that affect signing
- `CODE_SIGN_*`, `DEVELOPMENT_TEAM`, provisioning, keystore, Authenticode
- local `run` / `build` failures whose message is signing / entitlement / provision

Then: probe → select → declare → lint. Never ask “use free Apple ID?”.

## Probe (agent, automatic)

Stack-agnostic checklist (use host tools available on the machine):

| Platform family | Signals (examples)                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------- |
| Apple           | `security find-identity -v -p codesigning`; existing `CODE_SIGN_IDENTITY` / Team; ad-hoc `"-"` |
| Android         | debug keystore present; Gradle `signingConfigs`                                                |
| Windows         | Authenticode cert present vs unsigned local debug                                              |
| Linux           | typically unsigned local binary                                                                |

Record facts under `evidence` (no secrets, no private keys).

## Selection priority (prefer beginners)

For `goal: local_dev_run` or `device_debug`:

1. Platform free/local / ad-hoc / debug keystore paths
2. Free Apple ID personal team (device debug only when needed)
3. Paid team / Development identity **only if already configured locally** and
   (1)/(2) cannot satisfy a **declared** distribute goal or a hard OS
   requirement that cannot be implemented otherwise
4. Store / notarized Developer ID only for `distribute_*` goals

**Hard rules:**

1. Prefer changing product/plugin options to stay on free local signing (example
   class: macOS secure storage via legacy login keychain instead of Data
   Protection Keychain + `keychain-access-groups`) when `goal` is local.
2. If a capability truly requires paid provisioning, record residual
   `signing_blocked_needs_paid_or_capability` and explain in plain leftovers—
   do not silently force subscription.
3. `user_confirmation` **Must** be `not_required`. Asking is a contract
   violation (`code_signing_user_confirmation_forbidden`).

## Declaration shape

Write into Task Work / Delivery (and optionally campaign evidence):

```yaml
code_signing_strategy:
  schema: granoflow_code_signing_strategy_v1
  goal: local_dev_run # local_dev_run | device_debug | distribute_store | distribute_direct
  platform: macos # macos | ios | android | windows | linux | other:<id>
  selected:
    id: apple_adhoc_local
    label: "Free local / ad-hoc signing (no paid Apple Developer required)"
  evidence:
    identities_found: [] # non-secret summaries only
    existing_project_sign: null
  alternatives_rejected:
    - id: keychain_access_groups_entitlement
      reason: "Requires development certificate; breaks ad-hoc local build"
  user_confirmation: not_required
  declared_at: <iso8601>
```

### `selected.id` catalogs

**Local / free (default path):**

- `apple_adhoc_local`
- `free_apple_id_device`
- `android_debug_keystore`
- `windows_unsigned_local`
- `linux_unsigned_local`
- `other_local_*`

**Distribute / paid-capable:**

- `apple_development_team`
- `apple_developer_id`
- `distribute_store`
- `distribute_notarized`
- `android_release_keystore`
- `windows_authenticode`
- `other_distribute_*`

`goal` in `local_dev_run` / `device_debug` **Must not** select a distribute id
unless Project Work `default_signing_goal` is already `distribute_*`
(`code_signing_goal_distribution_mismatch`).

## Project Work field

```yaml
engineering:
  quality_gates:
    # Omit => local_dev_run
    default_signing_goal: local_dev_run # or device_debug | distribute_store | distribute_direct
```

## Campaign / Delivery hooks

| Stage                        | Behavior                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------- |
| Task Delivery (software)     | Signing-related edits require a declared strategy (`--require-strategy`)              |
| Integration / E2E build fail | Classify signing failures; re-probe and re-declare before product churn               |
| Closing Summary              | If non-default path used, one plain sentence; never imply paid required for local run |

## Lint

```bash
python3 skills/granoflow-agent-workflow/scripts/lint_code_signing_strategy.py \
  path/to/strategy.yaml --project-work path/to/project-work.yaml

python3 skills/granoflow-agent-workflow/scripts/lint_code_signing_strategy.py \
  --kind project_work path/to/project-work.yaml

python3 skills/granoflow-agent-workflow/scripts/lint_code_signing_strategy.py \
  --require-strategy
```

## Failure codes

- `code_signing_strategy_missing`
- `code_signing_strategy_incomplete`
- `code_signing_user_confirmation_forbidden`
- `code_signing_goal_distribution_mismatch`
- `code_signing_default_goal_invalid`
- `signing_blocked_needs_paid_or_capability` (runtime residual; not a lint schema error)
