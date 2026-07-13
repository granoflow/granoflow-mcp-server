# AI-Agent Context Pack API And MCP Surface Plan

Status: 73 implementation plan

Date: 2026-07-06

Mode: feature

Upstream analysis:
`docs-temp/70-codex-external-work-memory-task-card-context-pack-analysis-V02.md`

## Applicability Trim

This plan implements the first narrow slice of Granoflow as an external work
memory for engineering agents.

The first slice includes only three agent-neutral capabilities:

1. Read a structured context pack.
2. Write a completed engineering task record.
3. Write a reusable review card.

The first slice does not implement a generic AI memory system, RAG knowledge
base, chat-history recall, agent reasoning layer, embedding-ranking API, risk
scoring API, or cross-agent identity graph.

## Upstream Conclusion

The 70 conclusion is:

> Expose context packs to agents; store truth as tasks, task reviews, projects,
> milestones, review cards, and provenance links.

The 70 refinement is:

> Preserve existing similar-history and review-card similarity surfaces, but do
> not make `similar` the central agent API concept.

The implementation consequence is:

- Granoflow app owns the Local HTTP API behavior and storage rules.
- `granoflow-mcp-server` stays thin and only forwards structured requests to
  the Local HTTP API.
- Codex-friendly language can appear in MCP tool descriptions, but the Local
  HTTP API endpoint names should remain agent-neutral.

## SSOT And Affected Artifacts

Primary SSOT:

- `/Users/will/code/granoflow/lib/core/local_http_api/local_http_api_command_dispatcher.dart`
- `/Users/will/code/granoflow/lib/core/local_http_api/local_http_api_ai_agent_service.dart`
- `/Users/will/code/granoflow/lib/core/local_http_api/local_http_api_ai_agent_tools.dart`
- `/Users/will/code/granoflow/lib/core/local_http_api/local_http_api_capabilities.dart`
- `/Users/will/code/granoflow-mcp-server/src/tools.ts`
- `/Users/will/code/granoflow-mcp-server/tests/tools.test.ts`

Supporting existing services to inspect or reuse:

- `/Users/will/code/granoflow/lib/core/services/semantic_vector_search_service.dart`
- `/Users/will/code/granoflow/lib/core/services/ai_agent_project_context_builder.dart`
- `/Users/will/code/granoflow/lib/core/providers/task_query/task_query_detail_providers.dart`
- `/Users/will/code/granoflow/lib/core/services/review_card_similarity_suggestion_service.dart`
- `/Users/will/code/granoflow/lib/core/services/single_task_ai_review_card_import_service.dart`
- `/Users/will/code/granoflow/lib/core/services/task_write/task_write_gateway.dart`

Docs and workflow artifacts:

- `/Users/will/code/granoflow-mcp-server/README.md`
- `/Users/will/code/granoflow-mcp-server/skills/granoflow-agent-workflow/SKILL.md`
- `/Users/will/code/granoflow-mcp-server/skills/granoflow-agent-workflow/references/long-term-work-memory.md`

## Database Schema Confirmation

Recommended v1 decision: no database schema migration.

| Area                     | v1 decision                                                                            | Evidence                                                                                                                    | Confirmation status                                                              |
| ------------------------ | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Task completion          | Reuse existing task completion and `taskReview` storage                                | Existing MCP already calls `/v1/tasks/{id}/complete`; Local HTTP API has task import/export and historical mutation support | Confirmed for v1 if provenance is stored only where existing fields allow        |
| Review card              | Reuse existing review-card/note import or creation services                            | Existing review-card AI import and similarity preview services already write or preview card-shaped data                    | Confirmed for v1 if no new provenance columns are required                       |
| Provenance               | Store only minimum existing-field provenance; do not require new agent identity tables | 70 rejects cross-agent identity graph in v1                                                                                 | Confirmed for v1 with fail-closed condition below                                |
| Thread/commit provenance | Treat as optional source metadata                                                      | Current evidence does not prove durable fields exist for every source attribute                                             | Must fail closed if product requirement changes to durable structured provenance |

Fail-closed condition:

