import { createHash } from "node:crypto";
import { requestGranoflowApi } from "./api.js";

export type TaskAuthoringQualityValidator = (
  title: unknown,
  description: unknown,
  evidence: unknown,
) => Array<{ field: string; reason: string }>;

export type DescriptionImpactOperation =
  "update" | "review" | "completion" | "completion_summary" | "historical" | "node_completion";

export type DescriptionImpactWriteOptions = {
  taskId: string;
  review: unknown;
  operation: DescriptionImpactOperation;
  managedBlockMarkers?: { start: string; end: string };
  syntheticBody?: Record<string, unknown>;
  verifyFields?: boolean;
};

export type DescriptionImpactGate = {
  ok: true;
  currentTask: Record<string, unknown>;
  changedFields: string[];
  currentDescriptionSha256: string;
  expectedDescriptionSha256: string;
  review: Record<string, unknown>;
  operation: DescriptionImpactOperation;
};

type DescriptionImpactFailure = {
  ok: false;
  code: string;
  data: Record<string, unknown>;
  error: { message: string };
  runtime?: unknown;
};

const OPERATIONAL_FIELDS = new Set(["dueAt", "remindAt", "status", "tags"]);
const PLACEMENT_FIELDS = new Set(["projectId", "milestoneId", "dueAt"]);
const KNOWN_UPDATE_FIELDS = new Set([
  "title",
  "description",
  "dueAt",
  "remindAt",
  "projectId",
  "milestoneId",
  "status",
  "tags",
  "taskReview",
]);
const REWRITE_REASONS = new Set([
  "semantic_change",
  "description_correction",
  "post_completion_revision",
]);
const VALID_REASONS = new Set([
  "operational_only",
  "review_only",
  "completion_only",
  "completion_summary_only",
  "historical_time_only",
  "node_completion_only",
  "placement_reviewed_no_semantic_change",
  "title_clarification_no_semantic_change",
  ...REWRITE_REASONS,
]);

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function fail(
  code: string,
  message: string,
  data: Record<string, unknown> = {},
  runtime?: unknown,
): DescriptionImpactFailure {
  return { ok: false, code, data, error: { message }, runtime };
}

function extractTask(value: unknown): Record<string, unknown> | null {
  if (!isObject(value)) return null;
  if (isObject(value.entity)) return value.entity;
  if (isObject(value.data)) {
    if (isObject(value.data.entity)) return value.data.entity;
    if (typeof value.data.id === "string") return value.data;
  }
  return typeof value.id === "string" ? value : null;
}

function stableEqual(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}

export function taskDescriptionSha256(description: unknown): string {
  const text = typeof description === "string" ? description : "";
  return createHash("sha256").update(text, "utf8").digest("hex");
}

function changedFields(
  currentTask: Record<string, unknown>,
  body: Record<string, unknown>,
): string[] {
  return Object.keys(body)
    .filter((field) => field !== "expectedUpdatedAt")
    .filter((field) => !stableEqual(currentTask[field], body[field]))
    .sort();
}

function only(fields: string[], allowed: Set<string>): boolean {
  return fields.length > 0 && fields.every((field) => allowed.has(field));
}

function removeManagedBlock(text: string, markers: { start: string; end: string }): string | null {
  const startIndex = text.indexOf(markers.start);
  const endIndex = text.indexOf(markers.end);
  if (startIndex < 0 || endIndex < startIndex) return text;
  if (
    text.indexOf(markers.start, startIndex + markers.start.length) >= 0 ||
    text.indexOf(markers.end, endIndex + markers.end.length) >= 0
  ) {
    return null;
  }
  return `${text.slice(0, startIndex)}${text.slice(endIndex + markers.end.length)}`;
}

function reasonMatches(
  operation: DescriptionImpactOperation,
  reason: unknown,
  fields: string[],
): boolean {
  if (typeof reason !== "string" || !VALID_REASONS.has(reason)) return false;
  if (operation === "review")
    return reason === "review_only" && only(fields, new Set(["taskReview"]));
  if (operation === "completion") return reason === "completion_only";
  if (operation === "completion_summary") return reason === "completion_summary_only";
  if (operation === "historical") return reason === "historical_time_only";
  if (operation === "node_completion") return reason === "node_completion_only";
  if (reason === "operational_only") return only(fields, OPERATIONAL_FIELDS);
  if (reason === "placement_reviewed_no_semantic_change") return only(fields, PLACEMENT_FIELDS);
  if (reason === "title_clarification_no_semantic_change") {
    return fields.length === 1 && fields[0] === "title";
  }
  return REWRITE_REASONS.has(reason);
}

