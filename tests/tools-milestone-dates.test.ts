import { describe, expect, it, vi } from "vitest";
import {
  installToolTestLifecycle,
  startServer,
  parseToolText,
  collectHandlers,
} from "./tools-test-harness.js";

installToolTestLifecycle();

describe("tools-milestone-dates", () => {
  it("defaults the first omitted milestone deadline to today", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 6, 16, 12));
    const port = await startServer((request, response) => {
      expect(request.method).toBe("GET");
      expect(request.url).toBe("/v1/milestones");
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, code: "ok", data: { items: [] } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_create")?.({
      projectId: "project-1",
      title: "Default deadline",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      code: "dry_run",
      data: {
        body: {
          projectId: "project-1",
          dueAt: "2026-07-16T23:59:59.000",
        },
      },
    });
  });

  it("uses the same day when the first milestone is created on Saturday", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 6, 18, 12));
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, code: "ok", data: { items: [] } }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_create")?.({
      projectId: "project-1",
      title: "Saturday milestone",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      data: { body: { dueAt: "2026-07-18T23:59:59.000" } },
    });
  });

  it("advances an omitted milestone deadline past later deadlines in the same project", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 6, 16, 12));
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(
        JSON.stringify({
          ok: true,
          code: "ok",
          data: {
            items: [
              {
                id: "same-project-1",
                projectId: "project-1",
                dueAt: "2026-07-18T23:59:59.000",
              },
              {
                id: "same-project-2",
                projectId: "project-1",
                dueAt: "2026-07-31T23:59:59.000",
              },
              {
                id: "other-project",
                projectId: "project-2",
                dueAt: "2027-01-01T23:59:59.000",
              },
            ],
          },
        }),
      );
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_create")?.({
      projectId: "project-1",
      title: "Later milestone",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      data: { body: { dueAt: "2026-08-01T23:59:59.000" } },
    });
  });

  it("fails closed when the default milestone deadline cannot inspect the project schedule", async () => {
    const port = await startServer((_request, response) => {
      response.statusCode = 500;
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ message: "schedule unavailable" }));
    });
    process.env.GRANOFLOW_API_BASE_URL = `http://127.0.0.1:${port}`;
    const { handlers } = collectHandlers();

    const result = await handlers.get("granoflow_milestone_create")?.({
      projectId: "project-1",
      title: "Blocked milestone",
      dryRun: true,
    });

    expect(parseToolText(result)).toMatchObject({
      ok: false,
      code: "http_500",
    });
  });
});
