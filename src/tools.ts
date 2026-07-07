import { readFileSync } from "node:fs";

import { z } from "zod";

import {
  maybeCreateDailyReviewSuggestion,
  type MonthlyReviewSuggestion,
  type WeeklyReviewSuggestion,
} from "./config.js";
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
const historicalTaskMutationSchema = z.object({
  clientMutationId: z.string().min(1),
  op: z.enum(["create", "update", "softDelete"]),
  taskId: z.string().min(1).optional(),
  fields: z.record(z.string(), z.unknown()).optional(),
  reason: z.string().min(1).optional(),
});
const memoryBatchItemSchema = z.object({
  clientItemId: z.string().min(1).optional(),
  kind: z
    .enum(["task_completion", "task_review", "review_card_candidate"])
    .default("task_completion"),
  title: z.string().min(1),
  summary: z.string().min(1).optional(),
  completedAt: z.string().min(1).optional(),
  reviewCardCandidates: z.array(z.record(z.string(), z.unknown())).optional(),
});
const contextPackScopeSchema = z.enum(["task", "project", "repo"]);
const contextPackSourceSchema = z.object({
  taskId: z.string().min(1).optional(),
  threadId: z.string().min(1).optional(),
  commit: z.string().min(1).optional(),
});
const contextStewardEvidenceSchema = z
  .string()
  .min(1)
  .describe("Short evidence summary for why this context description changed.");
const milestoneArchiveClosureSchema = z.object({
  finalOutcome: z.string().min(1),
  verification: z.string().min(1),
  followUpMovedTo: z.string().min(1),
  milestoneDescription: z.string().min(1).optional(),
  completionSummary: z.string().min(1).optional(),
  projectDescription: z.string().min(1),
});
const resourceStatusSchema = z.string().min(1).optional();
const resolveMatchModeSchema = z.enum(["exact", "contains"]).default("exact");
const reviewCardDraftNoteFieldSchema = z.object({
  key: z.string().min(1).describe("Stable note field key such as phonetic or pronunciation."),
  label: z.string().min(1).describe("Human-readable note field label."),
  type: z.enum(["text", "text_to_speech"]),
  value: z.string().min(1),
  ttsLanguageCode: z
    .string()
    .min(1)
    .optional()
    .describe("Optional BCP-47 language code for text_to_speech fields, such as en-US."),
});
const reviewCardDraftSchema = z.object({
  clientCardId: z
    .string()
    .min(1)
    .describe("Stable caller-generated id for this draft, unique within the finish request."),
  cardType: z.enum(["basic_qa", "reverse_qa", "keyword_cloze"]).default("basic_qa"),
  front: z.string().min(1).describe("Front of the review card."),
  back: z.string().min(1).describe("Back of the review card."),
  sourceSummary: z
    .string()
    .optional()
    .describe("Short source note tying this card to the completed task."),
  noteFields: z
    .array(reviewCardDraftNoteFieldSchema)
    .optional()
    .describe("Optional structured note fields. Check /v1/ai-agent/tools capability first."),
  frontLayout: z.array(z.string().min(1)).optional(),
  backLayout: z.array(z.string().min(1)).optional(),
});

type ReviewCardDraft = z.infer<typeof reviewCardDraftSchema>;

type ResourceKind = "project" | "milestone" | "task";

type GranoflowRecord = {
  id?: unknown;
  title?: unknown;
  status?: unknown;
  projectId?: unknown;
  milestoneId?: unknown;
  [key: string]: unknown;
};

const AGENT_WORKFLOW_SKILL_URL = new URL(
  "../skills/granoflow-agent-workflow/SKILL.md",
  import.meta.url,
);
const FIRST_RUN_IMPORT_SKILL_URL = new URL(
  "../skills/granoflow-first-run-import/SKILL.md",
  import.meta.url,
);

function compactRecord(record: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(record).filter(([, value]) => value !== undefined));
}

function textResult(text: string) {
  return {
    content: [{ type: "text" as const, text }],
  };
}

function jsonTextResult(value: unknown) {
  return textResult(JSON.stringify(value, null, 2));
}

function readAgentWorkflowSkill(): string {
  return readFileSync(AGENT_WORKFLOW_SKILL_URL, "utf8");
}

function readFirstRunImportSkill(): string {
  return readFileSync(FIRST_RUN_IMPORT_SKILL_URL, "utf8");
}

function periodicReviewHasLog(value: unknown): boolean {
  if (!isObject(value)) {
    return false;
  }
  const data = isObject(value.data) ? value.data : null;
  const entity = data && isObject(data.entity) ? data.entity : null;
  if (!entity) {
    return false;
  }
  const content = typeof entity.content === "string" ? entity.content.trim() : "";
  const values = Array.isArray(entity.values) ? entity.values : [];
  return content.length > 0 || values.length > 0;
}

