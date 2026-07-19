import { describe, expect, it } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-milestone-archive", () => {
  it("previews milestone archive context closure with parent project update", async () => {
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

    const result = await handlers.get("granoflow_milestone_context_archive")?.({
      milestoneId: "milestone-1",
      projectId: "project-1",
      closure: {
        finalOutcome: "Context steward shipped.",
        verification: "Tests passed.",
        followUpMovedTo: "Next active milestone.",
        projectDescription: "Current state: context steward shipped.",
      },
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: true,
      code: "dry_run",
      data: {
        previewMode: "context_archive_closure",
        writesPerformed: false,
        steps: [
          expect.objectContaining({
            step: "finalize_milestone_context",
            path: "/v1/milestones/milestone-1/archive",
            appOwnedArchiveApiAvailable: false,
          }),
          expect.objectContaining({
            step: "update_parent_project_context",
            path: "/v1/projects/project-1",
            body: {
              description: "Current state: context steward shipped.",
            },
          }),
        ],
      },
    });
  });

  it("fails closed for real milestone archive context closure until app archive API exists", async () => {
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
      response.statusCode = 500;
      response.end(JSON.stringify({ ok: false }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_context_archive")?.({
      milestoneId: "milestone-1",
      projectId: "project-1",
      closure: {
        finalOutcome: "Context steward shipped.",
        verification: "Tests passed.",
        followUpMovedTo: "Next active milestone.",
        projectDescription: "Current state: context steward shipped.",
      },
      dryRun: false,
      confirmArchive: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "milestone_archive_api_unavailable",
      data: {
        requiredCapability: "app_owned_milestone_archive_api",
        writesPerformed: false,
      },
    });
  });
});
