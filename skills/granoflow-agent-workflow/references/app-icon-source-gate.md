# App Icon Source Gate

Single owner for deciding whether a software project that ships as a **mobile
or desktop App** has an application icon (icon), and—when user documents do not
provide one—how the host obtains an authorized source before any icon is
finalized.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "app-icon-source-gate"
)
```

Seeing `SKILL.md` alone does **not** count as loading this contract.
Skipping the load when the gate applies fails closed as
`app_icon_source_gate_unread`.

## When It Applies

The gate is **applicable** when Project Work (or clear user/product docs)
indicates the product is a **phone/tablet App or desktop native App**—for
example `scope.supported_platforms` / `scope.delivery_surfaces` include iOS,
Android, macOS, Windows, or Linux desktop installers, or product language
states mobile/desktop App packaging.

The gate is **`not_applicable`** for pure Web sites, CLI tools, libraries,
backend services, or docs-only projects with no App packaging surface. Record
the basis; do not invent an icon requirement.

## Required Field (`product.app_icon`)

Persist under Project Work:

```yaml
product:
  app_icon:
    applicability: required | not_applicable
    applicability_basis: <short factual basis>
    document_scan_status: found | missing | not_scanned
    # found => docs already supply an icon asset or explicit icon path
    source_choice: user_provided | ai_generated | downloaded_license_clear | unresolved | not_applicable
    asset_path: null | <repo-relative or absolute path>
    license_note: null | <license / provenance note when downloaded or AI-generated>
    user_decision_recorded: true | false
```

## Interactive Mode

When `applicability: required` and `document_scan_status: missing`:

1. Ask the user to choose exactly one source:
   - provide an icon themselves (`user_provided`);
   - let the AI generate one (`ai_generated`); or
   - download a **copyright-clear** asset (`downloaded_license_clear`).
2. Wait for the choice before finalizing any icon asset.
3. Record `source_choice`, `user_decision_recorded: true`, and
   `asset_path` / `license_note` when known.
4. Do **not** silently generate, download, or invent a final icon.

## Unattended Mode

Under an explicit unattended declaration:

- If docs already contain an icon (`document_scan_status: found`), record it and
  continue.
- If the icon is missing, **do not** silently pick a source. Park
  `app_icon_source_unresolved` as deferred/residual (or fail closed at Project
  Work confirm / initialization Done) and continue other solvable work.
- Never mark `source_choice` as resolved without a user decision or a document
  finding.

## Fail-Closed Codes

| Code                                | When                                                         |
| ----------------------------------- | ------------------------------------------------------------ |
| `app_icon_source_gate_unread`       | Gate applies but this reference was not loaded               |
| `app_icon_applicability_unresolved` | Mobile/desktop App signal present but `applicability` unset  |
| `app_icon_document_scan_missing`    | `document_scan_status` is `not_scanned` while required       |
| `app_icon_source_unresolved`        | Required + missing docs + `source_choice` still `unresolved` |
| `app_icon_source_lint_failed`       | `lint_app_icon_source_gate.py` reports structural errors     |

## Lint

```text
python3 skills/granoflow-agent-workflow/scripts/lint_app_icon_source_gate.py \
  path/to/project-work.yaml
```

## MCP Thin Boundary

This Skill instructs Agents. It does **not** authorize implementing icon
download/generation orchestration inside the MCP server runtime or Local HTTP
API.
