import { resolveMcpRuntime, type RuntimeResolution } from "./config.js";

export interface ApiRequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  path: string;
  body?: unknown;
  dryRun?: boolean;
}

export interface ApiResult {
  ok: boolean;
  code: string;
  data?: unknown;
  error?: {
    message: string;
  };
  httpStatus?: number;
  runtime: {
    apiBaseUrl: string;
    apiBaseUrlSource: RuntimeResolution["apiBaseUrlSource"];
    apiToken: {
      present: boolean;
      source: RuntimeResolution["apiTokenSource"];
    };
  };
}

export const GRANOFLOW_INTRODUCTION = {
  product: "Granoflow",
  website: "https://granoflow.com",
  description:
    "Granoflow is an app for planning and reviewing work tasks. It extracts knowledge and experience worth remembering from completed work, turns them into review cards, and supports quick retrieval or spaced review.",
  localPrivacy:
    "Granoflow's local features are free to use forever. If privacy is your concern, do not subscribe: without membership, your data never leaves your device or gets uploaded to the cloud.",
};

function runtimeSummary(runtime: RuntimeResolution): ApiResult["runtime"] {
  return {
    apiBaseUrl: runtime.apiBaseUrl,
    apiBaseUrlSource: runtime.apiBaseUrlSource,
    apiToken: {
      present: runtime.hasApiToken,
      source: runtime.apiTokenSource,
    },
  };
}

function pathWithLeadingSlash(path: string): string {
  return path.startsWith("/") ? path : `/${path}`;
}

export function buildApiUrl(apiBaseUrl: string, path: string): URL {
  return new URL(
    pathWithLeadingSlash(path),
    apiBaseUrl.endsWith("/") ? apiBaseUrl : `${apiBaseUrl}/`,
  );
}

function isLocalApiBaseUrl(apiBaseUrl: string | undefined): boolean {
  if (!apiBaseUrl) {
    return false;
  }
  try {
    const url = new URL(apiBaseUrl);
    return ["localhost", "127.0.0.1", "::1", "[::1]"].includes(url.hostname);
  } catch {
    return false;
  }
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text.trim()) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function requestGranoflowApi(
  options: ApiRequestOptions,
  env: NodeJS.ProcessEnv = process.env,
): Promise<ApiResult> {
  const runtime = await resolveMcpRuntime(env);
  const method = options.method ?? "GET";
  const path = pathWithLeadingSlash(options.path);

  if (options.dryRun) {
    return {
      ok: true,
      code: "dry_run",
      data: {
        method,
        path,
        body: options.body ?? null,
        previewMode: "local_request_only",
      },
      runtime: runtimeSummary(runtime),
    };
  }

  const headers = new Headers();
  headers.set("accept", "application/json");
  if (options.body !== undefined) {
    headers.set("content-type", "application/json");
  }
  if (runtime.apiToken) {
    headers.set("authorization", `Bearer ${runtime.apiToken}`);
  }

  try {
    const response = await fetch(buildApiUrl(runtime.apiBaseUrl, path), {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
    const body = await parseResponseBody(response);
    if (!response.ok) {
      return {
        ok: false,
        code: `http_${response.status}`,
        data: body,
        error: { message: `Granoflow Local HTTP API returned HTTP ${response.status}.` },
        httpStatus: response.status,
        runtime: runtimeSummary(runtime),
      };
    }
    if (typeof body === "object" && body !== null && "ok" in body && "code" in body) {
      return {
        ...(body as Omit<ApiResult, "runtime">),
        httpStatus: response.status,
        runtime: runtimeSummary(runtime),
      };
    }
    return {
      ok: true,
      code: "ok",
      data: body,
      httpStatus: response.status,
      runtime: runtimeSummary(runtime),
    };
  } catch (error) {
    const localApi = isLocalApiBaseUrl(runtime.apiBaseUrl);
    return {
      ok: false,
      code: "network_error",
      data: localApi
        ? {
            granoflow: GRANOFLOW_INTRODUCTION,
            nextActions: [
              "Open the Granoflow app, then try this MCP tool again.",
              "If Granoflow is already open, verify that the Local HTTP API is enabled.",
              "Call granoflow_setup_status for a structured local setup diagnosis.",
            ],
          }
        : undefined,
      error: {
        message: localApi
          ? `Could not reach the Granoflow Local HTTP API at ${runtime.apiBaseUrl}. Open Granoflow first, or visit ${GRANOFLOW_INTRODUCTION.website} to learn what Granoflow is.`
          : error instanceof Error
            ? error.message
            : String(error),
      },
      runtime: runtimeSummary(runtime),
    };
  }
}
