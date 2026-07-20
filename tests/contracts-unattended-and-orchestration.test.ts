import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

describe("contracts-unattended-and-orchestration", () => {
  it("resolves project Agent preferences across workflow entrypoints without weakening gates", () => {
    const paths = [
      "skills/granoflow-task-orchestrator/SKILL.md",
      "skills/granoflow-milestone-workflow/SKILL.md",
      "skills/granoflow-milestone-coordination/SKILL.md",
      "skills/granoflow-project-definition/SKILL.md",
      "skills/granoflow-persistent-milestone-runner/SKILL.md",
    ];
    for (const path of paths) {
      const contract = readFileSync(path, "utf8");
      expect(contract).toContain("granoflow_agent_preferences_get");
      expect(contract).toMatch(/never (weaken|create authorization)/i);
    }
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
      "external_impossible",
      "subjective_acceptance",
    ]) {
      expect(interaction).toContain(blockerClass);
    }
    expect(interaction).toContain("Explicit Unattended Declaration");
    expect(interaction).toContain("Solvable work is authorized");
    expect(interaction).toContain("deferred_external_work");
    expect(interaction).toContain("Unattended Residual Report");
    expect(interaction).toContain("defer_item");
    expect(interaction).toContain("complete_with_residuals");
    expect(normalizedInteraction).toMatch(
      /Never block the queue/i,
    );
    expect(normalizedInteraction).toMatch(
      /same active run.*does not require an envelope round trip/i,
    );
    expect(normalizedInteraction).toMatch(/later host turn.*confirmed envelope/i);
    expect(normalizedInteraction).toMatch(
      /Note\/Card[\s\S]*residual rather than blocking engineering/i,
    );
    expect(interaction).toContain("auto_accept_recommendation");
    expect(interaction).toMatch(/Project Definition[\s\S]*adopt recommendations immediately/i);
    const projectDefinition = readFileSync(
      "skills/granoflow-project-definition/SKILL.md",
      "utf8",
    );
    expect(projectDefinition).toContain("unattended-interaction-contract");
    expect(projectDefinition).toContain("auto_accept_recommendation");
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
});
