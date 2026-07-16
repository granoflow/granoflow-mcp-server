import { createHash } from "node:crypto";
import { readFileSync, realpathSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { extname, isAbsolute, relative, resolve } from "node:path";

import { z } from "zod";

import {
  maybeCreateDailyReviewSuggestion,
  type MonthlyReviewSuggestion,
  type WeeklyReviewSuggestion,
} from "./config.js";
import { requestGranoflowApi, type ApiRequestOptions, type ApiResult } from "./api.js";
import {
  applyCompletionSourceToBody,
  completionSourceTagSlug,
  ensureSourceTags,
  mergeTagSlugs,
  readSourceTagCatalog,
  type CompletionSource,
} from "./source-tags.js";
import {
  detectLocalApi,
  getSetupStatus,
  openGranoflowApp,
  openSetupConfig,
  writeSetupConfig,
} from "./setup.js";
import {
  BUNDLED_SKILL_IDS,
  bundledSkillResources,
  WorkflowResourceError,
} from "./workflow-resources.js";

const jsonInputSchema = z
  .record(z.string(), z.unknown())
  .describe("JSON object sent to the Granoflow Local HTTP API.");
const completionSourceSchema = z
  .enum(["ai", "human", "unknown"])
  .optional()
  .describe(
    "When ai or human, attach the matching AI/人工 source tag after ensuring it exists. Omit or unknown means no source tag.",
  );
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
const projectContextAttachmentSchema = z
  .enum(["snapshot", "rules", "project_snapshot.yaml", "project_rules.yaml"])
  .default("snapshot");
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
const TASK_REVIEW_START = "<!-- granoflow-task-review:v1:start -->";
const TASK_REVIEW_END = "<!-- granoflow-task-review:v1:end -->";
const TASK_COMPLETION_SUMMARY_START = "<!-- granoflow-task-completion-summary:v1:start -->";
const TASK_COMPLETION_SUMMARY_END = "<!-- granoflow-task-completion-summary:v1:end -->";
const resourceStatusSchema = z.string().min(1).optional();
const taskNodeStatusSchema = z.enum(["pending", "finished"]);
const taskNodeCreateSchema = z.object({
  title: z.string().min(1),
  parentId: z.string().min(1).optional(),
});
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
const DAILY_REVIEW_SKILL_URL = new URL(
  "../skills/granoflow-daily-review/SKILL.md",
  import.meta.url,
);
const FIRST_RUN_IMPORT_SKILL_URL = new URL(
  "../skills/granoflow-first-run-import/SKILL.md",
  import.meta.url,
);
const REVIEW_CARD_DRAFT_SKILL_URL = new URL(
  "../skills/granoflow-review-card-draft/SKILL.md",
  import.meta.url,
);
const GFMCP_RUNNER_SKILL_URL = new URL(
  "../skills/granoflow-gfmcp-runner/SKILL.md",
  import.meta.url,
);

function compactRecord(record: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(record).filter(([, value]) => value !== undefined));
}

