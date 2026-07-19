import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
import { readProjectInteractionStyle } from "./project-interaction-style.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowReviewCardDraftSchemaTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_review_card_draft_schema",
    "Fetch the Granoflow review card draft template and field schema from the running app. Call before creating reviewCardDrafts so card types, note fields, layouts, and fallbacks match app import rules.",
    {},
    async () => apiTool({ path: "/v1/ai-agent/review-card-drafts/schema" }),
  );
}

function registerGranoflowReviewCardSimilarTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, compactRecord } = context;
  registerTool(
    "granoflow_review_card_similar",
    "Find potentially similar Granoflow review cards. The app prefers vector search and falls back to agent-supplied keywords; the agent must prefilter results before showing them to the user.",
    {
      summary: z.string().min(1).max(500),
      keywords: z.array(z.string().min(1)).max(12).optional(),
      limit: z.number().int().min(1).max(20).default(8),
    },
    async ({ summary, keywords, limit }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards/similar",
        body: compactRecord({ summary, keywords, limit: limit ?? 8 }),
      }),
  );
}

function registerGranoflowReviewCardAuthoringPreviewTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_review_card_authoring_preview",
    "Preview controlled review-card creation, existing-card linking, or field-level updates for an existing project or inbox task. This endpoint performs no writes and returns a confirmation token plus shared-note impact.",
    {
      taskId: z.string().min(1),
      operations: z.array(z.record(z.string(), z.unknown())).min(1),
    },
    async ({ taskId, operations }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards/authoring/preview",
        body: { taskId, operations },
      }),
  );
}

function registerGranoflowReviewCardAuthoringApplyTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, compactRecord } = context;
  registerTool(
    "granoflow_review_card_authoring_apply",
    "Apply only user-approved operations from a current review-card authoring preview. Returns app-owned readback; never call without explicit approval of the previewed operations.",
    {
      previewToken: z.string().min(1),
      previewHash: z.string().min(1),
      approvedOperationIds: z.array(z.string().min(1)).min(1),
      approvedFieldsByOperation: z.record(z.string(), z.array(z.string().min(1)).min(1)).optional(),
    },
    async ({ previewToken, previewHash, approvedOperationIds, approvedFieldsByOperation }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards/authoring/apply",
        body: compactRecord({
          previewToken,
          previewHash,
          approvedOperationIds,
          approvedFieldsByOperation,
        }),
      }),
  );
}

function registerGranoflowContextPackTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, contextPackScopeSchema, contextPackApiTool } = context;
  registerTool(
    "granoflow_context_pack",
    "Read a structured Granoflow work-memory context pack for the current agent task. Returns typed facts and match signals, not planning hints or recommendations.",
    {
      scope: contextPackScopeSchema.default("repo"),
      repo: z.string().min(1).optional(),
      taskId: z.string().min(1).optional(),
      projectId: z.string().min(1).optional(),
      query: z.string().min(1).optional(),
      limit: z.number().int().min(1).max(25).default(12),
      client: z.string().min(1).default("mcp"),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the request without calling the app."),
    },
    async ({ scope, repo, taskId, projectId, query, limit, client, dryRun }) =>
      contextPackApiTool({
        method: "POST",
        path: "/v1/ai-agent/context-pack",
        body: compactRecord({
          scope,
          repo,
          taskId,
          projectId,
          query,
          limit: limit ?? 12,
          client: client ?? "mcp",
        }),
        dryRun: dryRun === true,
      }),
  );
}

function registerGranoflowHistoricalTaskCandidatesTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, historicalTaskCandidatesApiTool } = context;
  registerTool(
    "granoflow_historical_task_candidates",
    "Read App-owned historical task candidate facts and bounded evidence for one current task. The tool never ranks again or turns relationship facts into recommendations.",
    {
      taskId: z.string().min(1),
      summary: z.string().max(500).optional(),
      errorText: z.string().max(1000).optional(),
      module: z.string().min(1).optional(),
      paths: z.array(z.string().min(1).max(240)).max(20).optional(),
      limit: z.number().int().min(1).max(12).default(8),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the request without calling the app."),
    },
    async ({ taskId, summary, errorText, module, paths, limit, dryRun }) =>
      historicalTaskCandidatesApiTool({
        method: "POST",
        path: "/v1/ai-agent/tasks/similar-solutions",
        body: compactRecord({
          taskId,
          summary,
          errorText,
          module,
          paths,
          limit: limit ?? 8,
          client: "mcp",
        }),
        dryRun: dryRun === true,
      }),
  );
}

function registerGranoflowMemoryBatchPreviewTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, memoryBatchItemSchema, memoryBatchPreviewApiTool, isObject } = context;
  registerTool(
    "granoflow_memory_batch_preview",
    "Ask the running Granoflow app to preview an AI-agent memory batch before any write. Granoflow owns project/milestone matching and duplicate signals; this MCP tool only forwards after capability checks.",
    {
      source: z.record(z.string(), z.unknown()).optional(),
      target: z
        .object({
          projectId: z.string().min(1).optional(),
          milestoneId: z.string().min(1).optional(),
        })
        .optional(),
      items: z.array(memoryBatchItemSchema).min(1).max(20),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the HTTP request without calling the app."),
    },
    async ({ source, target, items, dryRun }) =>
      memoryBatchPreviewApiTool({
        method: "POST",
        path: "/v1/ai-agent/memory-batches/preview",
        body: compactRecord({
          source: isObject(source) ? source : undefined,
          target: isObject(target) ? target : undefined,
          items,
          dryRun: true,
        }),
        dryRun: dryRun === true,
      }),
  );
}

function registerGranoflowContextStewardStatusTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, contextStewardStatus } = context;
  registerTool(
    "granoflow_context_steward_status",
    "Read Granoflow project and milestone context-steward state, including active milestones and the archived-milestone final-snapshot policy.",
    {
      projectId: z.string().min(1).optional(),
    },
    async ({ projectId }) =>
      jsonTextResult(
        await contextStewardStatus({
          projectId: typeof projectId === "string" ? projectId : undefined,
        }),
      ),
  );
}

function registerGranoflowProjectContextAttachmentsEnsureTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, projectContextAttachmentApiTool } = context;
  registerTool(
    "granoflow_project_context_attachments_ensure",
    "Ensure Granoflow canonical project context YAML attachments exist: project_snapshot.yaml and project_rules.yaml. Defaults to dry-run.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews missing attachments without writing."),
    },
    async ({ projectId, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/ensure",
        body: compactRecord({
          projectId,
          dryRun: dryRun !== false,
        }),
        dryRun: false,
      }),
  );
}

function registerGranoflowProjectContextAttachmentReadTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, projectContextAttachmentApiTool, projectContextAttachmentSchema } =
    context;
  registerTool(
    "granoflow_project_context_attachment_read",
    "Read a bounded section of project_snapshot.yaml or project_rules.yaml. Defaults to header, summary, and the smallest matching section; full read requires explicit intent.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      attachment: projectContextAttachmentSchema,
      section: z.string().min(1).optional(),
      query: z.string().min(1).optional(),
      intent: z
        .enum(["normal", "full_audit", "export", "migration", "rewrite", "full_read"])
        .default("normal"),
      allowFullRead: z.boolean().default(false),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the HTTP request without calling the app."),
    },
    async ({ projectId, attachment, section, query, intent, allowFullRead, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/read",
        body: compactRecord({
          projectId,
          attachment,
          section,
          query,
          intent: intent === "normal" ? undefined : intent,
          allowFullRead: allowFullRead === true,
        }),
        dryRun: dryRun === true,
      }),
  );
}

function registerGranoflowProjectContextAttachmentReconcileTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, projectContextAttachmentApiTool, projectContextAttachmentSchema } =
    context;
  registerTool(
    "granoflow_project_context_attachment_reconcile",
    "Check or reconcile project context YAML freshness. Low-risk factual snapshot deltas can reconcile; rules and wording conflicts return a proposal.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      attachment: projectContextAttachmentSchema,
      dryRun: z.boolean().default(true).describe("When true, previews reconcile without writing."),
    },
    async ({ projectId, attachment, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/reconcile",
        body: compactRecord({
          projectId,
          attachment,
          dryRun: dryRun !== false,
        }),
        dryRun: false,
      }),
  );
}