function validateRewrite(
  currentTask: Record<string, unknown>,
  body: Record<string, unknown>,
  review: Record<string, unknown>,
  qualityValidator: TaskAuthoringQualityValidator,
): DescriptionImpactFailure | null {
  const description = body.description;
  const title = body.title ?? currentTask.title;
  if (typeof description !== "string" || description.trim().length === 0) {
    return fail(
      "task_description_rewrite_required",
      "A semantic task update must include the complete next description.",
    );
  }
  if (review.fiveDimensionsReviewed !== true) {
    return fail(
      "task_description_quality_failed",
      "Description rewrites require fiveDimensionsReviewed=true.",
    );
  }
  const issues = qualityValidator(title, description, review.authoringEvidence);
  if (issues.length > 0) {
    return fail(
      "task_description_quality_failed",
      "The rewritten task description failed the shared authoring quality gate.",
      { issues },
    );
  }
  if (
    ["semantic_change", "post_completion_revision"].includes(String(review.reasonCode)) &&
    (!Array.isArray(review.writebackRefs) || review.writebackRefs.length === 0)
  ) {
    return fail(
      "task_description_rewrite_required",
      "Semantic and post-completion rewrites require durable writebackRefs.",
    );
  }
  return null;
}

function validateUnchangedTitle(
  currentTask: Record<string, unknown>,
  body: Record<string, unknown>,
  review: Record<string, unknown>,
  qualityValidator: TaskAuthoringQualityValidator,
): DescriptionImpactFailure | null {
  if (review.reasonCode !== "title_clarification_no_semantic_change") return null;
  if (review.fiveDimensionsReviewed !== true) {
    return fail(
      "task_description_quality_failed",
      "Title clarification requires a fresh five-dimension review.",
    );
  }
  const issues = qualityValidator(body.title, currentTask.description, review.authoringEvidence);
  return issues.length === 0
    ? null
    : fail(
        "task_description_quality_failed",
        "The new title and existing description failed the quality gate.",
        { issues },
      );
}

function validateManagedSummary(
  currentTask: Record<string, unknown>,
  body: Record<string, unknown>,
  markers: { start: string; end: string } | undefined,
): DescriptionImpactFailure | null {
  if (!markers || typeof body.description !== "string") {
    return fail(
      "task_description_rewrite_required",
      "Completion Summary updates require the complete managed description.",
    );
  }
  const current = removeManagedBlock(
    typeof currentTask.description === "string" ? currentTask.description : "",
    markers,
  );
  const next = removeManagedBlock(body.description, markers);
  return current !== null && next !== null && current === next
    ? null
    : fail(
        "task_description_post_completion_overwrite_forbidden",
        "Completion Summary updates must preserve all text outside the managed block.",
      );
}

function validateReviewAndChange(
  currentTask: Record<string, unknown>,
  body: Record<string, unknown>,
  review: Record<string, unknown>,
  operation: DescriptionImpactOperation,
  fields: string[],
  markers: { start: string; end: string } | undefined,
  qualityValidator: TaskAuthoringQualityValidator,
): DescriptionImpactFailure | null {
  if (
    !["unchanged", "rewrite"].includes(String(review.decision)) ||
    !reasonMatches(operation, review.reasonCode, fields) ||
    typeof review.rationale !== "string" ||
    review.rationale.trim().length === 0
  ) {
    return fail(
      "task_description_impact_review_required",
      "descriptionImpactReview does not match the actual operation and changed fields.",
      { changedFields: fields },
    );
  }
  if (
    operation === "update" &&
    fields.some((field) => !KNOWN_UPDATE_FIELDS.has(field)) &&
    review.decision !== "rewrite"
  ) {
    return fail(
      "task_description_rewrite_required",
      "Unknown task fields require an explicit semantic rewrite.",
      { changedFields: fields },
    );
  }
  if (operation === "completion_summary") {
    return validateManagedSummary(currentTask, body, markers);
  }
  if (review.decision === "rewrite") {
    const rewriteFailure = validateRewrite(currentTask, body, review, qualityValidator);
    if (rewriteFailure) return rewriteFailure;
  } else if (fields.includes("description")) {
    return fail(
      "task_description_rewrite_required",
      "A changed description requires decision=rewrite.",
    );
  }
  const titleFailure = validateUnchangedTitle(currentTask, body, review, qualityValidator);
  if (titleFailure) return titleFailure;
  if (
    currentTask.status === "done" &&
    fields.includes("description") &&
    review.reasonCode !== "post_completion_revision"
  ) {
    return fail(
      "task_description_post_completion_overwrite_forbidden",
      "Completed task descriptions require a post-completion revision.",
    );
  }
  return null;
}

