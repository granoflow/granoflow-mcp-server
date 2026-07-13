# Task Review Context Promotion Entry

Project Context remains limited to `project_snapshot.yaml` and `project_rules.yaml`. Milestones use managed description/completion summary fields, not YAML attachments.

```yaml
id: <stable id>
kind: current_fact | durable_rule | durable_decision | active_stage_context | archived_stage_summary
scope: <project or milestone scope>
milestone_id: <id | null>
summary: <bounded summary>
rationale: <why it matters later>
future_trigger: <when to retrieve it>
recommended_action: <future action>
evidence: <safe references>
first_verified_at: <timestamp>
last_verified_at: <timestamp>
status: active | superseded | resolved
supersedes: <id | null>
```

Deduplicate by kind, scope, milestone, future trigger, and source; then use semantic similarity. Preserve a matched stable id and merge/update/leave unchanged. Only a genuinely new semantic entry receives a deterministic identity. A random UUID or summary hash alone is not semantic deduplication.

Active milestone description block:

```text
<!-- granoflow-milestone-context:v1:start -->
Freshness: current | stale | partial | source_gap | reconcile_failed
Last verified at: <timestamp | unknown>
Context: <bounded stage context>
Evidence: <short references>
<!-- granoflow-milestone-context:v1:end -->
```

Archived milestone descriptions are immutable in ordinary workflow; update only the safe completion summary. Living context carries this notice: `Freshness notice: Living context may lag behind implementation. Report conflicts and propose the required document or implementation update.`
