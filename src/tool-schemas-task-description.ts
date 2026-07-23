import { z } from "zod";

export const taskAuthoringEvidenceInputSchema = z
  .record(z.string(), z.unknown())
  .optional()
  .describe(
    "Required for AI or automation task creation: declare an action/outcome title, plain-language review, and exact analogy/example excerpts from the description.",
  );

export const descriptionImpactReviewSchema = z.object({
  reviewedTaskUpdatedAt: z.string().min(1),
  reviewedDescriptionSha256: z.string().regex(/^[0-9a-f]{64}$/),
  decision: z.enum(["unchanged", "rewrite"]),
  reasonCode: z.enum([
    "operational_only",
    "review_only",
    "completion_only",
    "completion_summary_only",
    "historical_time_only",
    "node_completion_only",
    "placement_reviewed_no_semantic_change",
    "title_clarification_no_semantic_change",
    "semantic_change",
    "description_correction",
    "post_completion_revision",
  ]),
  rationale: z.string().min(1),
  fiveDimensionsReviewed: z.boolean().optional(),
  authoringEvidence: taskAuthoringEvidenceInputSchema,
  writebackRefs: z.array(z.string().min(1)).optional(),
});

export const historicalTaskMutationSchema = z.object({
  clientMutationId: z.string().min(1),
  op: z.enum(["create", "update", "softDelete"]),
  taskId: z.string().min(1).optional(),
  fields: z.record(z.string(), z.unknown()).optional(),
  authoringEvidence: taskAuthoringEvidenceInputSchema,
  descriptionImpactReview: descriptionImpactReviewSchema.optional(),
  reason: z.string().min(1).optional(),
});