If implementation discovers that v1 cannot preserve acceptable source metadata
without new columns, new tables, or migration logic, stop implementation and
write a separate schema plan. Do not smuggle provenance into unrelated text
fields just to avoid a migration.

Implementation layer ownership if no migration is needed:

- Local HTTP API route parsing belongs in the command dispatcher.
- Request validation and response shaping belong in `LocalHttpApiAiAgentService`
  or small adjacent AI-agent serializers.
- Existing repositories and services own task/card writes.
- MCP owns only Zod input validation, tool descriptions, and forwarding.

## UI Confirmation

Recommended v1 decision: no UI change.

| Area                          | v1 decision                          | Evidence                                                   | Confirmation status |
| ----------------------------- | ------------------------------------ | ---------------------------------------------------------- | ------------------- |
| User-facing pages             | No new page, card, panel, or setting | The requested surface is agent/API/MCP behavior            | Confirmed           |
| Existing similar-history UI   | Preserve unchanged                   | 70 identifies it as a valid existing local UI surface      | Confirmed           |
| Review-card import preview UI | Preserve unchanged                   | Existing `review_card_similarity_preview_v1` remains valid | Confirmed           |
| Error/empty copy              | API/MCP structured errors only       | No visible app UI is changed                               | Confirmed           |

No ASCII UI sketch is required for v1 because there is no user-visible layout
change. If a later plan adds a visible "agent memory" or "context pack" page,
that plan must include UI component reuse and a separate UI confirmation.

## API Contract Draft

The Local HTTP API should expose three agent-neutral endpoints:

```text
POST /v1/ai-agent/context-pack
POST /v1/ai-agent/task-completions
POST /v1/ai-agent/review-cards
```

The tools discovery endpoint should advertise the capability:

```json
{
  "toolId": "granoflow_context_pack_v1",
  "kind": "work_memory",
  "enabled": true,
  "endpoints": {
    "contextPack": "/v1/ai-agent/context-pack",
    "taskCompletion": "/v1/ai-agent/task-completions",
    "reviewCard": "/v1/ai-agent/review-cards"
  },
  "capabilities": {
    "contextPack": {
      "capability": "context_pack_v1",
      "version": 1,
      "matchSignals": true,
      "recommendations": false,
      "embeddingScores": false
    }
  }
}
```

### Context Pack Request

```json
{
  "scope": "task",
  "repo": "granoflow/mcp-server",
  "taskId": "optional_granoflow_task_id",
  "projectId": "optional_granoflow_project_id",
  "query": "Fix flaky CI in build pipeline",
  "limit": 12,
  "client": "codex"
}
```

Validation rules:

- `scope` must be `task`, `project`, or `repo`.
- `limit` defaults to a small bounded value and must have a hard maximum.
- At least one locator must exist: `taskId`, `projectId`, `repo`, or non-empty
  `query`.
- `client` is optional and informational; it must not unlock broader access.
- The endpoint must return an explicit empty or unavailable state rather than a
  generic success with unrelated records.

### Context Pack Response

```json
{
  "ok": true,
  "data": {
    "model": "granoflow_task_review_card_context_v1",
    "request": {
      "scope": "repo",
      "repo": "granoflow/mcp-server",
      "query": "Fix flaky CI in build pipeline",
      "limit": 12,
      "client": "codex"
    },
    "tasks": [],
    "reviews": [],
    "cards": [],
    "unavailableReasons": []
  }
}
```

Each returned item should include:

- stable id;
- source type;
- title or short summary;
- status or outcome where relevant;
- `matchSignals`, such as `repo`, `project`, `task`, `tag:ci`, or `text`;
- provenance fields that already exist or can be safely derived.

The response must not include `recommendedUse`, `planningHints`, risk scores,
embedding vectors, embedding scores, or instructions telling the agent what to
decide.

### Task Completion Request

```json
{
  "repo": "granoflow/mcp-server",
  "title": "Fix flaky CI in build pipeline",
  "summary": "Fixed race condition in caching step.",
  "decisions": ["disabled shared cache in GitHub Actions"],
  "outcome": "success",
  "tags": ["ci", "build"],
  "client": "codex",
  "source": {
    "taskId": "optional_existing_granoflow_task_id",
    "threadId": "optional",
    "commit": "optional"
  }
}
```

