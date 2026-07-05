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
const resourceStatusSchema = z.string().min(1).optional();
const resolveMatchModeSchema = z.enum(["exact", "contains"]).default("exact");
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
  const normalizedCardDrafts = input.reviewCardDrafts?.map((draft) =>
    compactRecord({
      client_card_id: draft.clientCardId,
      card_type: draft.cardType,
      front: draft.front,
      back: draft.back,
      source_summary: draft.sourceSummary,
    }),
  );
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
    "Read the bundled Granoflow Agent Workflow skill. Call this when a user works with Granoflow tasks, finishes tasks, asks for daily, weekly, or monthly reviews, mood or efficiency review notes, task reviews, or review cards, or politely/strongly signals that Granoflow/MCP/generated agent output is wrong or misaligned. Do not call it for unrelated venting or unrelated disagreement.",
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
    "List Granoflow AI-agent tool contracts.",
    {},
    async () => apiTool({ path: "/v1/ai-agent/tools" }),
  );

  registerTool("granoflow_task_list", "List tasks from Granoflow.", {}, async () =>
    apiTool({ path: "/v1/tasks" }),
  );

  registerTool(
    "granoflow_task_export",
    "Export a task context for an AI agent.",
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
    "Update a Granoflow milestone with common structured fields. Defaults to dry-run.",
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
    async ({ milestoneId, projectId, title, description, dueAt, status, dryRun }) =>
      apiTool({
        method: "PATCH",
        path: `/v1/milestones/${String(milestoneId)}`,
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
