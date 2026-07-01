import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { promisify } from "node:util";

import { describe, expect, it } from "vitest";

const execFileAsync = promisify(execFile);
const packageJson = JSON.parse(await readFile("package.json", "utf8")) as { version: string };

describe("granoflow MCP server executable", () => {
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
});
