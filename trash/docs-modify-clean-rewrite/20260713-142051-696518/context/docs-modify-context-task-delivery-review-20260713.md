# Docs-Modify Frozen Context: Task Delivery and Deferred Task Review

## Frozen target

- Target: `/Users/will/code/granoflow-mcp-server/docs-temp/73-task-delivery-and-deferred-review-workflow-v01.md`
- SHA-256: `8b4b8b436762996d44c5751eb787a7789e190797e5c7e4666ba2c8e7dcedf847`
- Stage: draft 73 implementation plan; not implementation authorization.
- Review rule: every reviewer receives this exact target and context. Reviewers may propose changes but may not edit the target.

## User-confirmed intent

1. Public names are semantic: Task Analysis, Task Plan, Task Delivery, Task Review. Local numeric document names remain internal and must not leak into public MCP semantics.
2. Quick task capture must remain fast: bind a clearly suitable project and milestone when available; otherwise use the inbox. Capture does not generate Analysis or Plan attachments.
3. Analysis is interactive and progressive. Ask the complete baseline question set with AI recommendations, accept user confirmation or additions, then draft Analysis; use grill-me for deeper follow-up. Planning and execution must not begin before Analysis is sufficient and confirmed.
4. Any task entering execution, including software development, must first have a Plan attachment. Plan nodes need explicit deliverables, delivery standards, verification evidence, and downstream startup requirements.
5. Manual acceptance nodes do not block later safe execution. The Agent always re-reads the latest Granoflow task/node state because users may change or accept work from another device.
6. Completing a task and deeply reviewing it are separate by default. A user may review later after manual acceptance or at a dedicated review time.
7. Delivery is a separate attachment that records actual delivered results and differences from Analysis/Plan. Review records time use, rework, waste, improvements, knowledge, cards, and project/milestone context promotion.
8. Analysis, Plan, Delivery, and living Project/Milestone Context must display explicit scope/freshness notices. Actual code/runtime establishes current fact; active rules/specifications establish normative intent. Conflicts must be reported and closed by updating the appropriate implementation or document.
9. Learning and software-development treatment must not weaken generality. The accepted direction is one complete base contract plus composable thin profiles.
10. The current request is docs-modify review only. No target rewrite before the user confirms the unified suggestion ledger; no code or skill implementation in this phase.

## Repository rules and constraints

- The MCP server must stay thin and call the Granoflow Local HTTP API directly.
- Do not add direct SQLite, Drift, app build/run, screenshot, release orchestration, or external CLI execution dependencies.
- Do not print or persist tokens, OTPs, recovery codes, auth URLs, or secrets.
- Existing project quality gate after code changes is `npm run check` (Prettier, ESLint, TypeScript, Vitest).
- No `.cursor/rules` directory exists in this repository; the supplied AGENTS rules are the active project rules.
- Current branch: `develop`. No implementation or publication is authorized by this review.

## Current implementation evidence

- `skills/granoflow-agent-workflow/references/task-plan-template.md` currently exposes `plan_kind: general | learning | software_development | project_73 | project_76`.
- `skills/granoflow-agent-workflow/references/task-plan-workflow.md` currently tells the Agent to write a factual review before finishing the last AI node and uses `awaiting_manual_acceptance`.
- `skills/granoflow-agent-workflow/SKILL.md`, `README.md`, and `docs/user-install-demo.md` currently describe automatic meaningful `taskReview` and Review Card creation during finish.
- `src/tools.ts` currently exposes `granoflow_task_finish` with optional `taskReview` and `reviewCardDrafts`, and implements completion followed by optional review import.
- `granoflow_task_update_structured` already has optional `expectedUpdatedAt`; node batch/update/delete tools have required optimistic-concurrency revisions.
- `granoflow_task_attachment_add_markdown` currently describes only Analysis or Plan, so Delivery support requires contract wording and validation review.
- Canonical Project Context attachments currently are `project_snapshot.yaml` and `project_rules.yaml`; milestone data uses existing description/completionSummary boundaries.
- Existing tests assert the old automatic-review guidance and legacy finish payload behavior, so the plan must distinguish changed defaults from frozen compatibility.

## Review focus

- Find missing decisions affecting scope, ownership, API capability, write order, partial failure recovery, concurrency, privacy, rollback, rollout, and acceptance.
- Verify that the plan does not invent unsupported App/API capabilities and names capability gaps as pre-implementation gates.
- Tighten the test strategy into: existing tests to reuse, tests to modify, tests to add, baseline order, post-change full order, smoke/readback order.
- Check that marker/status semantics are queryable enough for v1 without silently overwriting existing user content.
- Check that Delivery/Review idempotency and multi-device behavior can be implemented with current or explicitly gated API capabilities.
- Keep UI, database migration, publication, and automatic card creation outside this iteration unless evidence proves they are unavoidable and the user explicitly expands scope.
- Use Simplified Chinese for findings. Preserve identifiers, paths, API names, and fixed English public semantic names where necessary.
