import { z } from "zod";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import type { ToolRegistrationContext, ToolRegistrar } from "./tools.js";
type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};
function registerGranoflowTaskCompletionRecordTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, contextPackSourceSchema, contextPackApiTool } = context;
  registerTool(
    "granoflow_task_completion_record",
    "Record an engineering task completion through Granoflow's controlled work-memory API and existing task write/complete paths.",
    {
      repo: z.string().min(1).optional(),
      title: z.string().min(1),
      summary: z.string().min(1),
      decisions: z.array(z.string().min(1)).optional(),
      outcome: z.enum(["success", "failed"]),
      tags: z.array(z.string().min(1)).optional(),
      client: z.string().min(1).default("mcp"),
      source: contextPackSourceSchema.optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ repo, title, summary, decisions, outcome, tags, client, source, dryRun }) =>
      contextPackApiTool({
        method: "POST",
        path: "/v1/ai-agent/task-completions",
        body: compactRecord({
          repo,
          title,
          summary,
          decisions,
          outcome,
          tags,
          client: client ?? "mcp",
          source,
        }),
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowReviewCardRecordTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, contextPackSourceSchema, contextPackApiTool } = context;
  registerTool(
    "granoflow_review_card_record",
    "Record a reusable review-card lesson through Granoflow's controlled work-memory API. The app may fail closed until controlled review-card import/create paths are available.",
    {
      title: z.string().min(1),
      problem: z.string().min(1),
      solution: z.string().min(1),
      tags: z.array(z.string().min(1)).optional(),
      client: z.string().min(1).default("mcp"),
      source: contextPackSourceSchema.optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ title, problem, solution, tags, client, source, dryRun }) =>
      contextPackApiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards",
        body: compactRecord({
          title,
          problem,
          solution,
          tags,
          client: client ?? "mcp",
          source,
        }),
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowTagListTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { apiTool } = context;
  registerTool(
    "granoflow_tag_list",
    "List tags from the Granoflow local catalog.",
    {
      kind: z
        .string()
        .optional()
        .describe("Optional tag kind filter forwarded to the Local HTTP API."),
    },
    async ({ kind }) => {
      const path =
        typeof kind === "string" && kind.trim()
          ? `/v1/tags?kind=${encodeURIComponent(kind.trim())}`
          : "/v1/tags";
      return apiTool({ path });
    },
  );
}

function registerGranoflowTagCreateTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { compactRecord, apiTool } = context;
  registerTool(
    "granoflow_tag_create",
    "Create a custom Granoflow tag. Defaults to dry-run.",
    {
      label: z.string().min(1),
      slug: z.string().min(1).optional(),
      iconKey: z.string().optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ label, slug, iconKey, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/tags",
        body: compactRecord({ label, slug, iconKey }),
        dryRun: dryRun !== false,
      }),
  );
}

function registerGranoflowSourceTagsEnsureTool(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  _schemas: RegistrationSchemas,
): void {
  const { jsonTextResult, requestGranoflowApi, extractItems, ensureSourceTags } = context;
  registerTool(
    "granoflow_source_tags_ensure",
    "Ensure the AI and 人工 completion source tags exist in Granoflow. Idempotent: reuses existing tags matched by slug or label.",
    {
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, only inspects the current catalog without creating missing tags."),
    },
    async ({ dryRun }) => {
      if (dryRun !== false) {
        const listResult = await requestGranoflowApi({ method: "GET", path: "/v1/tags" });
        return jsonTextResult({
          ...listResult,
          code: "dry_run",
          data: {
            previewMode: "catalog_inspection_only",
            tags: extractItems(listResult.data),
            expected: {
              ai: { label: "AI", slug: "custom_ai" },
              human: { label: "人工", slug: "custom_u4eba5de5" },
            },
          },
        });
      }
      return jsonTextResult(await ensureSourceTags());
    },
  );
}

export function registerTaskMemoryAndTagsTools(
  registerTool: ToolRegistrar,
  registerCapabilityTool: CapabilityRegistrar,
  context: ToolRegistrationContext,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerGranoflowTaskCompletionRecordTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowReviewCardRecordTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTagListTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowTagCreateTool(registerTool, registerCapabilityTool, context, schemas);
  registerGranoflowSourceTagsEnsureTool(registerTool, registerCapabilityTool, context, schemas);
}
