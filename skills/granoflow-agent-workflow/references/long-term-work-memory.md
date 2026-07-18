# Long-Term Work Memory

Read this reference before answering questions about historical decisions,
lessons, reflections, similar past work, or why something was done.

Granoflow MCP connects MCP-capable AI agents to a local task, review, and
long-term work memory layer. When the running app advertises `context_pack_v1`,
memory-style retrieval should start with `granoflow_context_pack`. When that
capability is unavailable, fall back to existing Granoflow tasks, task reviews,
review cards, projects, milestones, and periodic reviews. This is bounded,
evidence-based retrieval, not semantic search across all historical discussion.

## Memory Intent Detection

Treat the request as a long-term work memory request when the user asks:

- what was decided before;
- why an approach was chosen or rejected;
- whether a similar task, bug, release, or project happened before;
- what lessons exist about a topic, technology, customer, workflow, or failure;
- what was discussed about a plan, project, milestone, or recurring issue;
- how past work should inform the current task.

Examples:

- "What did we decide last time about the release plan?"
- "Why did we reject the CLI-wrapper approach?"
- "Have we solved a similar Flutter desktop bug before?"
- "Summarize my recent lessons about MCP publishing."
- "What historical evidence do we have about this project?"

Do not treat ordinary task creation, status changes, or simple todo listing as
memory retrieval unless the user asks for history, reasons, lessons, or similar
past work.

## Retrieval Order

Prefer existing Granoflow evidence in this order:

1. Call `granoflow_ai_agent_tools` and check for `context_pack_v1`.
2. If available, use `granoflow_context_pack` with the narrowest known scope,
   repo, task id, project id, and query. Treat returned tasks, reviews, cards,
   project descriptions, milestone descriptions, `matchSignals`,
   `emptyReasons`, and `unavailableReasons` as evidence, not as agent
   recommendations.
3. If context packs are unavailable, use `granoflow_task_list` to identify
   likely relevant tasks. Narrow by the
   user's keyword, project, milestone, status, date clue, or named artifact when
   available.
4. Use `granoflow_task_export` for a small set of likely relevant tasks.
5. Inspect exported `taskReview`, review-card drafts, project context,
   milestone context, completion timing, and task description.
6. Use `granoflow_review_day_show` when the user provides a date or when task
   dates clearly point to a daily review worth checking.
7. Use project and milestone list/resolve tools when the question is scoped to a
   project, milestone, roadmap, or release.
8. Ask the user for a narrower keyword, date range, project, or candidate task
   when the available result set is too broad.

## Project And Milestone Descriptions

Treat project and active milestone descriptions as living context when they are
present in context packs or resource results.

- Project descriptions summarize the current global map for a project.
- Active milestone descriptions summarize the current phase.
- Archived milestone descriptions are final snapshots for ordinary MCP
  workflow; do not update them through generic MCP milestone-description tools.
- When closing or archiving a milestone, preview the archive context closure:
  final milestone state plus the parent project description update.

If the current work changes project state, API/tool contracts, release status,
documentation truth, blockers, or next expected work, update the relevant
project or active milestone description during closeout when MCP tools are
available. If MCP is unavailable, report that context upkeep was skipped.

## Bounded Retrieval

Do not export every task just to simulate search.

When the task list is large or ambiguous:

- ask for a narrower keyword, project, date range, or concrete candidate task;
- prefer a small set of likely related tasks over broad local data sweeps;
- stop and report uncertainty when existing tools cannot support the requested
  historical lookup;
- explain whether context packs are unavailable, empty, or too broad for the
  current request.

## Decision And Lesson Extraction

Classify found evidence only when the source supports the category:

- `decision`: a chosen path, rejected alternative, tradeoff, or approval.
- `lesson`: reusable knowledge likely to help future work.
- `reflection`: a review observation about process, quality, mood, focus,
  efficiency, or direction.
- `risk`: an unresolved issue, caveat, blocker, or known failure mode.
- `fact`: project background, customer constraint, version, date, status, or
  stable context.

Do not force every result into all categories. If the evidence is thin, say so.

## Evidence Rules

Historical answers must be evidence-led.

For each material claim, include:

- the Granoflow source type, such as task, task review, review card, daily
  review, project, or milestone;
- the task title, project name, milestone name, or review date when available;
- whether the claim is directly recorded or inferred from related evidence.

Separate facts from inferences. Do not answer historical questions from memory
alone when Granoflow tools are available and the user expects a Granoflow-backed
answer.

## Similar Past Work

When the user asks whether something happened before, answer with:

- similar task or review source;
- what was done then;
- what happened or what result was recorded;
- reusable lesson;
- why it is or is not relevant to the current work.

If there are multiple candidates, rank them by directness, project match, date
proximity, and whether they contain a task review or review card.

When the running app advertises `historical_task_candidates_v2`, use
`granoflow_historical_task_candidates` for a known current task. Treat every
returned item as an App-owned candidate, not as a conclusion. Keep a candidate
only when the agent can state all three of the following:

- the inferred relationship, such as `regression_of`, `supersedes`,
  `requirement_changed_from`, `follow_up_to`, `reuses_solution_from`, or
  `avoids_failure_from`;
- the exact App-returned evidence source supporting that inference;
- the concrete change this evidence makes to the current analysis, plan, or
  verification.

Discard the candidate when any one of these is missing. Never write the inferred
relationship back as an App fact, and never replace an empty or degraded result
with generic search just to produce an answer.

## Missing Memory Handling

If Granoflow has no clear record, say that directly:

```text
I could not find a clear Granoflow record for that. I can only infer from the
current conversation unless you provide a narrower project, date, or keyword.
```

Do not invent a historical decision or lesson. Offer to preserve the current
conclusion as a task review or review card only when the user is actively
finishing, reviewing, or updating a Granoflow task.

## Privacy And Local Content

Granoflow is local-first, and memory retrieval may touch private work records.

- Summarize only the evidence needed to answer the user's question.
- Do not copy large private task bodies into chat when a short cited summary is
  enough.
- Do not place real user task content, API tokens, recovery codes, local config,
  or private conversation content in docs, tests, snapshots, or examples.
- Keep tool results and final answers structured enough that the user can see
  which source supports each claim.
