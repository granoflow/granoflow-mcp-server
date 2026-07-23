import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { mkdtemp, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

import { afterEach, beforeEach, vi } from "vitest";
import type { z } from "zod";

import { registerGranoflowTools } from "../src/tools.js";
import { taskDescriptionSha256 } from "../src/tool-runtime-task-description-impact.js";

export const servers: Array<{ close: () => Promise<void> }> = [];
export const taskImpactDescription =
  "用户需要让任务保持清晰且可长期理解。打个比方，这像更新地图前先核对道路是否改变。例如，只调整提醒时间时不应重写目的。";
export const taskImpactUpdatedAt = "2026-07-23T10:00:00.000Z";

export function taskDescriptionImpactReview(
  reasonCode: string,
  decision: "unchanged" | "rewrite" = "unchanged",
) {
  return {
    reviewedTaskUpdatedAt: taskImpactUpdatedAt,
    reviewedDescriptionSha256: taskDescriptionSha256(taskImpactDescription),
    decision,
    reasonCode,
    rationale: "The changed fields were compared with the current task meaning.",
  };
}

export function writeTaskReadback(
  response: ServerResponse,
  overrides: Record<string, unknown> = {},
): void {
  response.end(
    JSON.stringify({
      ok: true,
      data: {
        entity: {
          id: "task-1",
          title: "保持任务描述准确",
          description: taskImpactDescription,
          status: "pending",
          updatedAt: taskImpactUpdatedAt,
          ...overrides,
        },
      },
    }),
  );
}

export async function startTaskReadbackServer(): Promise<void> {
  const port = await startServer((request, response) => {
    response.setHeader("content-type", "application/json");
    if (request.url === "/v1/tasks/task-1") {
      writeTaskReadback(response);
      return;
    }
    response.statusCode = 404;
    response.end(JSON.stringify({ ok: false }));
  });
  process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
}

export async function startServer(
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

export async function readJsonBody(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const text = Buffer.concat(chunks).toString("utf8");
  return text.trim() ? JSON.parse(text) : null;
}

export function parseToolText(result: unknown): unknown {
  const content = (result as { content: Array<{ text: string }> }).content;
  return JSON.parse(content[0].text);
}

export function collectHandlers() {
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

export function localDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function installToolTestLifecycle(): void {
  afterEach(async () => {
    vi.useRealTimers();
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
}
