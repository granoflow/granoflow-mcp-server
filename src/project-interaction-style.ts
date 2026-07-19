import { requestGranoflowApi, type ApiResult } from "./api.js";

export type InteractionAudience = "beginner" | "professional";
export type InteractionExplanation = "detailed" | "concise";

export type ProjectInteractionStyle = {
  audience: InteractionAudience;
  explanation: InteractionExplanation;
  source: "project" | "default";
  projectId: string;
  rule: string;
  recordCopy: {
    audience: "beginner";
    explanation: "detailed";
    rule: string;
  };
};

const DEFAULT_STYLE = {
  audience: "beginner" as const,
  explanation: "detailed" as const,
};

function scalar(content: string, key: string): string | undefined {
  const match = content.match(new RegExp(`^\\s{2,}${key}:\\s*["']?([^"'\\n]+)`, "m"));
  return match?.[1]?.trim().toLowerCase();
}

export function resolveProjectInteractionStyle(
  projectId: string,
  content?: string,
): ProjectInteractionStyle {
  const audience = scalar(content ?? "", "audience");
  const explanation = scalar(content ?? "", "explanation");
  const hasStyle = /(^|\n)interaction_style:\s*$/m.test(content ?? "");
  const resolvedAudience = audience === "professional" ? "professional" : DEFAULT_STYLE.audience;
  const resolvedExplanation = explanation === "concise" ? "concise" : DEFAULT_STYLE.explanation;
  return {
    audience: resolvedAudience,
    explanation: resolvedExplanation,
    source: hasStyle ? "project" : "default",
    projectId,
    rule:
      resolvedAudience === "professional" && resolvedExplanation === "concise"
        ? "Use concise professional wording; explain terms only when asked."
        : "Assume a newcomer: use plain language, an example, and the reason for each specialist choice.",
    recordCopy: {
      audience: "beginner",
      explanation: "detailed",
      rule: "Save every Granoflow record in newcomer-friendly language with the scenario, consequence, and reason.",
    },
  };
}

function readContent(result: ApiResult): string | undefined {
  const data = result.data;
  if (!data || typeof data !== "object") return undefined;
  const content = (data as { content?: unknown }).content;
  return typeof content === "string" ? content : undefined;
}

export async function readProjectInteractionStyle(projectId: string, dryRun = false) {
  const result = await requestGranoflowApi({
    method: "POST",
    path: "/v1/ai-agent/project-context-attachments/read",
    body: { projectId, attachment: "project_rules.yaml", section: "interaction_style" },
    dryRun,
  });
  if (!result.ok) return result;
  return {
    ...result,
    data: {
      ...(typeof result.data === "object" && result.data !== null ? result.data : {}),
      interactionStyle: resolveProjectInteractionStyle(projectId, readContent(result)),
    },
  };
}
