import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

export async function tempConfigPath(name: string): Promise<string> {
  const dir = join(tmpdir(), `granoflow-mcp-${name}-${process.pid}-${Date.now()}`);
  await mkdir(dir, { recursive: true });
  return join(dir, "config.json");
}
