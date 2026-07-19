import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-budget-and-modes", () => {
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

  it("defines one read-only Git detection and workflow owner", () => {
    const git = reference("git-capability-detection.md");
    for (const contract of [
      "granoflow_agent_preferences_get",
      "granoflow_git_missing_notice_record",
      "current_branch",
      "develop",
      "git_flow",
      "normal skip",
    ]) {
      expect(git).toContain(contract);
    }
    expect(git).toMatch(/Preferences[\s\S]*never authorize push/i);
    expect(git).toMatch(/Detection[\s\S]*must not change refs/i);
  });

  it("defines one test-gated local Git checkpoint owner", () => {
    const git = reference("git-checkpoint-workflow.md");
    const workflow = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
    for (const contract of [
      "git add -A",
      "--no-verify",
      "task-owned",
      "Never push automatically",
    ]) {
      expect(git).toContain(contract);
    }
    expect(workflow).toContain("git-checkpoint-workflow.md");
  });
});
