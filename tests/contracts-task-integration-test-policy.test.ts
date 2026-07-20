import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const workflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
  "utf8",
);
const template = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-template.md",
  "utf8",
);
const delivery = readFileSync(
  "skills/granoflow-agent-workflow/references/task-delivery-profile-software-development.md",
  "utf8",
);
const deliveryWorkflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-delivery-workflow.md",
  "utf8",
);
const modes = readFileSync(
  "skills/granoflow-agent-workflow/references/execution-modes-and-acceptance-reports.md",
  "utf8",
);
const software = readFileSync(
  "skills/granoflow-agent-workflow/references/task-analysis-profile-software-development.md",
  "utf8",
);
const unattended = readFileSync(
  "skills/granoflow-agent-workflow/references/unattended-interaction-contract.md",
  "utf8",
);
const copyBoundary = readFileSync(
  "skills/granoflow-agent-workflow/references/user-visible-copy-boundary.md",
  "utf8",
);
const orchestrator = readFileSync("skills/granoflow-task-orchestrator/SKILL.md", "utf8");

describe("task integration test policy contracts", () => {
  it("requires unit sufficiency first, max two tests, and no agent execution", () => {
    expect(workflow).toContain("Task Integration Test Policy (manual run)");
    expect(workflow).toMatch(/Judge unit tests first/i);
    expect(workflow).toMatch(/Prefer unit tests/i);
    expect(workflow).toMatch(/At most \*\*2\*\*/i);
    expect(workflow).toMatch(/Do not execute/i);
    expect(workflow).toContain("not_run_manual_only");
    expect(workflow).toMatch(/Device is user-chosen/i);
    expect(workflow).toMatch(/user's local machine/i);
    expect(workflow).toContain("integration_test_device_unselected");

    for (const code of [
      "unit_test_sufficiency_unassessed",
      "integration_test_added_without_insufficiency",
      "integration_test_cap_exceeded",
      "integration_test_executed_by_agent",
      "integration_test_device_unselected",
    ]) {
      expect(workflow).toContain(code);
      expect(delivery).toContain(code);
      expect(deliveryWorkflow).toContain(code);
    }

    expect(template).toContain("unit_test_sufficiency:");
    expect(template).toContain("integration_test_requirement:");
    expect(template).toContain("integration_tests_added_count: 0 | 1 | 2");
    expect(template).toContain("integration_test_execution:");
    expect(template).toContain("integration_test_device_recommendation:");
    expect(template).toContain("integration_test_device:");
    expect(template).toMatch(/local_machine/);

    expect(software).toMatch(/at most \*\*2\*\* task-local integration tests/i);
    expect(software).toMatch(/do not execute/i);

    expect(modes).toContain("awaiting_manual_execution");
    expect(modes).toMatch(/not\*\* a license for the Agent to execute/i);
    expect(modes).toMatch(/humans run them/i);

    expect(unattended).toMatch(/do \*\*not\*\* run[\s\S]*integration tests/i);
    expect(orchestrator).toMatch(/at most 2 integration tests/i);
    expect(orchestrator).toContain("integration_test_executed_by_agent");
    expect(orchestrator).toMatch(/local machine/i);
    expect(orchestrator).toContain("integration_test_device_unselected");
  });

  it("forbids automated tests for copy-only / 文字验证 work", () => {
    expect(copyBoundary).toContain("Copy-Only Work: No Automated Tests");
    expect(copyBoundary).toContain("copy_change_tests_forbidden");
    expect(copyBoundary).toMatch(/Do not\*\* add, require, or run/i);
    expect(workflow).toContain("Copy-only exception");
    expect(workflow).toContain("copy_change_tests_forbidden");
    expect(template).toContain("copy_change_only:");
    expect(delivery).toContain("copy_change_tests_forbidden");
    expect(deliveryWorkflow).toContain("copy_change_tests_forbidden");
    expect(software).toMatch(/copy-only[\s\S]*no\*\* automated/i);
    expect(orchestrator).toContain("copy_change_tests_forbidden");
  });
});
