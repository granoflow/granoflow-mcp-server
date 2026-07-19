import { requestGranoflowApi, type ApiRequestOptions, type ApiResult } from "./api.js";
import {
  applyCompletionSourceToBody,
  completionSourceTagSlug,
  ensureSourceTags,
  mergeTagSlugs,
  readSourceTagCatalog,
  type CompletionSource,
} from "./source-tags.js";
import { compactRecord, isObject, jsonTextResult } from "./tool-runtime-core.js";
import type { TaskAuthoringQualityIssue } from "./tool-runtime-core.js";
import type { GranoflowRecord } from "./tools.js";

export const TASK_AUTHORING_PLACEHOLDERS = new Set([
  "none",
  "n/a",
  "na",
  "无",
  "没有",
  "不适用",
  "待分析",
  "待确认",
]);

export function validateTaskAuthoringQuality(
  title: unknown,
  description: unknown,
  evidence: unknown,
): TaskAuthoringQualityIssue[] {
  const issues: TaskAuthoringQualityIssue[] = [];
  const normalizedTitle = typeof title === "string" ? title.trim() : "";
  const normalizedDescription = typeof description === "string" ? description.trim() : "";
  const evidenceRecord = isObject(evidence) ? evidence : {};

  if (!normalizedTitle) issues.push({ field: "title", reason: "missing" });
  if (!normalizedDescription) issues.push({ field: "description", reason: "missing" });
  if (evidenceRecord.titleIntent !== "action_or_outcome") {
    issues.push({ field: "authoringEvidence.titleIntent", reason: "unsupported_value" });
  }
  if (evidenceRecord.plainLanguageReviewed !== true) {
    issues.push({
      field: "authoringEvidence.plainLanguageReviewed",
      reason: "must_be_true",
    });
  }

  const excerpts = [
    ["authoringEvidence.analogyExcerpt", evidenceRecord.analogyExcerpt],
    ["authoringEvidence.exampleExcerpt", evidenceRecord.exampleExcerpt],
  ] as const;
  const validExcerpts = new Map<string, string>();
  for (const [field, value] of excerpts) {
    const excerpt = typeof value === "string" ? value.trim() : "";
    if (!excerpt) {
      issues.push({ field, reason: "missing" });
    } else if (TASK_AUTHORING_PLACEHOLDERS.has(excerpt.toLowerCase())) {
      issues.push({ field, reason: "placeholder" });
    } else if (!normalizedDescription.includes(excerpt)) {
      issues.push({ field, reason: "not_in_description" });
    } else {
      validExcerpts.set(field, excerpt);
    }
  }
  const analogyExcerpt = validExcerpts.get("authoringEvidence.analogyExcerpt");
  const exampleExcerpt = validExcerpts.get("authoringEvidence.exampleExcerpt");
  if (analogyExcerpt !== undefined && analogyExcerpt === exampleExcerpt) {
    issues.push({ field: "authoringEvidence.exampleExcerpt", reason: "must_differ" });
  }
  return issues;
}

export function taskAuthoringQualityFailure(
  title: unknown,
  description: unknown,
  evidence: unknown,
) {
  const issues = validateTaskAuthoringQuality(title, description, evidence);
  if (issues.length === 0) return null;
  return jsonTextResult({
    ok: false,
    code: "task_authoring_quality_failed",
    data: { issues },
    error: {
      message:
        "AI and automation task creation requires an action/outcome title, a plain-language description, a real analogy, and a concrete example.",
    },
  });
}

export const ORDINARY_TASK_HISTORICAL_FIELDS = [
  "createdAt",
  "updatedAt",
  "startedAt",
  "endedAt",
  "deletedAt",
] as const;