async function checkPeriodicReviewSuggestion(
  kind: "week" | "month",
  date: string,
  target: WeeklyReviewSuggestion["target"] | MonthlyReviewSuggestion["target"],
  env: NodeJS.ProcessEnv,
): Promise<WeeklyReviewSuggestion | MonthlyReviewSuggestion | null> {
  const result = await requestGranoflowApi({ path: `/v1/reviews/${kind}s/${date}` }, env);
  if (!result.ok || periodicReviewHasLog(result)) {
    return null;
  }
  const data = isObject(result.data) ? result.data : null;
  const entity = data && isObject(data.entity) ? data.entity : {};
  if (kind === "month") {
    return {
      code: "monthly_review_suggested",
      year: typeof entity.year === "number" ? entity.year : undefined,
      month: typeof entity.month === "number" ? entity.month : undefined,
      target: target as MonthlyReviewSuggestion["target"],
      checkedDate: date,
      message:
        target === "last_month"
          ? "Last month's Granoflow monthly review does not appear to have a written log yet. Consider writing it after today's review."
          : "This month's Granoflow monthly review does not appear to have a written log yet. Consider writing it after today's review.",
      messageZh:
        target === "last_month"
          ? "上月的 Granoflow 本月回顾看起来还没有写日志。完成今日回顾后，建议顺手补一下上月月回顾。"
          : "本月的 Granoflow 本月回顾看起来还没有写日志。完成今日回顾后，建议顺手写一下本月月回顾。",
      nextActions: [
        "Open the Granoflow monthly review.",
        "Summarize the month's completed work, lessons, and unresolved risks.",
        "Extract durable lessons and decide which ones deserve review cards.",
      ],
    };
  }
  return {
    code: "weekly_review_suggested",
    weekStart: typeof entity.weekStart === "string" ? entity.weekStart : undefined,
    weekEnd: typeof entity.weekEnd === "string" ? entity.weekEnd : undefined,
    target: target as WeeklyReviewSuggestion["target"],
    checkedDate: date,
    message:
      target === "last_week"
        ? "Last week's Granoflow weekly review does not appear to have a written log yet. Consider writing it after today's review."
        : "This week's Granoflow weekly review does not appear to have a written log yet. Consider writing it after today's review.",
    messageZh:
      target === "last_week"
        ? "上周的 Granoflow 每周回顾看起来还没有写日志。完成今日回顾后，建议顺手补一下上周周回顾。"
        : "本周的 Granoflow 每周回顾看起来还没有写日志。完成今日回顾后，建议顺手写一下本周周回顾。",
    nextActions: [
      "Open the Granoflow weekly review.",
      "Summarize the week's completed work and unresolved risks.",
      "Extract durable lessons and decide which ones deserve review cards.",
    ],
  };
}

async function withDailyReviewSuggestion(
  toolName: string,
  result: ReturnType<typeof textResult>,
): Promise<ReturnType<typeof textResult>> {
  if (toolName === "granoflow_review_day_show") {
    return result;
  }
  const content = result.content[0];
  if (content.type !== "text") {
    return result;
  }
  try {
    const parsed: unknown = JSON.parse(content.text);
    if (!isObject(parsed)) {
      return result;
    }
    const suggestion = await maybeCreateDailyReviewSuggestion(
      process.env,
      new Date(),
      checkPeriodicReviewSuggestion,
    );
    if (!suggestion) {
      return result;
    }
    return jsonTextResult({
      ...parsed,
      dailyReviewSuggestion: suggestion,
    });
  } catch {
    return result;
  }
}

async function apiTool(options: ApiRequestOptions) {
  return jsonTextResult(await requestGranoflowApi(options));
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function unwrapApiData(value: unknown): unknown {
  if (!isObject(value)) {
    return value;
  }
  const outerData = value.data;
  if (isObject(outerData) && "items" in outerData) {
    return outerData;
  }
  if (isObject(outerData) && isObject(outerData.data) && "items" in outerData.data) {
    return outerData.data;
  }
  return outerData ?? value;
}

function extractItems(value: unknown): GranoflowRecord[] {
  const data = unwrapApiData(value);
  if (isObject(data) && Array.isArray(data.items)) {
    return data.items.filter(isObject);
  }
  return [];
}

function compactResource(record: GranoflowRecord): Record<string, unknown> {
  return compactRecord({
    id: record.id,
    title: record.title,
    status: record.status,
    projectId: record.projectId,
    milestoneId: record.milestoneId,
    dueAt: record.dueAt,
    startedAt: record.startedAt,
    endedAt: record.endedAt,
    description: record.description,
    taskReview: record.taskReview,
  });
}

function draftUsesEnhancedFields(draft: ReviewCardDraft): boolean {
  return (
    (draft.noteFields?.length ?? 0) > 0 ||
    (draft.frontLayout?.length ?? 0) > 0 ||
    (draft.backLayout?.length ?? 0) > 0
  );
}

function normalizeReviewCardDraft(draft: ReviewCardDraft): Record<string, unknown> {
  return compactRecord({
    client_card_id: draft.clientCardId,
    card_type: draft.cardType,
    front: draft.front,
    back: draft.back,
    source_summary: draft.sourceSummary,
    note_fields: draft.noteFields?.map((field) =>
      compactRecord({
        key: field.key,
        label: field.label,
        type: field.type,
        value: field.value,
        tts_language_code: field.ttsLanguageCode,
      }),
    ),
    front_layout: draft.frontLayout,
    back_layout: draft.backLayout,
  });
}

function supportsReviewCardDraftNoteFields(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (!isObject(tool) || tool.toolId !== "single_task_ai" || tool.enabled !== true) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    const reviewCards = isObject(capabilities.reviewCardDraftNoteFields)
      ? capabilities.reviewCardDraftNoteFields
      : {};
    return (
      reviewCards.enabled === true &&
      reviewCards.capability === "review_card_draft_note_fields_v1" &&
      Array.isArray(reviewCards.fieldTypes) &&
      reviewCards.fieldTypes.includes("text") &&
      reviewCards.fieldTypes.includes("text_to_speech") &&
      reviewCards.ttsLanguageCode === true &&
      reviewCards.layoutFields === true
    );
  });
}

