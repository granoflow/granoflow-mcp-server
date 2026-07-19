import { z } from "zod";

import { requestGranoflowApi, type ApiRequestOptions } from "./api.js";
import { apiTool, compactRecord, isObject, jsonTextResult } from "./tool-runtime-core.js";
import type { ReviewCardDraft } from "./tools.js";
import { historicalTaskMutationSchema } from "./tools.js";

export function draftUsesEnhancedFields(draft: ReviewCardDraft): boolean {
  return (
    (draft.noteFields?.length ?? 0) > 0 ||
    (draft.frontLayout?.length ?? 0) > 0 ||
    (draft.backLayout?.length ?? 0) > 0
  );
}

export function normalizeReviewCardDraft(draft: ReviewCardDraft): Record<string, unknown> {
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

export function supportsReviewCardDraftNoteFields(payload: unknown): boolean {
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

export function supportsHistoricalTaskMutations(payload: unknown): boolean {
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

export function supportsContextPack(payload: unknown): boolean {
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

export function supportsHistoricalTaskCandidates(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (
      !isObject(tool) ||
      tool.toolId !== "granoflow_historical_task_candidates_v2" ||
      tool.enabled !== true
    ) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    return (
      capabilities.capability === "historical_task_candidates_v2" &&
      capabilities.taskAnchored === true &&
      capabilities.appOwnedEvidence === true &&
      capabilities.relationshipFacts === true &&
      capabilities.recommendations === false
    );
  });
}

export function supportsMemoryBatchPreview(payload: unknown): boolean {
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

export function supportsContextSteward(payload: unknown): boolean {
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

export function supportsProjectContextAttachments(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const tools = isObject(data) && Array.isArray(data.tools) ? data.tools : [];
  return tools.some((tool) => {
    if (
      !isObject(tool) ||
      tool.toolId !== "granoflow_project_context_attachments_v1" ||
      tool.enabled !== true
    ) {
      return false;
    }
    const capabilities = isObject(tool.capabilities) ? tool.capabilities : {};
    const consistency = isObject(capabilities.consistencySafety)
      ? capabilities.consistencySafety
      : {};
    return (
      capabilities.freshnessCheck === true &&
      capabilities.incrementalReconcile === true &&
      capabilities.fullReadRequiresExplicitIntent === true &&
      consistency.rulesAndWordingConflicts === "proposal_required" &&
      consistency.secretOrPrivacyRisk === "fail_closed"
    );
  });
}

export async function requestPreviewWithMeta(
  options: ApiRequestOptions,
  meta: Record<string, unknown>,
) {
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

export async function contextPackApiTool(options: ApiRequestOptions) {
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

export async function historicalTaskCandidatesApiTool(options: ApiRequestOptions) {
  if (options.dryRun) {
    return apiTool(options);
  }
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  if (!toolsResult.ok || !supportsHistoricalTaskCandidates(toolsResult)) {
    return jsonTextResult({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "historical_task_candidates_v2",
        endpoint: options.path,
      },
      error: {
        message: "The running Granoflow app does not advertise historical_task_candidates_v2.",
      },
      runtime: toolsResult.runtime,
    });
  }
  return apiTool(options);
}

export async function memoryBatchPreviewApiTool(options: ApiRequestOptions) {
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

export async function projectContextAttachmentApiTool(options: ApiRequestOptions) {
  if (options.dryRun) {
    return apiTool(options);
  }
  const toolsResult = await requestGranoflowApi({ path: "/v1/ai-agent/tools" });
  if (!toolsResult.ok || !supportsProjectContextAttachments(toolsResult)) {
    return jsonTextResult({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "granoflow_project_context_attachments_v1",
        endpoint: options.path,
      },
      error: {
        message:
          "The running Granoflow app does not advertise granoflow_project_context_attachments_v1.",
      },
      runtime: toolsResult.runtime,
    });
  }
  return apiTool(options);
}

export async function mutateTaskHistory(input: {
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
