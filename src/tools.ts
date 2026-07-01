import { z } from "zod";

import { requestGranoflowApi, type ApiRequestOptions } from "./api.js";
import {
  detectLocalApi,
  getSetupStatus,
  openGranoflowApp,
  openSetupConfig,
  writeSetupConfig,
} from "./setup.js";

const jsonInputSchema = z
  .record(z.string(), z.unknown())
  .describe("JSON object sent to the Granoflow Local HTTP API.");

function textResult(text: string) {
  return {
    content: [{ type: "text" as const, text }],
  };
}

function jsonTextResult(value: unknown) {
  return textResult(JSON.stringify(value, null, 2));
}

async function apiTool(options: ApiRequestOptions) {
  return jsonTextResult(await requestGranoflowApi(options));
}

export function registerGranoflowTools(server: {
  tool: (
    name: string,
    description: string,
    schema: Record<string, z.ZodTypeAny>,
    handler: (args: Record<string, unknown>) => Promise<ReturnType<typeof textResult>>,
  ) => void;
}) {
  server.tool(
    "granoflow_setup_status",
    "Inspect Granoflow MCP config and Local HTTP API health without printing secrets.",
    {},
    async () => jsonTextResult(await getSetupStatus()),
  );

  server.tool(
    "granoflow_setup_detect_local_api",
    "Probe a bounded localhost port list for a running Granoflow Local HTTP API.",
    {
      ports: z
        .array(z.number().int().min(1).max(65_535))
        .max(20)
        .optional()
        .describe("Small localhost port candidate list. Defaults to known Granoflow candidates."),
      timeoutMs: z.number().int().min(50).max(5_000).optional(),
    },
    async ({ ports, timeoutMs }) =>
      jsonTextResult(
        await detectLocalApi({
          ports: Array.isArray(ports) ? ports.map(Number) : undefined,
          timeoutMs: typeof timeoutMs === "number" ? timeoutMs : undefined,
        }),
      ),
  );

  server.tool(
    "granoflow_setup_write_config",
    "Preview or write MCP-owned non-secret Granoflow connection config. Defaults to dry-run.",
    {
      apiBaseUrl: z.string().url().optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ apiBaseUrl, dryRun }) =>
      jsonTextResult(
        await writeSetupConfig({
          apiBaseUrl: typeof apiBaseUrl === "string" ? apiBaseUrl : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );

  server.tool(
    "granoflow_setup_open_config",
    "Create and optionally open the MCP-owned non-secret Granoflow config file.",
    {
      createIfMissing: z.boolean().default(true),
      open: z.boolean().default(false),
    },
    async ({ createIfMissing, open }) =>
      jsonTextResult(
        await openSetupConfig({
          createIfMissing: createIfMissing !== false,
          open: open === true,
        }),
      ),
  );

  server.tool(
    "granoflow_setup_open_app",
    "Preview or open the installed Granoflow app after user approval. Defaults to dry-run.",
    {
      appName: z.string().min(1).optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ appName, dryRun }) =>
      jsonTextResult(
        await openGranoflowApp({
          appName: typeof appName === "string" ? appName : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );

  server.tool(
    "granoflow_health",
    "Check whether the Granoflow Local HTTP API is reachable.",
    {},
    async () => apiTool({ path: "/v1/health" }),
  );

  server.tool(
    "granoflow_version",
    "Show Granoflow app and Local HTTP API version metadata.",
    {},
    async () => apiTool({ path: "/v1/version" }),
  );

  server.tool(
    "granoflow_capabilities",
    "List capabilities exposed by the running Granoflow app.",
    {},
    async () => apiTool({ path: "/v1/capabilities" }),
  );

  server.tool("granoflow_ai_agent_tools", "List Granoflow AI-agent tool contracts.", {}, async () =>
    apiTool({ path: "/v1/ai-agent/tools" }),
  );

  server.tool("granoflow_task_list", "List tasks from Granoflow.", {}, async () =>
    apiTool({ path: "/v1/tasks" }),
  );

  server.tool(
    "granoflow_task_export",
    "Export a task context for an AI agent.",
    { taskId: z.string().min(1).describe("Granoflow task id.") },
    async ({ taskId }) => apiTool({ path: `/v1/ai-agent/tasks/${String(taskId)}/export` }),
  );

  server.tool(
    "granoflow_task_validate",
    "Validate an AI-agent task result before importing it into Granoflow.",
    { input: jsonInputSchema },
    async ({ input }) =>
      apiTool({ method: "POST", path: "/v1/ai-agent/tasks/validate", body: input }),
  );

  server.tool(
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

  server.tool(
    "granoflow_task_create",
    "Create a Granoflow task from a JSON payload.",
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
        path: "/v1/tasks",
        body: input,
        dryRun: dryRun !== false,
      }),
  );

  server.tool(
    "granoflow_task_update",
    "Update a Granoflow task through the Local HTTP API.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      input: jsonInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ taskId, input, dryRun }) =>
      apiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}`,
        body: input,
        dryRun: dryRun !== false,
      }),
  );

  server.tool(
    "granoflow_task_complete",
    "Complete a Granoflow task.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      input: jsonInputSchema.optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ taskId, input, dryRun }) =>
      apiTool({
        method: "POST",
        path: `/v1/tasks/${String(taskId)}/complete`,
        body: input,
        dryRun: dryRun !== false,
      }),
  );

  server.tool("granoflow_project_list", "List Granoflow projects.", {}, async () =>
    apiTool({ path: "/v1/projects" }),
  );

  server.tool(
    "granoflow_review_day_show",
    "Show a Granoflow daily review by date.",
    { date: z.string().describe("Date in YYYY-MM-DD format.") },
    async ({ date }) => apiTool({ path: `/v1/reviews/days/${String(date)}` }),
  );

  server.tool(
    "granoflow_api_request",
    "Run an allowed Granoflow Local HTTP API request. Prefer dedicated tools when available.",
    {
      method: z.enum(["GET", "POST", "PATCH", "DELETE"]).default("GET"),
      path: z
        .string()
        .min(1)
        .refine((path) => path.startsWith("/v1/"), "path must start with /v1/"),
      input: jsonInputSchema.optional(),
      dryRun: z.boolean().default(true).describe("When true, previews write requests."),
    },
    async ({ method, path, input, dryRun }) =>
      apiTool({
        method: method as ApiRequestOptions["method"],
        path: String(path),
        body: input,
        dryRun: method === "GET" ? false : dryRun !== false,
      }),
  );
}
