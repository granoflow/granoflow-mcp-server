import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { promisify } from "node:util";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { describe, expect, it } from "vitest";

const execFileAsync = promisify(execFile);
const packageJson = JSON.parse(await readFile("package.json", "utf8")) as {
  version: string;
  bin: Record<string, string>;
};

async function readAgentReference(client: Client, referenceId: string) {
  const result = await client.callTool({
    name: "granoflow_bundled_skill_reference",
    arguments: { skillId: "granoflow-agent-workflow", referenceId },
  });
  const text = result.content.find((item) => item.type === "text");
  return JSON.parse(text?.type === "text" ? text.text : "null") as {
    ok: boolean;
    data: { content: string; path: string };
  };
}

describe("granoflow MCP server executable", () => {
  it("keeps one unambiguous npm-exec bin", () => {
    expect(packageJson.bin["granoflow-mcp-server"]).toBe("dist/index.js");
    expect(Object.keys(packageJson.bin)).toEqual(["granoflow-mcp-server"]);
  });

  it("prints a version without starting stdio transport", async () => {
    const { stdout, stderr } = await execFileAsync(process.execPath, [
      "dist/index.js",
      "--version",
    ]);

    expect(stdout.trim()).toBe(packageJson.version);
    expect(stderr).toBe("");
  });

  it("prints help without starting stdio transport", async () => {
    const { stdout, stderr } = await execFileAsync(process.execPath, ["dist/index.js", "--help"]);

    expect(stdout).toContain(`granoflow-mcp-server ${packageJson.version}`);
    expect(stdout).toContain("GRANOFLOW_API_BASE_URL");
    expect(stdout).toContain("GRANOFLOW_MCP_CONFIG_PATH");
    expect(stderr).toBe("");
  });

  it("dispatches the bundled GFMCP runner through the single public bin", async () => {
    const { stdout, stderr } = await execFileAsync(process.execPath, [
      "dist/index.js",
      "gfmcp-runner",
      "--help",
    ]);

    expect(stdout).toContain("Poll and safely execute GFMCP-tagged Granoflow tasks.");
    expect(stderr).toBe("");
  });

  it("lists and reads a bundled Analysis reference over the built MCP protocol", async () => {
    const client = new Client({ name: "granoflow-protocol-smoke", version: "1.0.0" });
    const transport = new StdioClientTransport({
      command: process.execPath,
      args: ["dist/index.js"],
      cwd: process.cwd(),
      env: { PATH: process.env.PATH ?? "" },
      stderr: "pipe",
    });

    try {
      await client.connect(transport);
      const tools = await client.listTools();
      expect(tools.tools.map((tool) => tool.name)).toContain("granoflow_bundled_skill_reference");

      const skillTools = [
        ["granoflow_agent_workflow_skill", "granoflow-agent-workflow"],
        ["granoflow_daily_review_skill", "granoflow-daily-review"],
        ["granoflow_first_run_import_skill", "granoflow-first-run-import"],
        ["granoflow_review_card_draft_skill", "granoflow-review-card-draft"],
        ["granoflow_gfmcp_runner_skill", "granoflow-gfmcp-runner"],
        ["granoflow_delegated_authorization_skill", "granoflow-delegated-authorization"],
        ["granoflow_task_orchestrator_skill", "granoflow-task-orchestrator"],
        ["granoflow_milestone_workflow_skill", "granoflow-milestone-workflow"],
        ["granoflow_milestone_coordination_skill", "granoflow-milestone-coordination"],
        ["granoflow_task_authoring_skill", "granoflow-task-authoring"],
        ["granoflow_portfolio_orchestrator_skill", "granoflow-portfolio-orchestrator"],
        ["granoflow_persistent_milestone_runner_skill", "granoflow-persistent-milestone-runner"],
        ["granoflow_project_definition_skill", "granoflow-project-definition"],
        ["granoflow_integration_test_campaign_skill", "granoflow-integration-test-campaign"],
      ] as const;
      for (const [toolName, skillId] of skillTools) {
        const skillResult = await client.callTool({ name: toolName, arguments: {} });
        const skillText = skillResult.content.find((item) => item.type === "text");
        const skillPayload = JSON.parse(skillText?.type === "text" ? skillText.text : "null") as {
          data: { references: Array<{ skillId: string }> };
        };
        expect(skillPayload.data.references.length).toBeGreaterThan(0);
        expect(skillPayload.data.references.every((item) => item.skillId === skillId)).toBe(true);
      }

      const result = await client.callTool({
        name: "granoflow_bundled_skill_reference",
        arguments: {
          skillId: "granoflow-agent-workflow",
          referenceId: "task-analysis-execution",
        },
      });
      const text = result.content.find((item) => item.type === "text");
      expect(text?.type).toBe("text");
      const payload = JSON.parse(text?.type === "text" ? text.text : "null") as {
        ok: boolean;
        data: { content: string; sha256: string; bytes: number; path: string };
      };
      const packaged = await readFile(
        "skills/granoflow-agent-workflow/references/task-analysis-execution.md",
        "utf8",
      );
      expect(payload).toMatchObject({
        ok: true,
        data: {
          path: "skills/granoflow-agent-workflow/references/task-analysis-execution.md",
          bytes: Buffer.byteLength(packaged),
          content: packaged,
          sha256: createHash("sha256").update(packaged).digest("hex"),
        },
      });

      const intakePayload = await readAgentReference(client, "requirement-intake-and-traceability");
      expect(intakePayload).toMatchObject({
        ok: true,
        data: {
          path: "skills/granoflow-agent-workflow/references/requirement-intake-and-traceability.md",
          content: expect.stringContaining("The inputs are evidence, not forms"),
        },
      });

      const parallelPayload = await readAgentReference(client, "parallel-task-execution");
      expect(parallelPayload).toMatchObject({
        ok: true,
        data: {
          path: "skills/granoflow-agent-workflow/references/parallel-task-execution.md",
          content: expect.stringContaining("Only `parallel_safe` pairs may share a batch"),
        },
      });

      const missingResult = await client.callTool({
        name: "granoflow_bundled_skill_reference",
        arguments: {
          skillId: "granoflow-agent-workflow",
          referenceId: "does-not-exist",
        },
      });
      const missingText = missingResult.content.find((item) => item.type === "text");
      expect(JSON.parse(missingText?.type === "text" ? missingText.text : "null")).toMatchObject({
        ok: false,
        code: "workflow_reference_not_found",
      });
    } finally {
      await client.close();
    }
  });
});
