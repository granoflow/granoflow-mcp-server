# Acceptance Report Manifest

The generator consumes one UTF-8 JSON object:

```json
{
  "schema": "granoflow_acceptance_report_v1",
  "title": "Single-device node relay acceptance",
  "generatedAt": "2026-07-18T14:00:00+08:00",
  "summary": "Capability routing and report preview are implemented.",
  "changes": {
    "code": ["Added capability-lane node selection."],
    "database": ["No table, column, or schema-version change."],
    "workflow": ["Added interactive, unattended, and layered_handoff modes."]
  },
  "verification": {
    "automated": [
      {
        "name": "MCP quality gate",
        "status": "passed",
        "evidence": "npm run check"
      }
    ],
    "integration": {
      "status": "planned_not_run",
      "reason": "This task prepares and statically checks the later test script.",
      "scripts": [
        {
          "path": "scripts/run-acceptance.sh",
          "check": "Shell syntax and referenced paths verified."
        }
      ]
    },
    "screenshots": {
      "status": "not_required",
      "reason": "No runtime UI claim is part of this task.",
      "items": []
    }
  }
}
```

Allowed status values are `passed`, `failed`, `planned_not_run`, and
`not_required`. Every integration/screenshot block requires a reason. Screenshot
items use paths relative to the manifest directory and require a caption. The
generator accepts PNG, JPEG, WebP, and GIF, limits each image to 8 MiB and the
final report to 25 MiB, then embeds the bytes as a `data:` URL.

The generator never executes entries in `integration.scripts`; `path` and
`check` are evidence text. `[dev]` is responsible for making those statements
true through source/static inspection. A later `[test]` task runs the script and
replaces the report with runtime evidence when that execution is required.
