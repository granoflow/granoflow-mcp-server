import { z } from "zod";
import { readMcpConfig, writeMcpConfig } from "./config.js";
import { readResolvedAgentPreferences } from "./project-agent-preferences.js";
import type { ToolRegistrar, ToolResult } from "./tools.js";

const preferencesSchema = z.object({
  audience: z.enum(["beginner", "professional"]).optional(),
  explanation: z.enum(["detailed", "concise"]).optional(),
  executionMode: z.enum(["interactive", "unattended"]).optional(),
  git: z
    .object({
      missingNotice: z.enum(["once", "always", "never"]).optional(),
      workflow: z.enum(["ask", "current_branch", "develop", "git_flow"]).optional(),
      checkpoint: z.object({ enabled: z.boolean().optional() }).optional(),
    })
    .optional(),
});

type Dependencies = {
  jsonTextResult: (value: unknown) => ToolResult;
};

export function registerAgentPreferenceTools(
  registerTool: ToolRegistrar,
  deps: Dependencies,
): void {
  registerTool(
    "granoflow_agent_preferences_get",
    "Resolve compact Agent preferences from project YAML, MCP-local defaults, and newcomer-safe defaults. Project values win field by field. This read never grants push, publish, deploy, deletion, login, secret access, or destructive Git actions.",
    {
      projectId: z.string().min(1).optional(),
      dryRun: z.boolean().default(false),
    },
    async ({ projectId, dryRun }) =>
      deps.jsonTextResult(
        await readResolvedAgentPreferences(
          typeof projectId === "string" ? projectId : undefined,
          dryRun === true,
        ),
      ),
  );

  registerTool(
    "granoflow_agent_preferences_write_defaults",
    "Preview or write non-secret MCP-local Agent defaults. Per-project overrides remain in project_rules.yaml. Defaults to dry-run and returns a redacted readback.",
    {
      preferences: preferencesSchema,
      dryRun: z.boolean().default(true),
    },
    async ({ preferences, dryRun }) => {
      const result = await writeMcpConfig(
        {
          agentPreferences: preferences as z.infer<typeof preferencesSchema>,
          dryRun: dryRun !== false,
        },
        process.env,
      );
      const readback = dryRun === false ? await readMcpConfig(process.env) : null;
      return deps.jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          ...result,
          readback:
            readback === null
              ? null
              : {
                  configPath: readback.configPath,
                  exists: readback.exists,
                  agentPreferences: readback.config.agentPreferences ?? {},
                },
        },
      });
    },
  );

  registerTool(
    "granoflow_git_missing_notice_record",
    "Record that the one-time newcomer Git-unavailable notice was shown. This stores only a boolean marker and never installs Git or changes a repository.",
    { shown: z.boolean().default(true), dryRun: z.boolean().default(true) },
    async ({ shown, dryRun }) =>
      deps.jsonTextResult({
        ok: true,
        code: "ok",
        data: await writeMcpConfig(
          { gitMissingNoticeShown: shown === true, dryRun: dryRun !== false },
          process.env,
        ),
      }),
  );
}