function supportsHistoricalTaskMutations(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (
      !isObject(tool) ||
      tool.toolId !== "granoflow_task_history_mutate" ||
      tool.enabled !== true
    ) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    const mutations = isObject(capabilities.historicalTaskMutations)
      ? capabilities.historicalTaskMutations
      : {};
    return (
      mutations.enabled === true &&
      mutations.capability === "historical_task_mutations_v1" &&
      mutations.preservesHistoricalTimes === true
    );
  });
}

function supportsContextPack(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (!isObject(tool) || tool.toolId !== "granoflow_context_pack_v1" || tool.enabled !== true) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    const contextPack = isObject(capabilities.contextPack) ? capabilities.contextPack : {};
    return (
      contextPack.capability === "context_pack_v1" &&
      contextPack.matchSignals === true &&
      contextPack.recommendations === false &&
      contextPack.embeddingScores === false
    );
  });
}

function supportsMemoryBatchPreview(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (
      !isObject(tool) ||
      tool.toolId !== "granoflow_memory_batch_preview_v1" ||
      tool.enabled !== true
    ) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    const preview = isObject(capabilities.memoryBatchPreview)
      ? capabilities.memoryBatchPreview
      : {};
    return (
      preview.capability === "memory_batch_preview_v1" &&
      preview.writesPerformed === false &&
      typeof preview.maxItems === "number" &&
      preview.maxItems >= 1
    );
  });
}

function supportsContextSteward(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (
      !isObject(tool) ||
      tool.toolId !== "granoflow_context_steward_v1" ||
      tool.enabled !== true
    ) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    return (
      capabilities.projectDescriptionLivingContext === true &&
      capabilities.activeMilestoneDescriptionLivingContext === true &&
      capabilities.archivedMilestoneOrdinaryUpdates === false &&
      capabilities.archiveFinalSummaryRequired === true
    );
  });
}

async function requestPreviewWithMeta(options: ApiRequestOptions, meta: Record<string, unknown>) {
  const preview = await requestGranoflowApi({ ...options, dryRun: true });
  const data = isObject(preview.data) ? preview.data : {};
  return {
    ...preview,
    data: {
      ...data,
      ...meta,
    },
  };
}

async function contextPackApiTool(options: ApiRequestOptions) {
  if (options.dryRun) {
    return apiTool(options);
  }
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  if (!toolsResult.ok || !supportsContextPack(toolsResult)) {
    return jsonTextResult({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "context_pack_v1",
        endpoint: options.path,
      },
      error: {
        message: "The running Granoflow app does not advertise context_pack_v1.",
      },
      runtime: toolsResult.runtime,
    });
  }
  return apiTool(options);
}

async function memoryBatchPreviewApiTool(options: ApiRequestOptions) {
  if (options.dryRun) {
    return apiTool(options);
  }
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  if (!toolsResult.ok || !supportsMemoryBatchPreview(toolsResult)) {
    return jsonTextResult({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "memory_batch_preview_v1",
        endpoint: options.path,
      },
      error: {
        message: "The running Granoflow app does not advertise memory_batch_preview_v1.",
      },
      runtime: toolsResult.runtime,
    });
  }
  return apiTool(options);
}

async function mutateTaskHistory(input: {
  dryRun?: boolean;
  source?: Record<string, unknown>;
  mutations?: z.infer<typeof historicalTaskMutationSchema>[];
}) {
  const body = {
    dryRun: input.dryRun !== false,
    source: input.source ?? { kind: "mcp_tool" },
    mutations: input.mutations ?? [],
  };
  if (body.dryRun) {
    return requestGranoflowApi({
      method: "POST",
      path: "/v1/ai-agent/tasks/historical-mutations",
      body,
      dryRun: true,
    });
  }
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  if (!toolsResult.ok || !supportsHistoricalTaskMutations(toolsResult)) {
    return {
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "historical_task_mutations_v1",
        endpoint: "/v1/ai-agent/tasks/historical-mutations",
      },
      error: {
        message: "The running Granoflow app does not advertise historical_task_mutations_v1.",
      },
      runtime: toolsResult.runtime,
    };
  }
  return requestGranoflowApi({
    method: "POST",
    path: "/v1/ai-agent/tasks/historical-mutations",
    body,
  });
}

async function resolveResourceById(kind: ResourceKind, id: string) {
  const result = await requestGranoflowApi({ path: listPathFor(kind) });
  if (!result.ok) {
    return { result, resource: null };
  }
  return {
    result,
    resource: extractItems(result).find((item) => item.id === id) ?? null,
  };
}

function isArchivedResource(resource: GranoflowRecord): boolean {
  return resource.status === "archived";
}

