# Codex External Work Memory With Task-Review-Card Context Packs

Status: 70 analysis final

Date: 2026-07-06

Mode: feature

## 详细描述

This document analyzes how Granoflow should support a need users often express
as "I wish Codex remembered its old threads, prior work, and lessons." The
answer should not be a generic memory database, a Codex-only recall layer, or a
single `similar` search endpoint.

The stable product judgment is:

> Granoflow should expose agent-friendly context packs, while storing durable
> truth as tasks, task reviews, projects, milestones, review cards, and their
> provenance links.

This preserves Granoflow's product model for humans while giving Codex, Cursor,
Claude Code, OpenCode, and other MCP-capable agents a structured external data
source for planning, risk checks, verification, and completion review.

## Core Decision

The design center is not "find similar tasks." Similarity is only one retrieval
signal. The real capability is:

> Given the current work intent, return scoped Granoflow context that explains
> what prior work, decisions, failures, evidence, and reusable lessons should
> inform the current agent run.

The API surface may present this as a context pack, but the schema must keep
Granoflow's task-review-card model visible. Agents should see typed sources,
not anonymous text snippets.

## Responsibility Layer

Granoflow owns durable work memory:

- `Task`: the unit of work, progress, timing, status, and scope.
- `TaskReview`: the completion record for decisions, tradeoffs, evidence,
  risks, and reusable observations.
- `ReviewCard`: a durable lesson extracted from work and kept available for
  future retrieval or practice.
- `Project` and `Milestone`: scope boundaries that prevent cross-project
  contamination.
- Links between tasks, reviews, cards, projects, and milestones: provenance and
  relationship truth.

Codex and other agents own active reasoning:

- interpret the current user request;
- request Granoflow context before planning when history is likely relevant;
- cite Granoflow sources instead of saying "I remember";
- convert retrieved context into current-task planning hints, risks, and
  verification reminders;
- write back meaningful task reviews and card-worthy lessons at completion.

The MCP server remains a thin protocol layer:

- forward structured requests to the Granoflow Local HTTP API;
- expose predictable MCP tools for multiple clients;
- avoid direct database access, semantic ranking logic, or Granoflow business
  rules.

## Evidence References

The current evidence base supports the analysis, but does not yet define an
implementation plan.

- `granoflow-mcp-server/AGENTS.md`: MCP server must stay thin, call the
  Granoflow Local HTTP API directly, keep structured tool results, avoid
  secrets, and avoid direct SQLite, Drift, app build/run, screenshot, or release
  orchestration logic.
- `granoflow-mcp-server/src/tools.ts`: current MCP surface exposes task
  list/export/finish and workflow guidance, but not a first-class task context
  pack.
- `granoflow/lib/core/services/semantic_vector_search_service.dart`:
  `SemanticVectorSearchService.search(...)` embeds query text, loads ready
  vectors, and ranks candidates by cosine similarity.
- `granoflow/lib/core/services/global_search_service.dart`: app-level search
  attempts semantic groups before falling back to text and structured search.
- `granoflow/lib/core/services/ai_agent_project_context_builder.dart`: project
  context already assembles projects, milestones, tasks, nodes, and document
  attachments, and can semantic-sort milestones and tasks.
- `granoflow/lib/core/local_http_api/*`: Local HTTP API currently exposes AI
  agent task export/import/validate, historical task mutations, and review-card
  similarity preview. That is narrower than a current-work context pack.

No 71 snapshot, 72 spec, or 74 decision log is treated as an upstream truth for
this `granoflow-mcp-server/docs-temp` analysis because this repository does not
currently carry that full governance chain for the topic. If implementation
planning moves into the main Granoflow app repository, the 73 plan should decide
which long-lived specs, snapshots, or decision logs need to become authoritative.

## Why Not `similar`

Do not center the next interface around `similar`.

`similar` is too small and ambiguous:

- it sounds like a search result rather than a work context;
- it hides whether a source is a task, task review, card, project, or
  milestone;
- it encourages blind copying of old breakdowns;
- it does not naturally carry provenance, conflict state, verification evidence,
  source confidence, or instructions for current use.

A better concept is `context pack`: a typed projection that explains what prior
Granoflow records mean for the current agent run.

## Terminology

Use the following naming convention until a 73 plan freezes exact API names:

- Natural-language concept: `context pack`.
- API identifier style: `context_pack`.
- Adjectival phrase: `context-pack` only when it modifies another noun.
- Storage model name: `task-review-card model`, meaning the combined model of
  tasks, task reviews, review cards, projects, milestones, and provenance links.

Candidate names such as `granoflow_task_context_pack` or
`granoflow_agent_context_pack` are examples, not final endpoint or MCP tool
names.

## Context Pack Shape

A good context pack keeps product semantics visible:

```json
{
  "model": "granoflow_task_review_card_context_v1",
  "currentTask": {
    "id": "task_123",
    "title": "Publish MCP server"
  },
  "projectContext": {
    "id": "project_1",
    "title": "Granoflow MCP"
  },
  "relatedTaskReviews": [
    {
      "taskId": "task_456",
      "taskTitle": "Repair npm 2FA publish blocker",
      "reviewSummary": "Cloud version truth must be checked before release.",
      "whyRelevant": "Same release workflow and same npm failure mode.",
      "sourceKind": "task_review"
    }
  ],
  "relatedReviewCards": [
    {
      "cardId": "card_789",
      "front": "Why check cloud version before npm publish?",
      "back": "Because local version may already be occupied."
    }
  ],
  "recommendedUse": {
    "planningHints": [],
    "risksToCheck": [],
    "verificationHints": [],
    "doNotUseFor": ["blind_copying_old_plan"]
  }
}
```

