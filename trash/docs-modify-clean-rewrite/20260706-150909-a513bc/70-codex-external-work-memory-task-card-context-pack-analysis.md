# Codex External Work Memory With Task-Card Storage Analysis

Status: 70 analysis

Date: 2026-07-06

Mode: feature

## 详细描述

This document analyzes how Granoflow should satisfy a user need that often
appears as "I wish Codex remembered its old threads, prior work, and lessons",
without turning Granoflow into a generic memory database or hiding its existing
task-review-card model behind an ambiguous `similar` API.

The core product judgment is:

> Granoflow should present agent-friendly work context, but store and explain
> that context through Granoflow's native task, task review, project/milestone,
> and review card model.

The target user behavior is multi-agent work. A user may use Codex, Cursor,
Claude Code, OpenCode, and other MCP-capable agents across different projects
and threads. Each agent can remember some of its own context, but the user still
needs a stable, user-owned layer that records what work happened, why decisions
were made, what failed, what was verified, and which lessons should be reused.

The interface problem is therefore not "find similar tasks". Similarity is only
one retrieval signal. The deeper problem is "give the current agent a scoped
work context pack that can improve planning, risk checks, verification, and
completion review".

## Current Responsibility Layer

Granoflow should own the durable work-memory layer:

- tasks as units of work and progress;
- task reviews as decisions, tradeoffs, evidence, risks, and completion
  summaries;
- review cards as reusable lessons worth future retrieval and practice;
- projects and milestones as scope boundaries;
- links between tasks, reviews, and cards as provenance.

Codex should own the active reasoning and execution layer:

- interpret the user's current request;
- ask Granoflow for relevant context when planning or reviewing work;
- cite retrieved Granoflow evidence instead of saying "I remember";
- write back task review and card-worthy lessons at completion time;
- treat missing or conflicting Granoflow records as uncertainty.

The MCP server should remain a thin protocol layer:

- expose Granoflow Local HTTP API capabilities as predictable MCP tools;
- keep results structured for Codex, Cursor, Claude Code, OpenCode, and similar
  clients;
- avoid reimplementing semantic ranking, task business logic, or direct database
  access.

## Established Facts

- The public MCP server is already positioned as a local task, review, and
  long-term work memory layer for MCP-capable agents.
- The current MCP server exposes task list/export/finish and workflow-skill
  guidance, but does not expose a first-class task context pack.
- Granoflow itself already has semantic vector infrastructure. The app includes
  `SemanticVectorSearchService.search(...)`, which embeds a query, loads ready
  vectors, and ranks by cosine similarity.
- Granoflow's app-level global search already attempts semantic groups before
  falling back to text and structured search.
- Granoflow also has an `AiAgentProjectContextBuilder` that builds project
  context out of projects, milestones, tasks, nodes, and document attachments,
  with semantic sorting for milestones and tasks when vector search is
  available.
- Local HTTP API currently exposes AI-agent task export/import/validate,
  historical task mutations, and review-card similarity preview. That is useful
  but narrower than "give an agent work context for this current task".

## Main Product Judgment

Do not center the next interface around `similar`.

`similar` is too small and invites the wrong behavior:

- it sounds like a search result rather than a work-memory context;
- it hides whether returned material is a task, review, card, project, or
  milestone;
- it encourages the agent to copy old task breakdowns instead of reasoning from
  evidence;
- it does not naturally carry provenance, conflict state, verification evidence,
  or "how to use this for the current task".

Use a context-pack shape instead.

The external agent surface can use names such as:

- `granoflow_task_context_pack`;
- `granoflow_work_memory_query`;
- `granoflow_agent_context_pack`.

The returned schema should still expose Granoflow concepts explicitly:

- `currentTask`;
- `projectContext`;
- `milestoneContext`;
- `relatedTaskReviews`;
- `relatedReviewCards`;
- `relatedProjects`;
- `relatedMilestones`;
- `sourceProvenance`;
- `recommendedUse`.

This keeps the agent-facing API ergonomic without erasing the product model.

## SSOT And Artifact Boundaries

Durable storage SSOT should stay in Granoflow's existing model family:

- task records;
- task review fields or review-note records;
- review card records;
- task-card and task-note links;
- project and milestone records;
- agent/source metadata attached to task completion or imports.

The context pack is a projection, not a new truth source.

This matters because users should be able to open Granoflow and understand the
same knowledge through product-native surfaces: task detail, project context,
task review, card practice, and related task/card links. If the API introduces a
separate "memory object" store too early, the product risks creating two
competing truths: one for humans and another for agents.

## AI Semantic Understanding Risk

There is a real risk if the API hides Granoflow's data structure behind a flat
memory/RAG response.

Bad shape:

```json
{
  "memories": [
    {
      "text": "Npm releases need cloud version checks."
    }
  ]
}
```