async function contextStewardStatus(input: { projectId?: string }) {
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  const projectsResult = await requestGranoflowApi({ path: "/v1/projects" });
  const milestonesResult = await requestGranoflowApi({ path: "/v1/milestones" });
  const projects = projectsResult.ok ? extractItems(projectsResult) : [];
  const milestones = milestonesResult.ok
    ? extractItems(milestonesResult).filter(
        (milestone) => !input.projectId || milestone.projectId === input.projectId,
      )
    : [];
  return {
    ok: toolsResult.ok && projectsResult.ok && milestonesResult.ok,
    code: toolsResult.ok && projectsResult.ok && milestonesResult.ok ? "ok" : "partial",
    data: {
      contextStewardAdvertised: toolsResult.ok && supportsContextSteward(toolsResult),
      archivedMilestoneOrdinaryUpdates: false,
      projectId: input.projectId,
      projects: projects
        .filter((project) => !input.projectId || project.id === input.projectId)
        .map(compactResource),
      activeMilestones: milestones
        .filter((milestone) => !isArchivedResource(milestone))
        .map(compactResource),
      archivedMilestones: milestones.filter(isArchivedResource).map(compactResource),
      policy: {
        projectDescription: "living_context",
        activeMilestoneDescription: "living_context",
        archivedMilestoneDescription: "final_snapshot_for_ordinary_mcp_workflow",
      },
    },
    runtime: toolsResult.runtime,
  };
}

async function projectContextUpdate(input: {
  projectId: string;
  description: string;
  evidenceSummary: string;
  dryRun?: boolean;
}) {
  const body = { description: input.description };
  const options = {
    method: "PATCH" as const,
    path: `/v1/projects/${input.projectId}`,
    body,
  };
  if (input.dryRun !== false) {
    return requestPreviewWithMeta(options, {
      contextSteward: {
        target: "project",
        evidenceSummary: input.evidenceSummary,
        descriptionPolicy: "living_context",
      },
    });
  }
  return requestGranoflowApi(options);
}

async function milestoneContextUpdate(input: {
  milestoneId: string;
  projectId?: string;
  description: string;
  evidenceSummary: string;
  dryRun?: boolean;
}) {
  const { result, resource } = await resolveResourceById("milestone", input.milestoneId);
  if (!result.ok) {
    return result;
  }
  if (!resource) {
    return {
      ok: false,
      code: "milestone_not_found",
      error: { message: "Granoflow milestone was not found." },
      runtime: result.runtime,
    };
  }
  if (isArchivedResource(resource)) {
    return {
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
      data: {
        milestone: compactResource(resource),
        policy: "archived_milestone_description_is_final_snapshot",
      },
      error: {
        message: "Archived milestone descriptions are final snapshots for ordinary MCP workflows.",
      },
      runtime: result.runtime,
    };
  }

  const body = compactRecord({
    projectId: input.projectId,
    description: input.description,
  });
  const options = {
    method: "PATCH" as const,
    path: `/v1/milestones/${input.milestoneId}`,
    body,
  };
  if (input.dryRun !== false) {
    return requestPreviewWithMeta(options, {
      contextSteward: {
        target: "active_milestone",
        evidenceSummary: input.evidenceSummary,
        descriptionPolicy: "living_context",
        currentMilestone: compactResource(resource),
      },
    });
  }
  return requestGranoflowApi(options);
}

async function milestoneContextArchive(input: {
  milestoneId: string;
  projectId: string;
  closure: z.infer<typeof milestoneArchiveClosureSchema>;
  dryRun?: boolean;
  confirmArchive?: boolean;
}) {
  const { result, resource } = await resolveResourceById("milestone", input.milestoneId);
  if (!result.ok) {
    return result;
  }
  if (!resource) {
    return {
      ok: false,
      code: "milestone_not_found",
      error: { message: "Granoflow milestone was not found." },
      runtime: result.runtime,
    };
  }
  if (isArchivedResource(resource)) {
    return {
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
      data: {
        milestone: compactResource(resource),
        policy: "archived_milestone_description_is_final_snapshot",
      },
      error: {
        message: "Archived milestone descriptions are final snapshots for ordinary MCP workflows.",
      },
      runtime: result.runtime,
    };
  }

  const completionSummary = input.closure.completionSummary ?? input.closure.finalOutcome;
  const milestoneDescription =
    input.closure.milestoneDescription ??
    [
      `Final outcome: ${input.closure.finalOutcome}`,
      `Verification: ${input.closure.verification}`,
      `Follow-up moved to: ${input.closure.followUpMovedTo}`,
    ].join("\n");
  const steps = [
    {
      step: "finalize_milestone_context",
      method: "POST",
      path: `/v1/milestones/${input.milestoneId}/archive`,
      body: {
        completionSummary,
        description: milestoneDescription,
      },
      appOwnedArchiveApiAvailable: false,
    },
    {
      step: "update_parent_project_context",
      method: "PATCH",
      path: `/v1/projects/${input.projectId}`,
      body: {
        description: input.closure.projectDescription,
      },
    },
  ];

  if (input.dryRun !== false) {
    return {
      ok: true,
      code: "dry_run",
      data: {
        previewMode: "context_archive_closure",
        milestone: compactResource(resource),
        steps,
        writesPerformed: false,
        nextActions: [
          "Review the final milestone state and parent project description update together.",
          "Do not update an archived milestone through ordinary MCP workflow after archive.",
        ],
      },
      runtime: result.runtime,
    };
  }

  return {
    ok: false,
    code: "milestone_archive_api_unavailable",
    data: {
      steps,
      requiredCapability: "app_owned_milestone_archive_api",
      confirmArchive: input.confirmArchive === true,
      writesPerformed: false,
    },
    error: {
      message:
        "The current Local HTTP API does not expose a safe app-owned milestone archive endpoint for MCP forwarding.",
    },
    runtime: result.runtime,
  };
}

