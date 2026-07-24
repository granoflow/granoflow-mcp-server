import { z } from "zod";

import {
  reviewTaskDescriptionImpact,
  verifyTaskDescriptionImpact,
} from "./tool-runtime-task-description-impact.js";
import type { ReviewCardDraft, ToolRegistrationContext, ToolRegistrar } from "./tools.js";

function impactResult<T extends { data?: unknown }>(
  context: ToolRegistrationContext,
  result: T,
  descriptionImpact: unknown,
) {
  return context.jsonTextResult({
    ...result,
    data: {
      ...(context.isObject(result.data) ? result.data : { result: result.data }),
      descriptionImpact,
    },
  });
}

async function completeNodeLessTaskWithImpact(
  context: ToolRegistrationContext,
  input: Record<string, unknown>,
) {
  const taskId = String(input.taskId);
  const body = context.isObject(input.input) ? input.input : {};
  const completionBody = { ...body, status: "done" };
  const gate = await reviewTaskDescriptionImpact(
    {
      taskId,
      review: input.descriptionImpactReview,
      operation: "completion",
      syntheticBody: completionBody,
    },
    completionBody,
    context.validateTaskAuthoringQuality,
  );
  if (!gate.ok) return context.jsonTextResult(gate);
  const result = await context.completeNodeLessTask({
    taskId,
    body,
    dryRun: input.dryRun !== false,
  });
  if (result.ok && input.dryRun === false) {
    const verification = await verifyTaskDescriptionImpact(taskId, gate, completionBody);
    if (!verification.ok) return context.jsonTextResult(verification);
    return impactResult(context, result, verification.data);
  }
  return impactResult(context, result, {
    changedFields: gate.changedFields,
    decision: gate.review.decision,
    reasonCode: gate.review.reasonCode,
    readbackStatus: "preview_only",
  });
}

function taskFinishSchema(context: ToolRegistrationContext) {
  return {
    taskId: z.string().min(1).describe("Granoflow task id."),
    projectId: z.string().min(1).optional(),
    milestoneId: z.string().min(1).optional(),
    summary: z.string().optional(),
    startedAt: z
      .string()
      .optional()
      .describe("Actual execution start time captured while AI execution remains pending."),
    taskReview: z.string().optional(),
    reviewCardDrafts: z.array(context.reviewCardDraftSchema).optional(),
    endedAt: z.string().optional(),
    completionSource: context.completionSourceSchema,
    descriptionImpactReview: context.descriptionImpactReviewSchema,
    confirmComplete: z.boolean().default(false),
    dryRun: z.boolean().default(true),
  };
}

async function finishTaskWithImpact(
  context: ToolRegistrationContext,
  input: Record<string, unknown>,
) {
  const taskId = String(input.taskId);
  const completionBody = context.compactRecord({
    status: "done",
    startedAt: input.startedAt,
    endedAt: input.endedAt,
    taskReview: input.taskReview,
  });
  const gate = await reviewTaskDescriptionImpact(
    {
      taskId,
      review: input.descriptionImpactReview,
      operation: "completion",
      syntheticBody: completionBody,
    },
    completionBody,
    context.validateTaskAuthoringQuality,
  );
  if (!gate.ok) return context.jsonTextResult(gate);
  const result = await context.finishTask({
    taskId,
    projectId: typeof input.projectId === "string" ? input.projectId : undefined,
    milestoneId: typeof input.milestoneId === "string" ? input.milestoneId : undefined,
    summary: typeof input.summary === "string" ? input.summary : undefined,
    startedAt: typeof input.startedAt === "string" ? input.startedAt : undefined,
    taskReview: typeof input.taskReview === "string" ? input.taskReview : undefined,
    reviewCardDrafts: Array.isArray(input.reviewCardDrafts)
      ? (input.reviewCardDrafts as ReviewCardDraft[])
      : undefined,
    endedAt: typeof input.endedAt === "string" ? input.endedAt : undefined,
    completionSource: context.parseCompletionSource(input.completionSource),
    confirmComplete: input.confirmComplete === true,
    dryRun: input.dryRun !== false,
  });
  if (result.ok && input.dryRun === false) {
    const verification = await verifyTaskDescriptionImpact(taskId, gate, completionBody);
    if (!verification.ok) return context.jsonTextResult(verification);
    return impactResult(context, result, verification.data);
  }
  return impactResult(context, result, {
    changedFields: gate.changedFields,
    decision: gate.review.decision,
    reasonCode: gate.review.reasonCode,
    readbackStatus: "preview_only",
  });
}

export function registerTaskCompletionTools(
  registerTool: ToolRegistrar,
  context: ToolRegistrationContext,
): void {
  registerTool(
    "granoflow_task_complete",
    "Low-level node-less compatibility endpoint. Never call it for a task with Work Document nodes; NodeService owns completion for node-backed tasks.",
    {
      taskId: z.string().min(1),
      input: context.jsonInputSchema.optional(),
      descriptionImpactReview: context.descriptionImpactReviewSchema,
      dryRun: z.boolean().default(true),
    },
    async (input) => completeNodeLessTaskWithImpact(context, input),
  );
  registerTool(
    "granoflow_task_finish",
    "Finish a node-less compatibility task after its required Delivery gate and verify status=done. For AI execution, keep the task pending until this completion action and supply the captured actual startedAt plus confirmed endedAt. Do not use for node-backed tasks.",
    taskFinishSchema(context),
    async (input) => finishTaskWithImpact(context, input),
  );
}
