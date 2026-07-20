/* eslint-disable max-lines */
import { createHash } from "node:crypto";
import { readFileSync, realpathSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { extname, isAbsolute, relative, resolve } from "node:path";

import {
  maybeCreateDailyReviewSuggestion,
  type MonthlyReviewSuggestion,
  type WeeklyReviewSuggestion,
} from "./config.js";
import { requestGranoflowApi, type ApiRequestOptions } from "./api.js";
import { z } from "zod";
import { extractItems } from "./tools.js";

export const AGENT_WORKFLOW_SKILL_URL = new URL(
  "../skills/granoflow-agent-workflow/SKILL.md",
  import.meta.url,
);
export const DAILY_REVIEW_SKILL_URL = new URL(
  "../skills/granoflow-daily-review/SKILL.md",
  import.meta.url,
);
export const FIRST_RUN_IMPORT_SKILL_URL = new URL(
  "../skills/granoflow-first-run-import/SKILL.md",
  import.meta.url,
);
export const REVIEW_CARD_DRAFT_SKILL_URL = new URL(
  "../skills/granoflow-review-card-draft/SKILL.md",
  import.meta.url,
);
export const GFMCP_RUNNER_SKILL_URL = new URL(
  "../skills/granoflow-gfmcp-runner/SKILL.md",
  import.meta.url,
);
export const DELEGATED_AUTHORIZATION_SKILL_URL = new URL(
  "../skills/granoflow-delegated-authorization/SKILL.md",
  import.meta.url,
);
export const TASK_ORCHESTRATOR_SKILL_URL = new URL(
  "../skills/granoflow-task-orchestrator/SKILL.md",
  import.meta.url,
);
export const MILESTONE_WORKFLOW_SKILL_URL = new URL(
  "../skills/granoflow-milestone-workflow/SKILL.md",
  import.meta.url,
);
export const MILESTONE_COORDINATION_SKILL_URL = new URL(
  "../skills/granoflow-milestone-coordination/SKILL.md",
  import.meta.url,
);
export const TASK_AUTHORING_SKILL_URL = new URL(
  "../skills/granoflow-task-authoring/SKILL.md",
  import.meta.url,
);
export const PORTFOLIO_ORCHESTRATOR_SKILL_URL = new URL(
  "../skills/granoflow-portfolio-orchestrator/SKILL.md",
  import.meta.url,
);
export const PERSISTENT_MILESTONE_RUNNER_SKILL_URL = new URL(
  "../skills/granoflow-persistent-milestone-runner/SKILL.md",
  import.meta.url,
);
export const PROJECT_DEFINITION_SKILL_URL = new URL(
  "../skills/granoflow-project-definition/SKILL.md",
  import.meta.url,
);
export const INTEGRATION_TEST_CAMPAIGN_SKILL_URL = new URL(
  "../skills/granoflow-integration-test-campaign/SKILL.md",
  import.meta.url,
);

export function compactRecord(record: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(record).filter(([, value]) => value !== undefined));
}

