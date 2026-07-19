import { z } from "zod";
import { compactRecord } from "./tools.js";

import type { CapabilityRegistrar } from "./tool-registration-evidence.js";

type RegistrationSchemas = {
  resourceIdSchema: z.ZodTypeAny;
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>;
};

function registerExperienceReadTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_experience_list",
    "List independent Experience records, optionally for a daily, weekly, or monthly review scope.",
    {
      periodKind: z.enum(["daily", "weekly", "monthly"]).optional(),
      scopeId: z.string().min(1).optional(),
      limit: z.number().int().min(1).max(100).default(50),
      offset: z.number().int().min(0).default(0),
    },
    "experience",
    ["list"],
    ({ periodKind, scopeId, limit, offset }) => {
      const query = new URLSearchParams();
      if (typeof periodKind === "string") query.set("periodKind", periodKind);
      if (typeof scopeId === "string") query.set("scopeId", scopeId);
      query.set("limit", String(limit));
      query.set("offset", String(offset));
      return { path: `/v1/experiences?${query}` };
    },
  );
  registerCapabilityTool(
    "granoflow_experience_get",
    "Get one Experience with provenance, task usages, Knowledge links, and merge redirect.",
    { experienceId: resourceIdSchema },
    "experience",
    ["review"],
    ({ experienceId }) => ({ path: `/v1/experiences/${String(experienceId)}` }),
  );
  registerCapabilityTool(
    "granoflow_project_experiences",
    "List independent Experience records derived from tasks in one project.",
    { projectId: resourceIdSchema },
    "experience",
    ["list-for-project"],
    ({ projectId }) => ({ path: `/v1/projects/${String(projectId)}/experiences` }),
  );
  registerCapabilityTool(
    "granoflow_milestone_experiences",
    "List independent Experience records derived from tasks in one milestone.",
    { milestoneId: resourceIdSchema },
    "experience",
    ["list-for-milestone"],
    ({ milestoneId }) => ({ path: `/v1/milestones/${String(milestoneId)}/experiences` }),
  );
  registerCapabilityTool(
    "granoflow_experience_search",
    "Search the independent Experience lane with explicit vector or degraded fallback status.",
    { query: z.string().min(1), limit: z.number().int().min(1).max(100).default(10) },
    "experience",
    ["search"],
    ({ query, limit }) => ({
      path: `/v1/experiences/search?q=${encodeURIComponent(String(query))}&limit=${Number(limit)}`,
    }),
  );
}

function registerExperienceAuthoringTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema, approvedAuthoringSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_experience_authoring_preview",
    "Preview Experience distillation for a task or periodic review with zero writes.",
    {
      scopeType: z.enum(["task", "daily", "weekly", "monthly"]),
      scopeId: resourceIdSchema,
      candidates: z.array(z.record(z.string(), z.unknown())).min(1),
    },
    "experience",
    ["authoring-preview"],
    ({ scopeType, scopeId, candidates }) => ({
      method: "POST",
      path: "/v1/experiences/authoring/preview",
      body: { scopeType, scopeId, candidates },
    }),
  );
  registerCapabilityTool(
    "granoflow_experience_authoring_apply",
    "Apply only user-approved Experience operations from a current preview.",
    approvedAuthoringSchema,
    "experience",
    ["authoring-apply"],
    (body) => ({ method: "POST", path: "/v1/experiences/authoring/apply", body }),
  );
}

function registerExperienceLifecycleTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_experience_update",
    "Edit all required fields of an independent Experience with optimistic revision checking.",
    {
      experienceId: resourceIdSchema,
      conclusion: z.string().min(1),
      rationale: z.string().min(1),
      context: z.string().min(1),
      boundary: z.string().min(1),
      nextAction: z.string().min(1),
      expectedRevision: z.number().int().min(1),
    },
    "experience",
    ["update"],
    ({ experienceId, ...body }) => ({
      method: "PATCH",
      path: `/v1/experiences/${String(experienceId)}`,
      body,
    }),
  );
  registerCapabilityTool(
    "granoflow_experience_delete_impact",
    "Preview the full impact of permanently deleting an Experience with zero writes.",
    { experienceId: resourceIdSchema },
    "experience",
    ["delete-impact"],
    ({ experienceId }) => ({ path: `/v1/experiences/${String(experienceId)}/delete-impact` }),
  );
  registerCapabilityTool(
    "granoflow_experience_delete",
    "Permanently delete an Experience and all relations after both impact and final confirmation.",
    {
      experienceId: resourceIdSchema,
      expectedRevision: z.number().int().min(1),
      previewHash: z.string().min(1),
      impactConfirmed: z.literal(true),
      permanentConfirmed: z.literal(true),
    },
    "experience",
    ["delete"],
    ({ experienceId, ...body }) => ({
      method: "DELETE",
      path: `/v1/experiences/${String(experienceId)}`,
      body,
    }),
  );
}

function registerExperienceRelationTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_experience_merge_preview",
    "Preview merging one Experience into a canonical Experience with zero writes.",
    {
      canonicalExperienceId: resourceIdSchema,
      mergedExperienceId: resourceIdSchema,
    },
    "experience",
    ["merge-preview"],
    ({ canonicalExperienceId, mergedExperienceId }) => ({
      method: "POST",
      path: `/v1/experiences/${String(canonicalExperienceId)}/merge/preview`,
      body: { mergedId: mergedExperienceId },
    }),
  );
  registerCapabilityTool(
    "granoflow_experience_merge_apply",
    "Apply an approved Experience merge and return the stable redirect readback.",
    {
      canonicalExperienceId: resourceIdSchema,
      mergedExperienceId: resourceIdSchema,
      expectedCanonicalRevision: z.number().int().min(1),
      expectedMergedRevision: z.number().int().min(1),
      previewHash: z.string().min(1),
      confirmed: z.literal(true),
    },
    "experience",
    ["merge-apply"],
    ({ canonicalExperienceId, mergedExperienceId, ...body }) => ({
      method: "POST",
      path: `/v1/experiences/${String(canonicalExperienceId)}/merge/apply`,
      body: { ...body, mergedId: mergedExperienceId },
    }),
  );
  registerCapabilityTool(
    "granoflow_experience_usage_link",
    "Link or update a confirmed task usage for an Experience.",
    {
      experienceId: resourceIdSchema,
      taskId: resourceIdSchema,
      kind: z.enum(["referenced", "applied", "validated", "contradicted"]),
      note: z.string().optional(),
      confirmed: z.literal(true),
    },
    "experience",
    ["usage-link"],
    ({ experienceId, taskId, kind, note }) => ({
      method: "POST",
      path: `/v1/experiences/${String(experienceId)}/usages`,
      body: compactRecord({ taskId, kind, note, confirmed: true }),
    }),
  );
  registerCapabilityTool(
    "granoflow_experience_usage_unlink_impact",
    "Preview whether unlinking an Experience from a task would leave it without task relations.",
    { experienceId: resourceIdSchema, taskId: resourceIdSchema },
    "experience",
    ["usage-unlink-impact"],
    ({ experienceId, taskId }) => ({
      path: `/v1/experiences/${String(experienceId)}/usages/${String(taskId)}/unlink-impact`,
    }),
  );
  registerCapabilityTool(
    "granoflow_experience_usage_unlink",
    "Unlink an Experience from one task without deleting Experience provenance.",
    {
      experienceId: resourceIdSchema,
      taskId: resourceIdSchema,
      confirmed: z.literal(true),
    },
    "experience",
    ["usage-unlink"],
    ({ experienceId, taskId }) => ({
      method: "DELETE",
      path: `/v1/experiences/${String(experienceId)}/usages/${String(taskId)}`,
      body: { confirmed: true },
    }),
  );
}

function registerKnowledgeAssessmentTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema, approvedAuthoringSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_knowledge_assessment_list",
    "List Knowledge eligibility assessments without creating cards.",
    {},
    "knowledge-assessment",
    ["list"],
    () => ({ path: "/v1/knowledge-assessments" }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_assessment_get",
    "Get one Knowledge assessment with typed source snapshots and freshness.",
    { assessmentId: resourceIdSchema },
    "knowledge-assessment",
    ["review"],
    ({ assessmentId }) => ({ path: `/v1/knowledge-assessments/${String(assessmentId)}` }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_assessment_preview",
    "Preview eligibility, disposition, learning cost, and duplicate handling with zero writes.",
    { candidates: z.array(z.record(z.string(), z.unknown())).min(1) },
    "knowledge-assessment",
    ["preview"],
    ({ candidates }) => ({
      method: "POST",
      path: "/v1/knowledge-assessments/authoring/preview",
      body: { candidates },
    }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_assessment_apply",
    "Apply only approved Knowledge assessment operations; this does not materialize cards.",
    approvedAuthoringSchema,
    "knowledge-assessment",
    ["apply"],
    (body) => ({
      method: "POST",
      path: "/v1/knowledge-assessments/authoring/apply",
      body,
    }),
  );
}

function registerKnowledgeMaterializationTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema, approvedAuthoringSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_knowledge_materialization_list",
    "List approved Knowledge materializations backed by existing Review Notes and Cards.",
    {},
    "knowledge-materialization",
    ["list"],
    () => ({ path: "/v1/knowledge-materializations" }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_materialization_get",
    "Get one Knowledge materialization with Note, Cards, source health, and control evidence.",
    { materializationId: resourceIdSchema },
    "knowledge-materialization",
    ["review"],
    ({ materializationId }) => ({
      path: `/v1/knowledge-materializations/${String(materializationId)}`,
    }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_materialization_preview",
    "Preview atomic Knowledge Note/Card creation or existing-Knowledge reuse with zero writes.",
    { candidates: z.array(z.record(z.string(), z.unknown())).min(1) },
    "knowledge-materialization",
    ["preview"],
    ({ candidates }) => ({
      method: "POST",
      path: "/v1/knowledge-materializations/authoring/preview",
      body: { candidates },
    }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_materialization_apply",
    "Apply approved Knowledge materializations atomically and return Note/Card readback.",
    approvedAuthoringSchema,
    "knowledge-materialization",
    ["apply"],
    (body) => ({
      method: "POST",
      path: "/v1/knowledge-materializations/authoring/apply",
      body,
    }),
  );
}

function registerKnowledgeControlTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_knowledge_control_preview",
    "Preview implemented or verified system-control evidence with zero writes.",
    {
      materializationId: resourceIdSchema,
      status: z.enum(["candidate", "implemented", "verified"]),
      evidence: z.record(z.string(), z.unknown()),
    },
    "knowledge-materialization",
    ["control-preview"],
    ({ materializationId, status, evidence }) => ({
      method: "POST",
      path: "/v1/knowledge-materializations/control/preview",
      body: { materializationId, status, evidence },
    }),
  );
  registerCapabilityTool(
    "granoflow_knowledge_control_apply",
    "Apply approved control evidence. Verified status remains App-owned and requires readback evidence.",
    {
      previewToken: z.string().min(1),
      previewHash: z.string().min(1),
      operationId: z.string().min(1),
      idempotencyKey: z.string().min(1),
    },
    "knowledge-materialization",
    ["control-apply"],
    (body) => ({
      method: "POST",
      path: "/v1/knowledge-materializations/control/apply",
      body,
    }),
  );
}

function registerTaskKnowledgePackTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema, approvedAuthoringSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_task_knowledge_pack",
    "Build a zero-write task analysis pack with separate Evidence, Experience, and Knowledge lanes.",
    {
      taskId: resourceIdSchema,
      query: z.string().min(1),
      limitPerLane: z.number().int().min(1).max(100).default(10),
    },
    "task-knowledge",
    ["pack"],
    ({ taskId, query, limitPerLane }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/pack`,
      body: { query, limitPerLane },
    }),
  );
  registerCapabilityTool(
    "granoflow_task_knowledge_references",
    "List current structured Task Work references for one task.",
    { taskId: resourceIdSchema },
    "task-knowledge",
    ["reference-list"],
    ({ taskId }) => ({ path: `/v1/task-knowledge/${String(taskId)}/references` }),
  );
  registerCapabilityTool(
    "granoflow_task_knowledge_adoption_preview",
    "Preview adopted, considered, or rejected Knowledge Pack decisions. Only adopted operations can write.",
    {
      taskId: resourceIdSchema,
      decisions: z.array(z.record(z.string(), z.unknown())).min(1),
    },
    "task-knowledge",
    ["adoption-preview"],
    ({ taskId, decisions }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/adoption/preview`,
      body: { decisions },
    }),
  );
  registerCapabilityTool(
    "granoflow_task_knowledge_adoption_apply",
    "Apply only approved adopted references and return Reference, Usage, and association readback.",
    { taskId: resourceIdSchema, ...approvedAuthoringSchema },
    "task-knowledge",
    ["adoption-apply"],
    ({ taskId, ...body }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/adoption/apply`,
      body,
    }),
  );
}

function registerTaskKnowledgeAuditTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema, approvedAuthoringSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_task_knowledge_audit_preview",
    "Preview removal of Task Work references no longer present in the fully rewritten document.",
    {
      taskId: resourceIdSchema,
      desiredReferences: z.array(z.record(z.string(), z.unknown())),
    },
    "task-knowledge",
    ["audit-preview"],
    ({ taskId, desiredReferences }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/audit/preview`,
      body: { desiredReferences },
    }),
  );
  registerCapabilityTool(
    "granoflow_task_knowledge_audit_apply",
    "Apply approved stale-reference removals while preserving applied Knowledge Usage history.",
    { taskId: resourceIdSchema, ...approvedAuthoringSchema },
    "task-knowledge",
    ["audit-apply"],
    ({ taskId, ...body }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/audit/apply`,
      body,
    }),
  );
}

function registerTaskKnowledgeUsageTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_task_knowledge_usage_preview",
    "Preview referenced to applied, validated, or contradicted Knowledge Usage transition with evidence.",
    {
      taskId: resourceIdSchema,
      materializationId: resourceIdSchema,
      status: z.enum(["applied", "validated", "contradicted"]),
      evidence: z.record(z.string(), z.unknown()),
    },
    "task-knowledge",
    ["usage-preview"],
    ({ taskId, materializationId, status, evidence }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/usage/preview`,
      body: { materializationId, status, evidence },
    }),
  );
  registerCapabilityTool(
    "granoflow_task_knowledge_usage_apply",
    "Apply one approved Knowledge Usage status transition and preserve its append-only event.",
    {
      taskId: resourceIdSchema,
      previewToken: z.string().min(1),
      previewHash: z.string().min(1),
      operationId: z.string().min(1),
      idempotencyKey: z.string().min(1),
    },
    "task-knowledge",
    ["usage-apply"],
    ({ taskId, ...body }) => ({
      method: "POST",
      path: `/v1/task-knowledge/${String(taskId)}/usage/apply`,
      body,
    }),
  );
}

function registerKnowledgeScopeTools(
  registerCapabilityTool: CapabilityRegistrar,
  { resourceIdSchema }: RegistrationSchemas,
): void {
  registerCapabilityTool(
    "granoflow_project_knowledge_usages",
    "List Knowledge actually adopted by tasks in one project. The result is read-only and derived.",
    { projectId: resourceIdSchema },
    "task-knowledge",
    ["project-list"],
    ({ projectId }) => ({ path: `/v1/projects/${String(projectId)}/knowledge-usages` }),
  );
  registerCapabilityTool(
    "granoflow_milestone_knowledge_usages",
    "List Knowledge actually adopted by tasks in one milestone. The result is read-only and derived.",
    { milestoneId: resourceIdSchema },
    "task-knowledge",
    ["milestone-list"],
    ({ milestoneId }) => ({ path: `/v1/milestones/${String(milestoneId)}/knowledge-usages` }),
  );
}

export function registerExperienceAndKnowledgeTools(
  registerCapabilityTool: CapabilityRegistrar,
  resourceIdSchema: z.ZodTypeAny,
  approvedAuthoringSchema: Record<string, z.ZodTypeAny>,
): void {
  const schemas = { resourceIdSchema, approvedAuthoringSchema };
  registerExperienceReadTools(registerCapabilityTool, schemas);
  registerExperienceAuthoringTools(registerCapabilityTool, schemas);
  registerExperienceLifecycleTools(registerCapabilityTool, schemas);
  registerExperienceRelationTools(registerCapabilityTool, schemas);
  registerKnowledgeAssessmentTools(registerCapabilityTool, schemas);
  registerKnowledgeMaterializationTools(registerCapabilityTool, schemas);
  registerKnowledgeControlTools(registerCapabilityTool, schemas);
  registerTaskKnowledgePackTools(registerCapabilityTool, schemas);
  registerTaskKnowledgeAuditTools(registerCapabilityTool, schemas);
  registerTaskKnowledgeUsageTools(registerCapabilityTool, schemas);
  registerKnowledgeScopeTools(registerCapabilityTool, schemas);
}
