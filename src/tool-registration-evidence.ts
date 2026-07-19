import { z } from "zod";

import type { ApiRequestOptions } from "./api.js";

export type CapabilityRegistrar = (
  name: string,
  description: string,
  schema: Record<string, z.ZodTypeAny>,
  resource: string,
  actions: readonly string[],
  build: (args: Record<string, unknown>) => ApiRequestOptions,
) => void;

export function registerEvidenceTools(
  registerCapabilityTool: CapabilityRegistrar,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  registerCapabilityTool(
    "granoflow_evidence_list",
    "List Evidence owned by one task, including source status and internal links.",
    { taskId: resourceIdSchema },
    "task",
    ["evidence.list"],
    ({ taskId }) => ({ path: `/v1/tasks/${String(taskId)}/evidence` }),
  );
  registerCapabilityTool(
    "granoflow_evidence_search",
    "Search the independent Evidence lane. The app reports vector or explicit degraded fallback status.",
    { query: z.string().min(1), limit: z.number().int().min(1).max(100).default(10) },
    "evidence",
    ["search"],
    ({ query, limit }) => ({
      path: `/v1/evidence/search?q=${encodeURIComponent(String(query))}&limit=${Number(limit)}`,
    }),
  );
  registerCapabilityTool(
    "granoflow_evidence_get",
    "Get one Evidence item with its task ownership and internal link.",
    { evidenceId: resourceIdSchema },
    "evidence",
    ["review"],
    ({ evidenceId }) => ({ path: `/v1/evidence/${String(evidenceId)}` }),
  );
  registerCapabilityTool(
    "granoflow_evidence_authoring_preview",
    "Preview Evidence candidates for a reviewed task with zero writes.",
    {
      taskId: resourceIdSchema,
      candidates: z.array(z.record(z.string(), z.unknown())).min(1),
    },
    "task",
    ["evidence.authoring-preview"],
    ({ taskId, candidates }) => ({
      method: "POST",
      path: `/v1/tasks/${String(taskId)}/evidence/authoring/preview`,
      body: { candidates },
    }),
  );
  registerCapabilityTool(
    "granoflow_evidence_authoring_apply",
    "Apply only user-approved Evidence operations from a current preview and return App readback.",
    {
      taskId: resourceIdSchema,
      ...approvedAuthoringSchema,
      expectedTaskReviewRevision: z.number().int().min(1),
      expectedTaskReviewHash: z.string().min(1),
    },
    "task",
    ["evidence.authoring-apply"],
    ({ taskId, ...body }) => ({
      method: "POST",
      path: `/v1/tasks/${String(taskId)}/evidence/authoring/apply`,
      body,
    }),
  );
  registerCapabilityTool(
    "granoflow_evidence_update",
    "Edit existing Evidence with optimistic revision checking.",
    {
      evidenceId: resourceIdSchema,
      statement: z.string().min(1),
      expectedRevision: z.number().int().min(1),
    },
    "evidence",
    ["update"],
    ({ evidenceId, statement, expectedRevision }) => ({
      method: "PATCH",
      path: `/v1/evidence/${String(evidenceId)}`,
      body: { statement, expectedRevision },
    }),
  );
  registerCapabilityTool(
    "granoflow_evidence_delete",
    "Delete existing Evidence after explicit confirmation. This does not run during sync or backup restore.",
    {
      evidenceId: resourceIdSchema,
      expectedRevision: z.number().int().min(1),
      confirmed: z.literal(true),
    },
    "evidence",
    ["delete"],
    ({ evidenceId, expectedRevision }) => ({
      method: "DELETE",
      path: `/v1/evidence/${String(evidenceId)}`,
      body: { expectedRevision, confirmed: true },
    }),
  );
}
