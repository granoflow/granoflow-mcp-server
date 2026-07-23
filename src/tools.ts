import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { basename } from "node:path";

import { z } from "zod";

import { requestGranoflowApi } from "./api.js";
import { ensureSourceTags, type CompletionSource } from "./source-tags.js";
import {
  detectLocalApi,
  getSetupStatus,
  openGranoflowApp,
  openSetupConfig,
  writeSetupConfig,
} from "./setup.js";
import { bundledSkillResources } from "./workflow-resources.js";
import {
  registerAuthorizationAndProjectSkillTools,
  registerSetupAndHealthTools,
  registerWorkflowSkillTools,
} from "./tool-registration-foundation.js";
import { registerEvidenceTools } from "./tool-registration-evidence.js";
import { registerExperienceAndKnowledgeTools } from "./tool-registration-experience-knowledge.js";
import { registerReviewAndContextTools } from "./tool-registration-review-context.js";
import { registerTaskMemoryAndTagsTools } from "./tool-registration-task-memory.js";
import { registerTaskCrudTools } from "./tool-registration-task-crud.js";
import { registerAttachmentTools } from "./tool-registration-attachments.js";
import { registerPrototypeTools } from "./tool-registration-prototypes.js";
import { registerTaskNodeTools } from "./tool-registration-task-nodes.js";
import { registerProjectMilestoneTools } from "./tool-registration-project-milestone.js";
import { registerUtilityTools } from "./tool-registration-utility.js";
import { registerAgentPreferenceTools } from "./tool-registration-agent-preferences.js";
import type { CapabilityRegistrar } from "./tool-registration-evidence.js";
import {
  AGENT_WORKFLOW_SKILL_URL,
  DAILY_REVIEW_SKILL_URL,
  FIRST_RUN_IMPORT_SKILL_URL,
  REVIEW_CARD_DRAFT_SKILL_URL,
  GFMCP_RUNNER_SKILL_URL,
  DELEGATED_AUTHORIZATION_SKILL_URL,
  TASK_ORCHESTRATOR_SKILL_URL,
  MILESTONE_WORKFLOW_SKILL_URL,
  MILESTONE_COORDINATION_SKILL_URL,
  TASK_AUTHORING_SKILL_URL,
  PORTFOLIO_ORCHESTRATOR_SKILL_URL,
  PERSISTENT_MILESTONE_RUNNER_SKILL_URL,
  PROJECT_DEFINITION_SKILL_URL,
  INTEGRATION_TEST_CAMPAIGN_SKILL_URL,
  E2E_TEST_CAMPAIGN_SKILL_URL,
  compactRecord,
  validateManagedBlock,
  textResult,
  jsonTextResult,
  readAgentWorkflowSkill,
  readDailyReviewSkill,
  readFirstRunImportSkill,
  readReviewCardDraftSkill,
  readGfmcpRunnerSkill,
  readDelegatedAuthorizationSkill,
  readTaskOrchestratorSkill,
  readMilestoneWorkflowSkill,
  readMilestoneCoordinationSkill,
  readTaskAuthoringSkill,
  readPortfolioOrchestratorSkill,
  readPersistentMilestoneRunnerSkill,
  readProjectDefinitionSkill,
  readIntegrationTestCampaignSkill,
  readE2eTestCampaignSkill,
  readAcceptanceDeliverySkill,
  isWithin,
  validatedWorkflowMarkdownPath,
  validatedLogicalAttachmentPath,
  validatedProjectDesignBaselinePath,
  validatedTaskPrototypePath,
  logicalAttachmentResource,
  logicalAttachmentPath,
  supportsTaskNodeWorkflow,
  supportsTaskWorkflowAttachmentReadback,
  supportsResourceActions,
  resourceCapabilityApiTool,
  extractEntity,
  addTaskWorkflowAttachment,
  taskNodeApiTool,
  requireTaskAnalysisPlanAttachment,
  completeNodeLessTask,
  periodicReviewHasLog,
  checkPeriodicReviewSuggestion,
  withDailyReviewSuggestion,
  apiTool,
  isObject,
  TaskAuthoringQualityIssue,
} from "./tool-runtime-core.js";
import type { ToolResult, ToolRegistrar } from "./tool-runtime-core.js";
import {
  apiToolForTaskWrite,
  compactResource,
  defaultMilestoneDueAt,
  extractItems,
  ordinaryTaskWriteFailure,
  parseCompletionSource,
  patchTaskCompletionSourceTag,
  taskAuthoringQualityFailure,
  validateTaskAuthoringQuality,
} from "./tool-runtime-authoring.js";
import {
  contextPackApiTool,
  draftUsesEnhancedFields,
  historicalTaskCandidatesApiTool,
  memoryBatchPreviewApiTool,
  mutateTaskHistory,
  normalizeReviewCardDraft,
  projectContextAttachmentApiTool,
  supportsReviewCardDraftNoteFields,
} from "./tool-runtime-capabilities.js";
import {
  contextStewardStatus,
  milestoneContextArchive,
  milestoneContextUpdate,
  projectContextUpdate,
  resolveResourceById,
} from "./tool-runtime-context.js";
export {
  AGENT_WORKFLOW_SKILL_URL,
  DAILY_REVIEW_SKILL_URL,
  FIRST_RUN_IMPORT_SKILL_URL,
  REVIEW_CARD_DRAFT_SKILL_URL,
  GFMCP_RUNNER_SKILL_URL,
  DELEGATED_AUTHORIZATION_SKILL_URL,
  TASK_ORCHESTRATOR_SKILL_URL,
  MILESTONE_WORKFLOW_SKILL_URL,
  MILESTONE_COORDINATION_SKILL_URL,
  TASK_AUTHORING_SKILL_URL,
  PORTFOLIO_ORCHESTRATOR_SKILL_URL,
  PERSISTENT_MILESTONE_RUNNER_SKILL_URL,
  PROJECT_DEFINITION_SKILL_URL,
  INTEGRATION_TEST_CAMPAIGN_SKILL_URL,
  E2E_TEST_CAMPAIGN_SKILL_URL,
  compactRecord,
  validateManagedBlock,
  textResult,
  jsonTextResult,
  readAgentWorkflowSkill,
  readDailyReviewSkill,
  readFirstRunImportSkill,
  readReviewCardDraftSkill,
  readGfmcpRunnerSkill,
  readDelegatedAuthorizationSkill,
  readTaskOrchestratorSkill,
  readMilestoneWorkflowSkill,
  readMilestoneCoordinationSkill,
  readTaskAuthoringSkill,
  readPortfolioOrchestratorSkill,
  readPersistentMilestoneRunnerSkill,
  readProjectDefinitionSkill,
  readIntegrationTestCampaignSkill,
  readE2eTestCampaignSkill,
  readAcceptanceDeliverySkill,
  isWithin,
  validatedWorkflowMarkdownPath,
  validatedLogicalAttachmentPath,
  validatedProjectDesignBaselinePath,
  validatedTaskPrototypePath,
  logicalAttachmentResource,
  logicalAttachmentPath,
  supportsTaskNodeWorkflow,
  supportsTaskWorkflowAttachmentReadback,
  supportsResourceActions,
  resourceCapabilityApiTool,
  extractEntity,
  addTaskWorkflowAttachment,
  taskNodeApiTool,
  requireTaskAnalysisPlanAttachment,
  completeNodeLessTask,
  periodicReviewHasLog,
  checkPeriodicReviewSuggestion,
  withDailyReviewSuggestion,
  apiTool,
  isObject,
  TaskAuthoringQualityIssue,
};
export type { ToolResult, ToolRegistrar };
import { finishTask, resolveResource, safeDeleteResource } from "./tool-task-lifecycle.js";

