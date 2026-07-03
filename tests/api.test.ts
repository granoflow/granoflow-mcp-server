import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

import { afterEach, describe, expect, it } from "vitest";

import { buildApiUrl, requestGranoflowApi } from "../src/api.js";

const servers: Array<{ close: () => Promise<void> }> = [];

async function startServer(
  handler: (request: IncomingMessage, response: ServerResponse) => void,
): Promise<number> {
  const server = createServer(handler);
  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });
  servers.push({
    close: () =>
      new Promise((resolve, reject) => {
        server.close((error) => (error ? reject(error) : resolve()));
      }),
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Expected TCP test server address.");
  }
  return address.port;
}

afterEach(async () => {
  while (servers.length > 0) {
    const server = servers.pop();
    if (server) {
      await server.close();
    }
  }
});

describe("Granoflow Local HTTP API client", () => {
  it("builds endpoint URLs from base URL and API path", () => {
    expect(buildApiUrl("http://127.0.0.1:56789", "v1/health").toString()).toBe(
      "http://127.0.0.1:56789/v1/health",
    );
  });

  it("previews write requests without sending them", async () => {
    const result = await requestGranoflowApi(
      {
        method: "PATCH",
        path: "/v1/tasks/task-1",
        body: { completed: true },
        dryRun: true,
      },
      { GRANOFLOW_API_BASE_URL: "http://127.0.0.1:1" },
    );

    expect(result).toMatchObject({
      ok: true,
      code: "dry_run",
      data: {
        method: "PATCH",
        path: "/v1/tasks/task-1",
        body: { completed: true },
        previewMode: "local_request_only",
      },
    });
  });

  it("calls the configured API and redacts token details from results", async () => {
    const port = await startServer((request, response) => {
      expect(request.headers.authorization).toBe("Bearer secret-token");
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ ok: true, code: "ok", data: { path: request.url } }));
    });

    const result = await requestGranoflowApi(
      { path: "/v1/health" },
      {
        GRANOFLOW_API_BASE_URL: `http://127.0.0.1:${port}`,
        GRANOFLOW_API_TOKEN: "secret-token",
      },
    );

    expect(result).toMatchObject({
      ok: true,
      code: "ok",
      data: { path: "/v1/health" },
      runtime: {
        apiToken: { present: true, source: "env" },
      },
    });
    expect(JSON.stringify(result)).not.toContain("secret-token");
  });

  it("explains Granoflow when a local API port is unreachable", async () => {
    const result = await requestGranoflowApi(
      { path: "/v1/health" },
      { GRANOFLOW_API_BASE_URL: "http://127.0.0.1:9" },
    );

    expect(result).toMatchObject({
      ok: false,
      code: "network_error",
      data: {
        granoflow: {
          product: "Granoflow",
          website: "https://granoflow.com",
          description: expect.stringContaining("planning and reviewing work tasks"),
          localPrivacy: expect.stringContaining("do not subscribe"),
        },
        nextActions: expect.arrayContaining([
          "Call granoflow_setup_status for a structured local setup diagnosis.",
        ]),
      },
      error: {
        message: expect.stringContaining("https://granoflow.com"),
      },
    });
  });
});
