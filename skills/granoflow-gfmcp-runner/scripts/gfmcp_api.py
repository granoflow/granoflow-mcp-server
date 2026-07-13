from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class GranoflowApiError(RuntimeError):
    """Stable local API failure without response-body or credential leakage."""


class GranoflowApi:
    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        self.base_url = (
            base_url or os.environ.get("GRANOFLOW_API_BASE_URL") or "http://127.0.0.1:43120"
        ).rstrip("/")
        self.token = token if token is not None else os.environ.get("GRANOFLOW_API_TOKEN")

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            f"{self.base_url}/{path.lstrip('/')}", data=data, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8") or "{}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise GranoflowApiError("Granoflow Local HTTP API request failed") from error
        if not isinstance(payload, dict) or payload.get("ok") is False:
            raise GranoflowApiError("Granoflow Local HTTP API rejected the request")
        return payload

    def health(self) -> dict[str, Any]:
        return self.request("GET", "/v1/health")

    def prepare(self) -> dict[str, Any]:
        return self.request("POST", "/v1/ai-agent/gfmcp/prepare", {})

    def safe_sync(self) -> dict[str, Any]:
        return self.request("POST", "/v1/sync/gfmcp-safe-run", {})

    def candidates(self) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode({"tag": "custom_gfmcp"})
        payload = self.request("GET", f"/v1/tasks?{query}")
        data = payload.get("data")
        items = data.get("items", []) if isinstance(data, dict) else []
        return [
            item for item in items if isinstance(item, dict) and item.get("status") == "pending"
        ]

    def task(self, task_id: str) -> dict[str, Any] | None:
        payload = self.request("GET", f"/v1/tasks/{urllib.parse.quote(task_id)}")
        data = payload.get("data")
        if isinstance(data, dict):
            entity = data.get("entity", data)
            return entity if isinstance(entity, dict) else None
        return None

    def update_description(self, task_id: str, description: str) -> None:
        self.request(
            "PATCH", f"/v1/tasks/{urllib.parse.quote(task_id)}", {"description": description}
        )