const jsonInputSchema = z
  .record(z.string(), z.unknown())
  .describe("JSON object sent to the Granoflow Local HTTP API.");
const completionSourceSchema = z
  .enum(["ai", "human", "unknown"])
  .optional()
  .describe(
    "When ai or human, attach the matching AI/人工 source tag after ensuring it exists. Omit or unknown means no source tag.",
  );
const taskAuthoringEvidenceInputSchema = z
  .record(z.string(), z.unknown())
  .optional()
  .describe(
    "Required for AI or automation task creation: declare an action/outcome title, plain-language review, and exact analogy/example excerpts from the description.",
  );
export const historicalTaskMutationSchema = z.object({
  clientMutationId: z.string().min(1),
  op: z.enum(["create", "update", "softDelete"]),
  taskId: z.string().min(1).optional(),
  fields: z.record(z.string(), z.unknown()).optional(),
  authoringEvidence: taskAuthoringEvidenceInputSchema,
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
const logicalAttachmentEntityTypeSchema = z.enum(["project", "milestone", "task"]);
const logicalAttachmentSlotSchema = z.enum([
  "project_work",
  "milestone_work",
  "task_work_execution",
  "task_work_post_completion_revision",
  "task_delivery",
  "ui_prototype",
  "data_model",
  "workflows",
  "acceptance_report",
]);
const projectWorkActionSchema = z.enum([
  "attach_partial_project_work",
  "create_milestone_manually",
  "create_task_manually",
  "create_milestone_automatically",
  "execute_task_automatically",
  "complete_task_automatically",
  "continue_project_automatically",
  "publish_automatically",
  "deploy_automatically",
  "complete_project_automatically",
]);
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
export const milestoneArchiveClosureSchema = z.object({
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
const approvedAuthoringSchema = {
  previewToken: z.string().min(1),
  previewHash: z.string().min(1),
  approvedOperationIds: z.array(z.string().min(1)).min(1),
  idempotencyKey: z.string().min(1),
};
const resourceIdSchema = z.string().min(1);

export type ReviewCardDraft = z.infer<typeof reviewCardDraftSchema>;

type ResourceKind = "project" | "milestone" | "task";

type GranoflowRecord = {
  id?: unknown;
  title?: unknown;
  status?: unknown;
  projectId?: unknown;
  milestoneId?: unknown;
  [key: string]: unknown;
};

export type ToolRegistrationContext = {
  basename: typeof basename;
  createHash: typeof createHash;
  readFileSync: typeof readFileSync;
  compactRecord: typeof compactRecord;
  contextPackScopeSchema: typeof contextPackScopeSchema;
  contextPackSourceSchema: typeof contextPackSourceSchema;
  memoryBatchItemSchema: typeof memoryBatchItemSchema;
  projectContextAttachmentSchema: typeof projectContextAttachmentSchema;
  contextStewardEvidenceSchema: typeof contextStewardEvidenceSchema;
  milestoneArchiveClosureSchema: typeof milestoneArchiveClosureSchema;
  jsonInputSchema: typeof jsonInputSchema;
  historicalTaskMutationSchema: typeof historicalTaskMutationSchema;
  completionSourceSchema: typeof completionSourceSchema;
  taskAuthoringEvidenceInputSchema: typeof taskAuthoringEvidenceInputSchema;
  resourceStatusSchema: typeof resourceStatusSchema;
  logicalAttachmentEntityTypeSchema: typeof logicalAttachmentEntityTypeSchema;
  logicalAttachmentSlotSchema: typeof logicalAttachmentSlotSchema;
  projectWorkActionSchema: typeof projectWorkActionSchema;
  taskNodeCreateSchema: typeof taskNodeCreateSchema;
  taskNodeStatusSchema: typeof taskNodeStatusSchema;
  reviewCardDraftSchema: typeof reviewCardDraftSchema;
  resolveMatchModeSchema: typeof resolveMatchModeSchema;
  TASK_REVIEW_START: typeof TASK_REVIEW_START;
  TASK_REVIEW_END: typeof TASK_REVIEW_END;
  TASK_COMPLETION_SUMMARY_START: typeof TASK_COMPLETION_SUMMARY_START;
  TASK_COMPLETION_SUMMARY_END: typeof TASK_COMPLETION_SUMMARY_END;
  apiTool: typeof apiTool;
  apiToolForTaskWrite: typeof apiToolForTaskWrite;
  addTaskWorkflowAttachment: typeof addTaskWorkflowAttachment;
  completeNodeLessTask: typeof completeNodeLessTask;
  contextPackApiTool: typeof contextPackApiTool;
  contextStewardStatus: typeof contextStewardStatus;
  defaultMilestoneDueAt: typeof defaultMilestoneDueAt;
  finishTask: typeof finishTask;
  historicalTaskCandidatesApiTool: typeof historicalTaskCandidatesApiTool;
  jsonTextResult: typeof jsonTextResult;
  memoryBatchPreviewApiTool: typeof memoryBatchPreviewApiTool;
  milestoneContextArchive: typeof milestoneContextArchive;
  milestoneContextUpdate: typeof milestoneContextUpdate;
  mutateTaskHistory: typeof mutateTaskHistory;
  projectContextAttachmentApiTool: typeof projectContextAttachmentApiTool;
  projectContextUpdate: typeof projectContextUpdate;
  requireTaskAnalysisPlanAttachment: typeof requireTaskAnalysisPlanAttachment;
  resolveResource: typeof resolveResource;
  safeDeleteResource: typeof safeDeleteResource;
  taskAuthoringQualityFailure: typeof taskAuthoringQualityFailure;
  taskNodeApiTool: typeof taskNodeApiTool;
  validatedLogicalAttachmentPath: typeof validatedLogicalAttachmentPath;
  validatedProjectDesignBaselinePath: typeof validatedProjectDesignBaselinePath;
  validatedTaskPrototypePath: typeof validatedTaskPrototypePath;
  validatedWorkflowMarkdownPath: typeof validatedWorkflowMarkdownPath;
  validateManagedBlock: typeof validateManagedBlock;
  logicalAttachmentResource: typeof logicalAttachmentResource;
  logicalAttachmentPath: typeof logicalAttachmentPath;
  resourceCapabilityApiTool: typeof resourceCapabilityApiTool;
  requestGranoflowApi: typeof requestGranoflowApi;
  extractItems: typeof extractItems;
  ensureSourceTags: typeof ensureSourceTags;
  isObject: typeof isObject;
  validateTaskAuthoringQuality: typeof validateTaskAuthoringQuality;
  ordinaryTaskWriteFailure: typeof ordinaryTaskWriteFailure;
  parseCompletionSource: typeof parseCompletionSource;
};

export type { CompletionSource };
export type { GranoflowRecord, ResourceKind };
export {
  compactResource,
  draftUsesEnhancedFields,
  extractItems,
  normalizeReviewCardDraft,
  patchTaskCompletionSourceTag,
  requestGranoflowApi,
  resolveResourceById,
  supportsReviewCardDraftNoteFields,
};

export function createToolRegistrationContext(): ToolRegistrationContext {
  return {
    basename,
    createHash,
    readFileSync,
    compactRecord,
    contextPackScopeSchema,
    contextPackSourceSchema,
    memoryBatchItemSchema,
    projectContextAttachmentSchema,
    contextStewardEvidenceSchema,
    milestoneArchiveClosureSchema,
    jsonInputSchema,
    historicalTaskMutationSchema,
    completionSourceSchema,
    taskAuthoringEvidenceInputSchema,
    resourceStatusSchema,
    logicalAttachmentEntityTypeSchema,
    logicalAttachmentSlotSchema,
    projectWorkActionSchema,
    taskNodeCreateSchema,
    taskNodeStatusSchema,
    reviewCardDraftSchema,
    resolveMatchModeSchema,
    TASK_REVIEW_START,
    TASK_REVIEW_END,
    TASK_COMPLETION_SUMMARY_START,
    TASK_COMPLETION_SUMMARY_END,
    apiTool,
    apiToolForTaskWrite,
    addTaskWorkflowAttachment,
    completeNodeLessTask,
    contextPackApiTool,
    contextStewardStatus,
    defaultMilestoneDueAt,
    finishTask,
    historicalTaskCandidatesApiTool,
    jsonTextResult,
    memoryBatchPreviewApiTool,
    milestoneContextArchive,
    milestoneContextUpdate,
    mutateTaskHistory,
    projectContextAttachmentApiTool,
    projectContextUpdate,
    requireTaskAnalysisPlanAttachment,
    resolveResource,
    safeDeleteResource,
    taskAuthoringQualityFailure,
    taskNodeApiTool,
    validatedLogicalAttachmentPath,
    validatedProjectDesignBaselinePath,
    validatedTaskPrototypePath,
    validatedWorkflowMarkdownPath,
    validateManagedBlock,
    logicalAttachmentResource,
    logicalAttachmentPath,
    resourceCapabilityApiTool,
    requestGranoflowApi,
    extractItems,
    ensureSourceTags,
    isObject,
    validateTaskAuthoringQuality,
    ordinaryTaskWriteFailure,
    parseCompletionSource,
  };
}

type ToolServer = {
  tool: (
    name: string,
    description: string,
    schema: Record<string, z.ZodTypeAny>,
    handler: (args: Record<string, unknown>) => Promise<ReturnType<typeof textResult>>,
  ) => void;
};

function createToolRegistrars(server: ToolServer): {
  registerTool: ToolRegistrar;
  registerCapabilityTool: CapabilityRegistrar;
} {
  const registerTool: ToolRegistrar = (name, description, schema, handler) => {
    server.tool(name, description, schema, async (args) =>
      withDailyReviewSuggestion(name, await handler(args)),
    );
  };
  const registerCapabilityTool: CapabilityRegistrar = (
    name,
    description,
    schema,
    resource,
    actions,
    build,
  ) =>
    registerTool(name, description, schema, async (args) =>
      resourceCapabilityApiTool(resource, actions, build(args)),
    );
  return { registerTool, registerCapabilityTool };
}

export function registerGranoflowTools(server: ToolServer) {
  const { registerTool, registerCapabilityTool } = createToolRegistrars(server);

  const foundationDependencies = {
    jsonTextResult,
    readAgentWorkflowSkill,
    readDailyReviewSkill,
    readFirstRunImportSkill,
    readReviewCardDraftSkill,
    readGfmcpRunnerSkill,
    readDelegatedAuthorizationSkill,
    readTaskOrchestratorSkill,
    readMilestoneWorkflowSkill,
    readMilestoneCoordinationSkill,
    readTaskAuthoringSkill,
    readPortfolioOrchestratorSkill,
    readPersistentMilestoneRunnerSkill,
    readProjectDefinitionSkill,
    readIntegrationTestCampaignSkill,
    readE2eTestCampaignSkill,
    readAcceptanceDeliverySkill,
    bundledSkillResources,
    apiTool,
    getSetupStatus,
    detectLocalApi,
    writeSetupConfig,
    openSetupConfig,
    openGranoflowApp,
  };
  registerWorkflowSkillTools(registerTool, foundationDependencies);
  registerAuthorizationAndProjectSkillTools(registerTool, foundationDependencies);

  registerSetupAndHealthTools(registerTool, foundationDependencies);
  registerAgentPreferenceTools(registerTool, { jsonTextResult });

  registerEvidenceTools(registerCapabilityTool, resourceIdSchema, approvedAuthoringSchema);

  registerExperienceAndKnowledgeTools(
    registerCapabilityTool,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  const registrationContext = createToolRegistrationContext();
  registerReviewAndContextTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  registerTaskMemoryAndTagsTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  registerTaskCrudTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  registerAttachmentTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  registerPrototypeTools(registerTool, registerCapabilityTool, registrationContext);
  registerTaskNodeTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  registerProjectMilestoneTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
  registerUtilityTools(
    registerTool,
    registerCapabilityTool,
    registrationContext,
    resourceIdSchema,
    approvedAuthoringSchema,
  );
}
