import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { mkdtemp, writeFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
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

async function readJsonBody(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const text = Buffer.concat(chunks).toString("utf8");
  return text.trim() ? JSON.parse(text) : null;
}

function parseToolText(result: unknown): unknown {
  const content = (result as { content: Array<{ text: string }> }).content;
  return JSON.parse(content[0].text);
}

function collectHandlers() {
  const handlers = new Map<string, (args: Record<string, unknown>) => Promise<unknown>>();
  const descriptions = new Map<string, string>();

  registerGranoflowTools({
    tool: (
      name: string,
      description: string,
      _schema: Record<string, z.ZodTypeAny>,
      handler: (args: Record<string, unknown>) => Promise<unknown>,
    ) => {
      handlers.set(name, handler);
      descriptions.set(name, description);
    },
  });

  return { descriptions, handlers };
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
        "granoflow_first_run_import_skill",
        "granoflow_setup_detect_local_api",
        "granoflow_setup_write_config",
        "granoflow_setup_open_config",
        "granoflow_setup_open_app",
        "granoflow_version",
        "granoflow_context_pack",
        "granoflow_memory_batch_preview",
        "granoflow_context_steward_status",
        "granoflow_project_context_update",
        "granoflow_milestone_context_update",
        "granoflow_milestone_context_archive",
        "granoflow_task_completion_record",
        "granoflow_review_card_record",
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
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_agent_workflow_skill")?.({});

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-agent-workflow/SKILL.md",
        skill: expect.stringContaining("User Dissatisfaction"),
      },
    });
    const serialized = JSON.stringify(parseToolText(result));
    expect(serialized).toContain("wrapper skill");
    expect(serialized).toContain("Long-Term Work Memory");
    expect(serialized).toContain("long-term-work-memory.md");
    expect(serialized).toContain("Process today's tasks");
    expect(serialized).toContain("处理今日任务");
    expect(serialized).toContain("Analyze the first task");
    expect(serialized).toContain("请分析第一个任务");
    expect(serialized).toContain("task-analysis-execution.md");
    expect(serialized).toContain("single-task workflow");
    expect(serialized).toContain("Create a task from this requirement");
    expect(serialized).toContain("把我们讨论的需求建一个任务");
    expect(serialized).toContain("discussed-requirement-task-capture.md");
    expect(serialized).toContain("explicit task-creation request is confirmation");
    expect(serialized).toContain("omit `projectId` and `milestoneId`");
    expect(serialized).toContain("user's language");
    expect(serialized).toContain("analysis document");
    expect(serialized).toContain("grill");
    expect(serialized).toContain("plan document");
    expect(serialized).toContain("Attach or safely link");
    expect(serialized).toContain("plain-language explanations");
    expect(serialized).toContain("notification task");
    expect(serialized).toContain("3 minutes");
    expect(serialized).toContain("10 minutes");
    expect(serialized).toContain("synced_to_server");
    expect(serialized).toContain("unknown_remote_visibility");
    expect(serialized).toContain("decision");
    expect(serialized).toContain("similar");
  });

  it("exposes the bundled first-run import workflow skill", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_first_run_import_skill")?.({});
    const parsed = parseToolText(result);

    expect(parsed).toMatchObject({
      ok: true,
      code: "ok",
      data: {
        path: "skills/granoflow-first-run-import/SKILL.md",
        skill: expect.stringContaining("Initialize Granoflow and import data"),
      },
    });
    const serialized = JSON.stringify(parsed);
    expect(serialized).toContain("初始化 Granoflow 并导入数据");
    expect(serialized).toContain("multilingual");
    expect(serialized).toContain("Cursor");
    expect(serialized).toContain("Codex");
    expect(serialized).toContain("Hermes");
    expect(serialized).toContain("Import Preview");
    expect(serialized).toContain("bounded batches");
    expect(serialized).toContain("hidden chat histories");
  });

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

  it("documents the discussed requirement task capture contract", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/discussed-requirement-task-capture.md",
      "utf8",
    );

    expect(reference).toContain("Create a task from this requirement");
    expect(reference).toContain("把我们讨论的需求建一个任务");
    expect(reference).toContain("quick capture");
    expect(reference).toContain("active milestone");
    expect(reference).toContain("omitting `projectId` and `milestoneId`");
    expect(reference).toContain("explicit task-creation request is confirmation");
    expect(reference).toContain("patch the missing field");
    expect(reference).toContain("Do not create review cards");
  });

  it("documents the task analysis and execution workflow contract", () => {
    const reference = readFileSync(
      "skills/granoflow-agent-workflow/references/task-analysis-execution.md",
      "utf8",
    );

    expect(reference).toContain("Analyze the first task");
    expect(reference).toContain("请分析第一个任务");
    expect(reference).toContain("first active task");
    expect(reference).toContain("project_context_orphaned");
    expect(reference).toContain("not_enough_information");
    expect(reference).toContain("waiting-for-user-input.md");
    expect(reference).toContain("card_context_unavailable");
    expect(reference).toContain("task_node_api_unavailable");
    expect(reference).toContain("Read the original task back");
    expect(reference).toContain("Execute only after user confirmation");
  });

  it("keeps public workflow catalog copy English-only while skills support localized triggers", () => {
    const publicDocs = [
      readFileSync("README.md", "utf8"),
      readFileSync("docs/user-install-demo.md", "utf8"),
      readFileSync("docs/directory-listings.md", "utf8"),
    ].join("\n");

    expect(publicDocs).toContain("Initialize Granoflow and import data");
    expect(publicDocs).toContain("Process today's tasks");
    expect(publicDocs).toContain("approval or missing information");
    expect(publicDocs).toContain("Create a task from this requirement");
    expect(publicDocs).toContain("project, milestone, or inbox");
    expect(publicDocs).toContain("Analyze the first task");
    expect(publicDocs).toContain("move it forward after your confirmation");
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
      readFileSync("skills/granoflow-agent-workflow/references/task-analysis-execution.md", "utf8"),
    ].join("\n");

    expect(skills).toContain("初始化 Granoflow 并导入数据");
    expect(skills).toContain("处理今日任务");
    expect(skills).toContain("把我们讨论的需求建一个任务");
    expect(skills).toContain("请分析第一个任务");
    expect(skills).toContain("strong match");
    expect(skills).toContain("omitting `projectId` and `milestoneId`");
    expect(skills).toContain("project_context_orphaned");
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
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain(
      "Initialize Granoflow and import data",
    );
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("their own language");
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("Cursor");
    expect(descriptions.get("granoflow_first_run_import_skill")).toContain("monthly milestones");
    expect(descriptions.get("granoflow_task_export")).toContain("reusable lessons");
    expect(descriptions.get("granoflow_ai_agent_tools")).toContain("memory-style questions");
  });

  it("previews structured task creation through the Local HTTP API", async () => {
    const { handlers } = collectHandlers();

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
    const { handlers } = collectHandlers();

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
    const { handlers } = collectHandlers();

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
    const { handlers } = collectHandlers();

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
    const { handlers } = collectHandlers();

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

  it("fails fast when enhanced review card fields are not advertised by the app", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [{ toolId: "single_task_ai", enabled: true }],
            },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_finish")?.({
      taskId: "task-1",
      projectId: "project-1",
      milestoneId: "milestone-1",
      taskReview: "Durable lesson.",
      reviewCardDrafts: [
        {
          clientCardId: "card-1",
          cardType: "basic_qa",
          front: "What is idempotent?",
          back: "A repeated operation has the same durable effect.",
          noteFields: [
            {
              key: "pronunciation",
              label: "Pronunciation",
              type: "text_to_speech",
              value: "idempotent",
              ttsLanguageCode: "en-US",
            },
          ],
          frontLayout: ["front", "pronunciation"],
          backLayout: ["back"],
        },
      ],
      confirmComplete: true,
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "review_card_draft_note_fields_unsupported",
      data: {
        unsupportedFields: ["noteFields", "frontLayout", "backLayout"],
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("previews historical task mutations through the dedicated AI-agent API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      source: { kind: "test", summary: "Backfill historical task." },
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "create",
          fields: {
            title: "Historical import",
            createdAt: "2026-07-01T09:00:00.000",
            startedAt: "2026-06-30T10:00:00.000",
          },
          reason: "Import existing work history.",
        },
      ],
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/tasks/historical-mutations",
        body: {
          dryRun: true,
          source: { kind: "test", summary: "Backfill historical task." },
          mutations: [
            expect.objectContaining({
              clientMutationId: "mutation-1",
              op: "create",
              fields: expect.objectContaining({
                createdAt: "2026-07-01T09:00:00.000",
                startedAt: "2026-06-30T10:00:00.000",
              }),
            }),
          ],
        },
      },
    });
  });

  it("previews context-pack requests through the dedicated AI-agent API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_context_pack")?.({
      scope: "repo",
      repo: "granoflow/mcp-server",
      query: "Fix flaky CI",
      limit: 8,
      client: "codex",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/context-pack",
        body: {
          scope: "repo",
          repo: "granoflow/mcp-server",
          query: "Fix flaky CI",
          limit: 8,
          client: "codex",
        },
      },
    });
  });

  it("previews memory batch preview requests through the dedicated AI-agent API", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_memory_batch_preview")?.({
      source: { client: "codex", threadId: "thread-1" },
      target: { projectId: "project-1", milestoneId: "milestone-1" },
      items: [
        {
          clientItemId: "item-1",
          kind: "task_completion",
          title: "Add batch memory preview",
          summary: "Preview before writing.",
          completedAt: "2026-07-07T10:00:00.000Z",
        },
      ],
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "POST",
        path: "/v1/ai-agent/memory-batches/preview",
        body: {
          source: { client: "codex", threadId: "thread-1" },
          target: { projectId: "project-1", milestoneId: "milestone-1" },
          dryRun: true,
          items: [
            expect.objectContaining({
              clientItemId: "item-1",
              title: "Add batch memory preview",
            }),
          ],
        },
      },
    });
  });

  it("previews project context description updates without extra fields", async () => {
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_project_context_update")?.({
      projectId: "project-1",
      description: "Current state: Granoflow MCP context steward is active.",
      evidenceSummary: "Implemented context steward plan.",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/projects/project-1",
        body: {
          description: "Current state: Granoflow MCP context steward is active.",
        },
        contextSteward: {
          target: "project",
          evidenceSummary: "Implemented context steward plan.",
          descriptionPolicy: "living_context",
        },
      },
    });
  });

  it("previews active milestone context updates after resolving milestone state", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/milestones") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [
                {
                  id: "milestone-1",
                  title: "Context steward",
                  status: "doing",
                  projectId: "project-1",
                },
              ],
            },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_context_update")?.({
      milestoneId: "milestone-1",
      projectId: "project-1",
      description: "Current phase: implementing context steward.",
      evidenceSummary: "Milestone remains active.",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/milestones/milestone-1",
        body: {
          projectId: "project-1",
          description: "Current phase: implementing context steward.",
        },
        contextSteward: {
          target: "active_milestone",
          descriptionPolicy: "living_context",
        },
      },
    });
    expect(requestedUrls).toEqual(["/v1/milestones"]);
  });

  it("blocks ordinary MCP milestone description updates when milestone is archived", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/milestones") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [
                {
                  id: "milestone-1",
                  title: "Archived milestone",
                  status: "archived",
                  projectId: "project-1",
                },
              ],
            },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const focused = await handlers.get("granoflow_milestone_context_update")?.({
      milestoneId: "milestone-1",
      description: "Should not be written.",
      evidenceSummary: "Attempted update.",
      dryRun: false,
    });
    const generic = await handlers.get("granoflow_milestone_update")?.({
      milestoneId: "milestone-1",
      description: "Should not be written.",
      dryRun: false,
    });

    expect(parseToolText(focused)).toMatchObject({
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
    });
    expect(parseToolText(generic)).toMatchObject({
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
    });
  });

  it("previews milestone archive context closure with parent project update", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/milestones") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [
                {
                  id: "milestone-1",
                  title: "Context steward",
                  status: "doing",
                  projectId: "project-1",
                },
              ],
            },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_context_archive")?.({
      milestoneId: "milestone-1",
      projectId: "project-1",
      closure: {
        finalOutcome: "Context steward shipped.",
        verification: "Tests passed.",
        followUpMovedTo: "Next active milestone.",
        projectDescription: "Current state: context steward shipped.",
      },
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "dry_run",
      data: {
        previewMode: "context_archive_closure",
        writesPerformed: false,
        steps: [
          expect.objectContaining({
            step: "finalize_milestone_context",
            path: "/v1/milestones/milestone-1/archive",
            appOwnedArchiveApiAvailable: false,
          }),
          expect.objectContaining({
            step: "update_parent_project_context",
            path: "/v1/projects/project-1",
            body: {
              description: "Current state: context steward shipped.",
            },
          }),
        ],
      },
    });
  });

  it("fails closed for real milestone archive context closure until app archive API exists", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/milestones") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [
                {
                  id: "milestone-1",
                  title: "Context steward",
                  status: "doing",
                  projectId: "project-1",
                },
              ],
            },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_context_archive")?.({
      milestoneId: "milestone-1",
      projectId: "project-1",
      closure: {
        finalOutcome: "Context steward shipped.",
        verification: "Tests passed.",
        followUpMovedTo: "Next active milestone.",
        projectDescription: "Current state: context steward shipped.",
      },
      dryRun: false,
      confirmArchive: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "milestone_archive_api_unavailable",
      data: {
        requiredCapability: "app_owned_milestone_archive_api",
        writesPerformed: false,
      },
    });
  });

  it("requires memory_batch_preview_v1 before calling memory batch preview", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { tools: [{ toolId: "granoflow_context_pack_v1", enabled: true }] },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_memory_batch_preview")?.({
      items: [{ title: "Add batch memory preview" }],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "memory_batch_preview_v1",
        endpoint: "/v1/ai-agent/memory-batches/preview",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("forwards memory batch preview after capability confirmation", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        requested.push({ method: request.method, url: request.url });
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [
                {
                  toolId: "granoflow_memory_batch_preview_v1",
                  enabled: true,
                  capabilities: {
                    memoryBatchPreview: {
                      capability: "memory_batch_preview_v1",
                      maxItems: 20,
                      writesPerformed: false,
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/memory-batches/preview") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            data: { previewMode: "server_side", writesPerformed: false, items: [] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_memory_batch_preview")?.({
      target: { projectId: "project-1" },
      items: [{ title: "Add batch memory preview" }],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        data: {
          previewMode: "server_side",
          writesPerformed: false,
        },
      },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/memory-batches/preview",
        body: {
          target: { projectId: "project-1" },
          items: [{ title: "Add batch memory preview" }],
          dryRun: true,
        },
      },
    ]);
  });

  it("requires context_pack_v1 before calling context-pack endpoints", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: { tools: [{ toolId: "single_task_ai", enabled: true }] },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_context_pack")?.({
      scope: "repo",
      repo: "granoflow/mcp-server",
      query: "Fix flaky CI",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "context_pack_v1",
        endpoint: "/v1/ai-agent/context-pack",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("forwards context-pack requests after capability confirmation", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        requested.push({ method: request.method, url: request.url });
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [
                {
                  toolId: "granoflow_context_pack_v1",
                  enabled: true,
                  capabilities: {
                    contextPack: {
                      capability: "context_pack_v1",
                      matchSignals: true,
                      recommendations: false,
                      embeddingScores: false,
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/context-pack") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            code: "ok",
            data: { model: "granoflow_task_review_card_context_v1", tasks: [] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_context_pack")?.({
      scope: "repo",
      repo: "granoflow/mcp-server",
      query: "Fix flaky CI",
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      data: {
        model: "granoflow_task_review_card_context_v1",
        tasks: [],
      },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/context-pack",
        body: {
          scope: "repo",
          repo: "granoflow/mcp-server",
          query: "Fix flaky CI",
          limit: 12,
          client: "mcp",
        },
      },
    ]);
  });

  it("previews controlled work-memory write endpoints without writing", async () => {
    const { handlers } = collectHandlers();

    const taskResult = await handlers.get("granoflow_task_completion_record")?.({
      repo: "granoflow/mcp-server",
      title: "Fix flaky CI",
      summary: "Fixed cache race.",
      outcome: "success",
      decisions: ["Use isolated cache."],
      dryRun: true,
    });
    const cardResult = await handlers.get("granoflow_review_card_record")?.({
      title: "CI cache race",
      problem: "Shared cache caused flaky CI.",
      solution: "Use isolated cache.",
      tags: ["ci"],
      dryRun: true,
    });

    expect(parseToolText(taskResult)).toMatchObject({
      code: "dry_run",
      data: { path: "/v1/ai-agent/task-completions" },
    });
    expect(parseToolText(cardResult)).toMatchObject({
      code: "dry_run",
      data: { path: "/v1/ai-agent/review-cards" },
    });
  });

  it("forwards controlled work-memory write endpoints after capability confirmation", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        requested.push({ method: request.method, url: request.url });
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [
                {
                  toolId: "granoflow_context_pack_v1",
                  enabled: true,
                  capabilities: {
                    contextPack: {
                      capability: "context_pack_v1",
                      matchSignals: true,
                      recommendations: false,
                      embeddingScores: false,
                    },
                    controlledWrites: {
                      taskCompletion: true,
                      reviewCard: "controlled_import_or_fail_closed",
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (
        request.url === "/v1/ai-agent/task-completions" ||
        request.url === "/v1/ai-agent/review-cards"
      ) {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            data: { status: "forwarded" },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    await handlers.get("granoflow_task_completion_record")?.({
      repo: "granoflow/mcp-server",
      title: "Fix flaky CI",
      summary: "Fixed cache race.",
      outcome: "success",
      decisions: ["Use isolated cache."],
      source: { taskId: "task-1", threadId: "thread-1" },
      dryRun: false,
    });
    await handlers.get("granoflow_review_card_record")?.({
      title: "CI cache race",
      problem: "Shared cache caused flaky CI.",
      solution: "Use isolated cache.",
      tags: ["ci"],
      source: { taskId: "task-1" },
      dryRun: false,
    });

    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/task-completions",
        body: {
          repo: "granoflow/mcp-server",
          title: "Fix flaky CI",
          summary: "Fixed cache race.",
          decisions: ["Use isolated cache."],
          outcome: "success",
          client: "mcp",
          source: { taskId: "task-1", threadId: "thread-1" },
        },
      },
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/review-cards",
        body: {
          title: "CI cache race",
          problem: "Shared cache caused flaky CI.",
          solution: "Use isolated cache.",
          tags: ["ci"],
          client: "mcp",
          source: { taskId: "task-1" },
        },
      },
    ]);
  });

  it("requires the historical task mutation capability before writing", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [{ toolId: "granoflow_task_history_mutate", enabled: true }],
            },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "softDelete",
          taskId: "task-1",
          reason: "Remove duplicate historical import.",
        },
      ],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "unsupported_capability",
      data: {
        requiredCapability: "historical_task_mutations_v1",
        endpoint: "/v1/ai-agent/tasks/historical-mutations",
      },
    });
    expect(requestedUrls).toEqual(["/v1/ai-agent/tools"]);
  });

  it("writes historical task mutations only after capability confirmation", async () => {
    const requested: Array<{ method?: string; url?: string; body?: unknown }> = [];
    const port = await startServer(async (request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/ai-agent/tools") {
        requested.push({ method: request.method, url: request.url });
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              tools: [
                {
                  toolId: "granoflow_task_history_mutate",
                  enabled: true,
                  capabilities: {
                    historicalTaskMutations: {
                      enabled: true,
                      capability: "historical_task_mutations_v1",
                      preservesHistoricalTimes: true,
                    },
                  },
                },
              ],
            },
          }),
        );
        return;
      }
      if (request.url === "/v1/ai-agent/tasks/historical-mutations") {
        requested.push({
          method: request.method,
          url: request.url,
          body: await readJsonBody(request),
        });
        response.end(
          JSON.stringify({
            ok: true,
            code: "historical_task_mutations_applied",
            data: { results: [{ clientMutationId: "mutation-1", ok: true }] },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_task_history_mutate")?.({
      source: { kind: "test" },
      mutations: [
        {
          clientMutationId: "mutation-1",
          op: "update",
          taskId: "task-1",
          fields: { startedAt: "2026-06-30T10:00:00.000" },
          reason: "Restore true start time.",
        },
      ],
      dryRun: false,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "historical_task_mutations_applied",
      data: { results: [{ clientMutationId: "mutation-1", ok: true }] },
    });
    expect(requested).toEqual([
      { method: "GET", url: "/v1/ai-agent/tools" },
      {
        method: "POST",
        url: "/v1/ai-agent/tasks/historical-mutations",
        body: {
          dryRun: false,
          source: { kind: "test" },
          mutations: [
            {
              clientMutationId: "mutation-1",
              op: "update",
              taskId: "task-1",
              fields: { startedAt: "2026-06-30T10:00:00.000" },
              reason: "Restore true start time.",
            },
          ],
        },
      },
    ]);
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
    const { handlers } = collectHandlers();

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
    const { handlers } = collectHandlers();

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
