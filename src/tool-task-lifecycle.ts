import * as tools from "./tools.js";
import type { ReviewCardDraft, ResourceKind } from "./tools.js";
import type { CompletionSource } from "./source-tags.js";

export function titleMatches(
  title: unknown,
  query: string,
  matchMode: "exact" | "contains",
): boolean {
  if (typeof title !== "string") {
    return false;
  }
  const normalizedTitle = title.trim().toLowerCase();
  const normalizedQuery = query.trim().toLowerCase();
  return matchMode === "exact"
    ? normalizedTitle === normalizedQuery
    : normalizedTitle.includes(normalizedQuery);
}

export function listPathFor(kind: ResourceKind): string {
  return `/v1/${kind}s`;
}

export async function resolveResource(
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
  const result = await tools.requestGranoflowApi({ path: listPathFor(kind) });
  if (!result.ok) {
    return result;
  }
  const matches = tools.extractItems(result).filter((item) => {
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
      matches: matches.map(tools.compactResource),
    },
    runtime: result.runtime,
  };
}

async function findLinkedTasks(kind: Exclude<ResourceKind, "task">, id: string) {
  const tasksResult = await tools.requestGranoflowApi({ path: "/v1/tasks" });
  return tasksResult.ok
    ? tools
        .extractItems(tasksResult)
        .filter((task) => (kind === "project" ? task.projectId === id : task.milestoneId === id))
    : [];
}

