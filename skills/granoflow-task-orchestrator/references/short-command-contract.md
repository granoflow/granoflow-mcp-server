# Short Command Contract

Natural language is the primary Interface. Short commands are optional explicit
route overrides for speed; they are not required for understanding Chinese,
English, or other languages.

## Commands

| Command | ASCII alias | Route          | Normal stopping point                                                                                    |
| ------- | ----------- | -------------- | -------------------------------------------------------------------------------------------------------- |
| `gf`    | none        | automatic      | selected from context                                                                                    |
| `gf记`  | `gf+`       | `capture`      | task id readback                                                                                         |
| `gf析`  | `gf?`       | `analyze`      | ready-to-confirm A or blocker; **does not invent 定稿**. User 确认/定稿 → opens Plan same wave           |
| `gf规`  | `gf>`       | `plan`         | finish A if needed; UI Plan Entry acceptance; then P + readiness (**no second Planning-permission ask**) |
| `gf做`  | `gf!`       | `run`          | A→P after 定稿; **pack accepted** before code; D uploaded and task `done`                                |
| `gf完`  | `gf.`       | `finish_audit` | evidence-backed closure                                                                                  |

Soft-merge / affinity: Analysis **确认/定稿** (or `gf规` / `gf做` when A is
ready) opens Plan for the same task—no second 「开始 Plan」. `gf析` alone stops
before 定稿. UI tasks still Must pass Plan Entry Prototype Acceptance
(auditable `file://` digest, then `verbal` / App / unattended auto-accept)
before Plan content—non-UI skips. Interactive milestone Plan acceptance pack
confirmation is a real stop. **Scheme 1:** no Execution until that milestone
pack is `accepted` (or valid unattended Planning grant).

The text after the command names the target and scope. If the target is
ambiguous because multiple existing tasks match, the host must not update one
by guess.

## Whole-project unattended (canonical)

Natural language may request a full unattended project pipeline without a `gf*`
shortcut. Treat an explicit unattended whole-project generate-and-deliver
request as `run` scope across project definition → portfolio → Scheme 1
milestone loops → final delivery / E2E, and apply
`granoflow-agent-workflow/unattended-interaction-contract` plus the
**Unattended Entry Continuity Checklist** in `long-task-run-continuity`
(Project E2E SoT + Layer B/C probe/arm or `host_wake_unavailable_notice`).

Canonical Chinese trigger (example):

```text
请用无人值守模式根据 docs 下的产品文档和用户故事生成 granoflow 项目并完成和交付它。长跑维护 Project E2E SoT，并在宿主支持时按 SoT next_step 定时唤醒续跑。
```

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
