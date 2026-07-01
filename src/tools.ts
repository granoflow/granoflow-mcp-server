import { z } from "zod";

import { resolveMcpRuntime } from "./config.js";
import { resultToText, runGranoflowCli } from "./cli.js";
import { detectLocalApi, getSetupStatus, openSetupConfig, writeSetupConfig } from "./setup.js";

const jsonInputSchema = z
  .record(z.string(), z.unknown())
  .describe("JSON object passed to granoflow-cli stdin.");

function textResult(text: string) {
  return {
    content: [{ type: "text" as const, text }],
  };
}

async function cliTool(args: string[], input?: unknown) {
  const runtime = await resolveMcpRuntime();
  const result = await runGranoflowCli(args, input, { env: runtime.env });
  return textResult(resultToText(result));
}

function jsonTextResult(value: unknown) {
  return textResult(JSON.stringify(value, null, 2));
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
    "Inspect Granoflow MCP config, environment resolution, and CLI health without printing secrets.",
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
      cliPath: z.string().min(1).optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ apiBaseUrl, cliPath, dryRun }) =>
      jsonTextResult(
        await writeSetupConfig({
          apiBaseUrl: typeof apiBaseUrl === "string" ? apiBaseUrl : undefined,
          cliPath: typeof cliPath === "string" ? cliPath : undefined,
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
    "granoflow_health",
    "Check whether the Granoflow local API is reachable.",
    {},
    async () => cliTool(["health"]),
  );

  server.tool(
    "granoflow_capabilities",
    "List capabilities exposed by the running Granoflow app.",
    {},
    async () => cliTool(["api", "capabilities"]),
  );

  server.tool("granoflow_ai_agent_tools", "List Granoflow AI-agent tool contracts.", {}, async () =>
    cliTool(["ai-agent", "tools"]),
  );

  server.tool("granoflow_task_list", "List tasks from Granoflow.", {}, async () =>
    cliTool(["task", "list"]),
  );

  server.tool(
    "granoflow_task_export",
    "Export a task context for an AI agent.",
    { taskId: z.string().min(1).describe("Granoflow task id.") },
    async ({ taskId }) => cliTool(["ai-agent", "task", "export", "--id", String(taskId)]),
  );

  server.tool(
    "granoflow_task_validate",
    "Validate an AI-agent task result before importing it into Granoflow.",
    { input: jsonInputSchema },
    async ({ input }) => cliTool(["ai-agent", "task", "validate", "--input", "-"], input),
  );

  server.tool(
    "granoflow_task_import",
    "Import an AI-agent task result into Granoflow. Use dryRun first unless the user explicitly asks to write.",
    {
      input: jsonInputSchema,
      dryRun: z.boolean().default(true).describe("When true, validates import without writing."),
    },
    async ({ input, dryRun }) =>
      cliTool(
        ["ai-agent", "task", "import", "--input", "-", ...(dryRun === false ? [] : ["--dry-run"])],
        input,
      ),
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
      cliTool(
        ["task", "create", "--input", "-", ...(dryRun === false ? [] : ["--dry-run"])],
        input,
      ),
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
      cliTool(
        [
          "task",
          "complete",
          "--id",
          String(taskId),
          ...(input === undefined ? [] : ["--input", "-"]),
          ...(dryRun === false ? [] : ["--dry-run"]),
        ],
        input,
      ),
  );

  server.tool("granoflow_project_list", "List Granoflow projects.", {}, async () =>
    cliTool(["project", "list"]),
  );

  server.tool(
    "granoflow_review_day_show",
    "Show a Granoflow daily review by date.",
    { date: z.string().describe("Date in YYYY-MM-DD format.") },
    async ({ date }) => cliTool(["review", "day", "show", "--date", String(date)]),
  );

  server.tool(
    "granoflow_cli",
    "Run an allowed granoflow-cli JSON command. Prefer dedicated tools when available.",
    {
      args: z
        .array(z.string())
        .min(1)
        .describe("granoflow-cli arguments, without the leading binary name."),
      input: jsonInputSchema.optional(),
    },
    async ({ args, input }) => cliTool((args as string[]).map(String), input),
  );
}
