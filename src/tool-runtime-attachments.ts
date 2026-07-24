import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { TextDecoder } from "node:util";

import { requestGranoflowApi } from "./api.js";
import {
  extractEntity,
  isObject,
  supportsResourceActions,
  supportsTaskWorkflowAttachmentReadback,
} from "./tool-runtime-core.js";

type TaskWorkflowLogicalSlot =
  "task_work_execution" | "task_work_post_completion_revision" | "task_delivery";

export type TaskWorkflowAttachmentInput = {
  taskId: string;
  filePath: string;
  idempotencyKey: string;
  expectedTaskUpdatedAt: string;
  dryRun: boolean;
};

type TaskWorkflowRoute =
  | { kind: "generic"; logicalSlot?: undefined }
  | { kind: "logical"; logicalSlot: TaskWorkflowLogicalSlot };

export function inferTaskWorkflowRoute(bytes: Buffer): TaskWorkflowRoute {
  let content: string;
  try {
    content = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    throw new Error("Task workflow Markdown must be valid UTF-8.");
  }
  const header = new Map<string, string>();
  for (const line of content.split(/\r?\n/, 120)) {
    if (/^##\s/.test(line)) break;
    const match = /^([a-z][a-z0-9_]*):\s*(.*?)\s*$/.exec(line);
    if (match) header.set(match[1], match[2]);
  }
  const documentType = header.get("document_type");
  if (!documentType) return { kind: "generic" };
  if (documentType === "task_delivery") {
    return { kind: "logical", logicalSlot: "task_delivery" };
  }
  if (documentType !== "task_work") {
    throw new Error(`Unsupported typed task workflow document_type: ${documentType}.`);
  }
  const documentSlot = header.get("document_slot");
  if (documentSlot === "execution") {
    return { kind: "logical", logicalSlot: "task_work_execution" };
  }
  if (documentSlot === "post_completion_revision") {
    return { kind: "logical", logicalSlot: "task_work_post_completion_revision" };
  }
  throw new Error(
    "Typed task_work Markdown requires document_slot: execution or post_completion_revision.",
  );
}

function withRouteMetadata<T extends object & { data?: unknown; code?: string }>(
  result: T,
  route: TaskWorkflowRoute,
  contentSha256: string,
): Record<string, unknown> {
  const existingData = isObject(result.data) ? result.data : {};
  return {
    ...result,
    data: {
      ...existingData,
      transport: "contentBase64",
      localPathRole: "mcp_read_boundary_only",
      route: route.kind === "logical" ? "logical_attachment_replace" : "legacy_generic_attachment",
      ...(route.logicalSlot ? { logicalSlot: route.logicalSlot } : {}),
      contentSha256,
      nextAction:
        result.code === "dry_run"
          ? "Repeat the same call with dryRun=false after reviewing this route."
          : "Use the returned attachment id and SHA-256 as the App-owned receipt.",
    },
  };
}

async function replaceTypedTaskAttachment(
  input: TaskWorkflowAttachmentInput,
  bytes: Buffer,
  route: Extract<TaskWorkflowRoute, { kind: "logical" }>,
  contentSha256: string,
) {
  const requiredActions = ["attachment.conditional-add", "attachment.read-content-hash"];
  const path = `/v1/tasks/${input.taskId}/attachments`;
  if (!input.dryRun) {
    const capabilities = await requestGranoflowApi({ path: "/v1/capabilities" });
    if (!capabilities.ok || !supportsResourceActions(capabilities, "task", requiredActions)) {
      return withRouteMetadata(
        {
          ok: false,
          code: "unsupported_capability",
          data: {
            resource: "task",
            requiredActions,
            endpoint: path,
          },
          error: {
            message: `The running Granoflow app does not advertise task: ${requiredActions.join(", ")}.`,
          },
          runtime: capabilities.runtime,
        },
        route,
        contentSha256,
      );
    }
  }
  const result = await requestGranoflowApi({
    method: "POST",
    path,
    body: {
      contentBase64: bytes.toString("base64"),
      fileName: basename(input.filePath),
      logicalSlot: route.logicalSlot,
      expectedUpdatedAt: input.expectedTaskUpdatedAt,
      expectedContentSha256: contentSha256,
      idempotencyKey: input.idempotencyKey,
      visualConfirmed: false,
    },
    dryRun: input.dryRun,
  });
  return withRouteMetadata(result, route, contentSha256);
}

async function addGenericTaskAttachment(
  input: TaskWorkflowAttachmentInput,
  bytes: Buffer,
  route: Extract<TaskWorkflowRoute, { kind: "generic" }>,
  contentSha256: string,
) {
  const body = {
    contentBase64: bytes.toString("base64"),
    fileName: basename(input.filePath),
    idempotencyKey: input.idempotencyKey,
    expectedTaskUpdatedAt: input.expectedTaskUpdatedAt,
    expectedContentSha256: contentSha256,
  };
  if (input.dryRun) {
    const result = await requestGranoflowApi({
      method: "POST",
      path: `/v1/tasks/${input.taskId}/attachments`,
      body,
      dryRun: true,
    });
    return withRouteMetadata(result, route, contentSha256);
  }
  const capabilities = await requestGranoflowApi({ path: "/v1/capabilities" });
  if (!capabilities.ok || !supportsTaskWorkflowAttachmentReadback(capabilities)) {
    return withRouteMetadata(
      {
        ok: false,
        code: "unsupported_capability",
        data: { requiredCapability: "task_workflow_attachment_readback_v1" },
        error: {
          message:
            "The running Granoflow app does not advertise conditional task attachment write and content/hash readback.",
        },
        runtime: capabilities.runtime,
      },
      route,
      contentSha256,
    );
  }
  const write = await requestGranoflowApi({
    method: "POST",
    path: `/v1/tasks/${input.taskId}/attachments`,
    body,
  });
  if (!write.ok) return withRouteMetadata(write, route, contentSha256);
  const entity = extractEntity(write);
  const attachmentId = typeof entity?.id === "string" ? entity.id : undefined;
  if (!attachmentId) {
    return withRouteMetadata(
      {
        ok: false,
        code: "attachment_readback_unavailable",
        data: { write },
        error: { message: "The app did not return the created task attachment id." },
        runtime: write.runtime,
      },
      route,
      contentSha256,
    );
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
  return withRouteMetadata(
    {
      ok: verified,
      code: verified ? "task_attachment_written" : "attachment_readback_mismatch",
      data: { attachment: entity, verified, write, readback },
      error: verified
        ? undefined
        : { message: "Task attachment content/hash readback did not match the local Markdown." },
      runtime: readback.runtime ?? write.runtime,
    },
    route,
    contentSha256,
  );
}

export async function addTaskWorkflowAttachment(input: TaskWorkflowAttachmentInput) {
  const bytes = readFileSync(input.filePath);
  const contentSha256 = createHash("sha256").update(bytes).digest("hex");
  const route = inferTaskWorkflowRoute(bytes);
  return route.kind === "logical"
    ? replaceTypedTaskAttachment(input, bytes, route, contentSha256)
    : addGenericTaskAttachment(input, bytes, route, contentSha256);
}
