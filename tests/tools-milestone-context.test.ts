import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-milestone-context", () => {
  it("previews active milestone context updates after resolving milestone state", async () => {
    const requestedUrls: string[] = [];
    const port = await startServer((request, response) => {
      requestedUrls.push(request.url ?? "");
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/milestones") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [
                {
                  id: "milestone-1",
                  title: "Context steward",
                  status: "doing",
                  projectId: "project-1",
                },
              ],
            },
          }),
        );
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_context_update")?.({
      milestoneId: "milestone-1",
      projectId: "project-1",
      description: "Current phase: implementing context steward.",
      evidenceSummary: "Milestone remains active.",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/milestones/milestone-1",
        body: {
          projectId: "project-1",
          description: "Current phase: implementing context steward.",
        },
        contextSteward: {
          target: "active_milestone",
          descriptionPolicy: "living_context",
        },
      },
    });
    expect(requestedUrls).toEqual(["/v1/milestones"]);
  });

  it("blocks ordinary MCP milestone description updates when milestone is archived", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/milestones") {
        response.end(
          JSON.stringify({
            ok: true,
            data: {
              items: [
                {
                  id: "milestone-1",
                  title: "Archived milestone",
                  status: "archived",
                  projectId: "project-1",
                },
              ],
            },
          }),
        );
        return;
      }
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const focused = await handlers.get("granoflow_milestone_context_update")?.({
      milestoneId: "milestone-1",
      description: "Should not be written.",
      evidenceSummary: "Attempted update.",
      dryRun: false,
    });
    const generic = await handlers.get("granoflow_milestone_update")?.({
      milestoneId: "milestone-1",
      description: "Should not be written.",
      dryRun: false,
    });

    expect(parseToolText(focused)).toMatchObject({
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
    });
    expect(parseToolText(generic)).toMatchObject({
      ok: false,
      code: "archived_milestone_context_locked_for_mcp",
    });
  });
});
