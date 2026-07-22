import { z } from "zod";

import type { ApiRequestOptions } from "./api.js";
import type { BundledSkillResources } from "./workflow-resources.js";
import { BUNDLED_SKILL_IDS, WorkflowResourceError } from "./workflow-resources.js";
import type { ToolRegistrar, ToolResult } from "./tools.js";

type SkillReader = () => string;

type FoundationDependencies = {
  jsonTextResult: (value: unknown) => ToolResult;
  readAgentWorkflowSkill: SkillReader;
  readDailyReviewSkill: SkillReader;
  readFirstRunImportSkill: SkillReader;
  readReviewCardDraftSkill: SkillReader;
  readGfmcpRunnerSkill: SkillReader;
  readDelegatedAuthorizationSkill: SkillReader;
  readTaskOrchestratorSkill: SkillReader;
  readMilestoneWorkflowSkill: SkillReader;
  readMilestoneCoordinationSkill: SkillReader;
  readTaskAuthoringSkill: SkillReader;
  readPortfolioOrchestratorSkill: SkillReader;
  readPersistentMilestoneRunnerSkill: SkillReader;
  readProjectDefinitionSkill: SkillReader;
  readIntegrationTestCampaignSkill: SkillReader;
  readE2eTestCampaignSkill: SkillReader;
  bundledSkillResources: BundledSkillResources;
  apiTool: (options: ApiRequestOptions) => Promise<ToolResult>;
  getSetupStatus: () => Promise<unknown>;
  detectLocalApi: (input: { ports?: number[]; timeoutMs?: number }) => Promise<unknown>;
  writeSetupConfig: (input: {
    apiBaseUrl?: string;
    apiPort?: number;
    dryRun: boolean;
  }) => Promise<unknown>;
  openSetupConfig: (input: { createIfMissing: boolean; open: boolean }) => Promise<unknown>;
  openGranoflowApp: (input: {
    appPath?: string;
    appName?: string;
    dryRun: boolean;
  }) => Promise<unknown>;
};

async function skillResult(
  deps: FoundationDependencies,
  path: string,
  skill: string,
  references: Promise<unknown>,
) {
  return deps.jsonTextResult({
    ok: true,
    code: "ok",
    data: { path, skill, references: await references },
  });
}

export function registerWorkflowSkillTools(
  registerTool: ToolRegistrar,
  deps: FoundationDependencies,
): void {
  const read = (
    name: string,
    description: string,
    path: string,
    skill: SkillReader,
    skillId: string,
  ) =>
    registerTool(
      name,
      description,
      {},
      async () =>
        await skillResult(deps, path, skill(), deps.bundledSkillResources.listReferences(skillId)),
    );

  read(
    "granoflow_agent_workflow_skill",
    "Read the bundled Granoflow Agent Workflow skill. Call this when a user works with Granoflow tasks, says 'Analyze the first task', says 'Start the first task', says 'Create a task from this requirement', says 'Process today's tasks', asks in their own language to analyze/start one selected task, create a task from a discussed requirement, or process tasks for a date/range/all-task scope, needs approval or missing information recorded in a task, finishes tasks, asks for weekly or monthly reviews, task reviews, review cards, historical context, decisions, lessons, similar past work, or long-term work memory, needs a project lifecycle progress board / next-step recommendation, or politely/strongly signals that Granoflow/MCP/generated agent output is wrong or misaligned. Use granoflow_daily_review_skill for an explicitly requested daily review or mood/efficiency note, and granoflow_first_run_import_skill for first-run import from Cursor, Codex, Hermes, or other agents. Do not call it for unrelated venting or unrelated disagreement.",
    "skills/granoflow-agent-workflow/SKILL.md",
    deps.readAgentWorkflowSkill,
    "granoflow-agent-workflow",
  );
  read(
    "granoflow_daily_review_skill",
    "Read the bundled Granoflow Daily Review skill. Call this when a user explicitly asks to review, summarize, or journal one day, including mood or efficiency notes. It requires display of evidence and a draft, conversation and explicit confirmation, then write and App/API readback of only approved daily-review fields.",
    "skills/granoflow-daily-review/SKILL.md",
    deps.readDailyReviewSkill,
    "granoflow-daily-review",
  );
  read(
    "granoflow_first_run_import_skill",
    "Read the bundled Granoflow First-Run Import skill. Call this when a user says 'Initialize Granoflow', optionally asks to import data, or uses an equivalent request in their own language. The workflow checks the connection, offers all unavailable recommended AI capability collections using only their names and plain-language functions, and previews authorized Cursor, Codex, Hermes, or other agent records as projects, monthly milestones, tasks, review-card candidates, and context backfills before any requested import write.",
    "skills/granoflow-first-run-import/SKILL.md",
    deps.readFirstRunImportSkill,
    "granoflow-first-run-import",
  );
  read(
    "granoflow_review_card_draft_skill",
    "Read the bundled core Granoflow review-card authoring skill. Call it for every lifecycle Card Checkpoint and every card search, link, create, or modification so similarity fallback, AI filtering, note quality, preview, approval, controlled writes, and readback use one workflow.",
    "skills/granoflow-review-card-draft/SKILL.md",
    deps.readReviewCardDraftSkill,
    "granoflow-review-card-draft",
  );
  read(
    "granoflow_gfmcp_runner_skill",
    "Read the bundled GFMCP automatic task runner skill. Use it to install, operate, or diagnose the optional five-minute Python worker for pending tasks tagged GFMCP.",
    "skills/granoflow-gfmcp-runner/SKILL.md",
    deps.readGfmcpRunnerSkill,
    "granoflow-gfmcp-runner",
  );
}

