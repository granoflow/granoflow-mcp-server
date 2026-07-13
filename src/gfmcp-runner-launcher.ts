#!/usr/bin/env node
import { spawnSync } from "node:child_process";

const script = new URL("../skills/granoflow-gfmcp-runner/scripts/gfmcp_runner.py", import.meta.url);
const candidates = process.platform === "win32" ? ["py", "python"] : ["python3", "python"];

for (const executable of candidates) {
  const result = spawnSync(executable, [script.pathname, ...process.argv.slice(2)], {
    stdio: "inherit",
  });
  if (!result.error) {
    process.exit(result.status ?? 1);
  }
  if ((result.error as NodeJS.ErrnoException).code !== "ENOENT") {
    throw result.error;
  }
}

console.error("Python 3 is required to run granoflow-gfmcp-runner.");
process.exit(127);
