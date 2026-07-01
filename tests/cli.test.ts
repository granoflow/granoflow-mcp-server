import { describe, expect, it } from "vitest";

import { normalizeCliArgs, resolveCliCommand } from "../src/cli.js";

describe("granoflow CLI adapter", () => {
  it("defaults to the granoflow binary", () => {
    expect(resolveCliCommand({})).toBe("granoflow");
  });

  it("uses GRANOFLOW_CLI_PATH when provided", () => {
    expect(resolveCliCommand({ GRANOFLOW_CLI_PATH: "/tmp/granoflow" })).toBe("/tmp/granoflow");
  });

  it("forces JSON output", () => {
    expect(normalizeCliArgs(["health"])).toEqual(["--json", "health"]);
    expect(normalizeCliArgs(["--json", "health"])).toEqual(["--json", "health"]);
  });

  it("does not expose offline backup package conversion through MCP", () => {
    expect(() => normalizeCliArgs(["backup", "decrypt"])).toThrow(/backup/);
  });
});
