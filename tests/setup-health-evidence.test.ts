import { describe, expect, it } from "vitest";
import { installSetupTestLifecycle, startServer } from "./setup-test-harness.js";
import { detectLocalApi } from "../src/setup.js";

installSetupTestLifecycle();

describe("setup-health-evidence", () => {
  it("detects a Granoflow-shaped localhost health response", async () => {
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ service: "granoflow", status: "ok" }));
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidates).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          apiBaseUrl: `http://127.0.0.1:${port}`,
          confidence: "high",
          authRequired: false,
        }),
      ]),
    );
    expect(result.candidateState).toBe("single_high_confidence");
  });

  it("does not mistake generic localhost status JSON for Granoflow", async () => {
    const port = await startServer((_request, response) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ status: "ok", version: "1.0.0" }));
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidates).toEqual([]);
    expect(result.candidateState).toBe("ambiguous_non_granoflow_service");
  });

  it("returns all high-confidence candidates instead of choosing between them", async () => {
    const handler = (_request: IncomingMessage, response: ServerResponse) => {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify({ service: "granoflow", status: "ok" }));
    };
    const firstPort = await startServer(handler);
    const secondPort = await startServer(handler);

    const result = await detectLocalApi({ ports: [firstPort, secondPort], timeoutMs: 500 });

    expect(result.candidateState).toBe("multiple_high_confidence");
    expect(result.candidates).toHaveLength(2);
  });

  it("accepts consistent Granoflow envelopes on both fixed v1 endpoints", async () => {
    const port = await startServer((request, response) => {
      response.setHeader("content-type", "application/json");
      if (request.url === "/v1/health" || request.url === "/v1/capabilities") {
        response.end(JSON.stringify({ ok: true, code: "ok", data: { path: request.url } }));
        return;
      }
      response.statusCode = 404;
      response.end(JSON.stringify({ status: "not_found" }));
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidateState).toBe("single_high_confidence");
    expect(result.candidates[0]).toMatchObject({
      apiBaseUrl: `http://127.0.0.1:${port}`,
      confidence: "high",
    });
  });

  it("treats fixed-path 401 responses as auth-required weak evidence", async () => {
    const port = await startServer((_request, response) => {
      response.statusCode = 401;
      response.end("unauthorized");
    });

    const result = await detectLocalApi({ ports: [port], timeoutMs: 500 });

    expect(result.candidates).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          apiBaseUrl: `http://127.0.0.1:${port}`,
          confidence: "low",
          authRequired: true,
        }),
      ]),
    );
    expect(result.candidateState).toBe("auth_required_only");
  });
});
