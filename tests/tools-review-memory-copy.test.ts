import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { installToolTestLifecycle, collectHandlers } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-review-memory-copy", () => {
  it("keeps daily review defaults flexible under one owner", () => {
    const dailySkill = readFileSync("skills/granoflow-daily-review/SKILL.md", "utf8");
    const dailyContract = readFileSync(
      "skills/granoflow-daily-review/references/daily-review-contract.md",
      "utf8",
    );
    const workflowReference = readFileSync(
      "skills/granoflow-agent-workflow/references/review-drafting.md",
      "utf8",
    );
    const combined = `${dailySkill}\n${dailyContract}`;

    expect(combined).toContain("Default display");
    expect(combined).toContain("not a required form");
    expect(combined).toContain("reorganize the draft");
    expect(combined).toContain("journal/report `content`");
    expect(combined).toContain("not task count");
    expect(combined).toContain("Do not diagnose");
    expect(combined).toContain("daily task ledger");
    expect(combined).toContain("reviewed_and_readback");
    expect(combined).toContain("card outcome");
    expect(combined).toContain("does not directly write `taskReview`");
    expect(combined).toContain("rework evidence");
    expect(workflowReference).toContain("granoflow_daily_review_skill");
    expect(workflowReference).not.toContain("## Daily Reviews");
  });

  it("keeps public workflow catalog copy English-only while skills support localized triggers", () => {
    const publicDocs = [
      readFileSync("README.md", "utf8"),
      readFileSync("docs/user-install-demo.md", "utf8"),
      readFileSync("docs/directory-listings.md", "utf8"),
    ].join("\n");

    expect(publicDocs).toContain("Initialize Granoflow");
    expect(publicDocs).toContain("recommended AI capability collections");
    expect(publicDocs).toContain("Process today's tasks");
    expect(publicDocs).toContain("approval or missing information");
    expect(publicDocs).toContain("Create a task from this requirement");
    expect(publicDocs).toContain("project, milestone, or inbox");
    expect(publicDocs).toContain("Analyze the first task");
    expect(publicDocs).toContain("AI recommendations");
    expect(publicDocs).toContain("before planning");
    expect(publicDocs).toContain("any agent-assisted work");
    expect(publicDocs).toContain("especially useful for software projects");
    expect(publicDocs).toContain("work is no longer a black box");
    expect(publicDocs).toContain("tomorrow, next month, or next year");
    expect(publicDocs).toContain("instead of inventing a fresh plan every time");
    expect(publicDocs).toContain("fragmenting the project");
    expect(publicDocs).not.toContain("write today's journal");
    expect(publicDocs).not.toContain("write a weekly report");
    expect(publicDocs).not.toContain("write a monthly report");
    expect(publicDocs).not.toContain("初始化 Granoflow 并导入数据");
    expect(publicDocs).not.toContain("处理今日任务");
    expect(publicDocs).not.toContain("需要我授权或补充信息时");
    expect(publicDocs).not.toContain("把我们讨论的需求建一个任务");
    expect(publicDocs).not.toContain("请分析第一个任务");

    const skills = [
      readFileSync("skills/granoflow-first-run-import/SKILL.md", "utf8"),
      readFileSync(
        "skills/granoflow-agent-workflow/references/daily-pending-task-triage.md",
        "utf8",
      ),
      readFileSync("skills/granoflow-agent-workflow/references/waiting-for-user-input.md", "utf8"),
      readFileSync(
        "skills/granoflow-agent-workflow/references/discussed-requirement-task-capture.md",
        "utf8",
      ),
      readFileSync(
        "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
        "utf8",
      ),
    ].join("\n");

    expect(skills).toContain("初始化 Granoflow 并导入数据");
    expect(skills).toContain("处理今日任务");
    expect(skills).toContain("把我们讨论的需求建一个任务");
    expect(skills).toContain("请分析第一个任务");
    expect(skills).toContain("strong match");
    expect(skills).toContain("omitting both `projectId` and `milestoneId`");
    expect(skills).toContain("notification task");
    expect(skills).toContain("synced_to_server");
    expect(skills).toContain("unknown_remote_visibility");
    expect(skills).toContain("user's language");
  });

  it("nudges agents toward memory guidance through tool descriptions", () => {
    const { descriptions } = collectHandlers();

    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain("long-term work memory");
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain(
      "Create a task from this requirement",
    );
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain("Analyze the first task");
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain("one selected task");
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain("discussed requirement");
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain("Process today's tasks");
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain("their own language");
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain(
      "needs approval or missing information",
    );
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain(
      "granoflow_first_run_import_skill",
    );
    expect(descriptions.get("granoflow_agent_workflow_skill")).toContain(
      "granoflow_daily_review_skill",
    );
    expect(descriptions.get("granoflow_daily_review_skill")).toContain("explicitly asks");
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("Initialize Granoflow");
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain(
      "all unavailable recommended AI capability collections",
    );
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("their own language");
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("Cursor");
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("monthly milestones");
    expect(descriptions.get("granoflow_task_export")).toContain("reusable lessons");
    expect(descriptions.get("granoflow_ai_agent_tools")).toContain("memory-style questions");
    expect(descriptions.get("granoflow_review_card_draft_skill")).toContain(
      "lifecycle Card Checkpoint",
    );
    expect(descriptions.get("granoflow_review_card_authoring_preview")).toContain("inbox task");
    expect(descriptions.get("granoflow_task_create_structured")).toContain(
      "today, tomorrow, or the milestone deadline",
    );
    expect(descriptions.get("granoflow_task_create")).toContain("authoringEvidence");
    expect(descriptions.get("granoflow_task_create_structured")).toContain(
      "real-analogy and concrete-example",
    );
    expect(descriptions.get("granoflow_task_create_structured")).toContain("App records startedAt");
    expect(descriptions.get("granoflow_task_create")).toContain("pending state");
    expect(descriptions.get("granoflow_task_update_structured")).toContain("status=doing");
    expect(descriptions.get("granoflow_task_history_mutate")).toContain(
      "Every create mutation requires",
    );
    expect(descriptions.get("granoflow_task_update_structured")).toContain(
      "today, tomorrow, or the milestone deadline",
    );
  });
});
