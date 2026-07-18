import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("Task Delivery and Deferred Task Review contracts", () => {
  it("publishes one structural-budget owner from init through delivery", () => {
    const budget = reference("software-structural-budget.md");
    const software = reference("task-analysis-profile-software-development.md");
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    const modes = reference("execution-modes-and-acceptance-reports.md");
    const delivery = reference("task-delivery-profile-software-development.md");

    const normalizedBudget = budget.replace(/\s+/g, " ");
    expect(normalizedBudget).toMatch(/production source \| 400 \/ 600 \| 60 \/ 100/);
    expect(normalizedBudget).toMatch(/tests \| 700 \/ 1000 \| 100 \/ 150/);
    expect(budget).toContain("does not require confirmation");
    expect(budget).toContain("recorded_pending_enforcement");
    expect(budget).toContain("Structural Change Forecast");
    expect(budget).toMatch(/execution notice, not a user-confirmation gate/i);
    for (const consumer of [software, workflow, template, modes, delivery]) {
      expect(consumer).toContain("software-structural-budget.md");
    }
    expect(workflow).toMatch(/unattended mode[\s\S]*continues/i);
    expect(delivery).toContain("actual final file and function/method sizes");
  });

  it("enforces one semantic minimum-change budget from authoring through acceptance", () => {
    const authoring = reference("task-authoring-quality-contract.md");
    const software = reference("task-analysis-profile-software-development.md");
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const delivery = reference("task-delivery-profile-software-development.md");
    const acceptance = reference("execution-modes-and-acceptance-reports.md");

    for (const contract of [authoring, software, template]) {
      const normalized = contract.replace(/\s+/g, " ");
      expect(normalized).toContain("required changes");
      expect(normalized).toContain("allowed touchpoints");
      expect(normalized).toContain("protected surfaces");
    }
    expect(authoring).toMatch(/smallest complete semantic change/i);
    expect(authoring).toMatch(/prototype\nonly the authorized delta/i);
    expect(authoring).toMatch(/whole-page redesign/i);
    expect(software).toMatch(/drive-by refactor/i);
    expect(workflow).toMatch(/map to a required change through Outcome or Evidence/i);
    expect(workflow).toMatch(/scope drift until confirmed/i);
    expect(delivery).toContain("planned-versus-actual minimum-change budget");
    expect(delivery).toContain("unplanned UI, code, API, schema, dependency, or architecture");
    expect(acceptance).toContain("planned-versus-actual minimum-change budget");
  });

  it("defines explicit execution modes, capability lanes, and always-on acceptance HTML", () => {
    const modes = reference("execution-modes-and-acceptance-reports.md");
    const workflow = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    for (const mode of ["interactive", "unattended", "layered_handoff"]) {
      expect(modes).toContain(mode);
    }
    for (const lane of [
      "[analysis]",
      "[plan]",
      "[dev]",
      "[test]",
      "[integration]",
      "[user]",
      "[action]",
      "[confirm]",
    ]) {
      expect(modes).toContain(lane);
    }
    expect(modes).toContain("legacy_v1");
    expect(modes).toContain("batch_v2");
    expect(modes).toMatch(/cannot\nreliably identify its own model or reasoning tier/i);
    expect(modes).toContain("acceptance_report");
    expect(modes).toContain("not_required");
    expect(modes).toContain("planned_not_run");
    expect(modes).toMatch(/Every implementation produces a self-contained acceptance HTML/i);
    expect(workflow).toContain("execution-modes-and-acceptance-reports.md");
  });

  it("gives unattended runs one general zero-interruption contract", () => {
    const interaction = reference("unattended-interaction-contract.md");
    const normalizedInteraction = interaction.replace(/\s+/g, " ");
    const modes = reference("execution-modes-and-acceptance-reports.md");
    const taskWork = reference("task-work-document-workflow.md");
    const orchestrator = readFileSync(
      "skills/granoflow-task-orchestrator/references/end-to-end-orchestration.md",
      "utf8",
    );
    const delegated = readFileSync("skills/granoflow-delegated-authorization/SKILL.md", "utf8");

    expect(interaction).toContain("interaction_budget: 0");
    for (const phase of [
      "Analysis confirmation",
      "Planning permission",
      "Plan confirmation",
      "Execution authorization",
      "test repair",
      "Delivery",
      "completion",
    ]) {
      expect(normalizedInteraction).toContain(phase);
    }
    for (const blockerClass of [
      "direction_change",
      "scope_drift",
      "forbidden_action",
      "missing_user_only_input",
      "subjective_acceptance",
    ]) {
      expect(interaction).toContain(blockerClass);
    }
    expect(normalizedInteraction).toMatch(
      /complete all independent safe work.*one batched question/i,
    );
    expect(normalizedInteraction).toMatch(
      /same active run.*does not require an envelope round trip/i,
    );
    expect(normalizedInteraction).toMatch(/later host turn.*confirmed envelope/i);
    expect(taskWork).toMatch(
      /qualifying current\s+unattended instruction is explicit authorization/i,
    );
    expect(taskWork).toMatch(/Agent self-confirmation\s+is not/i);
    for (const consumer of [modes, taskWork, orchestrator, delegated]) {
      expect(consumer).toContain("unattended-interaction-contract.md");
    }
  });

  it("routes task lifecycle intent through one context-aware orchestrator", () => {
    const orchestrator = readFileSync("skills/granoflow-task-orchestrator/SKILL.md", "utf8");
    const shortCommands = readFileSync(
      "skills/granoflow-task-orchestrator/references/short-command-contract.md",
      "utf8",
    );
    const agentWorkflow = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const delegated = readFileSync("skills/granoflow-delegated-authorization/SKILL.md", "utf8");

    for (const route of ["capture", "enrich", "analyze", "plan", "run", "finish_audit"]) {
      expect(orchestrator).toContain(route);
    }
    for (const shortcut of ["gf记", "gf析", "gf规", "gf做", "gf完"]) {
      expect(shortCommands).toContain(shortcut);
    }
    expect(agentWorkflow).toContain("granoflow_task_orchestrator_skill");
    expect(delegated).toContain("gf-local-safe-v1");
    expect(shortCommands).toMatch(/Publish|publish/);
    expect(shortCommands).toContain("target is\nambiguous");
  });

  it("uses one cross-host Knowledge Distillation workflow and stable capability failure", () => {
    const workflow = reference("knowledge-distillation-workflow.md");
    const taskWorkflow = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const daily = readFileSync("skills/granoflow-daily-review/SKILL.md", "utf8");
    const fixture = JSON.parse(
      readFileSync("tests/fixtures/knowledge-distillation-hosts.json", "utf8"),
    ) as {
      hosts: string[];
      requiredTools: string[];
      stableUnsupportedShape: { code: string };
    };

    expect(fixture.hosts).toEqual(["Cursor", "Codex", "Claude Code", "OpenCode", "OpenClaw"]);
    expect(fixture.stableUnsupportedShape.code).toBe("unsupported_capability");
    for (const tool of fixture.requiredTools) expect(workflow).toContain(tool);
    for (const lane of ["Evidence", "Experience", "Knowledge"]) {
      expect(workflow).toContain(lane);
    }
    expect(workflow).toMatch(/considered and rejected results remain zero-write/i);
    expect(workflow).toContain("Checklist, Skill, Linter, Test, App Guard");
    expect(workflow).toContain("full Task Work rewrite");
    expect(workflow).toContain("applied, validated, or contradicted");
    expect(taskWorkflow).toContain("knowledge-distillation-workflow.md");
    expect(daily).toMatch(/separate\s+Experience proposal pass/);
    expect(workflow).not.toMatch(/^## Grill Review$/m);
  });
  it("initializes Granoflow with one beginner-facing all-recommended Skill offer", () => {
    const onboarding = readFileSync("skills/granoflow-first-run-import/SKILL.md", "utf8");
    const catalog = readFileSync(
      "skills/granoflow-first-run-import/references/recommended-external-skills.md",
      "utf8",
    );

    expect(onboarding).toContain("Initialize Granoflow");
    expect(onboarding).toContain("初始化 Granoflow");
    expect(onboarding).toContain("recommended-external-skills.md");
    expect(onboarding).toContain("approved_all");
    expect(onboarding).toContain("capability_pack_not_ready");
    expect(onboarding).toMatch(/Ask exactly once/i);
    expect(onboarding).toMatch(/does not run[\s\S]*setup-matt-pocock-skills/i);

    for (const capability of [
      "Grill Finalizer",
      "Grill Me",
      "gstack",
      "Matt Pocock Skills",
      "Huashu Design",
      "Impeccable",
      "Apple Design",
      "GSAP Skills",
      "Baoyu Skills",
    ]) {
      expect(catalog).toContain(capability);
    }
    expect(catalog).toContain("granoflow_product_builder_v1");
    expect(catalog).toContain("complete recommended capability pack");
    expect(catalog).toContain("host-native confirmation");
    expect(catalog).toMatch(/runtime[\s\S]*only[\s\S]*relevant/i);
    expect(catalog).toContain("capability_pack_not_ready");

    const externalRouting = reference("external-skill-routing.md");
    expect(externalRouting).toContain("first-run onboarding contract");
    expect(externalRouting).toContain("default all-install choice");
    expect(externalRouting).toMatch(/installation breadth only[\s\S]*Runtime routing/i);
    expect(externalRouting).toContain("capability_pack_drift");
    expect(externalRouting).toMatch(/model_allowed[\s\S]*silently/i);

    const prompt = catalog.match(/## User Prompt\n([\s\S]*?)\n## /)?.[1] ?? "";
    expect(prompt).not.toBe("");
    for (const technicalField of [
      "repository",
      "license",
      "command",
      "scope",
      "reload",
      "network",
    ]) {
      expect(prompt.toLowerCase()).not.toContain(technicalField);
    }
  });

  it("uses one adaptive pre-execution Task Work Document for new tasks", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const capture = reference("discussed-requirement-task-capture.md");

    expect(template).toContain("document_type: task_work");
    expect(template).toContain("analysis_status: draft | awaiting_confirmation | confirmed");
    expect(template).toContain(
      "planning_status: not_assessed | not_required | draft | awaiting_confirmation | confirmed",
    );
    expect(template).toContain(
      "analysis_grill_status: not_run | passed | revisions_required | blocked",
    );
    expect(template).toContain(
      "readiness_grill_status: not_run | not_applicable | passed | revisions_required | blocked",
    );
    expect(template).toContain("prototype_requirement: required | not_required | conditional");
    expect(template).toContain("package_attachment_id");
    expect(template).toContain("package_sha256");
    expect(workflow).toContain("executionAdmission.allowed");
    expect(workflow).toContain("assetMode=file");
    expect(workflow).toMatch(/no\s+greater than 600 seconds/);
    expect(template).not.toContain("execution_status:");
    expect(template).toContain("pre-execution governance document");
    expect(template).toContain("five-\ndimension prose contract");
    expect(capture).toContain("Mandatory Description Standard");
    expect(capture).toContain("Title Standard");
    expect(capture).toContain("action verb + clear object or outcome");
    expect(capture).toContain("Do not make `Plan文档`");
    expect(capture).toContain("fluent, readable piece of task copy");
    expect(capture).toContain("not a\nquestionnaire");
    expect(capture).toContain("optional");
    expect(capture).toContain("evidence-based basis");
    expect(capture).not.toContain("Every task description must contain these five headings");
    expect(capture).toContain("历史工时未知");
    for (const core of ["Outcome", "Evidence", "Scope", "Risk", "Next Action"]) {
      expect(template).toContain(`## ${core}`);
    }
    expect(template).toContain("skill_routing: not_triggered");
    expect(template).toContain("card_checkpoint: not_triggered");
    expect(template).not.toContain("## Database / Migration");
    expect(template).not.toContain("## Execution Nodes");

    expect(workflow).toContain("Legal State Matrix");
    expect(workflow).toContain("invalid_task_work_state");
    expect(workflow).toContain("实施这个任务文档");
    expect(workflow).toContain("does not authorize execution");
    expect(workflow).toMatch(/complete, self-contained\s+checkpoint/);
    expect(workflow).toMatch(/App-owned content and\s+SHA-256/);
  });

  it("uses one task authoring quality contract across every creation route", () => {
    const contract = reference("task-authoring-quality-contract.md");
    const routeFiles = [
      "skills/granoflow-agent-workflow/references/discussed-requirement-task-capture.md",
      "skills/granoflow-task-orchestrator/SKILL.md",
      "skills/granoflow-milestone-workflow/references/milestone-collaboration-workflow.md",
      "skills/granoflow-project-definition/SKILL.md",
      "skills/granoflow-first-run-import/references/task-and-card-import.md",
      "skills/granoflow-delegated-authorization/references/host-routing-and-waiting.md",
    ];

    expect(contract).toContain("single semantic owner");
    expect(contract).toContain("non-programmer");
    expect(contract).toContain("one real analogy");
    expect(contract).toContain("one concrete example");
    expect(contract).toContain("task_authoring_quality_failed");
    expect(contract).toContain("old complete text");
    expect(contract).toContain("HTML prototype");
    expect(contract).toContain("two-dimensional Markdown table");
    expect(contract).toContain("bold formatting on every changed field");
    expect(contract).toContain("Mermaid flowchart");
    expect(contract).toContain("at most one such Markdown file per task");
    expect(contract).toContain("Human title-only quick capture");
    for (const path of routeFiles) {
      expect(readFileSync(path, "utf8")).toContain(
        "granoflow-agent-workflow/task-authoring-quality-contract",
      );
    }
  });

  it("keeps the initial draft analysis-only and gates attachment on two bundled Grills", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const routing = reference("external-skill-routing.md");
    const combined = `${template}\n${workflow}\n${skill}`;

    expect(combined).toMatch(/initial draft[\s\S]*Analysis.only/i);
    expect(combined).toMatch(/(?:must not|Do not) (?:contain|draft|add)[\s\S]*Execution Plan/i);
    expect(combined).toMatch(/Analysis Grill[\s\S]*before\s+Planning/i);
    expect(combined).toMatch(/automatically tell the user[\s\S]*readiness review/i);
    expect(combined).toMatch(/Execution Readiness Grill[\s\S]*before\s+(?:any\s+)?upload/i);
    for (const readiness of [
      "authorization",
      "login state",
      "credentials",
      "keys",
      "secret availability",
      "required data",
      "source materials",
      "tools and environment",
    ]) {
      expect(combined).toContain(readiness);
    }
    expect(combined).toMatch(/never (?:copy|persist)[\s\S]*secret value/i);
    expect(combined).toMatch(/upload does\s+not authorize execution/i);
    expect(workflow).toMatch(
      /analysis_grill_status=passed[\s\S]*readiness_grill_status=passed[\s\S]*uploaded/i,
    );
    expect(workflow).toMatch(
      /before the first authorized execution action[\s\S]*status=doing[\s\S]*App records/i,
    );
    expect(workflow).toMatch(/Analysis, Planning[\s\S]*must leave the task `pending`/i);
    expect(routing).toMatch(/MCP-bundled[\s\S]*mandatory phase gates/i);
    expect(routing).toMatch(/grill-finalizer[\s\S]*does not replace/i);
    for (const forbiddenHeading of [
      "## Grill Review",
      "## Analysis Grill",
      "## Execution Readiness Grill",
    ]) {
      expect(template).not.toContain(forbiddenHeading);
    }
    expect(combined).toMatch(/Grill[\s\S]*invisible authoring (?:gate|pass)/i);
    expect(combined).toMatch(/findings[\s\S]*revis(?:e|ing)[\s\S]*relevant[\s\S]*section/i);
    expect(combined).toMatch(/standalone Grill (?:heading|section)[\s\S]*forbidden/i);
    expect(combined).toMatch(/phase result[\s\S]*analysis_grill_status/i);
    expect(combined).toMatch(
      /(?:every completed bundled Grill|either bundled Grill)[\s\S]*full[\s-]*clean rewrite/i,
    );
    expect(combined).toMatch(/new versioned local (?:document|path|file)[\s\S]*work_version \+ 1/i);
    expect(combined).toMatch(/validate[\s\S]*delete the prior local file/i);
    expect(combined).toMatch(
      /only[\s\S]*rewritten (?:path|document|file)[\s\S]*hash[\s\S]*upload/i,
    );
    expect(combined).toContain("post_grill_rewrite_failed");
    expect(combined).toContain("post_grill_rewrite_required");
  });

  it("keeps comic as the static default and animation as an explicit extension", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const visualNarrative = reference("visual-narrative-task-work.md");

    expect(template).toContain("domain: <optional domain such as visual_narrative>");
    expect(template).toContain("task_mode: <optional domain mode such as comic | animation>");
    expect(workflow).toContain("visual-narrative-task-work.md");
    expect(workflow).toContain("Visual Narrative Mode");
    expect(visualNarrative).toContain("If the user does not specify a mode, default to `comic`");
    expect(visualNarrative).toContain(
      "Do not add timeline, motion, audio, transition, encoding, or playback nodes",
    );
    expect(visualNarrative).toContain("only after the user explicitly requests");
    expect(visualNarrative).toContain("Analysis confirmation does not authorize Planning");
    expect(visualNarrative).toContain("animation extension must not invalidate");
  });

  it("defines notes as the explanation and cards as study projections", () => {
    const cardSkill = readFileSync("skills/granoflow-review-card-draft/SKILL.md", "utf8");
    const defaults = readFileSync(
      "skills/granoflow-review-card-draft/references/card-quality-defaults.md",
      "utf8",
    );
    const authoring = reference("review-card-authoring.md");

    expect(cardSkill).toContain("one durable Note");
    expect(cardSkill).toContain("more concise front/back Cards");
    expect(defaults).toContain("two explicit components");
    expect(defaults).toContain("canonical explanation");
    expect(defaults).toContain("multiple independent recall units");
    expect(defaults).toMatch(/at least\s+one concrete example/);
    expect(defaults).toContain("plain-language analogy");
    expect(cardSkill).toMatch(/Every Note must contain at\s+least\s+one concrete example/);
    expect(
      readFileSync(
        "skills/granoflow-review-card-draft/references/lifecycle-card-checkpoints.md",
        "utf8",
      ),
    ).toContain("Before preview, validate every proposed Note");
    expect(authoring).toContain("two-part artifact");
  });

  it("defines thread image inspection and destination routing", () => {
    const visualEvidence = reference("thread-visual-evidence.md");
    expect(visualEvidence).toContain("Inventory the images actually present");
    expect(visualEvidence).toContain("task evidence");
    expect(visualEvidence).toContain("Note source/example");
    expect(visualEvidence).toContain("Card");
    expect(visualEvidence).toContain("read back the destination");
    expect(visualEvidence).toContain("visual_evidence: none");
  });

  it("selects true-false or multiple-choice cards only when the Note supports them", () => {
    const defaults = readFileSync(
      "skills/granoflow-review-card-draft/references/card-quality-defaults.md",
      "utf8",
    );
    const authoring = reference("review-card-authoring.md");
    expect(defaults).toContain("Use **true/false**");
    expect(defaults).toContain("Use **multiple-choice**");
    expect(defaults).toContain("options field rather than");
    expect(defaults).toContain("Do not force a choice format");
    expect(authoring).toContain("Card's options field");
  });

  it("keeps routine checks in the plan and reserves nodes for costly validation gates", () => {
    const workflow = reference("task-work-document-workflow.md");
    expect(workflow).toContain("Do not create a Granoflow node for every plan step");
    expect(workflow).toContain("deterministic checks such as unit tests, lint");
    expect(workflow).toContain("materially\nexpensive");
    expect(workflow).toContain("explicit opt-in gate");
    expect(workflow).toContain("Do not use a node merely because a test exists");
  });

  it("requires task descriptions to state a concrete failure or risk scenario", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("observed failure");
    expect(capture).toContain("who is affected");
    expect(capture).toContain("observable evidence");
    expect(template).toContain("cannot replace the scenario");
  });

  it("requires titles to expose the user-facing failure or result", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    expect(capture).toContain("user-facing problem, consequence");
    expect(capture).toContain("修复长请求被固定上限提前截断的问题");
    expect(capture).toContain("实现分层超时与移除静态 agent 限制");
    expect(skill).toContain("user-facing failure, consequence");
    expect(skill).toContain("internal architecture terms");
  });

  it("uses the task description as the factual seed for executable Task Work", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("user-facing factual summary");
    expect(workflow).toContain("starting source for Task Work");
    expect(workflow).toContain("must not invent facts");
    expect(template).toContain("factual seed");
    expect(template).toContain("merely repeats a title");
  });

  it("blocks persistence when the description fails the 30-second recall gate", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    expect(capture).toContain("Description Job: 30-Second Recall");
    expect(capture).toContain("Pre-Write Recall Gate");
    expect(capture).toContain(
      "generic workflow prose that could be pasted onto another task unchanged",
    );
    expect(workflow).toContain("30-second recall gate");
    expect(workflow).toContain("task_description_recall_gate_failed");
    expect(workflow).toMatch(/before upload, active-version selection, or completion/);
    expect(skill).toContain("30-second recall gate");
  });

  it("makes Task Work a source-grounded cold-start execution manual", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");

    expect(template).toContain("## Reader Summary");
    expect(template).toContain("## Facts And Source Discipline");
    expect(template).toContain(
      "directly inspected source files, screenshots, logs, or runtime state",
    );
    expect(template).toContain("### Step N: <plain-language action + result>");
    expect(template).toContain("Performer: agent | user | agent_then_user | shared");
    expect(template).toContain("client\nvisit");
    expect(template).toContain("## Cold-Handoff Completion Gate");
    expect(workflow).toContain("cold-start execution\nmanual");
    expect(workflow).toContain("task_work_cold_handoff_failed");
    expect(workflow).toContain("task_work_source_evidence_insufficient");
    expect(workflow).toContain("filename, path, title, or completion status proves only");
  });

  it("audits completed historical work without inventing a future plan", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    for (const document of [template, workflow, skill]) {
      expect(document).toContain("decision=completion_audit");
    }
    for (const section of [
      "Original Problem Or Event",
      "Actual Actions",
      "Actual Evidence",
      "Outcome And Differences",
      "Residuals / Unknowns",
    ]) {
      expect(template).toContain(section);
      expect(workflow).toContain(section);
    }
    expect(template).toContain("Do not invent a future plan");
    expect(workflow).toContain("Do not write a prospective Execution Plan");
  });

  it("limits Task Work to an execution slot and one post-completion revision", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");

    for (const document of [template, workflow, skill]) {
      expect(document).toContain("post_completion_revision");
      expect(document).toMatch(/at\s+most two/);
    }
    expect(template).toContain("document_slot: execution | post_completion_revision");
    expect(template).toContain("task_work_slot_count_exceeded");
    expect(template).toContain("Subsequent corrections update");
    expect(workflow).toContain("task_work_slot_identity_invalid");
    expect(workflow).toContain("unfinished `execution` slot");
    expect(workflow).toContain("Create that slot only once");
    expect(workflow).toContain("replacement is transactional");
    expect(skill).toContain("Before completion, every edit replaces the");
    expect(skill).toContain("later edits never create another slot");
  });

  it("keeps each problem as a separate paragraph and diagrams supplemental", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("each distinct problem as its own natural-language paragraph");
    expect(capture).toContain("does not replace it");
    expect(template).toContain("each problem as a separate natural-language paragraph");
  });

  it("requires semantic Markdown formatting for task writing", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    expect(capture).toContain("**bold**");
    expect(capture).toContain("_italics_");
    expect(capture).toContain("fenced code blocks");
    expect(template).toContain("Use Markdown semantically");
    expect(template).toContain("literal commands, APIs, fields, paths");
    expect(template).toContain("There is no formatting quota");
    expect(template).toContain("Plain paragraphs are valid");
  });

  it("applies Markdown semantics to the complete attached Task Work Document", () => {
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    expect(workflow).toContain("Task Work Markdown Quality");
    expect(workflow).toContain("attached Task Work Document");
    expect(template).toContain("complete attached Task Work Document");
    expect(template).toContain("is not a finished document");
  });

  it("reports local drafts honestly and reconciles after Local API recovery", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const workflow = reference("task-work-document-workflow.md");
    const combined = `${skill}\n${workflow}`;

    for (const state of [
      "bound_local_draft",
      "unbound_local_draft",
      "no_local_draft",
      "upload_blocked_api_unreachable",
      "attachment_readback_pending",
      "active_not_established",
      "reconciliation_required",
    ]) {
      expect(combined).toContain(state);
    }
    expect(combined).toContain("configuration_shadowed_by_env");
    expect(combined).toContain("reachable_auth_required");
    expect(combined).toMatch(/re-read the task, attachments, nodes, and task revision/i);
    expect(combined).toMatch(/execution\s+authorization does not survive/i);
    expect(combined).toMatch(/Only App-owned content or SHA-256 readback/i);
  });

  it("uses one lifecycle card-checkpoint owner across all task phases", () => {
    const owner = readFileSync(
      "skills/granoflow-review-card-draft/references/lifecycle-card-checkpoints.md",
      "utf8",
    );
    const work = reference("task-work-document-template.md");
    const delivery = reference("task-delivery-template.md");
    const review = reference("task-review-template.md");
    const completion = reference("task-completion-summary-template.md");

    expect(owner).toContain("task_work | execution | delivery | deferred_review");
    expect(owner).toContain(
      "status: completed | partial | deferred | conflict | verification_failed | not_applicable",
    );
    expect(owner).toContain("change_summary: changed | unchanged");
    expect(owner).toContain("approvedOperationIds");
    expect(owner).toContain("must not persist `previewToken`");
    expect(owner).toContain("projectTaskRequired=false");
    expect(owner).toContain("inboxTaskAuthoring=true");
    expect(owner).toContain("uncategorizedDeckFallback=true");
    expect(owner).toContain("task_not_found");

    for (const phaseTemplate of [delivery, review]) {
      expect(phaseTemplate).toContain("Card Checkpoint");
      expect(phaseTemplate).toContain("lifecycle-card-checkpoints.md");
    }
    expect(work).toContain("card_checkpoint: not_triggered");
    expect(work).toContain("Knowledge/Card Delta Trigger");
    expect(delivery).toContain("Disposition: accepted | superseded | deferred");
    expect(delivery).toContain("Card operation IDs");
    expect(completion).toContain("Delivery Card Checkpoint");
    expect(completion).toContain("Deferred Card Work");
    expect(completion).toContain("Card Verification Failures");
    expect(completion).not.toContain("card_checkpoint:");
  });

  it("uses base plus composable profiles without public local plan numbers", () => {
    const work = reference("task-work-document-template.md");
    const legacyAnalysis = reference("task-analysis-template.md");
    const legacyPlan = reference("task-plan-template.md");

    expect(work).toContain("profiles: [] | [learning] | [software_development]");
    expect(work).not.toMatch(/project_(73|76)/);
    expect(legacyAnalysis).toContain("legacy");
    expect(legacyPlan).toContain("legacy");
    expect(legacyAnalysis).toContain("Do not use it to create");
    expect(legacyPlan).toContain("Do not use it to create");
  });

  it("keeps Work Document nodes personal without assigning an owner", () => {
    const template = reference("task-work-document-template.md");

    expect(template).toContain("Execution Mode: agent | user_action | agent_then_user_acceptance");
    expect(template).not.toContain("Owner: AI | user | both");
    expect(template).toMatch(/The task always belongs\s+to the current individual user/);
    expect(template).toMatch(/The Agent is an execution tool, not the task\s+owner/);
  });

  it("requires concrete examples and material-boundary rationale", () => {
    const capture = reference("discussed-requirement-task-capture.md");
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const combined = `${capture}\n${template}\n${workflow}`;

    expect(combined).toMatch(/Every description must include at least one concrete example/i);
    expect(combined).toMatch(/meaningful choice, trade-off, or scope boundary/i);
    expect(combined).toMatch(/why this approach is reasonable/i);
    expect(combined).toMatch(
      /why the boundary belongs here|why the work stops at this boundary|why the boundary is set there/i,
    );
    expect(combined).toMatch(/do not invent a rationale|no material choice or boundary/i);
    expect(combined).toMatch(/cold-start reader/i);
    expect(combined).toMatch(/reproduction, inspection, or comparison/i);
    expect(combined).toMatch(/Do not fabricate an example|do not claim the Task Work is ready/i);
  });

  it("routes external Skills through one host-owned, authorization-safe contract", () => {
    const routing = reference("external-skill-routing.md");

    expect(routing).toContain("invocation_mode: model_allowed | user_only | unknown");
    expect(routing).toContain("phase: analysis | planning | execution | delivery | review");
    expect(routing).toContain("disable-model-invocation: true");
    expect(routing).toContain("declined");
    expect(routing).toContain("install_offered");
    expect(routing).toContain("pending_user_decision");
    expect(routing).toContain("model_fallback");
    expect(routing).toContain("capability_pack_drift");
    expect(routing).toMatch(/Do not reopen item-by-item installation choices/i);
    expect(routing).toMatch(/model_allowed[\s\S]*silently/i);
    expect(routing).toMatch(/rediscover[\s\S]*reload/i);
    expect(routing).toMatch(/grill-me[\s\S]*user_only/i);
    expect(routing).toMatch(/only[\s\S]*relevant[\s\S]*(?:provider|reviewer)/i);
    expect(routing).toMatch(/suggesting installation[\s\S]*does not authorize/i);
    expect(routing).toMatch(/Do not guess\s+an installation command/);
    expect(routing).toContain("Project and Granoflow rules take precedence");
    expect(routing).toMatch(/does not\s+authorize implementation/);
    expect(routing).not.toContain("Do not pause that fallback");
  });

  it("consumes a hash-verified delegated authorization before repeating a phase prompt", () => {
    const workflow = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
      "utf8",
    );
    const template = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-template.md",
      "utf8",
    );
    const waiting = readFileSync(
      "skills/granoflow-agent-workflow/references/waiting-for-user-input.md",
      "utf8",
    );
    const combined = `${workflow}\n${template}\n${waiting}`;

    expect(combined).toContain("granoflow_delegated_authorization_skill");
    expect(combined).toContain("authorizationOwnerTaskId");
    expect(combined).toContain("attachmentSha256");
    expect(combined).toContain("receiptVerified");
    expect(combined).toContain("analysisConfirmation");
    expect(combined).toContain("planningPermission");
    expect(combined).toContain("planConfirmation");
    expect(combined).toContain("executionAuthorization");
    expect(combined).toMatch(/decision=allowed[\s\S]*continue/i);
    expect(combined).toMatch(/decision=denied[\s\S]*waiting/i);
    expect(combined).toMatch(/tag[\s\S]*(?:not|never)[\s\S]*authorization/i);
  });

  it("offers relevant Grill helpers once and waits before honest fallback", () => {
    const routing = reference("external-skill-routing.md");
    const workflow = reference("task-work-document-workflow.md");
    const template = reference("task-work-document-template.md");
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const readme = readFileSync("README.md", "utf8");
    const active = `${routing}\n${workflow}\n${template}\n${skill}\n${readme}`;

    expect(template).toContain("install_offered");
    expect(template).toContain("pending_user_decision");
    expect(workflow).toMatch(/model_allowed[\s\S]*grill-finalizer/);
    expect(workflow).toMatch(/pending_user_decision[\s\S]*(?:wait|waiting)/i);
    expect(workflow).toMatch(/declined[\s\S]*model_fallback/);
    expect(active).toContain("disable-model-invocation: true");
    expect(active).toMatch(/user[_ -]only/i);
    expect(active).toMatch(/not (?:install|invoke)[\s\S]*(?:entire|whole) (?:family|series)/i);
    expect(active).toMatch(/installation authorization[\s\S]*does not authorize/i);
    expect(active).toMatch(
      /Bundle[\s\S]*installer[\s\S]*(?:license|licensing)[\s\S]*(?:redistribut|distribution)/i,
    );
    expect(active).not.toContain("immediately use bundled Grill");
    expect(active).not.toContain("falls back immediately");
    expect(active).not.toContain("complete bundled Grill");
  });

  it("records capability decisions only when Task Work triggers Skill routing", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const legacyAnalysis = reference("task-analysis-execution.md");
    const legacyPlan = reference("task-plan-workflow.md");

    expect(template).toContain("Capability And Skill Routing");
    expect(template).toContain("skill_routing: not_triggered");
    expect(template).toContain("external-skill-routing.md");
    expect(workflow).toContain("at most one directly relevant");
    expect(workflow).toContain("Never preload all Profiles");
    expect(legacyAnalysis).toContain("task-work-document-workflow.md");
    expect(legacyPlan).toContain("task-work-document-workflow.md");
  });

  it("publishes thin software routing without coupling every task to Matt Skills", () => {
    const skill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    const profile = reference("task-analysis-profile-software-development.md");
    const readme = readFileSync("README.md", "utf8");

    expect(skill).toContain("references/external-skill-routing.md");
    expect(skill).toContain("invocation permission");
    expect(profile).toMatch(/code, tests, builds, or an\s+engineering repository/);
    expect(profile).toContain("host-visible Skill metadata");
    expect(profile).toMatch(/Ordinary copywriting, manga, animation/);
    expect(readme).toContain("External Skill routing");
    expect(readme).toContain("user-only Skills");
    expect(readme).toContain("model capability fallback");
    expect(readme).toMatch(/does not scan or modify the host's global Skill environment/);
  });

  it("defines immutable Delivery with hash readback and single completion ownership", () => {
    const template = reference("task-delivery-template.md");
    const workflow = reference("task-delivery-workflow.md");

    for (const section of [
      "Final Outcome",
      "Deliverables",
      "Differences From Work Document",
      "Verification Evidence",
      "Residuals And Deferred Work",
      "Handoff And Usage",
      "Traceability",
    ]) {
      expect(template).toContain(section);
    }
    expect(template).toContain("content_sha256");
    expect(template).toContain("source_work_document");
    expect(template).not.toContain("source_analysis:");
    expect(template).not.toContain("source_plan:");
    expect(workflow).toContain("Legacy Delivery may read existing `source_analysis`");
    expect(workflow).toContain("Same filename/version plus same hash");
    expect(workflow).toContain("Filename-only list and HTTP success do not pass");
    expect(workflow).toContain("NodeService");
    expect(workflow).toContain("compatibility finish once");
    expect(workflow).toContain("create and read back Delivery first");
  });

  it("defines marker-safe resumable Review for inbox tasks", () => {
    const template = reference("task-review-template.md");
    const workflow = reference("task-review-workflow.md");

    expect(template).toContain("<!-- granoflow-task-review:v1:start -->");
    expect(template).toContain("<!-- granoflow-task-review:v1:end -->");
    expect(template).toContain("review_revision");
    expect(template).toContain("review_operation_id");
    expect(template).toContain("acceptance latency");
    expect(workflow).toContain("gaps over five minutes");
    expect(workflow).toContain("Completed inbox task");
    expect(workflow).toContain("expectedUpdatedAt");
    expect(workflow).toContain("Never replay completed steps");
  });

  it("defines completion-summary and milestone managed blocks", () => {
    const completion = reference("task-completion-summary-template.md");
    const promotion = reference("context-promotion-entry.md");

    expect(completion).toContain("granoflow-task-completion-summary:v1:start");
    expect(completion).toContain("Review status: pending | completed");
    expect(completion).toContain("task_completion_summary_markers_invalid");
    expect(promotion).toContain("granoflow-milestone-context:v1:start");
    expect(promotion).toContain("project_snapshot.yaml");
    expect(promotion).toContain("project_rules.yaml");
    expect(promotion).toContain("semantic similarity");
  });

  it("keeps ordinary completion separate from Review and cards in public docs", () => {
    const publicText = [
      readFileSync("README.md", "utf8"),
      readFileSync("docs/user-install-demo.md", "utf8"),
      readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8"),
    ].join("\n");

    expect(publicText).toContain("Deferred Task Review");
    expect(publicText).toContain("does not automatically create");
    expect(publicText).not.toContain("factual `taskReview` may be written automatically");
  });

  it("allows an explicitly requested daily review to orchestrate missing task reviews", () => {
    const workflow = reference("task-review-workflow.md");

    expect(workflow).toContain("explicitly requested daily review");
    expect(workflow).toContain("daily task ledger");
    expect(workflow).toContain("daily skill does not directly");
    expect(workflow).toContain("card outcome");
  });
});
