import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { installToolTestLifecycle } from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-workflow-docs", () => {
  it("documents the long-term work memory reference contract", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/long-term-work-memory.md",
      "utf8",
    );

    expect(reference).toContain("Memory Intent Detection");
    expect(reference).toContain("Retrieval Order");
    expect(reference).toContain("Bounded Retrieval");
    expect(reference).toContain("Evidence Rules");
    expect(reference).toContain("Missing Memory Handling");
    expect(reference).toContain("Privacy And Local Content");
  });

  it("documents the project context attachment safety contract", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/project-context-attachments.md",
      "utf8",
    );

    expect(reference).toContain("project_snapshot.yaml");
    expect(reference).toContain("project_rules.yaml");
    expect(reference).toContain("smallest matching section");
    expect(reference).toContain("proposal or conflict report");
    expect(reference).toContain("fail closed");
    expect(reference).toContain("project_context_attachments_unchanged");
    expect(reference).toContain("Hard Gate: Pre-Change Conflict Check");
    expect(reference).toContain("project_context_check_missing");
    expect(reference).toContain("project_context_conflict_unconfirmed");
    expect(reference).toContain("project_context_decision_not_emitted");
    expect(reference).toContain("revise_code");
    expect(reference).toContain("revise_context_yaml");
    expect(reference).toMatch(/explicitly emit/i);
  });

  it("documents project-scoped adaptive explanation style", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/project-interaction-style.md",
      "utf8",
    );
    expect(reference).toContain("project_rules.yaml");
    expect(reference).toContain("newcomer");
    expect(reference).toContain("interaction_budget: 0");
    expect(reference).toContain("only_after_explicit_user_request");
    expect(reference).toContain("never_ask_style_questions");
    expect(reference).toContain("beginner_detailed");
    expect(reference).toContain("Every Granoflow record");
  });

  it("documents the discussed requirement task capture contract", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/discussed-requirement-task-capture.md",
      "utf8",
    );

    expect(reference).toContain("Create a task from this requirement");
    expect(reference).toContain("把我们讨论的需求建一个任务");
    expect(reference).toContain("quick-capture workflow");
    expect(reference).toContain("active milestone");
    expect(reference).toContain("omitting both `projectId` and `milestoneId`");
    expect(reference).toContain("`granoflow_task_create_structured` with `dryRun=false`");
    expect(reference).toContain("task id returned by creation");
    expect(reference).toMatch(/Do not resolve the\s+newly created task by title/);
    expect(reference).toContain("Only the project is clear");
    expect(reference).toContain("learning task");
    expect(reference).toContain("software-development task");
    expect(reference).toContain("general task");
    expect(reference).toContain("No Task Work Document");
    expect(reference).toContain("No historical retrieval or default duplicate search");
    expect(reference).toContain("任务已经放入「<项目名>」项目「<里程碑名>」里程碑。");
    expect(reference).toContain("任务已收录到收集箱。");
  });

  it("documents the adaptive Task Work Document workflow contract", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
      "utf8",
    );

    expect(reference).toContain("pre-execution control-plane artifact");
    for (const heading of ["Outcome", "Evidence", "Scope", "Risk", "Next Action"]) {
      expect(reference).toContain(heading);
    }
    expect(reference).toContain("analysis_status");
    expect(reference).toContain("planning_status");
    expect(reference).toContain("invalid_task_work_state");
    expect(reference).toContain("实施这个任务文档");
    expect(reference).toContain("does not authorize execution");
    expect(reference).toContain("SHA-256 back");
  });

  it("keeps one adaptive base template with thin learning and software profiles", () => {
    const base = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-template.md",
      "utf8",
    );
    const learning = readFileSync(
      "skills/granoflow-agent-workflow/references/task-analysis-profile-learning.md",
      "utf8",
    );
    const software = readFileSync(
      "skills/granoflow-agent-workflow/references/task-analysis-profile-software-development.md",
      "utf8",
    );

    for (const dimension of ["Outcome", "Evidence", "Scope", "Risk", "Next Action"]) {
      expect(base).toContain(dimension);
    }
    expect(base).toContain("planning_status");
    expect(learning).toContain("independent mastery");
    expect(learning).not.toContain("## 1. Trigger");
    expect(software).toContain("database table/schema judgment");
    expect(software).toContain("real user-visible surface");
    expect(software).not.toContain("## 1. Trigger");
  });

  it("documents optional Work Document nodes and legacy Plan compatibility", () => {
    const workflow = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
      "utf8",
    );
    const template = readFileSync(
      "skills/granoflow-agent-workflow/references/task-work-document-template.md",
      "utf8",
    );
    const learning = readFileSync(
      "skills/granoflow-agent-workflow/references/task-plan-profile-learning.md",
      "utf8",
    );
    const software = readFileSync(
      "skills/granoflow-agent-workflow/references/task-plan-profile-software-development.md",
      "utf8",
    );

    expect(workflow).toContain("task-work-<safe-task-id>-execution-v<work_version>.md");
    expect(workflow).toContain("delete the prior local file");
    expect(workflow).toContain("post_grill_rewrite_required");
    expect(workflow).toContain("granoflow_task_attachment_add_markdown");
    expect(workflow).toContain("Task Delivery");
    expect(workflow).toContain("Historical Task Analysis and Task Plan");
    expect(template).toContain("Delivery Standard");
    expect(template).toContain("Downstream Startup Requirements");
    expect(template).not.toContain("project_73");
    expect(template).not.toContain("project_76");
    expect(learning).toContain("independent mastery gate");
    expect(software).toContain("file and method responsibility/size budgets");
  });
});