function registerGranoflowProjectContextAttachmentWriteTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, projectContextAttachmentApiTool, projectContextAttachmentSchema } =
    context;
  registerTool(
    "granoflow_project_context_attachment_write",
    "Write a project context YAML attachment through app-owned safety gates. project_rules.yaml requires confirmation; secret/privacy risks fail closed.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      attachment: projectContextAttachmentSchema,
      section: z.string().min(1).optional(),
      content: z.string().min(1),
      confirmed: z
        .boolean()
        .default(false)
        .describe("Required for project_rules.yaml rule, wording, or decision-note changes."),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the HTTP request without calling the app."),
    },
    async ({ projectId, attachment, section, content, confirmed, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/write",
        body: compactRecord({
          projectId,
          attachment,
          section,
          content,
          confirmed: confirmed === true,
        }),
        dryRun: dryRun === true,
      }),
  );
}

function registerGranoflowProjectInteractionStyleTool(
  registerTool: ToolRegistrar,
  _registerCapabilityTool: CapabilityRegistrar,
  _context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  registerTool(
    "granoflow_project_interaction_style",
    "Resolve the current project's explanation style. Missing or incomplete settings default to newcomer-friendly, detailed explanations; this tool never asks the user to choose.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      dryRun: z.boolean().default(false),
    },
    async ({ projectId, dryRun }) =>
      readProjectInteractionStyle(String(projectId), dryRun === true).then((result) => ({
        content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
      })),
  );
}

function registerGranoflowProjectContextUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, contextStewardEvidenceSchema, projectContextUpdate } = context;
  registerTool(
    "granoflow_project_context_update",
    "Update only a Granoflow project description as living context. Defaults to dry-run and requires an evidence summary.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      description: z.string().min(1),
      evidenceSummary: contextStewardEvidenceSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ projectId, description, evidenceSummary, dryRun }) =>
      jsonTextResult(
        await projectContextUpdate({
          projectId: String(projectId),
          description: String(description),
          evidenceSummary: String(evidenceSummary),
          dryRun: dryRun !== false,
        }),
      ),
  );
}

function registerGranoflowMilestoneContextUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, contextStewardEvidenceSchema, milestoneContextUpdate } = context;
  registerTool(
    "granoflow_milestone_context_update",
    "Update only an active Granoflow milestone description as living context. Fails closed for archived milestones and defaults to dry-run.",
    {
      milestoneId: z.string().min(1).describe("Granoflow milestone id."),
      projectId: z.string().min(1).optional(),
      description: z.string().min(1),
      evidenceSummary: contextStewardEvidenceSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ milestoneId, projectId, description, evidenceSummary, dryRun }) =>
      jsonTextResult(
        await milestoneContextUpdate({
          milestoneId: String(milestoneId),
          projectId: typeof projectId === "string" ? projectId : undefined,
          description: String(description),
          evidenceSummary: String(evidenceSummary),
          dryRun: dryRun !== false,
        }),
      ),
  );
}

function registerGranoflowMilestoneContextArchiveTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, milestoneArchiveClosureSchema, milestoneContextArchive } = context;
  registerTool(
    "granoflow_milestone_context_archive",
    "Preview a milestone archive context closure: final milestone state plus parent project description update. Real writes fail closed until the app exposes a safe archive API.",
    {
      milestoneId: z.string().min(1).describe("Granoflow milestone id."),
      projectId: z.string().min(1).describe("Parent Granoflow project id."),
      closure: milestoneArchiveClosureSchema,
      confirmArchive: z
        .boolean()
        .default(false)
        .describe("Reserved for future safe archive writes; dry-run remains the normal mode."),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the closure without writing."),
    },
    async ({ milestoneId, projectId, closure, confirmArchive, dryRun }) =>
      jsonTextResult(
        await milestoneContextArchive({
          milestoneId: String(milestoneId),
          projectId: String(projectId),
          closure: closure as z.infer<typeof milestoneArchiveClosureSchema>,
          confirmArchive: confirmArchive === true,
          dryRun: dryRun !== false,
        }),
      ),
  );
}

export function registerReviewAndContextTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowReviewCardDraftSchemaTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowReviewCardSimilarTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowReviewCardAuthoringPreviewTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowReviewCardAuthoringApplyTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowContextPackTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowHistoricalTaskCandidatesTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowMemoryBatchPreviewTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowContextStewardStatusTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectContextAttachmentsEnsureTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowProjectContextAttachmentReadTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowProjectContextAttachmentReconcileTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowProjectContextAttachmentWriteTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowProjectInteractionStyleTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowProjectContextUpdateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowMilestoneContextUpdateTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
  registerGranoflowMilestoneContextArchiveTool(
    registerTool,
    registerCapabilityTool,
    context,
    schemas,
  );
}