export async function safeDeleteResource(
  kind: Exclude<ResourceKind, "task">,
  input: {
    id: string;
    confirmTitle?: string;
    allowLinkedTasks?: boolean;
    dryRun?: boolean;
  },
) {
  const listResult = await tools.requestGranoflowApi({ path: listPathFor(kind) });
  if (!listResult.ok) {
    return listResult;
  }
  const resource = tools.extractItems(listResult).find((item) => item.id === input.id);
  if (!resource) {
    return {
      ok: false,
      code: `${kind}_not_found`,
      error: { message: `Granoflow ${kind} was not found.` },
      runtime: listResult.runtime,
    };
  }

  const linkedTasks = await findLinkedTasks(kind, input.id);
  const impact = {
    resource: tools.compactResource(resource),
    linkedTaskCount: linkedTasks.length,
    linkedTasks: linkedTasks.map(tools.compactResource),
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

  const deleteResult = await tools.requestGranoflowApi({
    method: "DELETE",
    path: `/v1/${kind}s/${input.id}`,
  });
  if (!deleteResult.ok) {
    return deleteResult;
  }
  const readback = await tools.requestGranoflowApi({ path: listPathFor(kind) });
  const stillPresent = readback.ok
    ? tools.extractItems(readback).some((item) => item.id === input.id)
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

type FinishTaskInput = {
  taskId: string;
  projectId?: string;
  milestoneId?: string;
  summary?: string;
  startedAt?: string;
  taskReview?: string;
  reviewCardDrafts?: ReviewCardDraft[];
  endedAt?: string;
  completionSource?: CompletionSource;
  confirmComplete?: boolean;
  dryRun?: boolean;
};

type FinishTaskPlan = {
  completionSource: CompletionSource;
  reviewImportBody?: Record<string, unknown>;
  steps: Array<Record<string, unknown>>;
};

function buildFinishSteps(
  input: FinishTaskInput,
  completionSource: CompletionSource,
  reviewImportBody: Record<string, unknown> | undefined,
): Array<Record<string, unknown>> {
  return [
    ...(completionSource === "unknown"
      ? []
      : [
          {
            method: "PATCH",
            path: `/v1/tasks/${input.taskId}`,
            body: { tags: `attach ${completionSource} source tag when missing` },
          },
        ]),
    {
      method: "POST",
      path: `/v1/tasks/${input.taskId}/complete`,
      body: tools.compactRecord({ startedAt: input.startedAt, endedAt: input.endedAt }),
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
}

export async function finishTask(input: FinishTaskInput) {
  const completionSource = input.completionSource ?? "ai";
  const normalizedCardDrafts = input.reviewCardDrafts?.map(tools.normalizeReviewCardDraft);
  const hasEnhancedCardDrafts =
    input.reviewCardDrafts?.some(tools.draftUsesEnhancedFields) ?? false;
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
    const runtime = await tools.requestGranoflowApi({ path: "/v1/health", dryRun: true });
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
    const toolsResult = await tools.requestGranoflowApi({ path: "/v1/ai-agent/tools" });
    if (!toolsResult.ok || !tools.supportsReviewCardDraftNoteFields(toolsResult)) {
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
        data: tools.compactRecord({
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
  const steps = buildFinishSteps(input, completionSource, reviewImportBody);

  return executeFinishTask(input, {
    completionSource,
    reviewImportBody,
    steps,
  });
}
async function executeFinishTask(input: FinishTaskInput, plan: FinishTaskPlan) {
  const { steps } = plan;
  if (input.dryRun !== false) {
    const preview = await tools.requestGranoflowApi({
      method: "POST",
      path: `/v1/tasks/${input.taskId}/complete`,
      body: tools.compactRecord({
        taskReview: input.taskReview,
        startedAt: input.startedAt,
        endedAt: input.endedAt,
      }),
      dryRun: true,
    });
    return {
      ...preview,
      data: {
        steps,
        previewMode: "local_request_sequence_only",
        finishGuidance: [
          "Use this compatibility path only when the latest task has no Plan nodes.",
          "Before completion, verify the required Task Delivery attachment and Completion Summary when this workflow entered Plan or Execution.",
          "Do not generate Task Review or Review Cards by default; schedule Deferred Task Review separately.",
          "Only pass legacy taskReview/reviewCardDrafts when the user explicitly requested inline review and approved that payload.",
        ],
      },
    };
  }

  return applyFinishTask(input, plan);
}

async function applyFinishTask(input: FinishTaskInput, plan: FinishTaskPlan) {
  const { completionSource, reviewImportBody, steps } = plan;
  if (input.confirmComplete !== true) {
    const runtime = await tools.requestGranoflowApi({ path: "/v1/health", dryRun: true });
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

  const nodesResult = await tools.requestGranoflowApi({
    path: `/v1/tasks/${input.taskId}/nodes`,
  });
  if (nodesResult.ok && tools.extractItems(nodesResult).length > 0) {
    return {
      ok: false,
      code: "node_managed_completion_required",
      data: {
        taskId: input.taskId,
        nodeCount: tools.extractItems(nodesResult).length,
        completionOwner: "task_node_service",
      },
      error: {
        message:
          "This task has Plan nodes. Write and verify Task Delivery, then finish the final required node; do not call a second completion endpoint.",
      },
      runtime: nodesResult.runtime,
    };
  }

  const documentGate = await tools.requireTaskAnalysisPlanAttachment(input.taskId);
  if (!documentGate.ok) return documentGate;

  const applied: unknown[] = [];

  const sourceTagPatch = await tools.patchTaskCompletionSourceTag(input.taskId, completionSource);
  if (sourceTagPatch && !sourceTagPatch.ok) {
    return sourceTagPatch;
  }
  if (sourceTagPatch) {
    applied.push({ step: "attach_source_tag", result: sourceTagPatch });
  }

  const completeResult = await tools.requestGranoflowApi({
    method: "POST",
    path: `/v1/tasks/${input.taskId}/complete`,
    body: tools.compactRecord({ startedAt: input.startedAt, endedAt: input.endedAt }),
  });
  applied.push({ step: "complete_task", result: completeResult });
  if (!completeResult.ok) {
    return completeResult;
  }

  if (reviewImportBody) {
    const importResult = await tools.requestGranoflowApi({
      method: "POST",
      path: "/v1/ai-agent/tasks/import",
      body: reviewImportBody,
    });
    applied.push({ step: "import_task_review_and_cards", result: importResult });
    if (!importResult.ok) {
      return importResult;
    }
  }

  const readback = await tools.requestGranoflowApi({ path: "/v1/tasks" });
  const task = tools.extractItems(readback).find((item) => item.id === input.taskId);
  const verified = task?.status === "done";
  return {
    ok: verified,
    code: verified ? "task_finished" : "finish_unverified",
    data: {
      task: task ? tools.compactResource(task) : null,
      verified,
      applied,
      readback: readback.ok ? { found: Boolean(task) } : readback,
    },
    runtime: completeResult.runtime,
  };
}
