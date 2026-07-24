import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import { registerTaskCompletionTools } from "./tool-registration-task-completion.js";
import {
  reviewTaskDescriptionImpact,
  verifyTaskDescriptionImpact,
} from "./tool-runtime-task-description-impact.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowTaskExecutionSnapshotTool(
  registerTool: ToolRegistrar,
  context: ToolRegistrationContext,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_task_execution_snapshot",
    "Read one App-owned execution snapshot containing task, parent project/milestone, current revisions, nodes, and current logical attachment receipts.",
    { taskId: z.string().min(1) },
    async ({ taskId }) =>
      apiTool({
        path: `/v1/ai-agent/tasks/${String(taskId)}/execution-snapshot`,
      }),
  );
}

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
    descriptionImpactReviewSchema,
    validateTaskAuthoringQuality,
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
      descriptionImpactReview: descriptionImpactReviewSchema.optional(),
      dryRun: z.boolean().default(true),
    },
    async ({
      taskId,
      nodeId,
      expectedUpdatedAt,
      title,
      status,
      descriptionImpactReview,
      dryRun,
    }) => {
      const impactGate =
        status === "finished"
          ? await reviewTaskDescriptionImpact(
              {
                taskId: String(taskId),
                review: descriptionImpactReview,
                operation: "node_completion",
                syntheticBody: { status: "done" },
                verifyFields: false,
              },
              { status: "done" },
              validateTaskAuthoringQuality,
            )
          : null;
      if (impactGate && !impactGate.ok) return jsonTextResult(impactGate);
      if (status === "finished" && dryRun === false) {
        const documentGate = await requireTaskAnalysisPlanAttachment(String(taskId));
        if (!documentGate.ok) return jsonTextResult(documentGate);
      }
      const result = await taskNodeApiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}/nodes/${String(nodeId)}`,
        body: compactRecord({ expectedUpdatedAt, title, status }),
        dryRun: dryRun !== false,
      });
      if (impactGate?.ok && dryRun === false) {
        const verification = await verifyTaskDescriptionImpact(
          String(taskId),
          impactGate,
          { status: "done" },
          false,
        );
        if (!verification.ok) return jsonTextResult(verification);
      }
      return result;
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

export function registerTaskNodeTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowTaskExecutionSnapshotTool(registerTool, context);
  registerGranoflowTaskNodeListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskNodeBatchCreateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskNodeUpdateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskNodeDeleteTool(registerTool, registerCapabilityTool, context, schemas);
  registerTaskCompletionTools(registerTool, context);
}
