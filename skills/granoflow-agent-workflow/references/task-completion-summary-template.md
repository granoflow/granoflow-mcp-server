# Task Completion Summary Managed Block

```markdown
<!-- granoflow-task-completion-summary:v1:start -->

## Task Completion Summary

- Final outcome:
- Delivery status:
- Task Analysis:
- Task Plan:
- Task Delivery:
- Delivery Card Checkpoint: <status/change summary and linked card ids>
- Deferred Card Work: none | <reason, owner, and next entry point>
- Card Verification Failures: none | <operation ids and safe verification action>
- Manual acceptance:
- Review status: pending | completed
- Deferred review steps:
- Residuals:
- Next entry point:

<!-- granoflow-task-completion-summary:v1:end -->
```

No marker means append one block. One valid pair means replace only its content. Duplicate, missing, reversed, or nested markers return `task_completion_summary_markers_invalid` and preserve all task description text.