function titleMatches(title: unknown, query: string, matchMode: "exact" | "contains"): boolean {
  if (typeof title !== "string") {
    return false;
  }
  const normalizedTitle = title.trim().toLowerCase();
  const normalizedQuery = query.trim().toLowerCase();
  return matchMode === "exact"
    ? normalizedTitle === normalizedQuery
    : normalizedTitle.includes(normalizedQuery);
}

function listPathFor(kind: ResourceKind): string {
  return `/v1/${kind}s`;
}

async function resolveResource(
  kind: ResourceKind,
  input: {
    query: string;
    matchMode?: "exact" | "contains";
    projectId?: string;
    milestoneId?: string;
    includeDone?: boolean;
  },
) {
  const matchMode = input.matchMode ?? "exact";
  const result = await requestGranoflowApi({ path: listPathFor(kind) });
  if (!result.ok) {
    return result;
  }
  const matches = extractItems(result).filter((item) => {
    if (!titleMatches(item.title, input.query, matchMode)) {
      return false;
    }
    if (input.projectId && item.projectId !== input.projectId) {
      return false;
    }
    if (input.milestoneId && item.milestoneId !== input.milestoneId) {
      return false;
    }
    if (!input.includeDone && item.status === "done") {
      return false;
    }
    return true;
  });
  return {
    ok: true,
    code: "resolved",
    data: {
      entityType: kind,
      query: input.query,
      matchMode,
      count: matches.length,
      ambiguous: matches.length > 1,
      matches: matches.map(compactResource),
    },
    runtime: result.runtime,
  };
}

async function safeDeleteResource(
  kind: Exclude<ResourceKind, "task">,
  input: {
    id: string;
    confirmTitle?: string;
    allowLinkedTasks?: boolean;
    dryRun?: boolean;
  },
) {
  const listResult = await requestGranoflowApi({ path: listPathFor(kind) });
  if (!listResult.ok) {
    return listResult;
  }
  const resource = extractItems(listResult).find((item) => item.id === input.id);
  if (!resource) {
    return {
      ok: false,
      code: `${kind}_not_found`,
      error: { message: `Granoflow ${kind} was not found.` },
      runtime: listResult.runtime,
    };
  }

  const tasksResult = await requestGranoflowApi({ path: "/v1/tasks" });
  const linkedTasks =
    tasksResult.ok && kind === "project"
      ? extractItems(tasksResult).filter((task) => task.projectId === input.id)
      : tasksResult.ok
        ? extractItems(tasksResult).filter((task) => task.milestoneId === input.id)
        : [];
  const impact = {
    resource: compactResource(resource),
    linkedTaskCount: linkedTasks.length,
    linkedTasks: linkedTasks.map(compactResource),
  };

  if (input.dryRun !== false) {
    return {
      ok: true,
      code: "dry_run",
      data: {
        method: "DELETE",
        path: `/v1/${kind}s/${input.id}`,
        impact,
        previewMode: "local_request_only",
        nextActions: [
          "Review the impact preview.",
          "Call again with dryRun=false, confirmTitle matching the current title, and allowLinkedTasks=true only if linked tasks may be affected.",
        ],
      },
      runtime: listResult.runtime,
    };
  }

  if (typeof resource.title === "string" && input.confirmTitle !== resource.title) {
    return {
      ok: false,
      code: "confirmation_required",
      data: {
        expectedConfirmTitle: resource.title,
        impact,
      },
      error: { message: "confirmTitle must match the current resource title before deletion." },
      runtime: listResult.runtime,
    };
  }

  if (linkedTasks.length > 0 && input.allowLinkedTasks !== true) {
    return {
      ok: false,
      code: "linked_tasks_present",
      data: impact,
      error: {
        message:
          "This resource has linked tasks. Re-run with allowLinkedTasks=true only after reviewing the impact.",
      },
      runtime: listResult.runtime,
    };
  }

  const deleteResult = await requestGranoflowApi({
    method: "DELETE",
    path: `/v1/${kind}s/${input.id}`,
  });
  if (!deleteResult.ok) {
    return deleteResult;
  }
  const readback = await requestGranoflowApi({ path: listPathFor(kind) });
  const stillPresent = readback.ok
    ? extractItems(readback).some((item) => item.id === input.id)
    : null;
  return {
    ok: stillPresent === false,
    code: stillPresent === false ? "deleted" : "delete_unverified",
    data: {
      deleted: stillPresent === false,
      impact,
      deleteResult,
      readback: readback.ok ? { stillPresent } : readback,
    },
    runtime: deleteResult.runtime,
  };
}

