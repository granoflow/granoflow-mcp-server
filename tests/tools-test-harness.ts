import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { mkdtemp, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

import { afterEach, beforeEach, vi } from "vitest";
import type { z } from "zod";

import { registerGranoflowTools } from "../src/tools.js";

export const servers: Array<{ close: () => Promise<void> }> = [];

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
