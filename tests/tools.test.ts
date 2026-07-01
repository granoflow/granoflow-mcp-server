import { describe, expect, it } from "vitest";
import type { z } from "zod";

import { registerGranoflowTools } from "../src/tools.js";

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
        "granoflow_setup_install_or_update_cli",
        "granoflow_setup_open_config",
      ]),
    );
  });
});
