# Granoflow Product Builder Capability Pack V1

This is the single owner for the external capability collections recommended
during Granoflow initialization. The host discovers, installs, reloads, and
verifies capabilities; Granoflow MCP never scans or changes the host Skill
environment.

The fixed pack id is `granoflow_product_builder_v1`. Granoflow owns the pack
membership and routing profile so users do not have to assemble a design and
engineering toolchain one Skill at a time.

## User Prompt

Granoflow recommends installing its complete Product Builder capability pack:

- Grill Finalizer: checks task analysis and plans for missing important issues.
- Grill Me: asks useful questions to make goals, requirements, and limits clear.
- gstack: helps review engineering approaches, investigate problems, verify features, and improve delivery quality.
- Matt Pocock Skills: improves coding, debugging, testing, and engineering implementation.
- gstack Design: defines one coherent project design system and reviews design quality.
- Huashu Design: creates high-fidelity HTML prototypes and motion-ready presentations.
- Impeccable: detects generic AI-looking UI and performs a taste-focused quality review.
- Apple Design: applies Apple platform interaction and visual conventions when relevant.
- GSAP Skills: implements complex web motion correctly when the project requires it.
- Baoyu Skills: creates visual communication assets such as covers, infographics, slides, and comics.

Install the complete recommended capability pack?

Render this prompt in the user's language. Preserve only each collection's name
and plain-language function. Do not append technical installation details to
the Granoflow prompt.

## Capability Registry

| Stable id            | User-visible name  | Availability evidence                | Trusted canonical source              |
| -------------------- | ------------------ | ------------------------------------ | ------------------------------------- |
| `grill-finalizer`    | Grill Finalizer    | Host-visible `grill-finalizer`       | Host-verified canonical provider only |
| `grill-me`           | Grill Me           | Host-visible `grill-me`              | Host-verified canonical provider only |
| `gstack`             | gstack             | Host-visible gstack installation     | `garrytan/gstack`                     |
| `matt-pocock-skills` | Matt Pocock Skills | Host-visible Matt Pocock collection  | Host-verified canonical provider only |
| `huashu-design`      | Huashu Design      | Host-visible `huashu-design`         | `alchaincyf/huashu-design`            |
| `impeccable`         | Impeccable         | Host-visible Impeccable collection   | `pbakaus/impeccable`                  |
| `apple-design`       | Apple Design       | Host-visible Apple Design Skill      | `emilkowalski/skills`                 |
| `gsap-skills`        | GSAP Skills        | Host-visible GSAP Skills collection  | `greensock/gsap-skills`               |
| `baoyu-skills`       | Baoyu Skills       | Host-visible Baoyu Skills collection | `JimLiu/baoyu-skills`                 |

The registry identifies recommended collections; it is not an installer or a
copy of any external catalog. If the host has no trusted installation mapping
for an item, do not guess. Report that capability as not ready.

`taste-skill` is intentionally excluded because gstack owns design exploration
and shotgun-style variation. `superpowers` is intentionally excluded because
Granoflow Task Work, bundled Grills, TDD, debugging, and review already own the
workflow control plane. These exclusions prevent two competing routers.

## One Onboarding Decision

Recommend `install all recommended capabilities` for every listed collection
that is not already available. The user does not select individual items.

```yaml
capability_pack:
  id: granoflow_product_builder_v1
  version: 1
  status: not_checked | ready | awaiting_confirmation | approved_all | declined | partial_failure
  offered: [<stable capability ids>]
  unavailable_after_install: [<stable capability ids>]
```

- If everything is available, do not show an installation question.
- On approval, install only the collections actually shown, then rediscover
  them and account for any host reload.
- A host-native confirmation may appear when the host platform requires it.
  Do not bypass, disguise, or duplicate that confirmation.
- Ask exactly once. A refusal records `declined`; do not convert the pack into
  item-by-item choices and do not ask again during this initialization.
- A declined or partial pack does not block connection, read-only Granoflow
  use, or manual data import. It does block automatic project design
  initialization with `capability_pack_not_ready`.
- Partial installation or rediscovery failure records `partial_failure` plus
  every unavailable stable id. Never claim degraded work is equivalent to the
  fixed project builder profile.

## Runtime Boundary

Installing the pack does not authorize invoking every Skill in it. A confirmed
Project Work `skill_routing` lock selects only the relevant capability for the
phase and condition. An available `model_allowed` capability is invoked without
another preference prompt and records evidence. A `user_only` or unknown Skill
remains user-only after installation.

Initialization installs the Matt Pocock collection but does not run
`setup-matt-pocock-skills`. That project-level setup waits until a real software
repository needs it.

Installation approval does not authorize data import, task implementation,
commit, push, publishing, login, payment, or any other gated action.
