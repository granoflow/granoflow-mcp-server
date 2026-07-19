import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { afterEach } from "vitest";

export const servers: Array<{ close: () => Promise<void> }> = [];
export const tempPaths: string[] = [];

export async function writeMcpConfig(
  config: Record<string, unknown>,
  filePathOrEnv: string | { GRANOFLOW_MCP_CONFIG_PATH?: string } = join(
    tmpdir(),
    `granoflow-mcp-test-${process.pid}-${Date.now()}.json`,
  ),
): Promise<string> {
  const filePath =
    typeof filePathOrEnv === "string"
      ? filePathOrEnv
      : (filePathOrEnv.GRANOFLOW_MCP_CONFIG_PATH ??
        join(tmpdir(), `granoflow-mcp-test-${process.pid}-${Date.now()}.json`));
  await mkdir(join(filePath, ".."), { recursive: true });
  await writeFile(filePath, JSON.stringify(config), "utf8");
  return filePath;
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

export function installSetupTestLifecycle(): void {
  afterEach(async () => {
    while (servers.length > 0) {
      const server = servers.pop();
      if (server) {
        await server.close();
      }
    }
    await Promise.all(
      tempPaths.splice(0).map((path) => rm(path, { recursive: true, force: true })),
    );
  });
}
