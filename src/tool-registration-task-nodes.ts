import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ReviewCardDraft, ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowTaskNodeListTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { taskNodeApiTool } = context;
  registerTool(
    "granoflow_task_node_list",
    "Read the latest Granoflow task nodes before planning, executing, or reconciling cross-device changes.",
    { taskId: z.string().min(1) },
    async ({ taskId }) => taskNodeApiTool({ path: `/v1/tasks/${String(taskId)}/nodes` }),
  );
}

function registerGranoflowTaskNodeBatchCreateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { taskNodeApiTool, taskNodeCreateSchema } = context;
  registerTool(
    "granoflow_task_node_batch_create",
    "Atomically create an ordered, idempotent task node batch through the Granoflow NodeService.",
    {
      taskId: z.string().min(1),
      idempotencyKey: z.string().min(1),
      expectedTaskUpdatedAt: z.string().datetime(),
      nodes: z.array(taskNodeCreateSchema).min(1).max(50),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, idempotencyKey, expectedTaskUpdatedAt, nodes, dryRun }) =>
      taskNodeApiTool({
        method: "POST",
        path: `/v1/tasks/${String(taskId)}/nodes`,
        body: { idempotencyKey, expectedTaskUpdatedAt, nodes },
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowTaskNodeUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    compactRecord,
    taskNodeApiTool,
    taskNodeStatusSchema,
    requireTaskAnalysisPlanAttachment,
    jsonTextResult,
  } = context;
  registerTool(
    "granoflow_task_node_update",
    "Update a task node title or apply pending/finished status with optimistic concurrency.",
    {
      taskId: z.string().min(1),
      nodeId: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      title: z.string().min(1).optional(),
      status: taskNodeStatusSchema.optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, nodeId, expectedUpdatedAt, title, status, dryRun }) => {
      if (status === "finished" && dryRun === false) {
        const documentGate = await requireTaskAnalysisPlanAttachment(String(taskId));
        if (!documentGate.ok) return jsonTextResult(documentGate);
      }
      return taskNodeApiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}/nodes/${String(nodeId)}`,
        body: compactRecord({ expectedUpdatedAt, title, status }),
        dryRun: dryRun !== false,
      });
    },
  );
}

function registerGranoflowTaskNodeDeleteTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { taskNodeApiTool } = context;
  registerTool(
    "granoflow_task_node_delete",
    "Soft-delete a task node tree after a confirmed Work Document amendment and explicit confirmation.",
    {
      taskId: z.string().min(1),
      nodeId: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      confirmed: z.literal(true),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, nodeId, expectedUpdatedAt, dryRun }) =>
      taskNodeApiTool({
        method: "DELETE",
        path: `/v1/tasks/${String(taskId)}/nodes/${String(nodeId)}`,
        body: { expectedUpdatedAt, confirmed: true },
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowTaskFinishTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    jsonTextResult,
    finishTask,
    reviewCardDraftSchema,
    completionSourceSchema,
    parseCompletionSource,
  } = context;
  registerTool(
    "granoflow_task_finish",
    "Finish a node-less compatibility task after its required Delivery gate and verify status=done. Derive endedAt from the confirmed completion time. startedAt must represent when execution actually began, normally already App-recorded by the status=doing transition; never substitute the earlier task discussion or creation time. If an evidence-based correction is required at completion, this tool sends it only through the supported complete action. Do not use for node-backed tasks. taskReview/reviewCardDrafts remain legacy explicit-inline compatibility only; deferred Review is the default.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      projectId: z
        .string()
        .min(1)
        .optional()
        .describe("Required when taskReview or reviewCardDrafts are provided."),
      milestoneId: z
        .string()
        .min(1)
        .optional()
        .describe("Required when taskReview or reviewCardDrafts are provided."),
      summary: z
        .string()
        .optional()
        .describe("Short import summary for the completion, review, and card write."),
      startedAt: z
        .string()
        .optional()
        .describe(
          "Actual execution start time, only for evidence-based correction through the complete action. Do not use task discussion or creation time.",
        ),
      taskReview: z
        .string()
        .optional()
        .describe(
          "Meaningful task review only. Omit this when the content would be a mere activity log.",
        ),
      reviewCardDrafts: z
        .array(reviewCardDraftSchema)
        .optional()
        .describe(
          "One card per durable knowledge point worth long-term memory; omit when there is nothing worth remembering.",
        ),
      endedAt: z
        .string()
        .optional()
        .describe(
          "Task end time inferred from the current agent conversation, preferably ISO-like.",
        ),
      completionSource: completionSourceSchema.describe(
        "Defaults to ai when an agent finishes the task. Use human for clearly human-completed work, or unknown to skip source tags.",
      ),
      confirmComplete: z.boolean().default(false).describe("Must be true when dryRun=false."),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the update/complete/import/readback sequence."),
    },
    async ({
      taskId,
      projectId,
      milestoneId,
      summary,
      startedAt,
      taskReview,
      reviewCardDrafts,
      endedAt,
      completionSource,
      confirmComplete,
      dryRun,
    }) =>
      jsonTextResult(
        await finishTask({
          taskId: String(taskId),
          projectId: typeof projectId === "string" ? projectId : undefined,
          milestoneId: typeof milestoneId === "string" ? milestoneId : undefined,
          summary: typeof summary === "string" ? summary : undefined,
          startedAt: typeof startedAt === "string" ? startedAt : undefined,
          taskReview: typeof taskReview === "string" ? taskReview : undefined,
          reviewCardDrafts: Array.isArray(reviewCardDrafts)
            ? (reviewCardDrafts as ReviewCardDraft[])
            : undefined,
          endedAt: typeof endedAt === "string" ? endedAt : undefined,
          completionSource: parseCompletionSource(completionSource),
          confirmComplete: confirmComplete === true,
          dryRun: dryRun !== false,
        }),
      ),
  );
}

export function registerTaskNodeTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowTaskNodeListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskNodeBatchCreateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskNodeUpdateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskNodeDeleteTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskFinishTool(registerTool, registerCapabilityTool, context, schemas);
}
