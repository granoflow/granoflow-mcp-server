import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { mkdtemp, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

import { afterEach, beforeEach } from "vitest";
import { describe, expect, it } from "vitest";
import type { z } from "zod";

import { registerGranoflowTools } from "../src/tools.js";

const servers: Array<{ close: () => Promise<void> }> = [];

async function startServer(
  handler: (request: IncomingMessage, response: ServerResponse) => void,
): Promise<number> {
  const server = createServer(handler);
  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });
  servers.push({
    close: () =>
      new Promise((resolve, reject) => {
        server.close((error) => (error ? reject(error) : resolve()));
      }),
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Expected TCP test server address.");
  }
  return address.port;
}

function parseToolText(result: unknown): unknown {
  const content = (result as { content: Array<{ text: string }> }).content;
  return JSON.parse(content[0].text);
}

function collectHandlers() {
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

  return handlers;
}

function localDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

afterEach(async () => {
  delete process.env.GRANOFLOW_API_BASE_URL;
  delete process.env.GRANOFLOW_MCP_CONFIG_PATH;
  while (servers.length > 0) {
    const server = servers.pop();
    if (server) {
      await server.close();
    }
  }
});

beforeEach(async () => {
  const dir = await mkdtemp(join(tmpdir(), `granoflow-mcp-tools-${process.pid}-`));
  process.env.GRANOFLOW_MCP_CONFIG_PATH = join(dir, "config.json");
  await writeFile(
    process.env.GRANOFLOW_MCP_CONFIG_PATH,
    `${JSON.stringify({ dailyReviewSuggestionLastShownDate: localDateKey(new Date()) }, null, 2)}\n`,
  );
});

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
        "granoflow_agent_workflow_skill",
        "granoflow_setup_detect_local_api",
        "granoflow_setup_write_config",
        "granoflow_setup_open_config",
        "granoflow_setup_open_app",
        "granoflow_version",
        "granoflow_task_create_structured",
        "granoflow_task_update",
        "granoflow_task_update_structured",
        "granoflow_task_finish",
        "granoflow_task_resolve",
        "granoflow_project_resolve",
        "granoflow_project_create",
        "granoflow_project_update",
        "granoflow_project_delete",
        "granoflow_milestone_list",
        "granoflow_milestone_resolve",
        "granoflow_milestone_create",
        "granoflow_milestone_update",
        "granoflow_milestone_delete",
        "granoflow_api_request",
      ]),
    );
  });

  it("exposes the bundled public Granoflow workflow skill", async () => {
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_agent_workflow_skill")?.({});

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-agent-workflow/SKILL.md",
        skill: expect.stringContaining("User Dissatisfaction"),
      },
    });
    expect(JSON.stringify(parseToolText(result))).toContain("wrapper skill");
  });

  it("previews structured task creation through the Local HTTP API", async () => {
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_task_create_structured")?.({
      title: "Ship MCP v0",
      description: "Release the package.",
      remindAt: "2026-07-05T10:05:00.000",
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
          remindAt: "2026-07-05T10:05:00.000",
        },
      },
    });
    expect(JSON.stringify(parseToolText(result))).not.toContain('"tags"');
  });

  it("previews structured task reminder updates through the Local HTTP API", async () => {
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_task_update_structured")?.({
      taskId: "task-1",
      remindAt: "2026-07-05T10:10:00.000",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/tasks/task-1",
        body: {
          remindAt: "2026-07-05T10:10:00.000",
        },
      },
    });
  });

  it("previews milestone creation through the Local HTTP API", async () => {
    const handlers = collectHandlers();

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

  it("previews finishing a task as a multi-step dry-run", async () => {
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_task_finish")?.({
      taskId: "task-1",
      projectId: "project-1",
      milestoneId: "milestone-1",
      summary: "Finished with durable learning.",
      startedAt: "2026-07-02T09:00:00.000",
      taskReview: "Done with evidence.",
      reviewCardDrafts: [
        {
          clientCardId: "card-1",
          cardType: "basic_qa",
          front: "What should be remembered?",
          back: "The durable lesson.",
        },
      ],
      endedAt: "2026-07-02T10:15:00.000",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        previewMode: "local_request_sequence_only",
        steps: expect.arrayContaining([
          expect.objectContaining({ method: "PATCH", path: "/v1/tasks/task-1" }),
          expect.objectContaining({ method: "POST", path: "/v1/tasks/task-1/complete" }),
          expect.objectContaining({
            method: "POST",
            path: "/v1/ai-agent/tasks/import",
            body: expect.objectContaining({
              "agent-id": "granoflow",
              "tool-id": "single_task_ai",
              data: expect.objectContaining({
                task_id: "task-1",
                project_id: "project-1",
                milestone_id: "milestone-1",
                task_review_update: {
                  mode: "replace",
                  content: "Done with evidence.",
                },
                review_card_drafts: [
                  expect.objectContaining({
                    client_card_id: "card-1",
                    card_type: "basic_qa",
                  }),
                ],
              }),
            }),
          }),
          expect.objectContaining({ method: "GET", path: "/v1/tasks" }),
        ]),
        finishGuidance: expect.arrayContaining([
          expect.stringContaining("startedAt and endedAt"),
          expect.stringContaining("Only pass taskReview"),
          expect.stringContaining("one reviewCardDraft"),
        ]),
      },
    });
  });

  it("requires project and milestone ids before importing review data", async () => {
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_task_finish")?.({
      taskId: "task-1",
      taskReview: "Worth keeping.",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "review_import_context_required",
      data: {
        requiredInput: {
          projectId: "Granoflow project id",
          milestoneId: "Granoflow milestone id",
        },
      },
    });
  });

  it("resolves task candidates without writing data", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      expect(request.method).toBe("GET");
      expect(request.url).toBe("/v1/tasks");
      response.end(
        JSON.stringify({
          ok: true,
          data: {
            items: [
              { id: "task-1", title: "Ship MCP", status: "pending", projectId: "project-1" },
              { id: "task-2", title: "Ship docs", status: "done", projectId: "project-1" },
            ],
          },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_task_resolve")?.({
      query: "Ship",
      matchMode: "contains",
      projectId: "project-1",
      includeDone: false,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "resolved",
      data: {
        entityType: "task",
        count: 1,
        matches: [expect.objectContaining({ id: "task-1", title: "Ship MCP" })],
      },
    });
  });

  it("previews safe project deletion and reports linked tasks", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/projects") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { items: [{ id: "project-1", title: "Granoflow MCP", status: "pending" }] },
          }),
        );
        return;
      }
      if (request.url === "/v1/tasks") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { items: [{ id: "task-1", title: "Linked", projectId: "project-1" }] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const handlers = collectHandlers();

    const result = await handlers.get("granoflow_project_delete")?.({
      projectId: "project-1",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        path: "/v1/projects/project-1",
        impact: {
          resource: { id: "project-1", title: "Granoflow MCP" },
          linkedTaskCount: 1,
        },
      },
    });
  });
});
