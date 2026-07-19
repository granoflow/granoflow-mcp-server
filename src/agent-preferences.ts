export type AgentAudience = "beginner" | "professional";
export type ExplanationStyle = "detailed" | "concise";
export type ExecutionModePreference = "interactive" | "unattended";
export type GitWorkflowPreference = "ask" | "current_branch" | "develop" | "git_flow";
export type GitMissingNoticePreference = "once" | "always" | "never";

export interface AgentPreferences {
  schemaVersion: 1;
  audience: AgentAudience;
  explanation: ExplanationStyle;
  executionMode: ExecutionModePreference;
  git: {
    missingNotice: GitMissingNoticePreference;
    workflow: GitWorkflowPreference;
    checkpoint: {
      enabled: boolean;
      trigger: "after_required_tests";
      taskOwnedFilesOnly: true;
      push: false;
    };
  };
}

export interface AgentPreferencesOverride {
  audience?: AgentAudience;
  explanation?: ExplanationStyle;
  executionMode?: ExecutionModePreference;
  git?: {
    missingNotice?: GitMissingNoticePreference;
    workflow?: GitWorkflowPreference;
    checkpoint?: {
      enabled?: boolean;
    };
  };
}

export type PreferenceSource = "project" | "local_default" | "safe_default";

export interface ResolvedAgentPreferences extends AgentPreferences {
  sources: {
    audience: PreferenceSource;
    explanation: PreferenceSource;
    executionMode: PreferenceSource;
    gitMissingNotice: PreferenceSource;
    gitWorkflow: PreferenceSource;
    gitCheckpoint: PreferenceSource;
  };
  rules: string[];
}

export const SAFE_AGENT_PREFERENCES: AgentPreferences = {
  schemaVersion: 1,
  audience: "beginner",
  explanation: "detailed",
  executionMode: "interactive",
  git: {
    missingNotice: "once",
    workflow: "ask",
    checkpoint: {
      enabled: false,
      trigger: "after_required_tests",
      taskOwnedFilesOnly: true,
      push: false,
    },
  },
};

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function oneOf<T extends string>(value: unknown, allowed: readonly T[]): T | undefined {
  return typeof value === "string" && allowed.includes(value as T) ? (value as T) : undefined;
}

export function normalizeAgentPreferencesOverride(value: unknown): AgentPreferencesOverride {
  if (!isObject(value)) return {};
  const git = isObject(value.git) ? value.git : {};
  const checkpoint = isObject(git.checkpoint) ? git.checkpoint : {};
  return {
    audience: oneOf(value.audience, ["beginner", "professional"]),
    explanation: oneOf(value.explanation, ["detailed", "concise"]),
    executionMode: oneOf(value.executionMode, ["interactive", "unattended"]),
    git: {
      missingNotice: oneOf(git.missingNotice, ["once", "always", "never"]),
      workflow: oneOf(git.workflow, ["ask", "current_branch", "develop", "git_flow"]),
      checkpoint: {
        enabled: typeof checkpoint.enabled === "boolean" ? checkpoint.enabled : undefined,
      },
    },
  };
}

function yamlScalar(content: string, key: string): string | undefined {
  const match = content.match(new RegExp(`^\\s{2,}${key}:\\s*["']?([^"'\\n#]+)`, "m"));
  return match?.[1]?.trim().toLowerCase();
}

function yamlBoolean(content: string, key: string): boolean | undefined {
  const value = yamlScalar(content, key);
  if (value === "true") return true;
  if (value === "false") return false;
  return undefined;
}

export function parseProjectAgentPreferences(content?: string): AgentPreferencesOverride {
  if (!content) return {};
  const section = content.match(/(?:^|\n)agent_preferences:\s*\n([\s\S]*?)(?=\n\S|$)/)?.[1];
  if (!section) return {};
  return normalizeAgentPreferencesOverride({
    audience: yamlScalar(section, "audience"),
    explanation: yamlScalar(section, "explanation"),
    executionMode: yamlScalar(section, "execution_mode"),
    git: {
      missingNotice: yamlScalar(section, "missing_notice"),
      workflow: yamlScalar(section, "workflow"),
      checkpoint: { enabled: yamlBoolean(section, "checkpoint_enabled") },
    },
  });
}

function choose<T>(
  project: T | undefined,
  local: T | undefined,
  fallback: T,
): { value: T; source: PreferenceSource } {
  if (project !== undefined) return { value: project, source: "project" };
  if (local !== undefined) return { value: local, source: "local_default" };
  return { value: fallback, source: "safe_default" };
}

export function resolveAgentPreferences(
  localValue?: unknown,
  projectContent?: string,
): ResolvedAgentPreferences {
  const local = normalizeAgentPreferencesOverride(localValue);
  const project = parseProjectAgentPreferences(projectContent);
  const audience = choose(project.audience, local.audience, SAFE_AGENT_PREFERENCES.audience);
  const explanation = choose(
    project.explanation,
    local.explanation,
    SAFE_AGENT_PREFERENCES.explanation,
  );
  const executionMode = choose(
    project.executionMode,
    local.executionMode,
    SAFE_AGENT_PREFERENCES.executionMode,
  );
  const missingNotice = choose(
    project.git?.missingNotice,
    local.git?.missingNotice,
    SAFE_AGENT_PREFERENCES.git.missingNotice,
  );
  const workflow = choose(
    project.git?.workflow,
    local.git?.workflow,
    SAFE_AGENT_PREFERENCES.git.workflow,
  );
  const checkpoint = choose(
    project.git?.checkpoint?.enabled,
    local.git?.checkpoint?.enabled,
    SAFE_AGENT_PREFERENCES.git.checkpoint.enabled,
  );
  return {
    schemaVersion: 1,
    audience: audience.value,
    explanation: explanation.value,
    executionMode: executionMode.value,
    git: {
      missingNotice: missingNotice.value,
      workflow: workflow.value,
      checkpoint: {
        enabled: checkpoint.value,
        trigger: "after_required_tests",
        taskOwnedFilesOnly: true,
        push: false,
      },
    },
    sources: {
      audience: audience.source,
      explanation: explanation.source,
      executionMode: executionMode.source,
      gitMissingNotice: missingNotice.source,
      gitWorkflow: workflow.source,
      gitCheckpoint: checkpoint.source,
    },
    rules: [
      explanation.value === "concise"
        ? "Use concise explanations while preserving safety notices and evidence."
        : "Explain specialist choices in plain language with a concrete example.",
      "A preference never authorizes push, publish, deploy, deletion, login, secrets, or destructive Git history changes.",
      checkpoint.value
        ? "Create a local checkpoint only after every required test passes and only for task-owned files."
        : "Do not create an automatic Git checkpoint.",
    ],
  };
}

export function mergeAgentPreferences(
  current: unknown,
  patch: AgentPreferencesOverride,
): AgentPreferencesOverride {
  const base = normalizeAgentPreferencesOverride(current);
  const normalized = normalizeAgentPreferencesOverride(patch);
  return {
    audience: normalized.audience ?? base.audience,
    explanation: normalized.explanation ?? base.explanation,
    executionMode: normalized.executionMode ?? base.executionMode,
    git: {
      missingNotice: normalized.git?.missingNotice ?? base.git?.missingNotice,
      workflow: normalized.git?.workflow ?? base.git?.workflow,
      checkpoint: {
        enabled: normalized.git?.checkpoint?.enabled ?? base.git?.checkpoint?.enabled,
      },
    },
  };
}
