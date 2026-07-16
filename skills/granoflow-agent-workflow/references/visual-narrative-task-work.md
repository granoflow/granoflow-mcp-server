# Visual Narrative Task Work Rules

Use this reference when a Task Work concerns comics, manga, storyboards,
illustration sequences, animation, video shots, motion design, or a request to
make a static visual asset move. This is a domain extension of the generic
Task Work lifecycle. It does not replace the generic Analysis, Planning,
Execution, Delivery, or Review gates.

## Domain model

The shared domain is `visual_narrative`. Its task modes are:

- `comic`: a complete static deliverable, including a single illustration,
  multi-panel comic, scene page, or static storyboard;
- `animation`: an optional temporal extension that adds duration, motion,
  shot continuity, audio, and playback acceptance.

Animation may reuse comic assets, but it is not merely a collection of comic
images. Comic work may finish without creating a timeline, video, audio, or
transition node.

Do not encode these modes as Granoflow's generic `profiles` values. Record them
as domain metadata or in the relevant Task Work section:

```yaml
domain: visual_narrative
task_mode: comic | animation
```

## Mode routing

Apply the first matching rule:

1. Explicit comic/static language such as comic, manga, illustration, panel,
   page, multi-panel, or static storyboard selects `comic`.
2. Explicit temporal language such as animation, video, make it move, camera
   motion, transition, duration, timeline, voice-over, or soundtrack selects
   `animation`.
3. If the user does not specify a mode, default to `comic` and keep the task
   eligible for static completion.
4. Character references, keyframes, multiple still images, or a shot list do
   not by themselves select `animation`.
5. Switch from `comic` to `animation` only after the user explicitly requests
   motion work or authorizes entry into the temporal extension.

If the request contains both modes, keep the shared visual-narrative work in
one Task Work document and make the animation extension an explicit downstream
branch. Do not force the comic branch to remain open after its static delivery
is accepted.

## Shared Analysis fields

Every visual-narrative Task Work should establish, when relevant:

- story intent and what the audience must understand;
- scene, shot, panel, or page role;
- characters and the approved identity/reference relationship;
- setting, props, and source assets;
- visual language and continuity constraints;
- allowed changes and locked facts;
- target surface such as page, phone, screen, video, or presentation;
- requested deliverables and acceptance evidence;
- asset version, approval, publication, and rollback boundaries.

Use stable asset identity in the task. A local path, folder name, public URL,
cloud provider, or naming convention belongs to a workspace/project adapter,
not to the generic domain contract.

## Comic mode

Comic Analysis and Planning may include:

- panel/page order and reading direction;
- composition and focal point;
- character expression, pose, and relationship;
- dialogue, captions, and text placement;
- static reference and style-continuity requirements;
- target canvas, device, or print/readability constraints.

Comic execution ends at static acceptance:

```text
Analysis → comic Planning → static generation/editing → comic acceptance → Delivery
```

Comic acceptance must prove, as applicable:

- the reading order, composition, and narrative focus are clear;
- character, setting, and visual style remain consistent;
- dialogue and captions are readable on the target surface;
- required references and versions are traceable;
- the user can accept the static result without reviewing animation-only work.

Do not add timeline, motion, audio, transition, encoding, or playback nodes to a
comic-only task.

## Animation mode

Animation extends the shared visual-narrative work with:

- temporal intent and duration;
- shot boundaries and camera behavior;
- start/end anchors and motion constraints;
- action, transition, and continuity requirements;
- audio, narration, subtitles, or soundtrack when requested;
- playback surface, encoding, and final playback evidence.

Animation execution may use this sequence:

```text
Analysis → visual asset preparation → animation shot Planning
→ motion/transition generation → audio/video processing
→ playback acceptance → Delivery
```

Animation acceptance must prove, as applicable:

- duration, shot order, start/end anchors, and motion match the story intent;
- character, setting, and style continuity survive across shots;
- audio, narration, and subtitles align with the visual result;
- the final media can play on the target surface;
- local outputs, manifests, references, and public assets agree when
  publication is in scope.

Do not infer that every animation task needs audio, public publication, or a
preceding complete comic. Load only the temporal capabilities named or required
by the confirmed outcome.

## Execution and authorization

The Agent may draft, inspect, compare, generate candidates, and run reversible
local checks after the relevant execution authorization. The following remain
separate user decisions:

- selecting or changing the comic/animation mode when the request is ambiguous;
- accepting a subjective visual or motion result;
- treating a candidate as an approved reusable asset;
- overwriting an existing asset;
- deleting or retiring an asset;
- uploading, publishing, or replacing a public asset;
- sending, paying, logging in, or using secrets/2FA.

Analysis confirmation does not authorize Planning. Planning confirmation does
not authorize execution. Execution authorization does not authorize destructive
or external publication actions.

## Failure and rollback

Record the failing stage and preserve the last accepted version. A failed
animation extension must not invalidate an already accepted comic deliverable.
If motion continuity fails, return to the last accepted still/keyframe branch;
if publication fails, keep the local delivery state separate from public
visibility; if subjective acceptance fails, keep the candidate as unapproved
unless the user explicitly requests replacement or retirement.

## Minimal examples

### Static comic request

```yaml
domain: visual_narrative
task_mode: comic
outcome: "Deliver a readable four-panel static comic page"
animation_extension: not_loaded
completion: "comic acceptance and Delivery"
```

### Motion extension request

```yaml
domain: visual_narrative
task_mode: animation
outcome: "Turn the approved still sequence into a playable short shot"
required_extensions:
  - shot_timing
  - motion_continuity
  - playback_acceptance
audio: only_if_requested
publication: only_if_authorized
```
