# Authoring Contract

## Preview Gate

- Preview must exist before any confirmed write.
- Confirmed write is the only valid formal write mode.

## Constraints

- [must] Expose one deep orchestration interface and delegate capture, Analysis, Plan, Execution, Delivery, completion, cards, and waiting to their existing owners. (deep-module design and shared-contract preference)
- [must] Treat plain natural language as primary; shortcuts are optional route overrides and must not be required for semantic understanding. (user request)
- [must] Use explicit facts rather than a fake numeric confidence score: current-work relation, imperative strength, outcome clarity, boundary clarity, evidence sufficiency, timing signal, and target ambiguity. (context-aware routing requirement)
- [must] Preserve inbox capture with no due date for incidental side thoughts, someday/later requests, weak placement, and missing timing evidence. (minimal-interruption capture contract)
- [must] Batch unresolved directional questions once and continue automatically when the user has invoked an approved bounded local-run profile and all grills pass without scope drift. (user request to reduce unattended waiting)
- [must_not] Never infer publish, push, deletion, payment, login, secrets or 2FA, external messaging, approved-asset overwrite, or scope expansion from context or a shortcut. (delegated authorization boundary)

## CLI Contract

- Generated Python entrypoints must support `python3 <script> --help` with exit code 0.
- Any entrypoint with side effects must support `--dry-run` or an equivalent preview mode.
- Dry-run output should include mode, mutates_state, planned_actions, artifacts, and warnings.
