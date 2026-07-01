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
const resourceStatusSchema = z.string().min(1).optional();
const resolveMatchModeSchema = z.enum(["exact", "contains"]).default("exact");

type ResourceKind = "project" | "milestone" | "task";

type GranoflowRecord = {
  id?: unknown;
  title?: unknown;
  status?: unknown;
  projectId?: unknown;
  milestoneId?: unknown;
  [key: string]: unknown;
};

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
  taskReview?: string;
  endedAt?: string;
  confirmComplete?: boolean;
  dryRun?: boolean;
}) {
  const updateBody = compactRecord({
    taskReview: input.taskReview,
    endedAt: input.endedAt,
  });
  const steps = [
    ...(Object.keys(updateBody).length > 0
      ? [{ method: "PATCH", path: `/v1/tasks/${input.taskId}`, body: updateBody }]
      : []),
    {
      method: "POST",
      path: `/v1/tasks/${input.taskId}/complete`,
      body: compactRecord({ endedAt: input.endedAt }),
    },
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
    "granoflow_task_create_structured",
    "Create a Granoflow task with common structured fields. Defaults to dry-run.",
    {
      title: z.string().min(1),
      description: z.string().optional(),
      dueAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ title, description, dueAt, projectId, milestoneId, status, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/tasks",
        body: compactRecord({
          title,
          description,
          dueAt,
          projectId,
          milestoneId,
          status,
        }),
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
    "granoflow_task_update_structured",
    "Update a Granoflow task with common structured fields. Defaults to dry-run.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      title: z.string().min(1).optional(),
      description: z.string().optional(),
      dueAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ taskId, title, description, dueAt, projectId, milestoneId, status, dryRun }) =>
      apiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}`,
        body: compactRecord({
          title,
          description,
          dueAt,
          projectId,
          milestoneId,
          status,
        }),
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

  server.tool(
    "granoflow_task_finish",
    "Write a task review, complete a Granoflow task, and read back status=done verification.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      taskReview: z.string().optional(),
      endedAt: z.string().optional(),
      confirmComplete: z.boolean().default(false).describe("Must be true when dryRun=false."),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the update/complete/readback sequence."),
    },
    async ({ taskId, taskReview, endedAt, confirmComplete, dryRun }) =>
      jsonTextResult(
        await finishTask({
          taskId: String(taskId),
          taskReview: typeof taskReview === "string" ? taskReview : undefined,
          endedAt: typeof endedAt === "string" ? endedAt : undefined,
          confirmComplete: confirmComplete === true,
          dryRun: dryRun !== false,
        }),
      ),
  );

  server.tool(
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

  server.tool("granoflow_project_list", "List Granoflow projects.", {}, async () =>
    apiTool({ path: "/v1/projects" }),
  );

  server.tool(
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

  server.tool(
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

  server.tool(
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

  server.tool(
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

  server.tool("granoflow_milestone_list", "List Granoflow milestones.", {}, async () =>
    apiTool({ path: "/v1/milestones" }),
  );

  server.tool(
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

  server.tool(
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

  server.tool(
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

  server.tool(
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
