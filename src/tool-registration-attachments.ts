import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowTaskAttachmentListTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_task_attachment_list",
    "List attachments for a Granoflow task.",
    { taskId: z.string().min(1) },
    async ({ taskId }) => apiTool({ path: `/v1/tasks/${String(taskId)}/attachments` }),
  );
}

function registerGranoflowLogicalAttachmentReplaceTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    basename,
    createHash,
    readFileSync,
    logicalAttachmentEntityTypeSchema,
    logicalAttachmentSlotSchema,
    validatedLogicalAttachmentPath,
    jsonTextResult,
    resourceCapabilityApiTool,
    logicalAttachmentResource,
    logicalAttachmentPath,
  } = context;
  registerTool(
    "granoflow_logical_attachment_replace",
    "Read local file bytes at the MCP boundary, upload them through the Local HTTP API as Base64, replace the current typed project, milestone, or task artifact, and require App-owned SHA-256 readback before it becomes current. The file path is not sent to or opened by the Granoflow app.",
    {
      entityType: logicalAttachmentEntityTypeSchema,
      entityId: z.string().min(1),
      logicalSlot: logicalAttachmentSlotSchema,
      filePath: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      idempotencyKey: z.string().min(1),
      visualConfirmed: z
        .boolean()
        .default(false)
        .describe("Must be true when logicalSlot is ui_prototype."),
      dryRun: z.boolean().default(true),
    },
    async ({
      entityType,
      entityId,
      logicalSlot,
      filePath,
      expectedUpdatedAt,
      idempotencyKey,
      visualConfirmed,
      dryRun,
    }) => {
      let file: string;
      try {
        file = validatedLogicalAttachmentPath(String(filePath), String(logicalSlot));
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "unsafe_attachment_path",
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
      const bytes = readFileSync(file);
      const contentSha256 = createHash("sha256").update(bytes).digest("hex");
      return resourceCapabilityApiTool(
        logicalAttachmentResource(String(entityType)),
        ["attachment.conditional-add", "attachment.read-content-hash"],
        {
          method: "POST",
          path: logicalAttachmentPath(String(entityType), String(entityId)),
          body: {
            contentBase64: bytes.toString("base64"),
            fileName: basename(file),
            logicalSlot: String(logicalSlot),
            expectedUpdatedAt: String(expectedUpdatedAt),
            expectedContentSha256: contentSha256,
            idempotencyKey: String(idempotencyKey),
            visualConfirmed: visualConfirmed === true,
          },
          dryRun: dryRun !== false,
        },
      );
    },
  );
}

function registerGranoflowLogicalAttachmentReadTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const {
    logicalAttachmentEntityTypeSchema,
    resourceCapabilityApiTool,
    logicalAttachmentResource,
    logicalAttachmentPath,
  } = context;
  registerTool(
    "granoflow_logical_attachment_read",
    "Read one current logical attachment receipt. Bounded Markdown/YAML includes content; acceptance HTML and other non-text artifacts return App-owned SHA-256 and size metadata without exposing content.",
    {
      entityType: logicalAttachmentEntityTypeSchema,
      entityId: z.string().min(1),
      attachmentId: z.string().min(1),
    },
    async ({ entityType, entityId, attachmentId }) =>
      resourceCapabilityApiTool(
        logicalAttachmentResource(String(entityType)),
        ["attachment.read-content-hash"],
        {
          path: `${logicalAttachmentPath(String(entityType), String(entityId))}/${String(attachmentId)}`,
        },
      ),
  );
}

function registerGranoflowProjectWorkEvaluateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { projectWorkActionSchema, apiTool } = context;
  registerTool(
    "granoflow_project_work_evaluate",
    "Evaluate the current Project Work YAML for a manual or automatic action. Partial attachment is allowed; gated actions fail with all relevant missing paths.",
    {
      projectId: z.string().min(1),
      action: projectWorkActionSchema,
      requiredPaths: z.array(z.string().min(1)).optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ projectId, action, requiredPaths, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/project-work/evaluate",
        body: {
          projectId: String(projectId),
          action: String(action),
          ...(requiredPaths ? { requiredPaths } : {}),
        },
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowProjectWorkConfirmTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_project_work_confirm",
    "Confirm the exact current Project Work content hash in the App. Confirmation does not authorize execution, commit, push, publish, deploy, deletion, payment, or messaging.",
    {
      projectId: z.string().min(1),
      expectedContentSha256: z.string().regex(/^[a-f0-9]{64}$/),
      confirmed: z.literal(true),
      dryRun: z.boolean().default(true),
    },
    async ({ projectId, expectedContentSha256, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/project-work/confirm",
        body: {
          projectId: String(projectId),
          expectedContentSha256: String(expectedContentSha256),
        },
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowTaskAttachmentAddMarkdownTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { validatedWorkflowMarkdownPath, jsonTextResult, addTaskWorkflowAttachment } = context;
  registerTool(
    "granoflow_task_attachment_add_markdown",
    "Read Markdown bytes locally and upload through the Local HTTP API as Base64. Typed Task Work and Task Delivery headers are automatically routed to their logical slots; legacy untyped Analysis/Plan stays a generic attachment. Defaults to dry-run.",
    {
      taskId: z.string().min(1),
      filePath: z.string().min(1),
      idempotencyKey: z.string().min(1),
      expectedTaskUpdatedAt: z.string().datetime(),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, filePath, idempotencyKey, expectedTaskUpdatedAt, dryRun }) => {
      let file: string;
      try {
        file = validatedWorkflowMarkdownPath(String(filePath));
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "unsafe_attachment_path",
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
      try {
        return jsonTextResult(
          await addTaskWorkflowAttachment({
            taskId: String(taskId),
            filePath: file,
            idempotencyKey: String(idempotencyKey),
            expectedTaskUpdatedAt: String(expectedTaskUpdatedAt),
            dryRun: dryRun !== false,
          }),
        );
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "task_workflow_header_invalid",
          data: {
            transport: "contentBase64",
            localPathRole: "mcp_read_boundary_only",
            writesPerformed: false,
          },
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
    },
  );
}

function registerGranoflowTaskAttachmentReadMarkdownTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_task_attachment_read_markdown",
    "Read a bounded Task Work Document, legacy Task Analysis/Plan, or Task Delivery Markdown attachment with its App-owned SHA-256 for verification.",
    {
      taskId: z.string().min(1),
      attachmentId: z.string().min(1),
    },
    async ({ taskId, attachmentId }) =>
      apiTool({
        path: `/v1/tasks/${String(taskId)}/attachments/${String(attachmentId)}`,
      }),
  );
}

function registerGranoflowTaskAttachmentDeleteTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_task_attachment_delete",
    "Delete a task attachment after explicit confirmation.",
    {
      taskId: z.string().min(1),
      attachmentId: z.string().min(1),
      confirmed: z.literal(true),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, attachmentId, dryRun }) =>
      apiTool({
        method: "DELETE",
        path: `/v1/tasks/${String(taskId)}/attachments/${String(attachmentId)}`,
        body: { confirmed: true },
        dryRun: dryRun !== false,
      }),
  );
}

export function registerAttachmentTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowTaskAttachmentListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowLogicalAttachmentReplaceTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowLogicalAttachmentReadTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowProjectWorkEvaluateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectWorkConfirmTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTaskAttachmentAddMarkdownTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowTaskAttachmentReadMarkdownTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowTaskAttachmentDeleteTool(registerTool, registerCapabilityTool, context, schemas);
}
