# Short Command Contract

Natural language is the primary Interface. Short commands are optional explicit
route overrides for speed; they are not required for understanding Chinese,
English, or other languages.

## Commands

| Command | ASCII alias | Route          | Normal stopping point                                                         |
| ------- | ----------- | -------------- | ----------------------------------------------------------------------------- |
| `gf`    | none        | automatic      | selected from context                                                         |
| `gf记`  | `gf+`       | `capture`      | task id readback                                                              |
| `gf析`  | `gf?`       | `analyze`      | confirmed A or blocker (**does not** auto-enter Plan)                         |
| `gf规`  | `gf>`       | `plan`         | finish A if needed; UI Plan Entry acceptance (digest + verbal/App/unattended); then P + readiness (**no second Planning-permission ask**) |
| `gf做`  | `gf!`       | `run`          | A→P auto-continue in-task; D uploaded and task `done`                         |
| `gf完`  | `gf.`       | `finish_audit` | evidence-backed closure                                                       |

Soft-merge rule: `gf规` / `gf做` never wait for a user phrase equivalent to
「开始 Plan」after Analysis deliverables are complete for the same task.
UI tasks still Must pass Plan Entry Prototype Acceptance (auditable
`file://` digest, then `verbal` / App / unattended auto-accept) before Plan
content—non-UI skips. Interactive milestone Plan acceptance pack confirmation
and execution authorization remain real stops when those gates apply.

The text after the command names the target and scope. If the target is
ambiguous because multiple existing tasks match, the host must not update one
by guess.

## User-Facing Artifact Names

Use these labels in conversation and compact status:

- `A`: confirmed Analysis;
- `P`: confirmed executable Plan;
- `D`: actual Task Delivery.

Internal attachments keep canonical `document_type`, metadata, and compatible
filenames such as `task-work-...md` and `task-delivery-...md`. The abbreviation
reduces typing; it does not create a second artifact format.

## `gf-local-safe-v1`

The first use requires one preview and explicit approval of this fixed profile.
After that approval, a user-origin `gf做 <bounded target>` or `gf! <bounded
target>` is an explicit conditional grant for that target. It allows:

- Granoflow task reads/writes, Task Work, nodes, Delivery, and completion
  readback;
- local versioned edits inside named repositories and paths;
- local lint, format, typecheck, build, tests, and package dry-run;
- A confirmation, Planning permission, P confirmation, and execution only after
  the required phase facts pass.

It never allows publish/deploy, commit/push, deletion, login, payment,
secret/2FA access, external messages, approved-asset overwrite, or scope
expansion. These remain explicit current decisions.

The profile is conditional, not a standing blank cheque. At every phase, the
host re-reads current task state and checks both Grills, unresolved decisions,
target, repository, paths, actions, revocation, and scope drift. A failure enters
the visible waiting workflow. An empty action list or any action outside the
fixed allowlist fails closed as `action_not_declared` or `unknown_action`.

Plain `gf` never increases authorization. A semantic instruction such as
“完成这个本地任务” can directly authorize its explicit safe scope, while
“看看这个任务” cannot.
