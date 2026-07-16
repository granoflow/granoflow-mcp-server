# Thread Visual Evidence

Use this reference whenever the current Agent thread contains one or more
images, screenshots, diagrams, scans, or other visual artifacts.

## Inspection

1. Inventory the images actually present in the thread; do not infer an image
   from a filename or from a textual mention.
2. For each image, record its role: task evidence, Note source/example, Card
   study aid, project asset, or temporary conversation context.
3. Check whether the image is readable, relevant, stable enough to retain, and
   safe to persist. Treat secrets, private identifiers, personal data, and
   temporary debugging screenshots as non-persistent unless explicitly needed
   and authorized.

## Destination Rules

- **Task:** attach the image when it proves current state, reproduces a bug,
  records a user-visible result, or is required for execution/acceptance.
- **Note:** attach or reference the image when it is durable evidence,
  explanation, diagram, example, or visual source for the Note.
- **Card:** use an image only when visual recall is the point of the Card, such
  as a UI state, diagram, character reference, or visual distinction. The Note
  remains the explanatory source; do not duplicate a decorative image across
  every Card.

An image may belong to more than one destination when each use has a distinct
purpose. A task screenshot may be evidence while a cropped diagram from it is a
Note/Card study aid.

## Persistence And Verification

- Preserve the original image identity, source, timestamp, and relationship to
  the thread when the host or App supports those fields.
- Prefer an App-owned attachment or supported media reference. Do not claim an
  image was uploaded when only a local path or chat-visible image exists.
- If the destination cannot accept images, keep a safe reference or concise
  visual description in the Note/task and report that media persistence was not
  available.
- After adding an image, read back the destination and verify the attachment or
  media reference. Image presence in the conversation alone is not evidence of
  persistence.

## No-Image Result

If the thread contains no relevant image, record `visual_evidence: none` in the
working analysis only when the workflow requires an explicit checkpoint. Do not
add empty image fields to ordinary tasks, Notes, or Cards.