async function finishTask(input: {
  taskId: string;
  projectId?: string;
  milestoneId?: string;
  summary?: string;
  startedAt?: string;
  taskReview?: string;
  reviewCardDrafts?: ReviewCardDraft[];
  endedAt?: string;
  confirmComplete?: boolean;
  dryRun?: boolean;
}) {
  const updateBody = compactRecord({
    startedAt: input.startedAt,
    endedAt: input.endedAt,
  });
  const normalizedCardDrafts = input.reviewCardDrafts?.map(normalizeReviewCardDraft);
  const hasEnhancedCardDrafts = input.reviewCardDrafts?.some(draftUsesEnhancedFields) ?? false;
  const hasReviewImport =
    typeof input.taskReview === "string" ||
    (normalizedCardDrafts !== undefined && normalizedCardDrafts.length > 0);
  if (
    hasReviewImport &&
    (typeof input.projectId !== "string" ||
      input.projectId.length === 0 ||
      typeof input.milestoneId !== "string" ||
      input.milestoneId.length === 0)
  ) {
    const runtime = await requestGranoflowApi({ path: "/v1/health", dryRun: true });
    return {
      ok: false,
      code: "review_import_context_required",
      data: {
        requiredInput: { projectId: "Granoflow project id", milestoneId: "Granoflow milestone id" },
      },
      error: {
        message:
          "projectId and milestoneId are required when writing taskReview or reviewCardDrafts.",
      },
      runtime: runtime.runtime,
    };
  }
  if (hasEnhancedCardDrafts) {
    const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
    if (!toolsResult.ok || !supportsReviewCardDraftNoteFields(toolsResult)) {
      return {
        ok: false,
        code: "review_card_draft_note_fields_unsupported",
        data: {
          unsupportedFields: ["noteFields", "frontLayout", "backLayout"],
          fallback:
            "Regenerate reviewCardDrafts without noteFields/frontLayout/backLayout. Keep phonetic, translation, and pronunciation hints directly in front/back so the card remains useful on older Granoflow apps.",
        },
        error: {
          message: "The running Granoflow app does not advertise review_card_draft_note_fields_v1.",
        },
        runtime: toolsResult.runtime,
      };
    }
  }
  const reviewImportBody = hasReviewImport
    ? {
        "agent-id": "granoflow",
        "tool-id": "single_task_ai",
        ver: "2.0",
        status: "success",
        data: compactRecord({
          task_id: input.taskId,
          project_id: input.projectId,
          milestone_id: input.milestoneId,
          summary: input.summary ?? "Task completed.",
          task_review_update:
            typeof input.taskReview === "string"
              ? {
                  mode: "replace",
                  content: input.taskReview,
                }
              : undefined,
          review_card_drafts: normalizedCardDrafts,
        }),
      }
    : undefined;
  const steps = [
    ...(Object.keys(updateBody).length > 0
      ? [{ method: "PATCH", path: `/v1/tasks/${input.taskId}`, body: updateBody }]
      : []),
    {
      method: "POST",
      path: `/v1/tasks/${input.taskId}/complete`,
      body: compactRecord({ endedAt: input.endedAt }),
    },
    ...(reviewImportBody
      ? [
          {
            method: "POST",
            path: "/v1/ai-agent/tasks/import",
            body: reviewImportBody,
          },
        ]
      : []),
    { method: "GET", path: "/v1/tasks", verify: "status=done and endedAt present when available" },
  ];

  if (input.dryRun !== false) {
    const preview = await requestGranoflowApi({
      method: "POST",
      path: `/v1/tasks/${input.taskId}/complete`,
      body: compactRecord({ taskReview: input.taskReview, endedAt: input.endedAt }),
      dryRun: true,
    });
    return {
      ...preview,
      data: {
        steps,
        previewMode: "local_request_sequence_only",
        finishGuidance: [
          "Before writing, infer startedAt and endedAt from the current agent conversation when evidence is available.",
          "Only pass taskReview when there is durable learning or a meaningful decision; omit it for a plain activity log.",
          "Create one reviewCardDraft per long-lived knowledge point worth remembering.",
        ],
      },
    };
  }

  if (input.confirmComplete !== true) {
    const runtime = await requestGranoflowApi({ path: "/v1/health", dryRun: true });
    return {
      ok: false,
      code: "confirmation_required",
      data: {
        steps,
        requiredInput: { confirmComplete: true },
      },
      error: { message: "Set confirmComplete=true to finish a Granoflow task." },
      runtime: runtime.runtime,
    };
  }

  const applied: unknown[] = [];
  if (Object.keys(updateBody).length > 0) {
    const updateResult = await requestGranoflowApi({
      method: "PATCH",
      path: `/v1/tasks/${input.taskId}`,
      body: updateBody,
    });
    applied.push({ step: "update_task", result: updateResult });
    if (!updateResult.ok) {
      return updateResult;
    }
  }

  const completeResult = await requestGranoflowApi({
    method: "POST",
    path: `/v1/tasks/${input.taskId}/complete`,
    body: compactRecord({ endedAt: input.endedAt }),
  });
  applied.push({ step: "complete_task", result: completeResult });
  if (!completeResult.ok) {
    return completeResult;
  }

  if (reviewImportBody) {
    const importResult = await requestGranoflowApi({
      method: "POST",
      path: "/v1/ai-agent/tasks/import",
      body: reviewImportBody,
    });
    applied.push({ step: "import_task_review_and_cards", result: importResult });
    if (!importResult.ok) {
      return importResult;
    }
  }

  const readback = await requestGranoflowApi({ path: "/v1/tasks" });
  const task = extractItems(readback).find((item) => item.id === input.taskId);
  const verified = task?.status === "done";
  return {
    ok: verified,
    code: verified ? "task_finished" : "finish_unverified",
    data: {
      task: task ? compactResource(task) : null,
      verified,
      applied,
      readback: readback.ok ? { found: Boolean(task) } : readback,
    },
    runtime: completeResult.runtime,
  };
}

