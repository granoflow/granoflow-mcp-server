import type { LocalApiDetectionInput, SetupOptions } from "./setup.js";

const DEFAULT_PORTS = [56789, 47631, 38080];
const MAX_PORT_CANDIDATES = 20;
const PROBE_PATHS = ["/health", "/api/capabilities", "/v1/health", "/v1/capabilities"];

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function validatePorts(ports: number[]): void {
  if (ports.length > MAX_PORT_CANDIDATES) {
    throw new Error(`ports must contain at most ${MAX_PORT_CANDIDATES} candidates.`);
  }
  for (const port of ports) {
    if (!Number.isInteger(port) || port < 1 || port > 65_535) {
      throw new Error("ports must be integers between 1 and 65535.");
    }
  }
}

function hasExplicitGranoflowIdentity(value: unknown): boolean {
  if (!isObject(value)) return false;
  const service = typeof value.service === "string" ? value.service.toLowerCase() : "";
  const product = typeof value.product === "string" ? value.product.toLowerCase() : "";
  return service === "granoflow" || product === "granoflow";
}

function hasGranoflowEnvelope(value: unknown): boolean {
  return isObject(value) && value.ok === true && typeof value.code === "string" && "data" in value;
}

async function fetchWithTimeout(
  fetchImpl: typeof fetch,
  url: string,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchImpl(url, { signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

type ProbeResult = {
  explicitPaths: string[];
  envelopePaths: string[];
  authPaths: string[];
  jsonResponseCount: number;
};

async function probePort(
  port: number,
  fetchImpl: typeof fetch,
  timeoutMs: number,
  checked: string[],
): Promise<ProbeResult> {
  const apiBaseUrl = `http://127.0.0.1:${port}`;
  const result: ProbeResult = {
    explicitPaths: [],
    envelopePaths: [],
    authPaths: [],
    jsonResponseCount: 0,
  };
  for (const path of PROBE_PATHS) {
    const url = `${apiBaseUrl}${path}`;
    checked.push(url);
    try {
      const response = await fetchWithTimeout(fetchImpl, url, timeoutMs);
      if (response.status === 401 || response.status === 403) {
        result.authPaths.push(path);
        continue;
      }
      if (response.status !== 200) continue;
      let json: unknown = null;
      try {
        json = await response.json();
        result.jsonResponseCount += 1;
      } catch {
        json = null;
      }
      if (hasExplicitGranoflowIdentity(json)) result.explicitPaths.push(path);
      else if (hasGranoflowEnvelope(json)) result.envelopePaths.push(path);
    } catch {
      // Bounded probes treat timeouts and connection refusals as ordinary negatives.
    }
  }
  return result;
}

function addProbeCandidate(
  candidates: Array<Record<string, unknown>>,
  port: number,
  result: ProbeResult,
): boolean {
  const consistentEnvelope =
    result.envelopePaths.includes("/v1/health") &&
    result.envelopePaths.includes("/v1/capabilities");
  if (result.explicitPaths.length > 0 || consistentEnvelope) {
    candidates.push({
      apiBaseUrl: `http://127.0.0.1:${port}`,
      path: result.explicitPaths[0] ?? "/v1/health",
      confidence: "high",
      authRequired: false,
      evidence:
        result.explicitPaths.length > 0
          ? "HTTP 200 JSON contains explicit Granoflow service identity."
          : "Two fixed v1 endpoints returned consistent Granoflow envelopes.",
    });
    return false;
  }
  if (result.authPaths.length > 0) {
    candidates.push({
      apiBaseUrl: `http://127.0.0.1:${port}`,
      path: result.authPaths[0],
      confidence: "low",
      authRequired: true,
      evidence: "A fixed candidate path requires authentication; service identity is unverified.",
    });
    return false;
  }
  return result.jsonResponseCount > 0;
}

function candidateState(
  candidates: Array<Record<string, unknown>>,
  ambiguousCount: number,
): string {
  const high = candidates.filter((candidate) => candidate.confidence === "high").length;
  const auth = candidates.filter((candidate) => candidate.authRequired === true).length;
  return high === 1
    ? "single_high_confidence"
    : high > 1
      ? "multiple_high_confidence"
      : auth > 0
        ? "auth_required_only"
        : ambiguousCount > 0
          ? "ambiguous_non_granoflow_service"
          : "none";
}

function nextProbeActions(state: string): string[] {
  if (state === "single_high_confidence") {
    return [
      "Preview the candidate, config path, old/new value, and env override in one dry-run.",
      "Ask once for confirmation before writing that exact config.",
    ];
  }
  if (state === "multiple_high_confidence") {
    return [
      "Show all high-confidence candidates and ask the user to choose one.",
      "Preview the selected config in dry-run mode before one write confirmation.",
    ];
  }
  if (state === "auth_required_only") {
    return [
      "Candidate paths require authentication; verify service identity and GRANOFLOW_API_TOKEN before persisting a URL.",
    ];
  }
  if (state === "ambiguous_non_granoflow_service") {
    return [
      "A local HTTP service responded without Granoflow identity; do not persist it automatically.",
      "Ask the user for the configured Granoflow port or full URL.",
    ];
  }
  return [
    "Start Granoflow and enable the Local HTTP API.",
    "If Granoflow is already running, ask once for its custom port or full URL.",
  ];
}

export async function detectLocalApi(
  input: LocalApiDetectionInput = {},
  options: SetupOptions = {},
) {
  const ports = input.ports ?? DEFAULT_PORTS;
  const timeoutMs = input.timeoutMs ?? 300;
  validatePorts(ports);
  const fetchImpl = options.fetch ?? fetch;
  const candidates: Array<Record<string, unknown>> = [];
  const checked: string[] = [];
  let ambiguousCount = 0;
  for (const port of [...new Set(ports)]) {
    ambiguousCount += Number(
      addProbeCandidate(candidates, port, await probePort(port, fetchImpl, timeoutMs, checked)),
    );
  }
  const state = candidateState(candidates, ambiguousCount);
  return {
    checked,
    candidates,
    candidateState: state,
    persistenceRecommended: candidates.some((candidate) => candidate.confidence === "high"),
    nextActions: nextProbeActions(state),
  };
}
