import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import { registerTaskHistoryMutationTool } from "./tool-registration-task-history.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowTaskListTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_task_list",
    "List tasks from Granoflow. Optionally filter by tag slug.",
    {
      tag: z.string().min(1).optional().describe("Return only tasks containing this tag slug."),
    },
    async ({ tag }) =>
      apiTool({
        path:
          typeof tag === "string" && tag.trim()
            ? `/v1/tasks?tag=${encodeURIComponent(tag.trim())}`
            : "/v1/tasks",
      }),
  );
}

function registerGranoflowTaskExportTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_task_export",
    "Export task details, reusable lessons, and App-admitted prototype inputs. The App is the sole execution-admission authority; this tool never guesses current or latest prototype versions.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      includePrototypes: z
        .boolean()
        .default(true)
        .describe("Include structured prototype admission and admitted assets."),
      assetMode: z
        .enum(["metadata", "file"])
        .default("metadata")
        .describe("Use file to request short-lived decrypted package paths."),
      ttlSeconds: z
        .number()
        .int()
        .min(1)
        .max(600)
        .default(600)
        .describe("Temporary prototype asset lifetime, capped at 600 seconds."),
      fetchMissing: z
        .boolean()
        .default(false)
        .describe("Allow the App to fetch a missing local package before export."),
    },
    async ({ taskId, includePrototypes, assetMode, ttlSeconds, fetchMissing }) => {
      const query = new URLSearchParams({
        includePrototypes: String(includePrototypes),
        assetMode: String(assetMode),
        ttlSeconds: String(ttlSeconds),
        fetchMissing: String(fetchMissing),
      });
      return apiTool({
        path: `/v1/ai-agent/tasks/${String(taskId)}/export?${query.toString()}`,
      });
    },
  );
}

function registerGranoflowTaskValidateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonInputSchema, apiTool } = context;
  registerTool(
    "granoflow_task_validate",
    "Validate an AI-agent task result before importing it into Granoflow.",
    { input: jsonInputSchema },
    async ({ input }) =>
      apiTool({ method: "POST", path: "/v1/ai-agent/tasks/validate", body: input }),
  );
}

function registerGranoflowTaskImportTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonInputSchema, apiTool } = context;
  registerTool(
    "granoflow_task_import",
    "Import an AI-agent task result into Granoflow. Use dryRun first unless the user explicitly asks to write.",
    {
      input: jsonInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ input, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/tasks/import",
        body: input,
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowTaskCreateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    jsonInputSchema,
    apiToolForTaskWrite,
    taskAuthoringQualityFailure,
    isObject,
    ordinaryTaskWriteFailure,
    parseCompletionSource,
  } = context;
  registerTool(
    "granoflow_task_create",
    "Create a current Granoflow task from a JSON payload in pending state. Do not include createdAt, updatedAt, startedAt, endedAt, or deletedAt. AI execution keeps the task pending until its completion owner changes it to done and records its actual start through granoflow_task_history_mutate; status=doing is reserved for human focus. AI and automation callers must include input.authoringEvidence proving an action/outcome title, plain-language review, and exact real-analogy and concrete-example excerpts. Invalid evidence returns task_authoring_quality_failed before any task write. A milestone-bound task without dueAt inherits the selected milestone deadline. Tags not in the local catalog are skipped automatically. Optional completionSource attaches AI/人工 source tags for completed-work capture.",
    {
      input: jsonInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ input, dryRun }) => {
      const record = isObject(input) ? { ...input } : {};
      const authoringEvidence = record.authoringEvidence;
      delete record.authoringEvidence;
      const qualityFailure = taskAuthoringQualityFailure(
        record.title,
        record.description,
        authoringEvidence,
      );
      if (qualityFailure) return qualityFailure;
      const writeFailure = ordinaryTaskWriteFailure(record, "create");
      if (writeFailure) return writeFailure;
      const completionSource = parseCompletionSource(record.completionSource);
      delete record.completionSource;
      return apiToolForTaskWrite(
        {
          method: "POST",
          path: "/v1/tasks",
          dryRun: dryRun !== false,
        },
        record,
        completionSource,
      );
    },
  );
}

function registerGranoflowTaskCreateStructuredTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    compactRecord,
    completionSourceSchema,
    taskAuthoringEvidenceInputSchema,
    apiToolForTaskWrite,
    taskAuthoringQualityFailure,
    ordinaryTaskWriteFailure,
    parseCompletionSource,
  } = context;
  registerTool(
    "granoflow_task_create_structured",
    "Create a current Granoflow task in pending state with common structured fields. Ordinary creation never accepts startedAt or other historical physical fields. AI execution stays pending until verified completion, records its actual start through granoflow_task_history_mutate, and never claims the human doing focus slot. AI and automation callers must provide authoringEvidence for an action/outcome title, plain-language review, and exact real-analogy and concrete-example excerpts. Invalid evidence returns task_authoring_quality_failed before any task write. A milestone-bound task without dueAt inherits the selected milestone deadline; an explicit later date fails closed. Tags not in the local catalog are skipped automatically. Defaults to dry-run.",
    {
      title: z.string().min(1),
      description: z.string().optional(),
      dueAt: z
        .string()
        .optional()
        .describe(
          "Explicit task deadline. When milestoneId is supplied and this is omitted, the task inherits the selected milestone deadline. A later explicit date fails closed.",
        ),
      remindAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: z
        .literal("pending")
        .optional()
        .describe("Ordinary current-task creation starts pending; omit or pass pending."),
      tags: z.array(z.string().min(1)).optional(),
      completionSource: completionSourceSchema,
      authoringEvidence: taskAuthoringEvidenceInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({
      title,
      description,
      dueAt,
      remindAt,
      projectId,
      milestoneId,
      status,
      tags,
      completionSource,
      authoringEvidence,
      dryRun,
    }) => {
      const qualityFailure = taskAuthoringQualityFailure(title, description, authoringEvidence);
      if (qualityFailure) return qualityFailure;
      const taskBody = compactRecord({
        title,
        description,
        dueAt,
        remindAt,
        projectId,
        milestoneId,
        status,
        tags,
      });
      const writeFailure = ordinaryTaskWriteFailure(taskBody, "create");
      if (writeFailure) return writeFailure;
      return apiToolForTaskWrite(
        {
          method: "POST",
          path: "/v1/tasks",
          dryRun: dryRun !== false,
        },
        taskBody,
        parseCompletionSource(completionSource),
      );
    },
  );
}

function registerGranoflowTaskUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonInputSchema, apiToolForTaskWrite, isObject, ordinaryTaskWriteFailure } = context;
  registerTool(
    "granoflow_task_update",
    "Update a current Granoflow task through the Local HTTP API. Do not include historical physical fields. AI execution must not set status=doing: keep pending, record actual startedAt through granoflow_task_history_mutate, and complete through NodeService or granoflow_task_finish. Human manual focus may set doing. Tags not in the local catalog are skipped automatically.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      input: jsonInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ taskId, input, dryRun }) => {
      const record = isObject(input) ? { ...input } : {};
      const descriptionImpactReview = record.descriptionImpactReview;
      delete record.descriptionImpactReview;
      const writeFailure = ordinaryTaskWriteFailure(record, "update");
      if (writeFailure) return writeFailure;
      return apiToolForTaskWrite(
        {
          method: "PATCH",
          path: `/v1/tasks/${String(taskId)}`,
          dryRun: dryRun !== false,
        },
        record,
        undefined,
        {
          taskId: String(taskId),
          review: descriptionImpactReview,
          operation: "update",
        },
      );
    },
  );
}

function registerGranoflowTaskUpdateStructuredTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    compactRecord,
    resourceStatusSchema,
    descriptionImpactReviewSchema,
    apiToolForTaskWrite,
  } = context;
  registerTool(
    "granoflow_task_update_structured",
    "Update a current Granoflow task with common structured fields. AI execution never sets status=doing: it remains pending until verified completion and writes actual execution time through granoflow_task_history_mutate. status=doing is for human manual focus and keeps the App-recorded start behavior. When moving it into a milestone without dueAt, inherit the milestone deadline; a later explicit date fails closed. Defaults to dry-run.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      title: z.string().min(1).optional(),
      description: z.string().optional(),
      taskReview: z.string().optional(),
      dueAt: z
        .string()
        .optional()
        .describe(
          "Explicit task deadline. When milestoneId is supplied and this is omitted, the task inherits the selected milestone deadline. A later explicit date fails closed.",
        ),
      remindAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      expectedUpdatedAt: z.string().datetime().optional(),
      descriptionImpactReview: descriptionImpactReviewSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({
      taskId,
      title,
      description,
      taskReview,
      dueAt,
      remindAt,
      projectId,
      milestoneId,
      status,
      expectedUpdatedAt,
      descriptionImpactReview,
      dryRun,
    }) =>
      apiToolForTaskWrite(
        {
          method: "PATCH",
          path: `/v1/tasks/${String(taskId)}`,
          dryRun: dryRun !== false,
        },
        compactRecord({
          title,
          description,
          taskReview,
          dueAt,
          remindAt,
          projectId,
          milestoneId,
          status,
          expectedUpdatedAt,
        }),
        undefined,
        {
          taskId: String(taskId),
          review: descriptionImpactReview,
          operation: "update",
        },
      ),
  );
}

function registerGranoflowTaskReviewUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    TASK_REVIEW_START,
    TASK_REVIEW_END,
    apiToolForTaskWrite,
    descriptionImpactReviewSchema,
    jsonTextResult,
    validateManagedBlock,
  } = context;
  registerTool(
    "granoflow_task_review_update",
    "Safely write a confirmed structured Task Review to any task, including completed inbox tasks, using the latest task revision. Review cards and context promotion remain separate controlled steps.",
    {
      taskId: z.string().min(1),
      taskReview: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      descriptionImpactReview: descriptionImpactReviewSchema,
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, taskReview, expectedUpdatedAt, descriptionImpactReview, dryRun }) => {
      const review = String(taskReview);
      const markers = validateManagedBlock(review, TASK_REVIEW_START, TASK_REVIEW_END);
      const revisionPresent = /\breview_revision:\s*[1-9]\d*\b/.test(review);
      const operationPresent = /\breview_operation_id:\s*\S+/.test(review);
      if (!markers.ok || !revisionPresent || !operationPresent) {
        return jsonTextResult({
          ok: false,
          code: "task_review_markers_invalid",
          data: {
            reason: !markers.ok
              ? markers.reason
              : !revisionPresent
                ? "review_revision_missing"
                : "review_operation_id_missing",
          },
          error: {
            message:
              "Structured Task Review requires one valid marker pair, a positive review_revision, and review_operation_id.",
          },
        });
      }
      return apiToolForTaskWrite(
        {
          method: "PATCH",
          path: `/v1/tasks/${String(taskId)}`,
          dryRun: dryRun !== false,
        },
        { taskReview: review, expectedUpdatedAt },
        undefined,
        {
          taskId: String(taskId),
          review: descriptionImpactReview,
          operation: "review",
        },
      );
    },
  );
}

function registerGranoflowTaskCompletionSummaryUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    TASK_COMPLETION_SUMMARY_START,
    TASK_COMPLETION_SUMMARY_END,
    apiToolForTaskWrite,
    descriptionImpactReviewSchema,
    jsonTextResult,
    validateManagedBlock,
  } = context;
  registerTool(
    "granoflow_task_completion_summary_update",
    "Safely update a task description that already preserves all user text and contains exactly one Task Completion Summary managed block.",
    {
      taskId: z.string().min(1),
      description: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      descriptionImpactReview: descriptionImpactReviewSchema,
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, description, expectedUpdatedAt, descriptionImpactReview, dryRun }) => {
      const nextDescription = String(description);
      const markers = validateManagedBlock(
        nextDescription,
        TASK_COMPLETION_SUMMARY_START,
        TASK_COMPLETION_SUMMARY_END,
      );
      if (!markers.ok) {
        return jsonTextResult({
          ok: false,
          code: "task_completion_summary_markers_invalid",
          data: { reason: markers.reason },
          error: { message: "Task Completion Summary markers are not safe to update." },
        });
      }
      return apiToolForTaskWrite(
        {
          method: "PATCH",
          path: `/v1/tasks/${String(taskId)}`,
          dryRun: dryRun !== false,
        },
        { description: nextDescription, expectedUpdatedAt },
        undefined,
        {
          taskId: String(taskId),
          review: descriptionImpactReview,
          operation: "completion_summary",
          managedBlockMarkers: {
            start: TASK_COMPLETION_SUMMARY_START,
            end: TASK_COMPLETION_SUMMARY_END,
          },
        },
      );
    },
  );
}

export function registerTaskCrudTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowTaskListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskExportTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskValidateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskImportTool(registerTool, registerCapabilityTool, context, schemas);
  registerTaskHistoryMutationTool(registerTool, context);
  registerGranoflowTaskCreateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskCreateStructuredTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskUpdateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskUpdateStructuredTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskReviewUpdateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskCompletionSummaryUpdateTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
}
