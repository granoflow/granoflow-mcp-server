import { describe, expect, it } from "vitest";
import type { z } from "zod";

import { registerGranoflowTools } from "../src/tools.js";

function parseToolText(result: unknown): unknown {
  const content = (result as { content: Array<{ text: string }> }).content;
  return JSON.parse(content[0].text);
}

describe("MCP tool registration", () => {
  it("registers setup tools on the MCP server surface", () => {
    const names: string[] = [];

    registerGranoflowTools({
      tool: (
        name: string,
        _description: string,
        _schema: Record<string, z.ZodTypeAny>,
        _handler: (args: Record<string, unknown>) => Promise<unknown>,
      ) => {
        names.push(name);
      },
    });

    expect(names).toEqual(
      expect.arrayContaining([
        "granoflow_setup_status",
        "granoflow_setup_detect_local_api",
        "granoflow_setup_write_config",
        "granoflow_setup_open_config",
        "granoflow_setup_open_app",
        "granoflow_version",
        "granoflow_task_create_structured",
        "granoflow_task_update",
        "granoflow_task_update_structured",
        "granoflow_project_create",
        "granoflow_project_update",
        "granoflow_milestone_list",
        "granoflow_milestone_create",
        "granoflow_milestone_update",
        "granoflow_api_request",
      ]),
    );
  });

  it("previews structured task creation through the Local HTTP API", async () => {
    const handlers = new Map<string, (args: Record<string, unknown>) => Promise<unknown>>();

    registerGranoflowTools({
      tool: (
        name: string,
        _description: string,
        _schema: Record<string, z.ZodTypeAny>,
        handler: (args: Record<string, unknown>) => Promise<unknown>,
      ) => {
        handlers.set(name, handler);
      },
    });

    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "Ship MCP v0",
      description: "Release the package.",
      projectId: "project-1",
      milestoneId: "milestone-1",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        path: "/v1/tasks",
        body: {
          projectId: "project-1",
        },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain('"tags"');
  });

  it("previews milestone creation through the Local HTTP API", async () => {
    const handlers = new Map<string, (args: Record<string, unknown>) => Promise<unknown>>();

    registerGranoflowTools({
      tool: (
        name: string,
        _description: string,
        _schema: Record<string, z.ZodTypeAny>,
        handler: (args: Record<string, unknown>) => Promise<unknown>,
      ) => {
        handlers.set(name, handler);
      },
    });

    const result = await handlers.get("granoflow_milestone_create")?.({
      projectId: "project-1",
      title: "First milestone",
      dueAt: "2026-07-08T23:59:59.000",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        path: "/v1/milestones",
        body: {
          projectId: "project-1",
        },
      },
    });
  });
});