This example is intentionally illustrative. A 73 plan should choose the exact
field naming style and response schema. The important requirement is that the
agent can distinguish stored facts from inferred recommendations.

Avoid this shape:

```json
{
  "memories": [
    {
      "text": "Npm releases need cloud version checks."
    }
  ]
}
```

That loses the Granoflow model and turns the result into generic RAG text.

## Retrieval Shape Judgment

Context-pack retrieval should not rely on semantic similarity alone.

The candidate set should be scoped first, then ranked:

1. Scope by explicit task, project, milestone, date, user query, or agent
   work intent when available.
2. Include existing relationship signals such as task-card links, task-note
   links, project membership, milestone membership, and task review content.
3. Use semantic vector search as a ranking and recall signal, not as the only
   source of truth.
4. Preserve typed entity groups instead of flattening every result into one
   score-only list.
5. Return uncertainty and empty-state reasons when evidence is thin.

The 73 plan should decide the first minimal query strategy. A conservative first
version can start with project or task scope and use semantic search only as an
ordering signal where existing app services already support it.

## Data Model Judgment

Do not introduce a generic first-class `memory` table as the default answer.

The durable source of truth should remain:

- tasks;
- task reviews or review-note records;
- review cards;
- task-card and task-note links;
- projects and milestones;
- source/provenance metadata attached around existing records where needed.

Additional metadata may still be required. The current 70 should not assume the
existing schema already stores everything needed for cross-agent work memory.
The 73 plan should explicitly inspect whether the current model can represent:

- `agentId`;
- client name, such as Codex, Cursor, Claude Code, or OpenCode;
- thread/session/source identifiers;
- source summaries;
- provenance links from context-pack entries back to stored records;
- supersession or "this lesson replaced that older lesson" semantics.

If new metadata is required, prefer append-only or relationship-oriented
extensions around the task-review-card model rather than a separate generic
memory store.

## Agent Behavior Judgment

Agents should change behavior at the beginning and end of work.

At task start, an agent should:

- request Granoflow context when history is likely to improve planning,
  debugging, release work, verification, or repeated workflow tasks;
- keep project, milestone, and task scope visible;
- cite retrieved Granoflow task reviews and cards as evidence;
- separate recorded facts from inferred recommendations;
- avoid copying old plans blindly.

At task finish, an agent should:

- update timing and completion state;
- write a task review only when there is durable value;
- create review cards for reusable lessons;
- attach source metadata for the agent/client/thread when available;
- flag conflicts or superseded lessons instead of silently overwriting history.

## Quality Attributes For Later Planning

This 70 does not define acceptance criteria, but it does identify quality
attributes that a 73 plan should turn into tests or checks:

- bounded result size;
- clear empty-state and unavailable-state reasons;
- explicit fallback when semantic vectors are disabled or model assets are not
  ready;
- source type visibility for every returned item;
- project and milestone boundary preservation;
- low risk of noisy context causing false historical claims;
- structured distinction between facts, inferences, and recommended current use.

## External Perception

The desired user perception is:

- "Codex can use my Granoflow work history when planning."
- "Different agents can share the same completed-task lessons."
- "I can inspect, correct, archive, or practice those lessons in Granoflow."
- "My agent is not just searching chat. It is learning from tasks and review
  cards I own."

The product should not feel like:

- a hidden vector database;
- a chat-history search box;
- a Codex-only plugin;
- a generic todo API with memory branding.

## Risks

High risk: flattening the response into generic text loses Granoflow's domain
semantics and makes agent behavior less reliable.

Medium risk: weak retrieval signals may return noisy context, causing agents to
cite irrelevant history. Scope filters and typed groups should reduce this risk.

Medium risk: cross-agent provenance is useful but can become confusing if
source, confidence, and supersession are not explicit.

Medium risk: overusing "memory" can make users think Granoflow is another
private agent memory layer. The product should instead emphasize user-owned work
history, tasks, reviews, and review cards.

Low risk: exact endpoint and MCP tool names are unresolved in this 70. That is
acceptable because naming belongs in the follow-up 73 plan.

## Out Of Scope

This analysis does not decide:

- exact endpoint names;
- MCP tool names;
- request and response schema details;
- database migration details;
- UI information architecture;
- tests and validation matrix;
- release sequence.

Those belong in a 73 implementation plan after user approval.

## Conclusion

Stable conclusion:

> Expose context packs to agents; store truth as tasks, task reviews, projects,
> milestones, review cards, and provenance links.

Proposed next action:

> Write a 73 plan for the first Granoflow context-pack API and MCP tool surface,
> after explicit user approval.

That 73 should choose the first narrow slice: project context, task context, or
current-query context; inspect whether metadata additions are required; reuse
existing semantic vector search and project context builder where appropriate;
and define the API, MCP tool, tests, and docs updates.