export function validateManagedBlock(
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

export function textResult(text: string) {
  return {
    content: [{ type: "text" as const, text }],
  };
}

export type ToolResult = ReturnType<typeof textResult>;
export type ToolRegistrar = (
  name: string,
  description: string,
  schema: Record<string, z.ZodTypeAny>,
  handler: (args: Record<string, unknown>) => Promise<ToolResult>,
) => void;

export function jsonTextResult(value: unknown) {
  return textResult(JSON.stringify(value, null, 2));
}

export function readAgentWorkflowSkill(): string {
  return readFileSync(AGENT_WORKFLOW_SKILL_URL, "utf8");
}

export function readDailyReviewSkill(): string {
  return readFileSync(DAILY_REVIEW_SKILL_URL, "utf8");
}

export function readFirstRunImportSkill(): string {
  return readFileSync(FIRST_RUN_IMPORT_SKILL_URL, "utf8");
}

export function readReviewCardDraftSkill(): string {
  return readFileSync(REVIEW_CARD_DRAFT_SKILL_URL, "utf8");
}

export function readGfmcpRunnerSkill(): string {
  return readFileSync(GFMCP_RUNNER_SKILL_URL, "utf8");
}

export function readDelegatedAuthorizationSkill(): string {
  return readFileSync(DELEGATED_AUTHORIZATION_SKILL_URL, "utf8");
}

export function readTaskOrchestratorSkill(): string {
  return readFileSync(TASK_ORCHESTRATOR_SKILL_URL, "utf8");
}

export function readMilestoneWorkflowSkill(): string {
  return readFileSync(MILESTONE_WORKFLOW_SKILL_URL, "utf8");
}

export function readMilestoneCoordinationSkill(): string {
  return readFileSync(MILESTONE_COORDINATION_SKILL_URL, "utf8");
}

export function readTaskAuthoringSkill(): string {
  return readFileSync(TASK_AUTHORING_SKILL_URL, "utf8");
}

export function readPortfolioOrchestratorSkill(): string {
  return readFileSync(PORTFOLIO_ORCHESTRATOR_SKILL_URL, "utf8");
}

export function readPersistentMilestoneRunnerSkill(): string {
  return readFileSync(PERSISTENT_MILESTONE_RUNNER_SKILL_URL, "utf8");
}

export function readProjectDefinitionSkill(): string {
  return readFileSync(PROJECT_DEFINITION_SKILL_URL, "utf8");
}

export function readIntegrationTestCampaignSkill(): string {
  return readFileSync(INTEGRATION_TEST_CAMPAIGN_SKILL_URL, "utf8");
}

export function isWithin(root: string, target: string): boolean {
  const path = relative(root, target);
  return path === "" || (!path.startsWith("..") && !isAbsolute(path));
}

export function validatedWorkflowMarkdownPath(filePath: string): string {
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

export function validatedLogicalAttachmentPath(filePath: string, slot: string): string {
  const absolute = realpathSync(resolve(filePath));
  const roots = [realpathSync(process.cwd()), realpathSync(tmpdir())];
  const extension = extname(absolute).toLowerCase();
  const allowed =
    slot === "project_work"
      ? [".yaml", ".yml"]
      : slot === "ui_prototype"
        ? [".zip"]
        : slot === "acceptance_report"
          ? [".html"]
          : [".md"];
  if (!allowed.includes(extension) || !roots.some((root) => isWithin(root, absolute))) {
    throw new Error(
      `Logical attachment ${slot} must use ${allowed.join(" or ")} under the current workspace or system temp directory.`,
    );
  }
  if (!statSync(absolute).isFile()) {
    throw new Error("Logical attachment path must reference a regular file.");
  }
  return absolute;
}

export function validatedProjectDesignBaselinePath(filePath: string): string {
  if (!isAbsolute(filePath)) {
    throw new Error("Project design baseline path must be absolute.");
  }
  const absolute = realpathSync(filePath);
  const roots = [realpathSync(process.cwd()), realpathSync(tmpdir())];
  if (
    extname(absolute).toLowerCase() !== ".zip" ||
    !roots.some((root) => isWithin(root, absolute))
  ) {
    throw new Error(
      "Project design baseline must be a .zip file under the current workspace or system temp directory.",
    );
  }
  const stat = statSync(absolute);
  if (!stat.isFile()) {
    throw new Error("Project design baseline path must reference a regular file.");
  }
  if (stat.size > 32 * 1024 * 1024) {
    throw new Error("Project design baseline package must not exceed 32 MiB.");
  }
  return absolute;
}

export function validatedTaskPrototypePath(filePath: string): string {
  if (!isAbsolute(filePath)) {
    throw new Error("Task prototype path must be absolute.");
  }
  const absolute = realpathSync(filePath);
  const roots = [realpathSync(process.cwd()), realpathSync(tmpdir())];
  if (
    extname(absolute).toLowerCase() !== ".granoprototype" ||
    !roots.some((root) => isWithin(root, absolute))
  ) {
    throw new Error(
      "Task prototype must be a .granoprototype file under the current workspace or system temp directory.",
    );
  }
  const stat = statSync(absolute);
  if (!stat.isFile()) {
    throw new Error("Task prototype path must reference a regular file.");
  }
  if (stat.size > 32 * 1024 * 1024) {
    throw new Error("Task prototype package must not exceed 32 MiB.");
  }
  return absolute;
}

export function logicalAttachmentResource(entityType: string): string {
  return entityType;
}

export function logicalAttachmentPath(entityType: string, entityId: string): string {
  const resource =
    entityType === "project" ? "projects" : entityType === "milestone" ? "milestones" : "tasks";
  return `/v1/${resource}/${entityId}/attachments`;
}

export function supportsTaskNodeWorkflow(payload: unknown): boolean {
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

export function supportsTaskWorkflowAttachmentReadback(payload: unknown): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const resources = isObject(data) && isObject(data.resources) ? data.resources : {};
  const task = Array.isArray(resources.task) ? resources.task : [];
  return ["attachment.conditional-add", "attachment.read-content-hash"].every((action) =>
    task.includes(action),
  );
}

export function supportsResourceActions(
  payload: unknown,
  resource: string,
  actions: readonly string[],
): boolean {
  const root = isObject(payload) && isObject(payload.data) ? payload.data : payload;
  const data = isObject(root) && isObject(root.data) ? root.data : root;
  const resources = isObject(data) && isObject(data.resources) ? data.resources : {};
  const advertised = Array.isArray(resources[resource]) ? resources[resource] : [];
  return actions.every((action) => advertised.includes(action));
}

export async function resourceCapabilityApiTool(
  resource: string,
  actions: readonly string[],
  options: ApiRequestOptions,
) {
  const capabilities = await requestGranoflowApi({ path: "/v1/capabilities" });
  if (!capabilities.ok || !supportsResourceActions(capabilities, resource, actions)) {
    return jsonTextResult({
      ok: false,
      code: "unsupported_capability",
      data: {
        resource,
        requiredActions: actions,
        endpoint: options.path,
      },
      error: {
        message: `The running Granoflow app does not advertise ${resource}: ${actions.join(", ")}.`,
      },
      runtime: capabilities.runtime,
    });
  }
  return apiTool(options);
}

export function extractEntity(value: unknown): Record<string, unknown> | null {
  if (!isObject(value)) return null;
  if (isObject(value.entity)) return value.entity;
  if (isObject(value.data)) return extractEntity(value.data);
  return null;
}

export async function addTaskWorkflowAttachment(input: {
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

export async function taskNodeApiTool(options: ApiRequestOptions) {
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

export async function requireTaskAnalysisPlanAttachment(taskId: string) {
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

export async function completeNodeLessTask(input: {
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

export function periodicReviewHasLog(value: unknown): boolean {
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

export async function checkPeriodicReviewSuggestion(
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

export async function withDailyReviewSuggestion(
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

export async function apiTool(options: ApiRequestOptions) {
  return jsonTextResult(await requestGranoflowApi(options));
}

export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export type TaskAuthoringQualityIssue = {
  field: string;
  reason: string;
};
