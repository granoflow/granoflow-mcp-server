# Third-Party Capability Matrix

Stack-agnostic honesty gate for **user-visible capabilities that depend on
third-party libraries or host APIs** (TTS, push, camera, IAP, maps, secure
speech, etc.).

This contract does **not** guarantee every library works on every OS. It forces
agents to **declare, probe, fall back, and residual**—and forbids claiming
“full platform support” without evidence.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "third-party-capability-matrix"
)
```

## When to read

- Project Definition after capability-critical dependency selection
- Plan / Readiness when a task touches a user-visible third-party path
- Delivery for software tasks that claim those capabilities work
- Integration / E2E campaigns before `green` / `full_user_path`

## Relationship to dependency selection

| Concern                                              | Owner                                                       |
| ---------------------------------------------------- | ----------------------------------------------------------- |
| Which package is chosen                              | `engineering.dependencies.approved` (`capability_critical`) |
| Runtime platforms, probe, fallback, ship-bar honesty | **this matrix**                                             |
| AO layer proof (secure store / OS / UI)              | `acceptance-outcome-contract`                               |
| Which hosts run E2E                                  | `e2e-host-capabilities`                                     |

A critical library row without a matching user-visible capability row (or an
explicit `no_user_visible_third_party_declaration`) fails closed as
`third_party_capability_matrix_incomplete` when the product path is user-facing.

## Record shape (Project Work)

```yaml
engineering:
  third_party_capabilities:
    schema: granoflow_third_party_capabilities_v1
    contract_loaded: true
    # not_started | incomplete | complete | not_applicable
    status: complete
    # Required when status=not_applicable (no user-visible third-party caps)
    no_user_visible_third_party_declaration: null
    rows:
      - capability: tts # stable id; should match dependencies.approved[].capability when applicable
        library: null # optional package name from approved[]
        user_visible: true
        required_platforms: [ios, android, macos] # subset of project platforms
        probe_method: runtime_call # host_api | runtime_call | entitlement_check | manual
        fallback: "Show TTS-unavailable state; reading still works"
        in_ship_bar: true
        # Filled at Delivery / campaign time per platform
        probe_by_platform:
          ios: available # unprobed | available | unavailable
          android: available
          macos: unprobed
        ao_ids: [AO-tts-speak] # optional links into acceptance_outcomes
        residual_code: null
```

Valid `probe_by_platform` values: `unprobed` | `available` | `unavailable`.
Every `required_platforms` entry **Must** appear as a key once probing starts
(Delivery / E2E). Missing keys while claiming complete → incomplete.

## Hard rules

1. **Declare before claim.** User-visible third-party paths need a matrix row
   (or explicit `not_applicable` declaration) before Project Work confirm when
   primary journeys depend on them.
2. **Fallback required.** `user_visible: true` requires non-empty `fallback`
   product/UX behavior when the capability is unavailable
   (`third_party_capability_fallback_missing`).
3. **Probe before available.** Do not set any platform to `available`, close a
   linked AO, or advertise “works on <platform>” while that platform is
   `unprobed` (`third_party_capability_unprobed`).
4. **No full-platform overclaim.** Claiming ship-bar / release / Closing Summary
   “全平台可用” / “works on all target platforms” while any
   `required_platforms` entry is `unprobed` or `unavailable` fails closed as
   `third_party_capability_overclaim`. Use residuals + fallback instead.
5. **Ship bar honesty.** If `in_ship_bar: true`, E2E `ship_bar` hosts that map
   to `required_platforms` must probe those platforms (or residual). If
   `in_ship_bar: false` for a primary-journey capability, Closing Summary must
   list it as leftover (`third_party_capability_ship_bar_excluded` when omitted).
6. **AO linkage.** Capabilities that need OS/host proof should appear as AO
   rows (`os_capability` / `ui_human_path` / etc.) per
   `acceptance-outcome-contract`. Matrix `available` does not replace AO
   evidence_kind rules.
7. **Secrets stay out.** Probe notes never store API keys, vendor tokens, or
   recovery secrets.

## Campaign rules

### Plan / Delivery

- Readiness for tasks that implement a listed capability: matrix row present +
  fallback set.
- Delivery: for each `in_ship_bar: true` row touched by the task, record
  `probe_by_platform` for platforms the change affects; leave untouched
  platforms `unprobed` only when explicitly out of scope with residual—not as
  silent success.

### `integration_campaign`

- May leave host/OS probes `deferred_e2e`.
- Must not close TTS/push/camera-style AOs with `test_double` evidence.

### `e2e_campaign`

- Before `full_user_path` or bare `green`, every `in_ship_bar: true` row’s
  required platforms covered by the host matrix must be `available` or
  explicitly residualled with leftover prose.
- Probe on the real verification host (speak once, permission grant, etc.)—
  inventory-only is not a probe.

## Fail-closed codes

| Code                                       | When                                                                      |
| ------------------------------------------ | ------------------------------------------------------------------------- |
| `third_party_capability_matrix_unloaded`   | Block missing / `contract_loaded≠true` / wrong schema                     |
| `third_party_capability_matrix_incomplete` | `status` incomplete, empty rows without not_applicable, or malformed row  |
| `third_party_capability_fallback_missing`  | `user_visible: true` without fallback                                     |
| `third_party_capability_unprobed`          | Claimed available / closed AO / ship claim while platform `unprobed`      |
| `third_party_capability_overclaim`         | Full-platform or green claim while required platform unprobed/unavailable |
| `third_party_capability_ship_bar_excluded` | Primary-path capability excluded from ship bar without Closing leftover   |
| `third_party_capability_platform_missing`  | `required_platforms` entry absent from `probe_by_platform` after probing  |

## Lint

```bash
python3 skills/granoflow-agent-workflow/scripts/lint_third_party_capability_matrix.py \
  --file <artifact.json>
```

## Worked pattern (TTS)

| Field              | Example                                                                          |
| ------------------ | -------------------------------------------------------------------------------- |
| capability         | `tts`                                                                            |
| required_platforms | project `supported_platforms` that must speak                                    |
| probe_method       | `runtime_call` (one audible utterance or engine ready check)                     |
| fallback           | Grey “朗读不可用” state; text reading continues                                  |
| overclaim          | Saying “iOS/Android/桌面全平台朗读” while desktop still `unprobed` → fail closed |
