import { execFile } from "node:child_process";
import { promisify } from "node:util";

import { describe, expect, it } from "vitest";

const execFileAsync = promisify(execFile);

describe("granoflow MCP server executable", () => {
  it("prints a version without starting stdio transport", async () => {
    const { stdout, stderr } = await execFileAsync(process.execPath, [
      "dist/index.js",
      "--version",
    ]);

    expect(stdout.trim()).toBe("0.1.0");
    expect(stderr).toBe("");
  });

  it("prints help without starting stdio transport", async () => {
    const { stdout, stderr } = await execFileAsync(process.execPath, ["dist/index.js", "--help"]);

    expect(stdout).toContain("granoflow-mcp-server 0.1.0");
    expect(stdout).toContain("GRANOFLOW_API_BASE_URL");
    expect(stdout).toContain("GRANOFLOW_MCP_CONFIG_PATH");
    expect(stderr).toBe("");
  });
});