export function ordinaryTaskWriteFailure(
  record: Record<string, unknown>,
  operation: "create" | "update",
) {
  const unsupportedFields = ORDINARY_TASK_HISTORICAL_FIELDS.filter((field) =>
    Object.prototype.hasOwnProperty.call(record, field),
  );
  if (unsupportedFields.length > 0) {
    return jsonTextResult({
      ok: false,
      code: "historical_fields_not_supported",
      data: {
        operation,
        unsupportedFields,
        currentTaskFlow:
          operation === "create"
            ? "Create the task as pending without historical fields. After Analysis/Plan readiness and execution authorization, update status to doing; the App records startedAt."
            : "For a current task, use status actions such as status=doing; the App owns startedAt/endedAt side effects.",
        historicalCorrectionTool: "granoflow_task_history_mutate",
      },
      error: {
        message:
          "Ordinary task writes do not accept historical physical fields. Do not retry the same write against the App.",
      },
    });
  }
  if (operation === "create" && record.status !== undefined && record.status !== "pending") {
    return jsonTextResult({
      ok: false,
      code: "task_creation_must_start_pending",
      data: {
        requestedStatus: record.status,
        requiredStatus: "pending",
        nextAction:
          "Create the task as pending. When execution actually begins after Analysis/Plan readiness and authorization, update it to status=doing; the App records startedAt.",
      },
      error: { message: "Ordinary current-task creation must start in pending state." },
    });
  }
  return null;
}

export function unwrapApiData(value: unknown): unknown {
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

export function extractItems(value: unknown): GranoflowRecord[] {
  const data = unwrapApiData(value);
  if (isObject(data) && Array.isArray(data.items)) {
    return data.items.filter(isObject);
  }
  return [];
}

export function localDateKey(date: Date): string {
  const year = String(date.getFullYear()).padStart(4, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function validDateKey(value: unknown): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (!match) {
    return null;
  }
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  const key = `${match[1]}-${match[2]}-${match[3]}`;
  return localDateKey(date) === key ? key : null;
}

export async function defaultMilestoneDueAt(
  projectId: string,
  now = new Date(),
): Promise<{ dueAt?: string; error?: ApiResult }> {
  const milestonesResult = await requestGranoflowApi({
    method: "GET",
    path: "/v1/milestones",
  });
  if (!milestonesResult.ok) {
    return { error: milestonesResult };
  }

  const candidate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const daysUntilNextSaturday = (6 - candidate.getDay() + 7) % 7 || 7;
  candidate.setDate(candidate.getDate() + daysUntilNextSaturday);

  const latestProjectDueDate = extractItems(milestonesResult)
    .filter((milestone) => milestone.projectId === projectId)
    .map((milestone) => validDateKey(milestone.dueAt))
    .filter((date): date is string => date !== null)
    .sort()
    .at(-1);

  while (latestProjectDueDate && localDateKey(candidate) <= latestProjectDueDate) {
    candidate.setDate(candidate.getDate() + 7);
  }
  return { dueAt: `${localDateKey(candidate)}T23:59:59.000` };
}

type TagFilterNotice = {
  acceptedTags: string[];
  skippedTags: Array<{ slug: string; reason: "unknown_tag" }>;
  catalogUnavailable?: boolean;
};

export function normalizeRequestedTags(tags: unknown): string[] {
  if (!Array.isArray(tags)) {
    return [];
  }
  return tags
    .map((tag) => (typeof tag === "string" ? tag.trim() : String(tag).trim()))
    .filter(Boolean);
}

export async function fetchKnownTagSlugs(): Promise<{
  slugs: Set<string>;
  catalogUnavailable: boolean;
}> {
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

export async function filterTagsForTaskWrite(tags: unknown): Promise<{
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

export function withTagFilterMetadata(result: ApiResult, tagFilter: TagFilterNotice): ApiResult {
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

export async function applyTaskBodyTagFilter(body: Record<string, unknown>): Promise<{
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

export async function apiToolForTaskWrite(
  options: ApiRequestOptions,
  body: Record<string, unknown>,
  completionSource?: CompletionSource,
) {
  const withSource = await applyCompletionSourceToBody(body, completionSource);
  const { body: filteredBody, tagFilter } = await applyTaskBodyTagFilter(withSource);
  const result = await requestGranoflowApi({ ...options, body: filteredBody });
  return jsonTextResult(tagFilter ? withTagFilterMetadata(result, tagFilter) : result);
}

export function parseCompletionSource(value: unknown): CompletionSource | undefined {
  if (value === "ai" || value === "human" || value === "unknown") {
    return value;
  }
  return undefined;
}

export function extractTaskEntity(value: unknown): GranoflowRecord | null {
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

export async function patchTaskCompletionSourceTag(
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

export function compactResource(record: GranoflowRecord): Record<string, unknown> {
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