function validateManagedBlock(
  value: string,
  startMarker: string,
  endMarker: string,
): { ok: true } | { ok: false; reason: string } {
  const start = value.indexOf(startMarker);
  const end = value.indexOf(endMarker);
  if (start < 0 || end < 0) return { ok: false, reason: "missing_marker" };
  if (start > end) return { ok: false, reason: "reversed_markers" };
  if (value.indexOf(startMarker, start + startMarker.length) >= 0) {
    return { ok: false, reason: "duplicate_start_marker" };
  }
  if (value.indexOf(endMarker, end + endMarker.length) >= 0) {
    return { ok: false, reason: "duplicate_end_marker" };
  }
  return { ok: true };
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

function readDailyReviewSkill(): string {
  return readFileSync(DAILY_REVIEW_SKILL_URL, "utf8");
}

function readFirstRunImportSkill(): string {
  return readFileSync(FIRST_RUN_IMPORT_SKILL_URL, "utf8");
}

function readReviewCardDraftSkill(): string {
  return readFileSync(REVIEW_CARD_DRAFT_SKILL_URL, "utf8");
}

function readGfmcpRunnerSkill(): string {
  return readFileSync(GFMCP_RUNNER_SKILL_URL, "utf8");
}

function isWithin(root: string, target: string): boolean {
  const path = relative(root, target);
  return path === "" || (!path.startsWith("..") && !isAbsolute(path));
}

function validatedWorkflowMarkdownPath(filePath: string): string {
  const absolute = realpathSync(resolve(filePath));
  const roots = [realpathSync(process.cwd()), realpathSync(tmpdir())];
  if (
    extname(absolute).toLowerCase() !== ".md" ||
    !roots.some((root) => isWithin(root, absolute))
  ) {
    throw new Error(
      "Task workflow attachments must be Markdown files under the current workspace or system temp directory.",
    );
  }
  if (!statSync(absolute).isFile()) {
    throw new Error("Task workflow attachment path must reference a regular file.");
  }
  return absolute;
}

function supportsTaskNodeWorkflow(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const resources = isObject(data) && isObject(data.resources) ? data.resources : {};
  const task = Array.isArray(resources.task) ? resources.task : [];
  return [
    "node.list",
    "node.batch-create",
    "node.update-title",
    "node.apply-status",
    "node.delete",
  ].every((action) => task.includes(action));
}

function supportsTaskWorkflowAttachmentReadback(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const resources = isObject(data) && isObject(data.resources) ? data.resources : {};
  const task = Array.isArray(resources.task) ? resources.task : [];
  return ["attachment.conditional-add", "attachment.read-content-hash"].every((action) =>
    task.includes(action),
  );
}

function extractEntity(value: unknown): Record<string, unknown> | null {
  if (!isObject(value)) return null;
  if (isObject(value.entity)) return value.entity;
  if (isObject(value.data)) return extractEntity(value.data);
  return null;
}

async function addTaskWorkflowAttachment(input: {
  taskId: string;
  filePath: string;
  idempotencyKey: string;
  expectedTaskUpdatedAt: string;
  dryRun: boolean;
}) {
  const file = validatedWorkflowMarkdownPath(input.filePath);
  const contentSha256 = createHash("sha256").update(readFileSync(file)).digest("hex");
  const body = {
    file,
    idempotencyKey: input.idempotencyKey,
    expectedTaskUpdatedAt: input.expectedTaskUpdatedAt,
    expectedContentSha256: contentSha256,
  };
  if (input.dryRun) {
    return requestGranoflowApi({
      method: "POST",
      path: `/v1/tasks/${input.taskId}/attachments`,
      body,
      dryRun: true,
    });
  }
  const capabilities = await requestGranoflowApi({ path: "/v1/capabilities" });
  if (!capabilities.ok || !supportsTaskWorkflowAttachmentReadback(capabilities)) {
    return {
      ok: false,
      code: "unsupported_capability",
      data: { requiredCapability: "task_workflow_attachment_readback_v1" },
      error: {
        message:
          "The running Granoflow app does not advertise conditional task attachment write and content/hash readback.",
      },
      runtime: capabilities.runtime,
    };
  }
  const write = await requestGranoflowApi({
    method: "POST",
    path: `/v1/tasks/${input.taskId}/attachments`,
    body,
  });
  if (!write.ok) return write;
  const entity = extractEntity(write);
  const attachmentId = typeof entity?.id === "string" ? entity.id : undefined;
  if (!attachmentId) {
    return {
      ok: false,
      code: "attachment_readback_unavailable",
      data: { write },
      error: { message: "The app did not return the created task attachment id." },
      runtime: write.runtime,
    };
  }
  const readback = await requestGranoflowApi({
    path: `/v1/tasks/${input.taskId}/attachments/${attachmentId}`,
  });
  const readbackData = isObject(readback.data) ? readback.data : {};
  const storedHash =
    typeof readbackData.contentSha256 === "string"
      ? readbackData.contentSha256
      : isObject(readbackData.data) && typeof readbackData.data.contentSha256 === "string"
        ? readbackData.data.contentSha256
        : undefined;
  const verified = readback.ok && storedHash === contentSha256;
  return {
    ok: verified,
    code: verified ? "task_attachment_written" : "attachment_readback_mismatch",
    data: { attachment: entity, contentSha256, verified, write, readback },
    error: verified
      ? undefined
      : { message: "Task attachment content/hash readback did not match the local Markdown." },
    runtime: readback.runtime ?? write.runtime,
  };
}

async function taskNodeApiTool(options: ApiRequestOptions) {
  if (options.method === "GET" || options.dryRun) return apiTool(options);
  const capabilities = await requestGranoflowApi({ path: "/v1/capabilities" });
  if (!capabilities.ok || !supportsTaskNodeWorkflow(capabilities)) {
    return jsonTextResult({
      ok: false,
      code: "unsupported_capability",
      data: { requiredCapability: "task_node_workflow_v1", endpoint: options.path },
      error: {
        message: "The running Granoflow app does not advertise task node workflow support.",
      },
      runtime: capabilities.runtime,
    });
  }
  return apiTool(options);
}

async function requireTaskAnalysisPlanAttachment(taskId: string) {
  const attachments = await requestGranoflowApi({
    path: `/v1/tasks/${taskId}/attachments`,
  });
  if (!attachments.ok) return attachments;
  const items = extractItems(attachments);
  const names = items
    .map((item) => (typeof item.displayName === "string" ? item.displayName : ""))
    .filter(Boolean);
  const hasTaskWork = names.some((name) => /^task-work-.*\.md$/i.test(name));
  const hasLegacyAnalysis = names.some((name) => /^task-analysis-.*\.md$/i.test(name));
  const hasLegacyPlan = names.some((name) => /^task-plan-.*\.md$/i.test(name));
  if (hasTaskWork || (hasLegacyAnalysis && hasLegacyPlan)) {
    return { ok: true, code: "task_analysis_plan_attachment_present", data: { names } };
  }
  return {
    ok: false,
    code: "task_analysis_plan_attachment_required",
    data: {
      taskId,
      attachmentNames: names,
      accepted: ["task-work-*.md", "task-analysis-*.md + task-plan-*.md"],
    },
    error: {
      message:
        "Task completion requires an attached and readable Task Work Document, or legacy Task Analysis and Task Plan attachments.",
    },
    runtime: attachments.runtime,
  };
}

async function completeNodeLessTask(input: {
  taskId: string;
  body?: Record<string, unknown>;
  dryRun: boolean;
}) {
  if (input.dryRun) {
    return requestGranoflowApi({
      method: "POST",
      path: `/v1/tasks/${input.taskId}/complete`,
      body: input.body,
      dryRun: true,
    });
  }
  const nodes = await requestGranoflowApi({ path: `/v1/tasks/${input.taskId}/nodes` });
  if (nodes.ok && extractItems(nodes).length > 0) {
    return {
      ok: false,
      code: "node_managed_completion_required",
      data: {
        taskId: input.taskId,
        nodeCount: extractItems(nodes).length,
        completionOwner: "task_node_service",
      },
      error: {
        message:
          "This task has Plan nodes. Write and verify Task Delivery, then finish the final required node.",
      },
      runtime: nodes.runtime,
    };
  }
  const documentGate = await requireTaskAnalysisPlanAttachment(input.taskId);
  if (!documentGate.ok) return documentGate;
  return requestGranoflowApi({
    method: "POST",
    path: `/v1/tasks/${input.taskId}/complete`,
    body: input.body,
  });
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

type TagFilterNotice = {
  acceptedTags: string[];
  skippedTags: Array<{ slug: string; reason: "unknown_tag" }>;
  catalogUnavailable?: boolean;
};

function normalizeRequestedTags(tags: unknown): string[] {
  if (!Array.isArray(tags)) {
    return [];
  }
  return tags
    .map((tag) => (typeof tag === "string" ? tag.trim() : String(tag).trim()))
    .filter(Boolean);
}

async function fetchKnownTagSlugs(): Promise<{ slugs: Set<string>; catalogUnavailable: boolean }> {
  const result = await requestGranoflowApi({ method: "GET", path: "/v1/tags" });
  if (!result.ok) {
    return { slugs: new Set(), catalogUnavailable: true };
  }
  const slugs = new Set<string>();
  for (const item of extractItems(result.data)) {
    if (typeof item.slug === "string" && item.slug.trim()) {
      slugs.add(item.slug.trim());
    }
  }
  return { slugs, catalogUnavailable: false };
}

async function filterTagsForTaskWrite(tags: unknown): Promise<{
  tags?: string[];
  tagFilter: TagFilterNotice;
}> {
  const requested = normalizeRequestedTags(tags);
  if (requested.length === 0) {
    return {
      tags: undefined,
      tagFilter: { acceptedTags: [], skippedTags: [] },
    };
  }
  const { slugs, catalogUnavailable } = await fetchKnownTagSlugs();
  if (catalogUnavailable) {
    return {
      tags: undefined,
      tagFilter: {
        acceptedTags: [],
        skippedTags: requested.map((slug) => ({ slug, reason: "unknown_tag" })),
        catalogUnavailable: true,
      },
    };
  }
  const acceptedTags: string[] = [];
  const skippedTags: Array<{ slug: string; reason: "unknown_tag" }> = [];
  for (const slug of requested) {
    if (slugs.has(slug)) {
      acceptedTags.push(slug);
    } else {
      skippedTags.push({ slug, reason: "unknown_tag" });
    }
  }
  return {
    tags: acceptedTags.length > 0 ? acceptedTags : undefined,
    tagFilter: { acceptedTags, skippedTags },
  };
}

function withTagFilterMetadata(result: ApiResult, tagFilter: TagFilterNotice): ApiResult {
  if (
    tagFilter.skippedTags.length === 0 &&
    !tagFilter.catalogUnavailable &&
    tagFilter.acceptedTags.length === 0
  ) {
    return result;
  }
  const data: Record<string, unknown> = isObject(result.data)
    ? { ...result.data }
    : { value: result.data };
  data.tagFilter = tagFilter;
  return { ...result, data };
}

async function applyTaskBodyTagFilter(body: Record<string, unknown>): Promise<{
  body: Record<string, unknown>;
  tagFilter?: TagFilterNotice;
}> {
  if (!("tags" in body)) {
    return { body };
  }
  const { tags, tagFilter } = await filterTagsForTaskWrite(body.tags);
  const nextBody = { ...body };
  if (tags !== undefined) {
    nextBody.tags = tags;
  } else {
    delete nextBody.tags;
  }
  const hasTagFilter =
    tagFilter.skippedTags.length > 0 ||
    tagFilter.catalogUnavailable === true ||
    tagFilter.acceptedTags.length > 0;
  return hasTagFilter ? { body: nextBody, tagFilter } : { body: nextBody };
}

async function apiToolForTaskWrite(
  options: ApiRequestOptions,
  body: Record<string, unknown>,
  completionSource?: CompletionSource,
) {
  const withSource = await applyCompletionSourceToBody(body, completionSource);
  const { body: filteredBody, tagFilter } = await applyTaskBodyTagFilter(withSource);
  const result = await requestGranoflowApi({ ...options, body: filteredBody });
  return jsonTextResult(tagFilter ? withTagFilterMetadata(result, tagFilter) : result);
}

function parseCompletionSource(value: unknown): CompletionSource | undefined {
  if (value === "ai" || value === "human" || value === "unknown") {
    return value;
  }
  return undefined;
}

function extractTaskEntity(value: unknown): GranoflowRecord | null {
  if (!isObject(value)) {
    return null;
  }
  const data = value.data;
  if (isObject(data) && isObject(data.entity)) {
    return data.entity;
  }
  if (isObject(data) && isObject(data.data) && isObject(data.data.entity)) {
    return data.data.entity;
  }
  return null;
}

async function patchTaskCompletionSourceTag(
  taskId: string,
  completionSource: CompletionSource = "ai",
): Promise<ApiResult | null> {
  if (completionSource === "unknown") {
    return null;
  }
  const ensured = await ensureSourceTags();
  const catalog = readSourceTagCatalog(ensured);
  if (!catalog) {
    return ensured;
  }
  const slug = completionSourceTagSlug(completionSource, catalog);
  if (!slug) {
    return null;
  }
  const readResult = await requestGranoflowApi({ path: `/v1/tasks/${taskId}` });
  if (!readResult.ok) {
    return readResult;
  }
  const entity = extractTaskEntity(readResult.data);
  const currentTags = entity?.tags;
  const merged = mergeTagSlugs(currentTags, [slug]);
  const unchanged =
    Array.isArray(currentTags) &&
    currentTags.length === merged.length &&
    merged.every((tag) => currentTags.includes(tag));
  if (unchanged) {
    return null;
  }
  return requestGranoflowApi({
    method: "PATCH",
    path: `/v1/tasks/${taskId}`,
    body: { tags: merged },
  });
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

function supportsProjectContextAttachments(payload: unknown): boolean {
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

async function projectContextAttachmentApiTool(options: ApiRequestOptions) {
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
  completionSource?: CompletionSource;
  confirmComplete?: boolean;
  dryRun?: boolean;
}) {
  const completionSource = input.completionSource ?? "ai";
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
          "Use this compatibility path only when the latest task has no Plan nodes.",
          "Before completion, verify the required Task Delivery attachment and Completion Summary when this workflow entered Plan or Execution.",
          "Do not generate Task Review or Review Cards by default; schedule Deferred Task Review separately.",
          "Only pass legacy taskReview/reviewCardDrafts when the user explicitly requested inline review and approved that payload.",
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

  const nodesResult = await requestGranoflowApi({
    path: `/v1/tasks/${input.taskId}/nodes`,
  });
  if (nodesResult.ok && extractItems(nodesResult).length > 0) {
    return {
      ok: false,
      code: "node_managed_completion_required",
      data: {
        taskId: input.taskId,
        nodeCount: extractItems(nodesResult).length,
        completionOwner: "task_node_service",
      },
      error: {
        message:
          "This task has Plan nodes. Write and verify Task Delivery, then finish the final required node; do not call a second completion endpoint.",
      },
      runtime: nodesResult.runtime,
    };
  }

  const documentGate = await requireTaskAnalysisPlanAttachment(input.taskId);
  if (!documentGate.ok) return documentGate;

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

  const sourceTagPatch = await patchTaskCompletionSourceTag(input.taskId, completionSource);
  if (sourceTagPatch && !sourceTagPatch.ok) {
    return sourceTagPatch;
  }
  if (sourceTagPatch) {
    applied.push({ step: "attach_source_tag", result: sourceTagPatch });
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
    "Read the bundled Granoflow Agent Workflow skill. Call this when a user works with Granoflow tasks, says 'Analyze the first task', says 'Start the first task', says 'Create a task from this requirement', says 'Process today's tasks', asks in their own language to analyze/start one selected task, create a task from a discussed requirement, or process tasks for a date/range/all-task scope, needs approval or missing information recorded in a task, finishes tasks, asks for weekly or monthly reviews, task reviews, review cards, historical context, decisions, lessons, similar past work, or long-term work memory, or politely/strongly signals that Granoflow/MCP/generated agent output is wrong or misaligned. Use granoflow_daily_review_skill for an explicitly requested daily review or mood/efficiency note, and granoflow_first_run_import_skill for first-run import from Cursor, Codex, Hermes, or other agents. Do not call it for unrelated venting or unrelated disagreement.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-agent-workflow/SKILL.md",
          skill: readAgentWorkflowSkill(),
          references: await bundledSkillResources.listReferences("granoflow-agent-workflow"),
        },
      }),
  );

  registerTool(
    "granoflow_daily_review_skill",
    "Read the bundled Granoflow Daily Review skill. Call this when a user explicitly asks to review, summarize, or journal one day, including mood or efficiency notes. It requires display of evidence and a draft, conversation and explicit confirmation, then write and App/API readback of only approved daily-review fields.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-daily-review/SKILL.md",
          skill: readDailyReviewSkill(),
          references: await bundledSkillResources.listReferences("granoflow-daily-review"),
        },
      }),
  );

  registerTool(
    "granoflow_first_run_import_skill",
    "Read the bundled Granoflow First-Run Import skill. Call this when a user says 'Initialize Granoflow', optionally asks to import data, or uses an equivalent request in their own language. The workflow checks the connection, offers all unavailable recommended AI capability collections using only their names and plain-language functions, and previews authorized Cursor, Codex, Hermes, or other agent records as projects, monthly milestones, tasks, review-card candidates, and context backfills before any requested import write.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-first-run-import/SKILL.md",
          skill: readFirstRunImportSkill(),
          references: await bundledSkillResources.listReferences("granoflow-first-run-import"),
        },
      }),
  );

  registerTool(
    "granoflow_review_card_draft_skill",
    "Read the bundled core Granoflow review-card authoring skill. Call it for every lifecycle Card Checkpoint and every card search, link, create, or modification so similarity fallback, AI filtering, note quality, preview, approval, controlled writes, and readback use one workflow.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-review-card-draft/SKILL.md",
          skill: readReviewCardDraftSkill(),
          references: await bundledSkillResources.listReferences("granoflow-review-card-draft"),
        },
      }),
  );

  registerTool(
    "granoflow_gfmcp_runner_skill",
    "Read the bundled GFMCP automatic task runner skill. Use it to install, operate, or diagnose the optional five-minute Python worker for pending tasks tagged GFMCP.",
    {},
    async () =>
      jsonTextResult({
        ok: true,
        code: "ok",
        data: {
          path: "skills/granoflow-gfmcp-runner/SKILL.md",
          skill: readGfmcpRunnerSkill(),
          references: await bundledSkillResources.listReferences("granoflow-gfmcp-runner"),
        },
      }),
  );

  registerTool(
    "granoflow_bundled_skill_reference",
    "Read one public Markdown reference from a bundled Granoflow skill. Discover valid referenceId values from that skill's references manifest first. This read-only package operation does not call the Granoflow Local HTTP API or require an API token.",
    {
      skillId: z.enum(BUNDLED_SKILL_IDS),
      referenceId: z
        .string()
        .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/)
        .describe("Reference identifier from the selected bundled skill manifest."),
    },
    async ({ skillId, referenceId }) => {
      try {
        return jsonTextResult({
          ok: true,
          code: "ok",
          data: await bundledSkillResources.readReference(String(skillId), String(referenceId)),
        });
      } catch (error) {
        if (error instanceof WorkflowResourceError) {
          return jsonTextResult({
            ok: false,
            code: error.code,
            error: { message: error.message },
          });
        }
        throw error;
      }
    },
  );

  registerTool(
    "granoflow_gfmcp_prepare",
    "Create or repair the GFMCP custom tag and its app-localized task description template. Granoflow owns localization and idempotency.",
    { dryRun: z.boolean().default(true) },
    async ({ dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/gfmcp/prepare",
        body: {},
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_gfmcp_safe_sync",
    "Ask the Granoflow app to perform a safe pre-poll sync only when current authorization permits it. Defaults to dry-run and never guesses membership or key state.",
    { dryRun: z.boolean().default(true) },
    async ({ dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/sync/gfmcp-safe-run",
        body: {},
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_gfmcp_candidates",
    "List pending Granoflow tasks tagged GFMCP. The tag marks eligibility but does not grant authorization for privileged or external actions.",
    {},
    async () => apiTool({ path: "/v1/tasks?tag=custom_gfmcp" }),
  );

  registerTool(
    "granoflow_setup_status",
    "Inspect Granoflow MCP config and Local HTTP API health without printing secrets.",
    {},
    async () => jsonTextResult(await getSetupStatus()),
  );

  registerTool(
    "granoflow_setup_detect_local_api",
    "Probe a bounded localhost port list for Granoflow identity. This never scans all ports or writes config.",
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
    "Preview or write one user-confirmed MCP-owned non-secret Granoflow API URL or local port. Defaults to dry-run; writes are reread and verified immediately.",
    {
      apiBaseUrl: z.string().url().optional(),
      apiPort: z.number().int().min(1).max(65_535).optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ apiBaseUrl, apiPort, dryRun }) =>
      jsonTextResult(
        await writeSetupConfig({
          apiBaseUrl: typeof apiBaseUrl === "string" ? apiBaseUrl : undefined,
          apiPort: typeof apiPort === "number" ? apiPort : undefined,
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
    "granoflow_review_card_draft_schema",
    "Fetch the Granoflow review card draft template and field schema from the running app. Call before creating reviewCardDrafts so card types, note fields, layouts, and fallbacks match app import rules.",
    {},
    async () => apiTool({ path: "/v1/ai-agent/review-card-drafts/schema" }),
  );

  registerTool(
    "granoflow_review_card_similar",
    "Find potentially similar Granoflow review cards. The app prefers vector search and falls back to agent-supplied keywords; the agent must prefilter results before showing them to the user.",
    {
      summary: z.string().min(1).max(500),
      keywords: z.array(z.string().min(1)).max(12).optional(),
      limit: z.number().int().min(1).max(20).default(8),
    },
    async ({ summary, keywords, limit }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards/similar",
        body: compactRecord({ summary, keywords, limit: limit ?? 8 }),
      }),
  );

  registerTool(
    "granoflow_review_card_authoring_preview",
    "Preview controlled review-card creation, existing-card linking, or field-level updates for an existing project or inbox task. This endpoint performs no writes and returns a confirmation token plus shared-note impact.",
    {
      taskId: z.string().min(1),
      operations: z.array(z.record(z.string(), z.unknown())).min(1),
    },
    async ({ taskId, operations }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards/authoring/preview",
        body: { taskId, operations },
      }),
  );

  registerTool(
    "granoflow_review_card_authoring_apply",
    "Apply only user-approved operations from a current review-card authoring preview. Returns app-owned readback; never call without explicit approval of the previewed operations.",
    {
      previewToken: z.string().min(1),
      previewHash: z.string().min(1),
      approvedOperationIds: z.array(z.string().min(1)).min(1),
      approvedFieldsByOperation: z.record(z.string(), z.array(z.string().min(1)).min(1)).optional(),
    },
    async ({ previewToken, previewHash, approvedOperationIds, approvedFieldsByOperation }) =>
      apiTool({
        method: "POST",
        path: "/v1/ai-agent/review-cards/authoring/apply",
        body: compactRecord({
          previewToken,
          previewHash,
          approvedOperationIds,
          approvedFieldsByOperation,
        }),
      }),
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
    "granoflow_project_context_attachments_ensure",
    "Ensure Granoflow canonical project context YAML attachments exist: project_snapshot.yaml and project_rules.yaml. Defaults to dry-run.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews missing attachments without writing."),
    },
    async ({ projectId, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/ensure",
        body: compactRecord({
          projectId,
          dryRun: dryRun !== false,
        }),
        dryRun: false,
      }),
  );

  registerTool(
    "granoflow_project_context_attachment_read",
    "Read a bounded section of project_snapshot.yaml or project_rules.yaml. Defaults to header, summary, and the smallest matching section; full read requires explicit intent.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      attachment: projectContextAttachmentSchema,
      section: z.string().min(1).optional(),
      query: z.string().min(1).optional(),
      intent: z
        .enum(["normal", "full_audit", "export", "migration", "rewrite", "full_read"])
        .default("normal"),
      allowFullRead: z.boolean().default(false),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the HTTP request without calling the app."),
    },
    async ({ projectId, attachment, section, query, intent, allowFullRead, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/read",
        body: compactRecord({
          projectId,
          attachment,
          section,
          query,
          intent: intent === "normal" ? undefined : intent,
          allowFullRead: allowFullRead === true,
        }),
        dryRun: dryRun === true,
      }),
  );

  registerTool(
    "granoflow_project_context_attachment_reconcile",
    "Check or reconcile project context YAML freshness. Low-risk factual snapshot deltas can reconcile; rules and wording conflicts return a proposal.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      attachment: projectContextAttachmentSchema,
      dryRun: z.boolean().default(true).describe("When true, previews reconcile without writing."),
    },
    async ({ projectId, attachment, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/reconcile",
        body: compactRecord({
          projectId,
          attachment,
          dryRun: dryRun !== false,
        }),
        dryRun: false,
      }),
  );

  registerTool(
    "granoflow_project_context_attachment_write",
    "Write a project context YAML attachment through app-owned safety gates. project_rules.yaml requires confirmation; secret/privacy risks fail closed.",
    {
      projectId: z.string().min(1).describe("Granoflow project id."),
      attachment: projectContextAttachmentSchema,
      section: z.string().min(1).optional(),
      content: z.string().min(1),
      confirmed: z
        .boolean()
        .default(false)
        .describe("Required for project_rules.yaml rule, wording, or decision-note changes."),
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, previews the HTTP request without calling the app."),
    },
    async ({ projectId, attachment, section, content, confirmed, dryRun }) =>
      projectContextAttachmentApiTool({
        method: "POST",
        path: "/v1/ai-agent/project-context-attachments/write",
        body: compactRecord({
          projectId,
          attachment,
          section,
          content,
          confirmed: confirmed === true,
        }),
        dryRun: dryRun === true,
      }),
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

  registerTool(
    "granoflow_tag_list",
    "List tags from the Granoflow local catalog.",
    {
      kind: z
        .string()
        .optional()
        .describe("Optional tag kind filter forwarded to the Local HTTP API."),
    },
    async ({ kind }) => {
      const path =
        typeof kind === "string" && kind.trim()
          ? `/v1/tags?kind=${encodeURIComponent(kind.trim())}`
          : "/v1/tags";
      return apiTool({ path });
    },
  );

  registerTool(
    "granoflow_tag_create",
    "Create a custom Granoflow tag. Defaults to dry-run.",
    {
      label: z.string().min(1),
      slug: z.string().min(1).optional(),
      iconKey: z.string().optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ label, slug, iconKey, dryRun }) =>
      apiTool({
        method: "POST",
        path: "/v1/tags",
        body: compactRecord({ label, slug, iconKey }),
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_source_tags_ensure",
    "Ensure the AI and 人工 completion source tags exist in Granoflow. Idempotent: reuses existing tags matched by slug or label.",
    {
      dryRun: z
        .boolean()
        .default(false)
        .describe("When true, only inspects the current catalog without creating missing tags."),
    },
    async ({ dryRun }) => {
      if (dryRun !== false) {
        const listResult = await requestGranoflowApi({ method: "GET", path: "/v1/tags" });
        return jsonTextResult({
          ...listResult,
          code: "dry_run",
          data: {
            previewMode: "catalog_inspection_only",
            tags: extractItems(listResult.data),
            expected: {
              ai: { label: "AI", slug: "custom_ai" },
              human: { label: "人工", slug: "custom_u4eba5de5" },
            },
          },
        });
      }
      return jsonTextResult(await ensureSourceTags());
    },
  );

  registerTool(
    "granoflow_task_list",
    "List tasks from Granoflow. Optionally filter by tag slug.",
    {
      tag: z.string().min(1).optional().describe("Return only tasks containing this tag slug."),
    },
    async ({ tag }) =>
      apiTool({
        path:
          typeof tag === "string" && tag.trim()
            ? `/v1/tasks?tag=${encodeURIComponent(tag.trim())}`
            : "/v1/tasks",
      }),
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
    "Create a Granoflow task from a JSON payload. Tags not in the local catalog are skipped automatically. Optional completionSource attaches AI/人工 source tags for completed-work capture.",
    {
      input: jsonInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ input, dryRun }) => {
      const record = isObject(input) ? { ...input } : {};
      const completionSource = parseCompletionSource(record.completionSource);
      delete record.completionSource;
      return apiToolForTaskWrite(
        {
          method: "POST",
          path: "/v1/tasks",
          dryRun: dryRun !== false,
        },
        record,
        completionSource,
      );
    },
  );

  registerTool(
    "granoflow_task_create_structured",
    "Create a Granoflow task with common structured fields. Derive startedAt from the earliest task-related user question in the current agent thread before writing. Tags not in the local catalog are skipped automatically. Defaults to dry-run.",
    {
      title: z.string().min(1),
      description: z.string().optional(),
      startedAt: z
        .string()
        .optional()
        .describe("Earliest task-related user question time derived from the agent thread."),
      dueAt: z.string().optional(),
      remindAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      tags: z.array(z.string().min(1)).optional(),
      completionSource: completionSourceSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({
      title,
      description,
      startedAt,
      dueAt,
      remindAt,
      projectId,
      milestoneId,
      status,
      tags,
      completionSource,
      dryRun,
    }) =>
      apiToolForTaskWrite(
        {
          method: "POST",
          path: "/v1/tasks",
          dryRun: dryRun !== false,
        },
        compactRecord({
          title,
          description,
          startedAt,
          dueAt,
          remindAt,
          projectId,
          milestoneId,
          status,
          tags,
        }),
        parseCompletionSource(completionSource),
      ),
  );

  registerTool(
    "granoflow_task_update",
    "Update a Granoflow task through the Local HTTP API. Tags not in the local catalog are skipped automatically.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      input: jsonInputSchema,
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ taskId, input, dryRun }) =>
      apiToolForTaskWrite(
        {
          method: "PATCH",
          path: `/v1/tasks/${String(taskId)}`,
          dryRun: dryRun !== false,
        },
        input as Record<string, unknown>,
      ),
  );

  registerTool(
    "granoflow_task_update_structured",
    "Update a Granoflow task with common structured fields. Defaults to dry-run.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      title: z.string().min(1).optional(),
      description: z.string().optional(),
      taskReview: z.string().optional(),
      dueAt: z.string().optional(),
      remindAt: z.string().optional(),
      projectId: z.string().min(1).optional(),
      milestoneId: z.string().min(1).optional(),
      status: resourceStatusSchema,
      expectedUpdatedAt: z.string().datetime().optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({
      taskId,
      title,
      description,
      taskReview,
      dueAt,
      remindAt,
      projectId,
      milestoneId,
      status,
      expectedUpdatedAt,
      dryRun,
    }) =>
      apiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}`,
        body: compactRecord({
          title,
          description,
          taskReview,
          dueAt,
          remindAt,
          projectId,
          milestoneId,
          status,
          expectedUpdatedAt,
        }),
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_task_review_update",
    "Safely write a confirmed structured Task Review to any task, including completed inbox tasks, using the latest task revision. Review cards and context promotion remain separate controlled steps.",
    {
      taskId: z.string().min(1),
      taskReview: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, taskReview, expectedUpdatedAt, dryRun }) => {
      const review = String(taskReview);
      const markers = validateManagedBlock(review, TASK_REVIEW_START, TASK_REVIEW_END);
      const revisionPresent = /\breview_revision:\s*[1-9]\d*\b/.test(review);
      const operationPresent = /\breview_operation_id:\s*\S+/.test(review);
      if (!markers.ok || !revisionPresent || !operationPresent) {
        return jsonTextResult({
          ok: false,
          code: "task_review_markers_invalid",
          data: {
            reason: !markers.ok
              ? markers.reason
              : !revisionPresent
                ? "review_revision_missing"
                : "review_operation_id_missing",
          },
          error: {
            message:
              "Structured Task Review requires one valid marker pair, a positive review_revision, and review_operation_id.",
          },
        });
      }
      return apiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}`,
        body: { taskReview: review, expectedUpdatedAt },
        dryRun: dryRun !== false,
      });
    },
  );

  registerTool(
    "granoflow_task_completion_summary_update",
    "Safely update a task description that already preserves all user text and contains exactly one Task Completion Summary managed block.",
    {
      taskId: z.string().min(1),
      description: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, description, expectedUpdatedAt, dryRun }) => {
      const nextDescription = String(description);
      const markers = validateManagedBlock(
        nextDescription,
        TASK_COMPLETION_SUMMARY_START,
        TASK_COMPLETION_SUMMARY_END,
      );
      if (!markers.ok) {
        return jsonTextResult({
          ok: false,
          code: "task_completion_summary_markers_invalid",
          data: { reason: markers.reason },
          error: { message: "Task Completion Summary markers are not safe to update." },
        });
      }
      return apiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}`,
        body: { description: nextDescription, expectedUpdatedAt },
        dryRun: dryRun !== false,
      });
    },
  );

  registerTool(
    "granoflow_task_complete",
    "Low-level node-less compatibility endpoint. Never call it for a task with Work Document nodes; NodeService owns completion for node-backed tasks.",
    {
      taskId: z.string().min(1).describe("Granoflow task id."),
      input: jsonInputSchema.optional(),
      dryRun: z
        .boolean()
        .default(true)
        .describe("When true, previews the request without writing."),
    },
    async ({ taskId, input, dryRun }) =>
      jsonTextResult(
        await completeNodeLessTask({
          taskId: String(taskId),
          body: isObject(input) ? input : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );

  registerTool(
    "granoflow_task_attachment_list",
    "List attachments for a Granoflow task.",
    { taskId: z.string().min(1) },
    async ({ taskId }) => apiTool({ path: `/v1/tasks/${String(taskId)}/attachments` }),
  );

  registerTool(
    "granoflow_task_attachment_add_markdown",
    "Conditionally attach a versioned Task Work Document, legacy Task Analysis/Plan, or Task Delivery Markdown file and verify App-owned content/hash readback.",
    {
      taskId: z.string().min(1),
      filePath: z.string().min(1),
      idempotencyKey: z.string().min(1),
      expectedTaskUpdatedAt: z.string().datetime(),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, filePath, idempotencyKey, expectedTaskUpdatedAt, dryRun }) => {
      let file: string;
      try {
        file = validatedWorkflowMarkdownPath(String(filePath));
      } catch (error) {
        return jsonTextResult({
          ok: false,
          code: "unsafe_attachment_path",
          error: { message: error instanceof Error ? error.message : String(error) },
        });
      }
      return jsonTextResult(
        await addTaskWorkflowAttachment({
          taskId: String(taskId),
          filePath: file,
          idempotencyKey: String(idempotencyKey),
          expectedTaskUpdatedAt: String(expectedTaskUpdatedAt),
          dryRun: dryRun !== false,
        }),
      );
    },
  );

  registerTool(
    "granoflow_task_attachment_read_markdown",
    "Read a bounded Task Work Document, legacy Task Analysis/Plan, or Task Delivery Markdown attachment with its App-owned SHA-256 for verification.",
    {
      taskId: z.string().min(1),
      attachmentId: z.string().min(1),
    },
    async ({ taskId, attachmentId }) =>
      apiTool({
        path: `/v1/tasks/${String(taskId)}/attachments/${String(attachmentId)}`,
      }),
  );

  registerTool(
    "granoflow_task_attachment_delete",
    "Delete a task attachment after explicit confirmation.",
    {
      taskId: z.string().min(1),
      attachmentId: z.string().min(1),
      confirmed: z.literal(true),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, attachmentId, dryRun }) =>
      apiTool({
        method: "DELETE",
        path: `/v1/tasks/${String(taskId)}/attachments/${String(attachmentId)}`,
        body: { confirmed: true },
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_task_node_list",
    "Read the latest Granoflow task nodes before planning, executing, or reconciling cross-device changes.",
    { taskId: z.string().min(1) },
    async ({ taskId }) => taskNodeApiTool({ path: `/v1/tasks/${String(taskId)}/nodes` }),
  );

  registerTool(
    "granoflow_task_node_batch_create",
    "Atomically create an ordered, idempotent task node batch through the Granoflow NodeService.",
    {
      taskId: z.string().min(1),
      idempotencyKey: z.string().min(1),
      expectedTaskUpdatedAt: z.string().datetime(),
      nodes: z.array(taskNodeCreateSchema).min(1).max(50),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, idempotencyKey, expectedTaskUpdatedAt, nodes, dryRun }) =>
      taskNodeApiTool({
        method: "POST",
        path: `/v1/tasks/${String(taskId)}/nodes`,
        body: { idempotencyKey, expectedTaskUpdatedAt, nodes },
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_task_node_update",
    "Update a task node title or apply pending/finished status with optimistic concurrency.",
    {
      taskId: z.string().min(1),
      nodeId: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      title: z.string().min(1).optional(),
      status: taskNodeStatusSchema.optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, nodeId, expectedUpdatedAt, title, status, dryRun }) => {
      if (status === "finished" && dryRun === false) {
        const documentGate = await requireTaskAnalysisPlanAttachment(String(taskId));
        if (!documentGate.ok) return jsonTextResult(documentGate);
      }
      return taskNodeApiTool({
        method: "PATCH",
        path: `/v1/tasks/${String(taskId)}/nodes/${String(nodeId)}`,
        body: compactRecord({ expectedUpdatedAt, title, status }),
        dryRun: dryRun !== false,
      });
    },
  );

  registerTool(
    "granoflow_task_node_delete",
    "Soft-delete a task node tree after a confirmed Work Document amendment and explicit confirmation.",
    {
      taskId: z.string().min(1),
      nodeId: z.string().min(1),
      expectedUpdatedAt: z.string().datetime(),
      confirmed: z.literal(true),
      dryRun: z.boolean().default(true),
    },
    async ({ taskId, nodeId, expectedUpdatedAt, dryRun }) =>
      taskNodeApiTool({
        method: "DELETE",
        path: `/v1/tasks/${String(taskId)}/nodes/${String(nodeId)}`,
        body: { expectedUpdatedAt, confirmed: true },
        dryRun: dryRun !== false,
      }),
  );

  registerTool(
    "granoflow_task_finish",
    "Finish a node-less compatibility task after its required Delivery gate and verify status=done. Derive endedAt from the confirmed completion time in the current agent thread; if startedAt is missing, recover it from the thread or mark an evidence-based estimate. Do not use for node-backed tasks. taskReview/reviewCardDrafts remain legacy explicit-inline compatibility only; deferred Review is the default.",
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
      completionSource: completionSourceSchema.describe(
        "Defaults to ai when an agent finishes the task. Use human for clearly human-completed work, or unknown to skip source tags.",
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
      completionSource,
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
          completionSource: parseCompletionSource(completionSource),
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
