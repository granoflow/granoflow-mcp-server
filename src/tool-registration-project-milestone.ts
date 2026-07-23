import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowTaskResolveTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, resolveMatchModeSchema, resolveResource } = context;
  registerTool(
    "granoflow_task_resolve",
    "Resolve Granoflow task candidates by title without creating or updating data.",
    {
      query: z.string().min(1),
      matchMode: resolveMatchModeSchema,
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      includeDone: z.boolean().default(false),
    },
    async ({ query, matchMode, projectId, milestoneId, includeDone }) =>
      jsonTextResult(
        await resolveResource("task", {
          query: String(query),
          matchMode: matchMode as "exact" | "contains" | undefined,
          projectId: typeof projectId === "string" ? projectId : undefined,
          milestoneId: typeof milestoneId === "string" ? milestoneId : undefined,
          includeDone: includeDone === true,
        }),
      ),
  );
}

function registerGranoflowProjectListTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool("granoflow_project_list", "List Granoflow projects.", {}, async () =>
    apiTool({ path: "/v1/projects" }),
  );
}

function registerGranoflowProjectResolveTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, resolveMatchModeSchema, resolveResource } = context;
  registerTool(
    "granoflow_project_resolve",
    "Resolve Granoflow project candidates by title without creating or updating data.",
    {
      query: z.string().min(1),
      matchMode: resolveMatchModeSchema,
      includeDone: z.boolean().default(false),
    },
    async ({ query, matchMode, includeDone }) =>
      jsonTextResult(
        await resolveResource("project", {
          query: String(query),
          matchMode: matchMode as "exact" | "contains" | undefined,
          includeDone: includeDone === true,
        }),
      ),
  );
}

function registerGranoflowProjectCreateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, resourceStatusSchema, compactRecord } = context;
  registerTool(
    "granoflow_project_create",
    "Create a Granoflow project with common structured fields. Defaults to dry-run.",
    {
      title: z.string().min(1),
      description: z.string().optional(),
      domainTag: z.string().min(1).optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ title, description, domainTag, status, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/projects",
        body: compactRecord({
          title,
          description,
          domainTag,
          status,
        }),
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowProjectUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, resourceStatusSchema, compactRecord } = context;
  registerTool(
    "granoflow_project_update",
    "Update a Granoflow project with common structured fields. Defaults to dry-run.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      title: z.string().min(1).optional(),
      description: z.string().optional(),
      domainTag: z.string().min(1).optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ projectId, title, description, domainTag, status, dryRun }) =>
      apiTool({
        method: "PATCH",
        path: `/v1/projects/${String(projectId)}`,
        body: compactRecord({
          title,
          description,
          domainTag,
          status,
        }),
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowProjectDeleteTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, safeDeleteResource } = context;
  registerTool(
    "granoflow_project_delete",
    "Safely delete a Granoflow project. Defaults to dry-run and requires confirmTitle for writes.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      confirmTitle: z.string().min(1).optional(),
      allowLinkedTasks: z.boolean().default(false),
      dryRun: z.boolean().default(true),
    },
    async ({ projectId, confirmTitle, allowLinkedTasks, dryRun }) =>
      jsonTextResult(
        await safeDeleteResource("project", {
          id: String(projectId),
          confirmTitle: typeof confirmTitle === "string" ? confirmTitle : undefined,
          allowLinkedTasks: allowLinkedTasks === true,
          dryRun: dryRun !== false,
        }),
      ),
  );
}

function registerGranoflowMilestoneListTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool("granoflow_milestone_list", "List Granoflow milestones.", {}, async () =>
    apiTool({ path: "/v1/milestones" }),
  );
}

function registerGranoflowMilestoneResolveTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, resolveMatchModeSchema, resolveResource } = context;
  registerTool(
    "granoflow_milestone_resolve",
    "Resolve Granoflow milestone candidates by title without creating or updating data.",
    {
      query: z.string().min(1),
      matchMode: resolveMatchModeSchema,
      projectId: z.string().min(1).optional(),
      includeDone: z.boolean().default(false),
    },
    async ({ query, matchMode, projectId, includeDone }) =>
      jsonTextResult(
        await resolveResource("milestone", {
          query: String(query),
          matchMode: matchMode as "exact" | "contains" | undefined,
          projectId: typeof projectId === "string" ? projectId : undefined,
          includeDone: includeDone === true,
        }),
      ),
  );
}

function registerGranoflowMilestoneCreateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, jsonTextResult, resourceStatusSchema, compactRecord, defaultMilestoneDueAt } =
    context;
  registerTool(
    "granoflow_milestone_create",
    "Create a Granoflow milestone with common structured fields. When dueAt is omitted, the first project milestone defaults to today and each later milestone defaults to at least one local calendar day after the latest project deadline. Defaults to dry-run.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      title: z.string().min(1),
      description: z.string().optional(),
      dueAt: z
        .string()
        .optional()
        .describe(
          "Explicit deadline. When omitted, uses today at 23:59:59.000 for the first project milestone, then one local calendar day after the latest valid project deadline.",
        ),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ projectId, title, description, dueAt, status, dryRun }) => {
      let effectiveDueAt = typeof dueAt === "string" ? dueAt : undefined;
      if (!effectiveDueAt) {
        const defaultDeadline = await defaultMilestoneDueAt(String(projectId));
        if (defaultDeadline.error) {
          return jsonTextResult(defaultDeadline.error);
        }
        effectiveDueAt = defaultDeadline.dueAt;
      }
      return apiTool({
        method: "POST",
        path: "/v1/milestones",
        body: compactRecord({
          projectId,
          title,
          description,
          dueAt: effectiveDueAt,
          status,
        }),
        dryRun: dryRun !== false,
      });
    },
  );
}

function registerGranoflowMilestoneDeleteTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, safeDeleteResource } = context;
  registerTool(
    "granoflow_milestone_delete",
    "Safely delete a Granoflow milestone. Defaults to dry-run and requires confirmTitle for writes.",
    {
      milestoneId: z.string().min(1).describe("Granoflow milestone id."),
      confirmTitle: z.string().min(1).optional(),
      allowLinkedTasks: z.boolean().default(false),
      dryRun: z.boolean().default(true),
    },
    async ({ milestoneId, confirmTitle, allowLinkedTasks, dryRun }) =>
      jsonTextResult(
        await safeDeleteResource("milestone", {
          id: String(milestoneId),
          confirmTitle: typeof confirmTitle === "string" ? confirmTitle : undefined,
          allowLinkedTasks: allowLinkedTasks === true,
          dryRun: dryRun !== false,
        }),
      ),
  );
}

function registerGranoflowMilestoneUpdateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool, jsonTextResult, resourceStatusSchema, compactRecord, milestoneContextUpdate } =
    context;
  registerTool(
    "granoflow_milestone_update",
    "Update a Granoflow milestone with common structured fields. Defaults to dry-run. Use granoflow_milestone_context_update for description upkeep; description updates fail closed for archived milestones.",
    {
      milestoneId: z.string().min(1).describe("Granoflow milestone id."),
      projectId: z.string().min(1).optional(),
      title: z.string().min(1).optional(),
      description: z.string().optional(),
      dueAt: z.string().optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ milestoneId, projectId, title, description, dueAt, status, dryRun }) => {
      if (typeof description === "string") {
        return jsonTextResult(
          await milestoneContextUpdate({
            milestoneId: String(milestoneId),
            projectId: typeof projectId === "string" ? projectId : undefined,
            description,
            evidenceSummary: "Generic milestone update requested a description change.",
            dryRun: dryRun !== false,
          }),
        );
      }
      return apiTool({
        method: "PATCH",
        path: `/v1/milestones/${String(milestoneId)}`,
        body: compactRecord({
          projectId,
          title,
          dueAt,
          status,
        }),
        dryRun: dryRun !== false,
      });
    },
  );
}

export function registerProjectMilestoneTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowTaskResolveTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectResolveTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectCreateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectUpdateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowProjectDeleteTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowMilestoneListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowMilestoneResolveTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowMilestoneCreateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowMilestoneDeleteTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowMilestoneUpdateTool(registerTool, registerCapabilityTool, context, schemas);
}
