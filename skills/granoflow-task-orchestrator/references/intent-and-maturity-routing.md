# Intent And Maturity Routing

Read this before selecting `capture`, `enrich`, `analyze`, `plan`, `run`, or
`finish_audit`. The host Agent interprets natural language and supplies bounded
structured facts; the packaged router applies the stable policy. The MCP server
does not run a model or scan chat history.

## Routing Facts

Use facts, not a numeric confidence score:

- `request`: current user instruction;
- `currentWorkRelation`: `same_work | side_thought | unrelated | none`;
- `imperative`: `remember_later | register | analyze | plan | execute`;
- `outcomeClear`, `boundariesClear`, `evidenceSufficient`;
- `alreadyComplete`, supported only by inspected delivery evidence;
- `targetAmbiguous`: whether an existing-resource write could hit multiple tasks;
- timing, placement, gate, action, and authorization facts when applicable.

Do not turn absent evidence into `false` certainty. If the host cannot establish
a required fact, omit it and use the conservative route.

## Precedence

1. An explicit short command selects a route but does not waive its phase gates.
2. A confirmed `alreadyComplete` fact selects `finish_audit`.
3. `side_thought` selects `capture`, unless the user explicitly overrides it.
4. A semantic imperative selects its route.
5. `register` plus clear Outcome, boundaries, and evidence selects `enrich`;
   otherwise it selects `capture`.
6. Unsupported or contradictory facts fail closed instead of guessing.

Existing target ambiguity blocks update, finish, and review writes. New-task
capture may safely use inbox without asking.

## Route Contract

| Route          | When                                               | Task depth        | Stop point                      |
| -------------- | -------------------------------------------------- | ----------------- | ------------------------------- |
| `capture`      | side thought, later/someday, weak context          | `minimal`         | task id readback                |
| `enrich`       | registration request backed by a mature discussion | `contextual`      | rich task readback              |
| `analyze`      | explicit or semantic Analysis request              | `contextual`      | confirmed A or decision blocker |
| `plan`         | explicit or semantic Planning request              | `contextual`      | readiness passed                |
| `run`          | explicit end-to-end execution request              | `execution_ready` | D and `done` readback           |
| `finish_audit` | evidence says work already happened                | `execution_ready` | verified closure                |

Low information falls toward `capture` or `analyze`, never directly toward
execution. A route is a workflow decision, not permission for every action in
that workflow.

## Concrete Examples

- During a production fix, “顺便记一下以后加导入预览” is a `side_thought`:
  capture it in inbox without a date and return to the production fix.
- After a design discussion, “把刚才的需求建个任务” with clear Outcome,
  boundaries, and evidence is `enrich`: preserve those facts and recommend A.
- “把这两个任务实现、验证并在 GF 完成” is `run`; it still stops if the
  selected task is ambiguous, a Grill fails, or a forbidden action appears.
- If code and tests already prove the requested change exists, route to
  `finish_audit` rather than manufacturing a future Plan.

## Deterministic Router

Use `scripts/route_task_intent.py` when hosts need reproducible routing or test
fixtures:

```bash
python3 scripts/route_task_intent.py --facts /absolute/path/facts.json
```

The result includes `route`, `taskDepth`, `stopPoint`, `placementPolicy`,
`duePolicy`, `executionAuthorized`, and a stable `reasonCode`.
