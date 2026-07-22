# E2E Host Capabilities

How the agent probes `screenshot_capability` and `vision_capability`, derives
the verification host matrix, writes results into campaign state, and applies
policies.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-e2e-test-campaign",
  referenceId: "e2e-host-capabilities"
)
```

## Window Capability

Probe **independently** of screenshots: a PNG file does not prove a user-visible
window. Set `window_capability: available | unavailable` on campaign state,
evidence pack, and closing summary.

| Host signal                  | Probe                                                                 |
| ---------------------------- | --------------------------------------------------------------------- |
| Desktop native app           | Process running **and** an on-screen OS window (e.g. CGWindow / HWND) |
| Headed browser / webview     | Visible headed viewport (not headless CDP-only)                       |
| Simulator / emulator         | Device window or host viewer is on screen                             |
| No display / windowless bind | `unavailable`                                                         |

`capture_surface: os_window` **Must** have `window_capability: available`.

When `unavailable`, do **not** close as green / green_with_residuals or
`phase: complete`—fail closed as `e2e_campaign_window_required` (residuals cannot
waive). Mid-flight evidence may record `unavailable` for debugging only.

## Screenshot Capability

Probe once per campaign (re-probe after host change). Set
`screenshot_capability: available | unavailable` on campaign state and evidence
pack companion fields.

| Host signal                   | Probe                                                                                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------- |
| Cursor browser / computer use | `browser_take_screenshot` or desktop capture succeeds                                               |
| Flutter / desktop driver      | **Visible** device/desktop window; PNG under `temp/` from live viewport or OS window capture        |
| Playwright / Cypress harness  | **Headed** runner emits PNG to `temp/e2e-campaign/...`                                              |
| Headless CI without display   | `unavailable` → **whole campaign fail-closed** (`e2e_campaign_window_required`); do not claim green |

`display_mode` defaults to `visible_window`. Explicit `headless` fails closed as
`e2e_campaign_headless_ui_forbidden`. Pure `flutter test` without `flutter drive`
(or equivalent visible host) fails closed the same way when any journey is
`covered`.

When `available`, enforce `screenshot_policy: required_if_capable`—each declared
checkpoint **Must** produce a file under `temp/e2e-campaign/<round>/screenshots/<step_id>.png`
with `capture_surface: os_window` or `driver_viewport`.

When `unavailable`, do **not** close the campaign as green / green_with_residuals
or `phase: complete`—fail closed as `e2e_campaign_window_required` (residuals
cannot waive). Mid-flight evidence packs may still record unavailable with a
`screenshot_unavailable` residual for debugging only.

## Desktop visible-window harness tips

Stack-agnostic; Flutter examples are illustrative only (not product hardcoding):

- Process CWD may not be the repo root under drive/run — load packaged assets via
  the app bundle / asset API; write campaign artifacts under an absolute project
  root (`--dart-define` / env), never assume relative `assets/` or `temp/` paths.
- OS app sandboxes may block writes into the workspace `temp/` — prefer an
  external capture watcher, or a project-chosen Debug entitlement policy
  (Release sandbox stays on).
- Test doubles (crypto iterations, clocks, storage) **Must** match the library
  profile under test, or imports/decrypts hang or fail falsely.
- Some `integration_test` / `flutter drive` bindings create **no** OS window —
  probe `window_capability` first; if unavailable, switch to a headed
  `flutter run` (or equivalent) visible runner before claiming `covered`.
- If Project Work declares a fail-closed `seed_corpus` special requirement, UI
  import journeys **Must** use that corpus (same rule as IT)—do not substitute
  random fake files.

## Secure Storage Capability

Probe independently when any Acceptance Outcome uses
`layer: platform_secure_store` (see
`granoflow-agent-workflow/acceptance-outcome-contract`):

| Host signal                         | Probe                                                             |
| ----------------------------------- | ----------------------------------------------------------------- |
| Production secure storage available | One real write+read (or entitled Keychain/Keystore path) succeeds |
| Missing entitlement / plugin fail   | `unavailable`                                                     |
| Test double / in-memory fake only   | **Not** a valid probe—do not claim `available`                    |

Set `secure_storage_capability: available | unavailable` on suite plan /
closing summary when closing that layer. Closing
`platform_secure_store` without a probe fails closed as
`e2e_campaign_secure_storage_unprobed`; `unavailable` fails as
`e2e_campaign_secure_storage_unavailable`.

## Vision Capability

Probe whether the active model/host can **read images** for acceptance:

| Host signal                             | Probe                            |
| --------------------------------------- | -------------------------------- |
| Multimodal chat (images in context)     | `vision_capability: available`   |
| Text-only model or blocked image upload | `vision_capability: unavailable` |

Policies:

```yaml
vision_policy: on_if_capable
vision_result: not_run | passed | failed | skipped
```

When `vision_capability: available`, run vision against checkpoint screenshots
using `vision_criteria` from the suite plan when present.

Also, when Evidence Pack `prototype_task_reviews.reviews` is non-empty (Phase B
of `granoflow-agent-workflow/prototype-implementation-fidelity`—every finalized
task-level prototype), run vision compare of each screenshot against its
`prototype_link` when capable; ignore orientation / desktop-vs-mobile
form-factor adaptations as non-diffs; re-answer the three fidelity questions
for remaining material gaps; record per-row `vision_compare`, `ai_pass`, and
`decision` (`matched` | `revise_to_prototype` ⇒ remediate without user confirm

- next full round). `keep_implementation` is forbidden until
  `user_final_acceptance`. Screenshots + prototype links **Must** still be shown
  in the full compare loop regardless of vision.

When skipped (policy off, timeout, or host block), set `vision_result: skipped`
and add residual `e2e_campaign_vision_skipped` or `vision_skipped`.

## Verification Host Matrix (multi-device)

Derive **where** to run UI journeys from Project Work
`scope.supported_platforms` (+ optional
`engineering.quality_gates.verification_host_matrix` / `ship_bar`). Never
hardcode product-specific flows into this Skill.

```yaml
schema: granoflow_verification_host_matrix_v1
derived_from: [scope.supported_platforms]
concurrency: parallel_when_capable # or sequential
primary_form_factors: [] # phone_portrait | tablet_landscape | desktop_landscape | web | ...
hosts:
  - id: desktop_native
    kind: desktop | simulator | emulator | physical_device | remote_farm | browser | other
    platforms: [macos]
    status: unprobed | available | unavailable | deferred_external
    residual_code: null