export async function reviewTaskDescriptionImpact(
  input: DescriptionImpactWriteOptions,
  body: Record<string, unknown>,
  qualityValidator: TaskAuthoringQualityValidator,
): Promise<DescriptionImpactGate | DescriptionImpactFailure> {
  if (!isObject(input.review)) {
    return fail(
      "task_description_impact_review_required",
      "Every task update requires descriptionImpactReview.",
    );
  }
  const review = input.review;
  const read = await requestGranoflowApi({ path: `/v1/tasks/${input.taskId}` });
  if (!read.ok) {
    return fail(
      "task_description_impact_review_required",
      "The current task could not be read before its description impact review.",
      {},
      read.runtime,
    );
  }
  const currentTask = extractTask(read.data);
  if (!currentTask) {
    return fail(
      "task_description_impact_review_required",
      "The current task readback did not contain an entity.",
      {},
      read.runtime,
    );
  }
  const currentSha = taskDescriptionSha256(currentTask.description);
  if (
    review.reviewedTaskUpdatedAt !== currentTask.updatedAt ||
    review.reviewedDescriptionSha256 !== currentSha
  ) {
    return fail(
      "task_description_review_digest_mismatch",
      "The reviewed task revision or description SHA is stale.",
      {
        currentUpdatedAt: currentTask.updatedAt,
        currentDescriptionSha256: currentSha,
      },
      read.runtime,
    );
  }
  const effectiveBody = input.syntheticBody ?? body;
  const fields = changedFields(currentTask, effectiveBody);
  const validationFailure = validateReviewAndChange(
    currentTask,
    effectiveBody,
    review,
    input.operation,
    fields,
    input.managedBlockMarkers,
    qualityValidator,
  );
  if (validationFailure) return validationFailure;
  return {
    ok: true,
    currentTask,
    changedFields: fields,
    currentDescriptionSha256: currentSha,
    expectedDescriptionSha256: taskDescriptionSha256(
      effectiveBody.description ?? currentTask.description,
    ),
    review,
    operation: input.operation,
  };
}

export async function verifyTaskDescriptionImpact(
  taskId: string,
  gate: DescriptionImpactGate,
  body: Record<string, unknown>,
  verifyFields = true,
): Promise<{ ok: true; data: Record<string, unknown> } | DescriptionImpactFailure> {
  const readback = await requestGranoflowApi({ path: `/v1/tasks/${taskId}` });
  if (!readback.ok) {
    return fail(
      "task_description_readback_mismatch",
      "Task update succeeded but readback failed.",
      {},
      readback.runtime,
    );
  }
  const task = extractTask(readback.data);
  const actualSha = taskDescriptionSha256(task?.description);
  const fieldsMatch =
    task !== null &&
    (!verifyFields || gate.changedFields.every((field) => stableEqual(task[field], body[field])));
  if (!task || actualSha !== gate.expectedDescriptionSha256 || !fieldsMatch) {
    return fail(
      "task_description_readback_mismatch",
      "Task readback does not match the reviewed update.",
      {
        changedFields: gate.changedFields,
        expectedDescriptionSha256: gate.expectedDescriptionSha256,
      },
      readback.runtime,
    );
  }
  return {
    ok: true,
    data: {
      changedFields: gate.changedFields,
      decision: gate.review.decision,
      reasonCode: gate.review.reasonCode,
      descriptionSha256: actualSha,
      readbackStatus: "verified",
    },
  };
}
