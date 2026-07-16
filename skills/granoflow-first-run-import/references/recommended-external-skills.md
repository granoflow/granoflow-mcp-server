# Recommended External Skills

This is the single owner for the external capability collections recommended
during Granoflow initialization. The host discovers, installs, reloads, and
verifies capabilities; Granoflow MCP never scans or changes the host Skill
environment.

## User Prompt

To help Granoflow work better for you, we recommend these AI capabilities:

- Grill Finalizer: checks task analysis and plans for missing important issues.
- Grill Me: asks useful questions to make goals, requirements, and limits clear.
- gstack: helps review engineering approaches, investigate problems, verify features, and improve delivery quality.
- Matt Pocock Skills: improves coding, debugging, testing, and engineering implementation.

Install all recommended capabilities?

Render this prompt in the user's language. Preserve only each collection's name
and plain-language function. Do not append technical installation details to
the Granoflow prompt.

## Capability Registry

| Stable id            | User-visible name  | Availability evidence               | Trusted installation mapping          |
| -------------------- | ------------------ | ----------------------------------- | ------------------------------------- |
| `grill-finalizer`    | Grill Finalizer    | Host-visible `grill-finalizer`      | Host-verified canonical provider only |
| `grill-me`           | Grill Me           | Host-visible `grill-me`             | Host-verified canonical provider only |
| `gstack`             | gstack             | Host-visible gstack installation    | Host-verified canonical provider only |
| `matt-pocock-skills` | Matt Pocock Skills | Host-visible Matt Pocock collection | Host-verified canonical provider only |

The registry identifies recommended collections; it is not an installer or a
copy of any external catalog. If the host has no trusted installation mapping
for an item, do not guess. Report that capability as not ready.

## Onboarding Decision

Recommend `install all recommended capabilities` for every listed collection
that is not already available. The user does not select individual items.

```yaml
recommended_external_skills:
  status: not_checked | all_available | awaiting_confirmation | approved_all | declined_for_onboarding | partial_failure
  offered: [<stable capability ids>]
  unavailable_after_install: [<stable capability ids>]
```

- If everything is available, do not show an installation question.
- On approval, install only the collections actually shown, then rediscover
  them and account for any host reload.
- A host-native confirmation may appear when the host platform requires it.
  Do not bypass, disguise, or duplicate that confirmation.
- On the first refusal, explain once that these capabilities improve analysis,
  planning, coding, investigation, and verification while Granoflow still works
  without them. Ask one final time.
- On the second refusal, record `declined_for_onboarding` and do not ask again
  during this initialization. A later real task may recommend one relevant
  capability through the normal external Skill routing contract.
- Partial installation or rediscovery failure does not block initialization.

## Runtime Boundary

Installing a collection does not authorize invoking every Skill in it. Runtime
routing selects only the relevant Skill whose invocation metadata permits the
host action. A `user_only` Skill remains user-only after installation.

Initialization installs the Matt Pocock collection but does not run
`setup-matt-pocock-skills`. That project-level setup waits until a real software
repository needs it.

Installation approval does not authorize data import, task implementation,
commit, push, publishing, login, payment, or any other gated action.