assignment_policy: journey_at_least_one_capable_host
```

### Derivation (required kinds)

| Platforms include              | Required host kind (candidate) |
| ------------------------------ | ------------------------------ |
| macos / windows / linux        | `desktop`                      |
| ios                            | `simulator` (prefer)           |
| android                        | `emulator` (prefer)            |
| web only (no native platforms) | `browser`                      |
| platforms empty                | **no** invented desktop host   |

Probe each candidate once per campaign. When ≥2 hosts are `available` and
`concurrency: parallel_when_capable`, the agent **May** run disjoint journey
subsets in parallel. Do not claim green for a host that did not execute its
assigned journeys.

Unavailable **required** host → residual `e2e_campaign_host_unavailable` (or
`verification_host_unavailable`). Closing as `green` without residual fails
closed; `green_with_residuals` requires plain-language leftovers.

### Ship bar

| Value               | Meaning                                                              |
| ------------------- | -------------------------------------------------------------------- |
| `market_smoke`      | **Default** when omitted. Every adopted journey on ≥1 capable host   |
| `form_factor_smoke` | `market_smoke` + each declared primary form factor has ≥1 checkpoint |
| `full_campaign`     | Full matrix × required hosts                                         |

Hard fails for `market_smoke` (agent judgment; not all are lintable): crash on
launch, primary journey blocked, destructive wrong-key / data-loss path,
declared primary form factor missing with no residual.

## User-Facing Copy

Tell the user:

- Screenshots are saved in the project **temp folder** and shown in chat.
- Whether vision ran or was skipped (plain language—not internal codes alone).
- Which hosts ran (desktop / simulator / emulator) in everyday language.

Do **not** mention git, `.gitignore`, or repository hygiene to the user. When
the workspace is a git repo and `temp/` is not ignored, silently ensure ignore
(see `e2e-evidence-pack.md`).

## Third-Party User-Visible Capabilities

Load `granoflow-agent-workflow/third-party-capability-matrix` when Project Work
lists `engineering.third_party_capabilities` rows with `in_ship_bar: true`
(TTS, push, camera, …).

On each host that maps to a `required_platforms` entry:

1. Run the row’s `probe_method` once (e.g. one TTS utterance / engine ready).
2. Write `probe_by_platform[<platform>] = available | unavailable`.
3. Inventory-only or stub doubles are **not** probes.

Before bare `green` or `user_path_claim: full_user_path`, every ship-bar row’s
required platforms covered by this campaign’s host matrix must be `available`
or residualled with Closing leftovers. Claiming 全平台 / all-target-platform
success while any required platform is `unprobed` or `unavailable` fails closed
as `third_party_capability_overclaim` (also `third_party_capability_unprobed`).

Lint with
`skills/granoflow-agent-workflow/scripts/lint_third_party_capability_matrix.py`
(`--require-complete` / `--claim-full-platform` as appropriate).

## Write-Back

After probing, update:

1. `granoflow_e2e_campaign_state_v1` — capability enums + policies + optional
   `host_matrix` snapshot
2. `granoflow_e2e_evidence_pack_v1` — `screenshot_capability` mirror when needed
   for lint cross-checks
3. Project Work `engineering.quality_gates.verification_host_matrix` when the
   campaign first derives it (provenance `recommended` / `inspected_fact`)
4. Project Work `engineering.third_party_capabilities.probe_by_platform` when
   third-party rows were probed

Lint campaign state, suite plan, coverage, and host matrix with
`scripts/lint_e2e_campaign_artifacts.py`.
