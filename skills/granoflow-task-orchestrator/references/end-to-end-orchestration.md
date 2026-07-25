# End-To-End Orchestration

Read this for `plan`, `run`, or `finish_audit`. The Orchestrator owns ordering
and stopping points, not the implementation of every phase.

For an unattended `run`, read
`granoflow-agent-workflow/unattended-interaction-contract.md` and carry its one
zero-interruption decision across every downstream owner. Downstream phase
rules cannot reintroduce ordinary confirmation questions.

## Phase Owners

| Phase                                    | Owner                                           |
| ---------------------------------------- | ----------------------------------------------- |
| task create/update and target resolution | Granoflow Task Copilot plus dedicated MCP tools |
| A and its bundled Grill                  | Granoflow Agent Workflow Task Work owner        |
| P, readiness Grill, and execution nodes  | Task Work/Plan workflow                         |
| unattended gate evaluation               | Granoflow Delegated Authorization               |
| continuous task execution                | Granoflow Task Runner or GFMCP runner           |
| D and node/task completion               | Delivery workflow and NodeService               |
| cards                                    | Granoflow Review Card Draft owner               |
| project/milestone living context         | Granoflow Context Steward                       |

Do not copy these downstream algorithms into this skill. Route to their current
bundled references and use their structured tools.

## Composed Routes

### `plan`

Resolve or create one task. **Soft-merge Analysis→Plan:** if A is incomplete,
finish Analysis (Grill, UI prototype + `prototype_link_ledger` when UI applies)
first. **Plan Entry Prototype Acceptance Gate:** non-UI tasks skip; UI tasks
Must show an auditable Prototype Link Digest and record acceptance
(`verbal` | `app_visual_confirmed` | `unattended_auto_accept` after digest)
via `lint_plan_entry_prototype_acceptance.py` before any Planning content.
Then enter Planning **without a separate Planning-permission round trip**.
Build P (Plan Design Gate), update the living milestone Plan acceptance pack
draft, confirm P under the interaction contract, run the readiness Grill,
upload/hash-read back Task Work, create meaningful nodes, and stop
execution-ready. P does not imply execution unless a direct instruction or
valid delegated grant says so.

### `run`

Resolve or create bounded tasks. For a multi-task run, read
`granoflow-agent-workflow/parallel-task-execution`, form evidence-backed safe
batches, and dispatch each whole safe batch concurrently when the host supports
it. Then for each task:

1. create the right-depth task record and recover historical timing through the
   dedicated mutation surface when needed;
2. complete and confirm A, applying bundled Grill findings directly;
3. **auto-continue** into P in the same wave (no pause merely because A was
   reached) **only after** Plan Entry Prototype Acceptance Gate is green
   (force parent-chat digest + acceptance when UI; unattended may
   `unattended_auto_accept` only after auditable links): build and confirm P,
   refresh the living milestone acceptance pack + HTML links, batch only true
   decision-changing questions once, and run the readiness Grill;
4. validate direct or delegated authorization against current facts;
5. capture AI execution start time without changing `pending` to `doing`,
   execute only allowed local work, and verify each deliverable;
6. upload and content/hash-read back D;
7. finish the final required node and let NodeService complete the parent;
8. re-read task status and timestamps; continue with the next dependency batch
   only when the user requested a multi-task run.

An end-to-end request does not pause merely because A or P was reached, and
does **not** pause for a courtesy “开始 Plan” after Analysis is complete. It
pauses only for a real unresolved direction, unsafe target ambiguity, failed
readiness, interactive milestone Plan acceptance pack confirmation, scope
drift, forbidden action, missing material, or external authorization. Classify
the stop through the shared unattended interaction contract rather than
inventing a phase-specific prompt.

### `finish_audit`

When evidence shows the work already happened, do not create a fictional future
P. Reconstruct actual actions and evidence in the Task Work completion-audit
branch, write D, and close only when acceptance is proven.

## Batch Questions

Ask one batch containing only decisions that can change Outcome, Evidence,
Scope, Risk, target identity, or authorization. Include the current
understanding, recommendation, alternatives, impact, and requested decision.
Continue independent safe work before waiting.

## Verified Completion

Never equate local edits, a green unit test, HTTP success, or an uploaded
filename with completion. A planned task is complete only when:

- required gates and full project checks pass;
- App-owned Task Work and D content or SHA-256 readback matches;
- every required node is `finished`;
- the task readback is `status=done` with `endedAt`;
- any project/milestone context upkeep decision is recorded.

If any evidence is partial, keep the task pending and record the precise
residual instead of reporting success.
