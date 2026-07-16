# External Skill Routing

Read this reference whenever Task Work, Execution, Delivery, or Review may
benefit from a Skill that is not bundled with Granoflow MCP.

Granoflow MCP is the control-plane read/write surface. It never scans a host's
Skill directories, installs third-party software, or invokes external Skills.
The host Agent/runtime discovers, invokes, installs, and verifies Skills in its
own environment.

## Routing Record

The active Task Work Document owns the complete pre-execution capability
decision. When Planning is triggered, it adds only node-relevant strategy in the
same document family.

```yaml
external_skills:
  - skill: <stable skill name>
    source: <repository, plugin, package, or provider>
    phase: analysis | planning | execution | delivery | review
    purpose: <required capability and reason>
    invocation_mode: model_allowed | user_only | unknown
    availability: available | missing | unknown
    decision: selected | install_offered | install_approved | declined | fallback | not_required
    result: pending_user_decision | used | unavailable | install_failed | invocation_failed | model_fallback
    evidence: <host observation, produced artifact, applied contract, or none>
```

Use `available` only after host-side discovery. MCP responses and assumptions do
not prove host availability. Record actual output, an observable artifact, or
the applied Skill contract as evidence; never record hidden reasoning.

## Select By Need And Phase

Select only Skills whose trigger and capability match the task and current
phase. Never invoke every installed Skill mechanically.

- Task Work Analysis may use diagnosis or architecture Skills to establish facts,
  boundaries, risks, and Evidence.
- Task Work Planning may use design and test-strategy Skills to define nodes and gates.
- Execution may use implementation Skills only after the user explicitly
  instructs the host to implement the unique confirmed active Work Document or
  a verified legacy Plan.
- Delivery and Review may use verification or review Skills without reopening
  execution authorization.

Using a Skill while authoring Task Work does not authorize implementation.
Do not enter an implementation Skill early merely because it is installed.

## Invocation Mode

- `model_allowed`: the Skill is relevant and its metadata permits model
  invocation. When it is available, the host may invoke it directly.
- `user_only`: the Skill has `disable-model-invocation: true` or an equivalent
  restriction. Explain the benefit and suggest that the user invoke it; the
  host must not invoke it automatically.
- `unknown`: invocation permission cannot be established. Fail closed and
  treat it as user-only until verified.

A router follows the same rule. A user-only router such as `ask-matt` may be
recommended but not automatically invoked. Do not copy a third-party
repository's changing Skill catalog into Granoflow workflow documents.

## Availability And Fallback

For a relevant Skill:

1. If it is `available` and `model_allowed`, invoke it and record `used` plus
   evidence.
2. If it is `available` and `user_only`, suggest explicit user invocation.
3. If it is `missing` or `unknown` and materially relevant, make one installation
   suggestion and record `install_offered + pending_user_decision`.
4. If there is no answer, remain waiting. Do not install, infer refusal, or claim
   fallback. Resume from the same waiting record without repeating the offer.
5. If the user approves the displayed source, scope, and command, record
   `install_approved`, install only that confirmed unit, then rediscover it and
   account for any required host reload before treating it as available.
6. If the user declines, record `declined` and `model_fallback`, acknowledge the
   fallback once, and continue with the current model's capabilities.
7. If installation, rediscovery, reload, or invocation fails, record the failure and
   continue with `model_fallback`.

Do not repeat the same suggestion for the same task, Skill, source, installation
scope, and missing reason. This is not a permanent refusal: a new task, a user
request, or a material capability change may justify a new suggestion.

Only block when the user explicitly made the Skill a hard dependency and the
task objectively cannot continue without it. A missing optional Skill never
cancels the task.

For Task Work Grill work, the MCP-bundled Analysis and Execution Readiness
checks remain mandatory phase gates. An available model-invocable
`grill-finalizer` is an optional enhanced evidence path before a bundled gate
concludes; it does not replace the bundled checklist or decide the phase result.
`grill-me` declares `disable-model-invocation: true`,
so route it as `user_only`: suggest user invocation and accept its returned
result, but never invoke it automatically. Select only the relevant gstack or
other provider reviewer; do not install or invoke an entire family. A missing
optional provider does not waive, block, or weaken a bundled gate. After a
decline or failure, record honest `model_fallback` evidence and still complete
the bundled checklist without claiming equivalence to a provider that did not
run.

The first-run onboarding contract is the only collection-install exception:
when `granoflow-first-run-import/references/recommended-external-skills.md` is
active, the host may offer every unavailable recommended collection as one
default all-install choice. This exception changes installation breadth only.
Runtime routing still invokes only relevant, permitted Skills and never invokes
an entire family mechanically.

## Installation Confirmation

Installation changes the host environment and may use the network. Before any
installation, the host must show:

- the exact Skill or capability that is missing and its task-specific benefit;
- the verified canonical source and license when available;
- the actual installation scope: one Skill, a collection, plugin, repository,
  or repository configuration;
- the verified command that will run;
- any known account, network, cost, data-outbound, reload, or restart impact.

Ask for explicit confirmation of that exact source, scope, and command. A
different source, scope, or command requires a new confirmation. Do not guess
an installation command. If the canonical command cannot be verified, provide
the source and recommend manual installation instead.

After installation, rediscover the Skill in the host environment and account
for any required host reload. A successful command exit code alone does not
prove `available`. Failed installation or rediscovery becomes
`install_failed -> model_fallback`.

Installation confirmation authorizes only the displayed installation. It does
not authorize a Task Work draft, Analysis/Planning confirmation, implementation, commit,
push, publishing, login, payment, secrets, deletion, messages, or other
irreversible work.

Suggesting installation does not authorize copying, packaging, licensing, or
redistributing an external Skill. This workflow does not create a Bundle,
installer, license project, registry, or distribution project; any such scope
expansion requires a separate user decision.

## Precedence And Authorization

Project and Granoflow rules take precedence over an external Skill:

```text
current explicit user instruction
  > project AGENTS/CLAUDE/repository rules
  > confirmed Granoflow Task Work, Authorization Matrix, and phase gates
  > external Skill method
```

If a Skill asks to commit, push, create issues, publish, install dependencies,
expand scope, or perform another action that the higher rules did not authorize,
skip that action and record the conflict. Invoking a Skill never grants new
authority.

## Software Development Collection

Consider engineering Skills such as those from `mattpocock/skills` only when
the task involves code, tests, builds, packages, engineering repositories, or
code-bearing MCP, Agent, or Skill development. Choose from host-visible trigger
metadata according to the actual need; do not maintain or invoke the complete
collection.

Do not route this collection for ordinary copywriting, manga design, animation
ideas, non-code research, or general administration. Discussing a Skill's
positioning or prompt-only workflow does not by itself make the task software
development.

Whether external engineering Skills are available or not, retain the software
Profile's minimum lint, format, type/static, tests, build, runtime smoke,
compatibility/migration, and real-user-surface Evidence.