export function registerAuthorizationAndProjectSkillTools(
  registerTool: ToolRegistrar,
  deps: FoundationDependencies,
): void {
  const read = (
    name: string,
    description: string,
    path: string,
    skill: SkillReader,
    skillId: string,
  ) =>
    registerTool(
      name,
      description,
      {},
      async () =>
        await skillResult(deps, path, skill(), deps.bundledSkillResources.listReferences(skillId)),
    );

  read(
    "granoflow_delegated_authorization_skill",
    "Read the bundled Granoflow Delegated Authorization skill. Use it when a user wants bounded unattended continuation or when a Task Work phase gate may consume a confirmed, current authorization envelope. The skill and its validator never infer consent from tags, urgency, or absence.",
    "skills/granoflow-delegated-authorization/SKILL.md",
    deps.readDelegatedAuthorizationSkill,
    "granoflow-delegated-authorization",
  );
  read(
    "granoflow_task_orchestrator_skill",
    "Read the bundled context-aware Granoflow Task Orchestrator. Use it as the single upper-layer entrypoint when natural language or gf shortcuts may mean quick capture, context enrichment, Analysis, Planning, end-to-end local-safe execution, or completion audit. It delegates every phase to the existing workflow owners and never turns inferred intent into external or destructive authorization.",
    "skills/granoflow-task-orchestrator/SKILL.md",
    deps.readTaskOrchestratorSkill,
    "granoflow-task-orchestrator",
  );
  read(
    "granoflow_milestone_workflow_skill",
    "Read the bundled Granoflow Milestone Workflow skill. Requires complete confirmed Project Work; frontend projects also require confirmed Design Baseline with App Shell. Creates milestones singly or in batch (full portfolio when empty; amend when gaps). Does not author tasks or run charter/execution—hand off to task-authoring, portfolio-orchestrator, or milestone-coordination.",
    "skills/granoflow-milestone-workflow/SKILL.md",
    deps.readMilestoneWorkflowSkill,
    "granoflow-milestone-workflow",
  );
  read(
    "granoflow_milestone_coordination_skill",
    "Read the bundled Granoflow Milestone Coordination skill. Charter, coordinate, integrate, and close one active milestone after milestone and task entities exist. Does not batch-create milestones or author task titles/descriptions.",
    "skills/granoflow-milestone-coordination/SKILL.md",
    deps.readMilestoneCoordinationSkill,
    "granoflow-milestone-coordination",
  );
  read(
    "granoflow_task_authoring_skill",
    "Read the bundled Granoflow Task Authoring skill. Create tasks via skeleton batches and create_one loops (full description batch size 1) with task-authoring-quality-contract. Does not run Analysis, Plan, or execution.",
    "skills/granoflow-task-authoring/SKILL.md",
    deps.readTaskAuthoringSkill,
    "granoflow-task-authoring",
  );
  read(
    "granoflow_portfolio_orchestrator_skill",
    "Read the bundled Granoflow Portfolio Orchestrator skill. After Project Definition, create all milestones then quality-author each milestone's tasks until Portfolio Ready. Orchestrates milestone-workflow and task-authoring; does not execute child work.",
    "skills/granoflow-portfolio-orchestrator/SKILL.md",
    deps.readPortfolioOrchestratorSkill,
    "granoflow-portfolio-orchestrator",
  );
  read(
    "granoflow_persistent_milestone_runner_skill",
    "Read the bundled provider-neutral Granoflow Persistent Milestone Runner skill. Use it for restart-safe milestone execution with leases, heartbeat, bounded attempt history, no-progress replanning, resumable interaction nodes, explicit authorization manifests, and evidence-gated completion. A separate user Skill may choose the worker command or model.",
    "skills/granoflow-persistent-milestone-runner/SKILL.md",
    deps.readPersistentMilestoneRunnerSkill,
    "granoflow-persistent-milestone-runner",
  );
  read(
    "granoflow_project_definition_skill",
    "Read the bundled Granoflow Project Definition skill. Activate with phrases such as Initialize this project, Define this project, 初始化这个项目, or 定义这个项目—not Initialize Granoflow. Runs three steps: Project Work intake (stack capability + skill routing), Design Baseline with Design Tokens, and landscape/portrait App Shell under contract fidelity; then hands off to portfolio-orchestrator.",
    "skills/granoflow-project-definition/SKILL.md",
    deps.readProjectDefinitionSkill,
    "granoflow-project-definition",
  );
  read(
    "granoflow_integration_test_campaign_skill",
    "Read the bundled Granoflow Integration Test Campaign skill. Call when the user wants a standard integration-test campaign (service_path / cross-module real I/O): orchestrate, auto-drive until green, plain-language closing summary. Not E2E UI/screenshots and not task-local write-only integration tests.",
    "skills/granoflow-integration-test-campaign/SKILL.md",
    deps.readIntegrationTestCampaignSkill,
    "granoflow-integration-test-campaign",
  );
  read(
    "granoflow_e2e_test_campaign_skill",
    "Read the bundled Granoflow E2E Test Campaign skill. Call after integration_campaign is green for the final test stage: build user-flow coverage from Project Work, author missing UI journeys, auto-fix bugs, capture screenshots under temp/ and always show them to the user. Not service_path-only integration campaigns.",
    "skills/granoflow-e2e-test-campaign/SKILL.md",
    deps.readE2eTestCampaignSkill,
    "granoflow-e2e-test-campaign",
  );
}

