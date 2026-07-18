from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class GranoflowApiError(RuntimeError):
    """Stable local API failure without response or credential leakage."""


def _find_list(value: Any, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        for key in keys:
            items = value.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        for child in value.values():
            found = _find_list(child, keys)
            if found:
                return found
    return []


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

    def tasks(self, milestone_id: str) -> list[dict[str, Any]]:
        payload = self.request("GET", "/v1/tasks")
        return [
            task
            for task in _find_list(payload, ("items",))
            if task.get("milestoneId") == milestone_id and task.get("status") != "deleted"
        ]

    def task(self, task_id: str) -> dict[str, Any] | None:
        payload = self.request("GET", f"/v1/tasks/{urllib.parse.quote(task_id)}")
        value: Any = payload
        while isinstance(value, dict):
            if isinstance(value.get("entity"), dict):
                return value["entity"]
            if isinstance(value.get("data"), dict):
                value = value["data"]
                continue
            if value.get("id") == task_id:
                return value
            break
        return None

    def attachments(self, task_id: str) -> list[dict[str, Any]]:
        payload = self.request("GET", f"/v1/tasks/{urllib.parse.quote(task_id)}/attachments")
        return _find_list(payload, ("items",))

    def attachment(self, task_id: str, attachment_id: str) -> dict[str, Any]:
        return self.request(
            "GET",
            f"/v1/tasks/{urllib.parse.quote(task_id)}/attachments/{urllib.parse.quote(attachment_id)}",
        )

    def nodes(self, task_id: str) -> list[dict[str, Any]]:
        payload = self.request("GET", f"/v1/tasks/{urllib.parse.quote(task_id)}/nodes")
        return _find_list(payload, ("items", "nodes"))

    def update_node(self, task_id: str, node_id: str, updated_at: str, status: str) -> None:
        self.request(
            "PATCH",
            f"/v1/tasks/{urllib.parse.quote(task_id)}/nodes/{urllib.parse.quote(node_id)}",
            {"expectedUpdatedAt": updated_at, "status": status},
        )

    def update_description(self, task_id: str, description: str) -> None:
        self.request(
            "PATCH", f"/v1/tasks/{urllib.parse.quote(task_id)}", {"description": description}
        )
