import { describe, expect, it } from "vitest";
import { mkdir } from "node:fs/promises";
import { installSetupTestLifecycle } from "./setup-test-harness.js";
import { tempPaths } from "./setup-test-harness.js";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { openGranoflowApp } from "../src/setup.js";

installSetupTestLifecycle();

describe("setup-launch-guards", () => {
  it("previews opening the installed Granoflow app by default", async () => {
    const result = await openGranoflowApp(
      {
        appName: "Granoflow",
      },
      {
        runCommand: async () => ({ exitCode: 1, stdout: "", stderr: "" }),
      },
    );

    expect(result).toMatchObject({
      dryRun: true,
      appName: "Granoflow",
      attempts: expect.arrayContaining([
        expect.objectContaining({ kind: "path", args: ["/Applications/granoflow.app"] }),
        expect.objectContaining({ kind: "appName", args: ["-a", "Granoflow"] }),
      ]),
    });
    expect(JSON.stringify(result)).toContain("Granoflow");
  });

  it("refuses even a preview when any Granoflow process is already running", async () => {
    const calls: Array<{ command: string; args: string[] }> = [];
    const result = await openGranoflowApp(
      { dryRun: true },
      {
        runCommand: async (command, args) => {
          calls.push({ command, args });
          return {
            exitCode: 0,
            stdout: "123\n456\n",
            stderr: "",
          };
        },
      },
    );

    expect(result).toMatchObject({
      ok: false,
      code: "granoflow_app_already_running",
      dryRun: true,
      appProcess: { checked: true, running: true, count: 2 },
    });
    expect(result.nextActions).toEqual(
      expect.arrayContaining([
        expect.stringContaining("Do not open another Granoflow instance"),
        expect.stringContaining("configured API URL or port"),
      ]),
    );
    expect(calls).toEqual([{ command: "pgrep", args: ["-ix", "granoflow"] }]);
  });

  it("fails closed when the Granoflow process check cannot be completed", async () => {
    const calls: Array<{ command: string; args: string[] }> = [];
    const result = await openGranoflowApp(
      { dryRun: false },
      {
        runCommand: async (command, args) => {
          calls.push({ command, args });
          throw new Error("pgrep unavailable");
        },
      },
    );

    expect(result).toMatchObject({
      ok: false,
      code: "granoflow_process_check_failed",
      dryRun: false,
      appProcess: { checked: false, running: null },
    });
    expect(calls).toEqual([{ command: "pgrep", args: ["-ix", "granoflow"] }]);
  });

  it("refuses a concurrent real open while another MCP launch lease is active", async () => {
    const root = join(tmpdir(), `granoflow-open-lease-${process.pid}-${Date.now()}`);
    const launchLockPath = join(root, "app-launch.lock");
    tempPaths.push(root);
    await mkdir(launchLockPath, { recursive: true });
    let commandCalled = false;

    const result = await openGranoflowApp(
      { dryRun: false },
      {
        launchLockPath,
        runCommand: async () => {
          commandCalled = true;
          return { exitCode: 1, stdout: "", stderr: "" };
        },
      },
    );

    expect(result).toMatchObject({
      ok: false,
      code: "granoflow_app_launch_in_progress",
      dryRun: false,
    });
    expect(commandCalled).toBe(false);
  });

  it("opens the first successful Granoflow app candidate", async () => {
    const root = join(tmpdir(), `granoflow-open-success-${process.pid}-${Date.now()}`);
    const launchLockPath = join(root, "app-launch.lock");
    tempPaths.push(root);
    await mkdir(root, { recursive: true });
    const calls: string[][] = [];
    const result = await openGranoflowApp(
      { appPath: "/Custom/granoflow.app", dryRun: false },
      {
        launchLockPath,
        runCommand: async (command, args) => {
          calls.push(args);
          if (command === "pgrep") {
            return { exitCode: 1, stdout: "", stderr: "" };
          }
          return {
            exitCode: args[0] === "/Applications/granoflow.app" ? 0 : 1,
            stdout: "",
            stderr: args[0] === "/Applications/granoflow.app" ? "" : "not found",
          };
        },
      },
    );

    expect(result).toMatchObject({ ok: true, dryRun: false });
    expect(calls).toEqual([
      ["-ix", "granoflow"],
      ["/Custom/granoflow.app"],
      ["/Applications/granoflow.app"],
    ]);
    await expect(mkdir(launchLockPath)).rejects.toMatchObject({ code: "EEXIST" });
  });
});