export function registerGranoflowTools(server: {
  tool: (
    name: string,
    description: string,
    schema: Record<string, z.ZodTypeAny>,
    handler: (args: Record<string, unknown>) => Promise<ReturnType<typeof textResult>>,
  ) => void;
}) {
  const registerTool = (
    name: string,
    description: string,
    schema: Record<string, z.ZodTypeAny>,
    handler: (args: Record<string, unknown>) => Promise<ReturnType<typeof textResult>>,
  ) => {
    server.tool(name, description, schema, async (args) =>
      withDailyReviewSuggestion(name, await handler(args)),
    );
  };

  registerTool(
    "granoflow_agent_workflow_skill",
    "Read the bundled Granoflow Agent Workflow skill. Call this when a user works with Granoflow tasks, says 'Create a task from this requirement', says 'Process today's tasks', asks in their own language to create a task from a discussed requirement or process tasks for a date/range/all-task scope, needs approval or missing information recorded in a task, finishes tasks, asks for daily, weekly, or monthly reviews, mood or efficiency review notes, task reviews, review cards, historical context, decisions, lessons, similar past work, or long-term work memory, or politely/strongly signals that Granoflow/MCP/generated agent output is wrong or misaligned. Use granoflow_first_run_import_skill for first-run import from Cursor, Codex, Hermes, or other agents. Do not call it for unrelated venting or unrelated disagreement.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-agent-workflow/SKILL.md",
          skill: readAgentWorkflowSkill(),
        },
      }),
  );

  registerTool(
    "granoflow_first_run_import_skill",
    "Read the bundled Granoflow First-Run Import skill. Call this when a user says 'Initialize Granoflow and import data' or asks in their own language to import data from Cursor, Codex, Hermes, or another agent into Granoflow. The workflow previews authorized source records as projects, monthly milestones, tasks, review-card candidates, and context backfills before writing.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-first-run-import/SKILL.md",
          skill: readFirstRunImportSkill(),
        },
      }),
  );

  registerTool(
    "granoflow_setup_status",
    "Inspect Granoflow MCP config and Local HTTP API health without printing secrets.",
    {},
    async () => jsonTextResult(await getSetupStatus()),
  );

  registerTool(
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

  registerTool(
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

  registerTool(
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

  registerTool(
    "granoflow_setup_open_app",
    "Preview or open the installed Granoflow app after user approval. Defaults to dry-run.",
    {
      appPath: z.string().min(1).optional(),
      appName: z.string().min(1).optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ appName, appPath, dryRun }) =>
      jsonTextResult(
        await openGranoflowApp({
          appPath: typeof appPath === "string" ? appPath : undefined,
          appName: typeof appName === "string" ? appName : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );

  registerTool(
    "granoflow_health",
    "Check whether the Granoflow Local HTTP API is reachable.",
    {},
    async () => apiTool({ path: "/v1/health" }),
  );

  registerTool(
    "granoflow_version",
    "Show Granoflow app and Local HTTP API version metadata.",
    {},
    async () => apiTool({ path: "/v1/version" }),
  );

  registerTool(
    "granoflow_capabilities",
    "List capabilities exposed by the running Granoflow app.",
    {},
    async () => apiTool({ path: "/v1/capabilities" }),
  );

  registerTool(
    "granoflow_ai_agent_tools",
    "List Granoflow AI-agent tool contracts from the running app. Use with granoflow_agent_workflow_skill for task, review, and memory-style questions.",
    {},
    async () => apiTool({ path: "/v1/ai-agent/tools" }),
  );

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

  registerTool("granoflow_task_list", "List tasks from Granoflow.", {}, async () =>
    apiTool({ path: "/v1/tasks" }),
  );

  registerTool(
    "granoflow_task_export",
    "Export task details, completion review, project context, and reusable lessons for evidence-based task or memory retrieval.",
    { taskId: z.string().min(1).describe("Granoflow task id.") },
    async ({ taskId }) => apiTool({ path: `/v1/ai-agent/tasks/${String(taskId)}/export` }),
  );

  registerTool(
    "granoflow_task_validate",
    "Validate an AI-agent task result before importing it into Granoflow.",
    { input: jsonInputSchema },
    async ({ input }) =>
      apiTool({ method: "POST", path: "/v1/ai-agent/tasks/validate", body: input }),
  );

  registerTool(
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

  registerTool(
    "granoflow_task_history_mutate",
    "Create, update, or soft-delete historical Granoflow task facts through the dedicated AI-agent API. Use dryRun first; when dryRun=false, the running app must advertise historical_task_mutations_v1.",
    {
      source: z
        .record(z.string(), z.unknown())
        .optional()
        .describe("Source metadata such as {kind, threadId, summary, startedAt, endedAt}."),
      mutations: z.array(historicalTaskMutationSchema).max(20),
      dryRun: z
        .boolean()
        .default(true)
        .describe(
          "When true, previews without writing. Set false only with explicit user approval.",
        ),
    },
    async ({ source, mutations, dryRun }) =>
      jsonTextResult(
        await mutateTaskHistory({
          source: isObject(source) ? source : undefined,
          mutations: Array.isArray(mutations)
            ? (mutations as z.infer<typeof historicalTaskMutationSchema>[])
            : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );

  registerTool(
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

  registerTool(
    "granoflow_task_create_structured",
    "Create a Granoflow task with common structured fields. Defaults to dry-run.",
    {
      title: z.string().min(1),
      description: z.string().optional(),
      dueAt: z.string().optional(),
      remindAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ title, description, dueAt, remindAt, projectId, milestoneId, status, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/tasks",
        body: compactRecord({
          title,
          description,
          dueAt,
          remindAt,
          projectId,
          milestoneId,
          status,
        }),
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
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

  registerTool(
    "granoflow_task_update_structured",
    "Update a Granoflow task with common structured fields. Defaults to dry-run.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      title: z.string().min(1).optional(),
      description: z.string().optional(),
      dueAt: z.string().optional(),
      remindAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({
      taskId,
      title,
      description,
      dueAt,
      remindAt,
      projectId,
      milestoneId,
      status,
      dryRun,
    }) =>
      apiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}`,
        body: compactRecord({
          title,
          description,
          dueAt,
          remindAt,
          projectId,
          milestoneId,
          status,
        }),
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_task_complete",
    "Low-level compatibility endpoint to complete a Granoflow task. Prefer granoflow_task_finish for any user-facing completion request so startedAt, endedAt, review, and review cards can be captured.",
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

  registerTool(
    "granoflow_task_finish",
    "Finish a Granoflow task from the current agent conversation: infer startedAt and endedAt, write only meaningful review content, create one review card per durable knowledge point, complete the task, and verify status=done.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      projectId: z
        .string()
        .min(1)
        .optional()
        .describe("Required when taskReview or reviewCardDrafts are provided."),
      milestoneId: z
        .string()
        .min(1)
        .optional()
        .describe("Required when taskReview or reviewCardDrafts are provided."),
      summary: z
        .string()
        .optional()
        .describe("Short import summary for the completion, review, and card write."),
      startedAt: z
        .string()
        .optional()
        .describe(
          "Task start time inferred from the current agent conversation, preferably ISO-like.",
        ),
      taskReview: z
        .string()
        .optional()
        .describe(
          "Meaningful task review only. Omit this when the content would be a mere activity log.",
        ),
      reviewCardDrafts: z
        .array(reviewCardDraftSchema)
        .optional()
        .describe(
          "One card per durable knowledge point worth long-term memory; omit when there is nothing worth remembering.",
        ),
      endedAt: z
        .string()
        .optional()
        .describe(
          "Task end time inferred from the current agent conversation, preferably ISO-like.",
        ),
      confirmComplete: z.boolean().default(false).describe("Must be true when dryRun=false."),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the update/complete/import/readback sequence."),
    },
    async ({
      taskId,
      projectId,
      milestoneId,
      summary,
      startedAt,
      taskReview,
      reviewCardDrafts,
      endedAt,
      confirmComplete,
      dryRun,
    }) =>
      jsonTextResult(
        await finishTask({
          taskId: String(taskId),
          projectId: typeof projectId === "string" ? projectId : undefined,
          milestoneId: typeof milestoneId === "string" ? milestoneId : undefined,
          summary: typeof summary === "string" ? summary : undefined,
          startedAt: typeof startedAt === "string" ? startedAt : undefined,
          taskReview: typeof taskReview === "string" ? taskReview : undefined,
          reviewCardDrafts: Array.isArray(reviewCardDrafts)
            ? (reviewCardDrafts as ReviewCardDraft[])
            : undefined,
          endedAt: typeof endedAt === "string" ? endedAt : undefined,
          confirmComplete: confirmComplete === true,
          dryRun: dryRun !== false,
        }),
      ),
  );

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

  registerTool("granoflow_project_list", "List Granoflow projects.", {}, async () =>
    apiTool({ path: "/v1/projects" }),
  );

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

  registerTool("granoflow_milestone_list", "List Granoflow milestones.", {}, async () =>
    apiTool({ path: "/v1/milestones" }),
  );

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

  registerTool(
    "granoflow_milestone_create",
    "Create a Granoflow milestone with common structured fields. Defaults to dry-run.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      title: z.string().min(1),
      description: z.string().optional(),
      dueAt: z.string().optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ projectId, title, description, dueAt, status, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/milestones",
        body: compactRecord({
          projectId,
          title,
          description,
          dueAt,
          status,
        }),
        dryRun: dryRun !== false,
      }),
  );

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

  registerTool(
    "granoflow_review_day_show",
    "Show a Granoflow daily review by date.",
    { date: z.string().describe("Date in YYYY-MM-DD format.") },
    async ({ date }) => apiTool({ path: `/v1/reviews/days/${String(date)}` }),
  );

  registerTool(
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