Validation rules:

- `title`, `summary`, and `outcome` are required.
- `outcome` must be `success` or `failed` in v1.
- `decisions`, `tags`, and `source` are optional and bounded.
- The endpoint must not create duplicate tasks blindly when `source.taskId` or
  another explicit task locator is present.
- If the request cannot map safely to an existing task or a new task creation,
  return a structured failure.

### Review Card Request

```json
{
  "title": "CI cache race condition pattern",
  "problem": "Flaky CI caused by shared cache state.",
  "solution": "Use isolated cache per job.",
  "tags": ["ci", "github-actions"],
  "client": "codex",
  "source": {
    "taskId": "optional_granoflow_task_id",
    "threadId": "optional",
    "commit": "optional"
  }
}
```

Validation rules:

- `title`, `problem`, and `solution` are required.
- The created card must remain a reusable lesson, not a raw log.
- If a `taskId` is supplied, the card should be linked to that task through the
  existing task-card or task-note relationship path.
- Duplicate protection must reuse existing review-card duplicate rules where
  available; otherwise v1 should return a preview/failure instead of writing
  ambiguous duplicates.

## MCP Tool Surface

Add three thin MCP tools after the Local HTTP API endpoints exist:

- `granoflow_context_pack`
- `granoflow_task_completion_record`
- `granoflow_review_card_record`

Tool behavior:

- Validate input with Zod.
- Forward directly to Local HTTP API.
- Preserve structured API responses.
- Do not compute semantic similarity in Node.
- Do not inspect SQLite, Drift, app files, or local embeddings.
- Do not print tokens, secrets, raw local paths from returned content, or hidden
  provenance beyond what the API intentionally returns.

The MCP tools should first call or encourage checking `granoflow_ai_agent_tools`
when capability negotiation matters. If the running app does not advertise
`context_pack_v1`, the tools should return a structured unavailable response
rather than emulating the feature with broad `granoflow_api_request` calls.

## Implementation Steps

### Stage 1: App API Contract

1. Extend the AI-agent tools/capabilities declaration with
   `context_pack_v1`.
2. Add route parsing for:
   - `POST /v1/ai-agent/context-pack`
   - `POST /v1/ai-agent/task-completions`
   - `POST /v1/ai-agent/review-cards`
3. Add service methods for each action in `LocalHttpApiAiAgentService` or a
   small adjacent service if the file approaches the size budget.
4. Implement validation and structured errors before any write behavior.
5. Implement context-pack retrieval using existing task/project scope first,
   then existing semantic search only as a recall/ranking signal where already
   available.
6. Implement task completion write by reusing task write/complete paths.
7. Implement review-card write by reusing existing review-card import or
   creation services, with duplicate protection.
8. Add app-side tests for route mapping, validation, empty states, unavailable
   states, and successful forwarding to service actions.

Stage 1 may ship without MCP changes only if the API is discoverable through
`/v1/ai-agent/tools`.

### Stage 2: MCP Thin Wrappers

1. Add Zod schemas for the three new MCP tools in
   `/Users/will/code/granoflow-mcp-server/src/tools.ts`.
2. Register the new tools with descriptions that emphasize external work
   memory and structured facts.
3. Forward each tool to the matching Local HTTP API endpoint.
4. Add tests in `/Users/will/code/granoflow-mcp-server/tests/tools.test.ts`
   that verify:
   - registration;
   - dry structured forwarding body;
   - unavailable capability behavior if implemented in the wrapper;
   - no recommendation fields are fabricated by MCP.
5. Update README/tool documentation and bundled workflow guidance to prefer
   `granoflow_context_pack` over manual task-list/export chains when the
   capability exists.

### Stage 3: Verification And Docs

1. Run app-side targeted Local HTTP API tests in `/Users/will/code/granoflow`.
2. Run the app repository's required static gates for touched Dart files.
3. Run `npm run check` in `/Users/will/code/granoflow-mcp-server`.
4. Manually smoke the MCP tool against a running Granoflow Local HTTP API when
   the app endpoint is available.