function registerBundledAndGfmcpTools(
  registerTool: ToolRegistrar,
  deps: FoundationDependencies,
): void {
  registerTool(
    "granoflow_bundled_skill_reference",
    "Read one public Markdown reference from a bundled Granoflow skill. Discover valid referenceId values from that skill's references manifest first. This read-only package operation does not call the Granoflow Local HTTP API or require an API token.",
    {
      skillId: z.enum(BUNDLED_SKILL_IDS),
      referenceId: z
        .string()
        .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/)
        .describe("Reference identifier from the selected skill's references manifest."),
    },
    async ({ skillId, referenceId }) => {
      try {
        return deps.jsonTextResult({
          ok: true,
          code: "ok",
          data: await deps.bundledSkillResources.readReference(
            String(skillId),
            String(referenceId),
          ),
        });
      } catch (error) {
        if (error instanceof WorkflowResourceError) {
          return deps.jsonTextResult({
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
      deps.apiTool({
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
      deps.apiTool({
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
    async () => deps.apiTool({ path: "/v1/tasks?tag=custom_gfmcp" }),
  );
}

export function registerSetupAndHealthTools(
  registerTool: ToolRegistrar,
  deps: FoundationDependencies,
): void {
  registerBundledAndGfmcpTools(registerTool, deps);
  registerTool(
    "granoflow_setup_status",
    "Inspect Granoflow MCP config and Local HTTP API health without printing secrets.",
    {},
    async () => deps.jsonTextResult(await deps.getSetupStatus()),
  );
  registerTool(
    "granoflow_setup_detect_local_api",
    "Probe a bounded localhost port list for Granoflow identity. This never scans all ports or writes config.",
    {
      ports: z.array(z.number().int().min(1).max(65_535)).max(20).optional(),
      timeoutMs: z.number().int().min(50).max(5_000).optional(),
    },
    async ({ ports, timeoutMs }) =>
      deps.jsonTextResult(
        await deps.detectLocalApi({
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
      deps.jsonTextResult(
        await deps.writeSetupConfig({
          apiBaseUrl: typeof apiBaseUrl === "string" ? apiBaseUrl : undefined,
          apiPort: typeof apiPort === "number" ? apiPort : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );
  registerTool(
    "granoflow_setup_open_config",
    "Create and optionally open the MCP-owned non-secret Granoflow config file.",
    { createIfMissing: z.boolean().default(true), open: z.boolean().default(false) },
    async ({ createIfMissing, open }) =>
      deps.jsonTextResult(
        await deps.openSetupConfig({
          createIfMissing: createIfMissing !== false,
          open: open === true,
        }),
      ),
  );
  registerTool(
    "granoflow_setup_open_app",
    "Preview or open the installed Granoflow app after user approval. Uses a cross-process launch lease for real opens, and refuses if another MCP launch is in progress, any Granoflow process is already running, or process state cannot be verified, even when the configured Local HTTP API URL or port is unreachable. Defaults to dry-run.",
    {
      appPath: z.string().min(1).optional(),
      appName: z.string().min(1).optional(),
      dryRun: z.boolean().default(true),
    },
    async ({ appName, appPath, dryRun }) =>
      deps.jsonTextResult(
        await deps.openGranoflowApp({
          appPath: typeof appPath === "string" ? appPath : undefined,
          appName: typeof appName === "string" ? appName : undefined,
          dryRun: dryRun !== false,
        }),
      ),
  );
  for (const [name, description, path] of [
    ["granoflow_health", "Check whether the Granoflow Local HTTP API is reachable.", "/v1/health"],
    ["granoflow_version", "Show Granoflow app and Local HTTP API version metadata.", "/v1/version"],
    [
      "granoflow_capabilities",
      "List capabilities exposed by the running Granoflow app.",
      "/v1/capabilities",
    ],
    [
      "granoflow_ai_agent_tools",
      "List Granoflow AI-agent tool contracts from the running app. Use with granoflow_agent_workflow_skill for task, review, and memory-style questions.",
      "/v1/ai-agent/tools",
    ],
  ] as const) {
    registerTool(name, description, {}, async () => deps.apiTool({ path }));
  }
}