This gives the agent text but not the domain semantics. It cannot reliably tell
whether the item was a completed task, a decision, a review card, a project
constraint, or an inferred lesson.

Better shape:

```json
{
  "model": "granoflow_task_review_card_context_v1",
  "currentTask": {
    "id": "task_123",
    "title": "Publish MCP server"
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

This shape helps the agent reason because the schema teaches the model what each
piece means. The product structure becomes a semantic affordance rather than an
implementation detail.

## Current Fit And Gaps

Current fit:

- Granoflow already has a task-card model suitable for durable work memory.
- Semantic vector search can rank task, project, milestone, review-card, and
  review objects internally.
- AI-agent project context already has a project-context builder pattern that is
  closer to context pack than to simple search.
- MCP tooling already has a completion routine that writes meaningful reviews
  and review-card drafts, which is the right write-back rhythm.

Current gaps:

- No Local HTTP API endpoint appears to expose a general agent context pack for
  a current task or current user request.
- No MCP tool currently makes "retrieve work context before planning" a
  first-class action.
- Existing memory guidance still talks about bounded evidence lookup and similar
  past work, but the stronger framing should be shared multi-agent work memory.
- The public vocabulary risks overusing "memory" or "similar" without making
  task-review-card semantics explicit.

## Interface Judgment

The API should expose a projection that agents can use directly, while keeping
storage native.

Good interface properties:

- scoped by task, project, milestone, user query, or agent-provided work intent;
- returns typed Granoflow sources, not anonymous text chunks;
- includes relevance reason and source provenance;
- separates directly recorded facts from inferred recommendations;
- includes review cards as reusable lessons, not just task search hits;
- includes uncertainty, conflict, and stale-context signals;
- tells the agent how to use the context for planning, risk checking, or
  verification.

Poor interface properties:

- `similar` as the central noun;
- untyped `memories[]` with only text and score;
- returning old task breakdowns without warning against blind copying;
- hiding project/milestone boundaries;
- mixing agent-generated inference into stored facts without labels.

## Agent Behavior Judgment

Agents should change behavior in two places.

At task start:

- request Granoflow context when the user asks for planning, implementation, bug
  diagnosis, release, review, or repeated workflow work;
- use project/milestone/task scope when available;
- cite Granoflow task reviews and cards as evidence;
- convert context into current-task planning hints, risks, and verification
  reminders.

At task finish:

- update task timing and completion state;
- write a task review only when it contains durable value;
- create review cards for reusable lessons;
- include agent/client/thread/source metadata;
- mark any superseded or conflicting lesson as a candidate for review rather
  than silently overwriting history.

## Data Model Judgment

Do not introduce a first-class generic `memory` table as the default answer.

If additional metadata is needed later, prefer append-only extensions around the
existing model:

- source metadata for agent/client/thread/import context;
- provenance links from task reviews and cards to source events;
- supersession metadata for replaced lessons;
- typed extraction fields inside task review or review-note structures only when
  the product needs them.

This keeps the user-facing model stable: work produces tasks, reviews, and
cards. Agents receive context packs, but the app remains understandable to
humans.

## External Perception

For non-technical users, the expected result should feel like this:

- "Codex knows what happened before because it can read my Granoflow work
  history."
- "Cursor and Claude Code can benefit from the same lessons Codex wrote back."
- "I can inspect and correct those lessons in Granoflow."
- "My agent does not just remember chat; it learns from completed tasks and
  review cards that I own."

The product should not feel like:

- a hidden vector database;
- another chat-history search box;
- a Codex-only plugin;
- a generic todo API with memory branding.

## Applicability Trimming

This analysis applies to Granoflow MCP and Local HTTP API design.

It does not decide:

- exact endpoint names;
- request/response schema details;
- migration or table changes;
- MCP tool names;
- UI placement;
- release sequence;
- tests and validation matrix.

Those belong in a `73` plan if the user decides to implement.

## Risk Notes

Semantic retrieval can improve relevance, but it cannot replace domain shape.
Task, review, card, project, and milestone types should remain visible in the
response.

Cross-agent storage is valuable, but it creates provenance and correction
requirements. A context pack that hides agent source or confidence will make
future debugging harder.

Codex memory should be treated as helpful but non-authoritative. Granoflow
should not compete with Codex by claiming to be "the agent's memory"; it should
be the user's durable work-memory layer that agents can read and write.

## Conclusion

Recommended next action: `upgrade_73`.

The decision boundary is now clear enough to plan implementation, but not small
enough for direct code changes. The next document should be a `73` plan covering:

- the first context-pack API shape;
- whether to start from project context, task context, or current query context;
- how to reuse existing semantic vector search and project context builder;
- the MCP tool surface and agent workflow skill updates;
- whether any storage metadata is required beyond existing tasks, task reviews,
  cards, and links;
- tests and API documentation updates.

Stable conclusion:

> Expose context packs to agents; store truth as tasks, task reviews, projects,
> milestones, and review cards.
