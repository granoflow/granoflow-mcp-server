import { requestGranoflowApi, type ApiResult } from "./api.js";
import { readMcpConfig } from "./config.js";
import { resolveAgentPreferences } from "./agent-preferences.js";

function readContent(result: ApiResult): string | undefined {
  if (!result.data || typeof result.data !== "object") return undefined;
  const direct = result.data as { content?: unknown; data?: unknown };
  const nested =
    direct.data && typeof direct.data === "object"
      ? (direct.data as { content?: unknown }).content
      : undefined;
  const content = direct.content ?? nested;
  return typeof content === "string" ? content : undefined;
}

export async function readResolvedAgentPreferences(
  projectId?: string,
  dryRun = false,
  env: NodeJS.ProcessEnv = process.env,
) {
  const local = await readMcpConfig(env);
  if (!projectId) {
    return {
      ok: true,
      code: "ok",
      data: {
        projectId: null,
        configPath: local.configPath,
        configExists: local.exists,
        configError: local.error,
        preferences: resolveAgentPreferences(local.config.agentPreferences),
      },
    };
  }

  const project = await requestGranoflowApi(
    {
      method: "POST",
      path: "/v1/ai-agent/project-context-attachments/read",
      body: { projectId, attachment: "project_rules.yaml", section: "agent_preferences" },
      dryRun,
    },
    env,
  );
  if (!project.ok) return project;
  return {
    ...project,
    data: {
      ...(typeof project.data === "object" && project.data !== null ? project.data : {}),
      projectId,
      configPath: local.configPath,
      configExists: local.exists,
      configError: local.error,
      preferences: resolveAgentPreferences(local.config.agentPreferences, readContent(project)),
    },
  };
}