5. Update docs to explain that similar-history UI and review-card similarity
   preview are preserved but narrower than context packs.

## Code Structure Budgets

### Granoflow App

Soft file budget:

- New small serializers/services: target under 220 lines each.
- Existing large Local HTTP API files: avoid growing any touched file by more
  than about 120 lines without extracting a real protocol-boundary helper.

Soft method budget:

- Route parsing branches should stay short and declarative.
- Validation methods should target under 60 lines each.
- Response shapers should target under 80 lines each.

Responsibility boundaries:

- Route files parse method/path only.
- AI-agent service methods validate and orchestrate.
- Repository/service layer performs writes.
- Semantic search remains in existing app services.
- MCP tool handlers forward only.

Prohibited structure tactics:

- no mechanical splitting by line count;
- no generic `memory_utils` dumping ground;
- no new business logic in MCP;
- no copy-pasted review-card import logic;
- no direct database reads from MCP or Local HTTP route handlers.

### MCP Server

Soft file budget:

- Prefer keeping each new Zod schema compact and close to its tool.
- If `src/tools.ts` becomes harder to scan, extract only protocol-specific
  schema/normalization helpers with clear names.

Soft method budget:

- Tool handlers should remain one validation/forwarding action.
- No handler should construct a context pack itself.

## Acceptance Criteria

App API:

- `GET /v1/ai-agent/tools` advertises `context_pack_v1`.
- `POST /v1/ai-agent/context-pack` validates scope, locator, limit, and client.
- Context-pack responses group `tasks`, `reviews`, and `cards` as structured
  facts.
- Context-pack responses include bounded `matchSignals` but no recommendations,
  planning hints, risk scores, embedding scores, or vectors.
- Empty and unavailable states are structured and test-covered.
- `POST /v1/ai-agent/task-completions` records a successful or failed
  engineering completion without duplicating an explicitly referenced task.
- `POST /v1/ai-agent/review-cards` records a reusable lesson or fails closed
  on ambiguous duplicate/write conditions.

MCP:

- `granoflow_context_pack` forwards to `/v1/ai-agent/context-pack`.
- `granoflow_task_completion_record` forwards to
  `/v1/ai-agent/task-completions`.
- `granoflow_review_card_record` forwards to `/v1/ai-agent/review-cards`.
- MCP responses preserve the Local HTTP API shape.
- MCP does not fabricate ranking explanations, recommendations, or inferred
  actions.

Verification:

- App-side targeted tests pass.
- `npm run check` passes in `/Users/will/code/granoflow-mcp-server`.
- A manual smoke test against a running local app confirms capability discovery
  and at least one read request.

## Rollback Plan

If the app API fails:

- remove the new `/v1/ai-agent/*` route branches;
- remove the `context_pack_v1` tool declaration;
- keep existing single-task AI and review-card similarity endpoints unchanged.

If MCP wrappers fail:

- remove the three new tool registrations and tests;
- keep existing `granoflow_task_export`, `granoflow_task_finish`, and
  `granoflow_api_request` behavior unchanged.

If provenance requires schema work:

- stop before writing data;
- preserve the 70 and this 73 as upstream context;
- write a schema-specific plan that covers migration, model, repository,
  serializer, sync, backup, and rollback behavior.

## Fail-Closed Conditions

Do not proceed in the same implementation if any of these become true:

- v1 requires a new database table or migration;
- review-card writes cannot use existing duplicate protection;
- context retrieval would need broad unscoped all-history export;
- MCP would need to inspect local Granoflow database files directly;
- returned context would expose secrets, raw tokens, or unsafe local paths;
- the implementation starts turning match signals into recommendations or risk
  scoring.

## Backwrite Checklist

After implementation:

- Update this 73 with actual endpoint names and any deviations.
- Update the 70 if the core boundary changes.
- Update long-term work-memory workflow docs to prefer context packs when
  available.
- If schema changes are introduced by a later plan, create or update the
  relevant 72/spec and migration docs.
- Record a 74 decision if v1 deliberately omits durable thread/commit
  provenance or postpones it to a future version.
