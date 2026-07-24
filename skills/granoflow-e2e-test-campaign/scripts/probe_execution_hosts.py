#!/usr/bin/env python3
"""Inventory local execution hosts and select the bounded E2E test scope.

Virtual devices are capabilities, not mandatory test targets. This script never
installs a VM stack or image and only runs read-only inventory commands.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_verification_host_matrix_v1"
PROVIDER_RANK = {"official_virtual": 0, "third_party_virtual": 1, "external": 2}


def _run(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout if completed.returncode == 0 else None


def current_platform() -> str:
    return {
        "darwin": "macos",
        "windows": "windows",
        "linux": "linux",
    }.get(platform.system().lower(), platform.system().lower())


def probe_hosts() -> list[dict[str, Any]]:
    current = current_platform()
    hosts: list[dict[str, Any]] = [
        {
            "id": f"{current}_current",
            "label": f"Current {current} development host",
            "kind": "desktop",
            "provider": "current_platform",
            "platforms": [current],
            "status": "available",
            "e2e_capable": True,
            "inventory_source": "python.platform",
        }
    ]
    hosts.extend(_probe_apple_simulators())
    hosts.extend(_probe_android_emulators())
    hosts.extend(_probe_third_party_virtualization())
    return hosts


def _probe_apple_simulators() -> list[dict[str, Any]]:
    if shutil.which("xcrun") is None:
        return []
    raw = _run(["xcrun", "simctl", "list", "devices", "available", "--json"])
    if raw is None:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    rows: list[dict[str, Any]] = []
    for runtime, devices in (payload.get("devices") or {}).items():
        if not isinstance(devices, list):
            continue
        for device in devices:
            if not isinstance(device, dict) or not device.get("isAvailable", True):
                continue
            identifier = device.get("udid")
            if not isinstance(identifier, str):
                continue
            rows.append(
                {
                    "id": f"apple_simulator_{identifier}",
                    "label": device.get("name") or identifier,
                    "kind": "simulator",
                    "provider": "official_virtual",
                    "platforms": ["ios"],
                    "status": "available",
                    "e2e_capable": True,
                    "inventory_source": "xcrun simctl",
                    "runtime": runtime,
                    "state": device.get("state"),
                }
            )
    return rows


def _probe_android_emulators() -> list[dict[str, Any]]:
    emulator = shutil.which("emulator")
    if emulator is None:
        return []
    raw = _run([emulator, "-list-avds"])
    if raw is None:
        return []
    return [
        {
            "id": f"android_emulator_{_slug(name)}",
            "label": name,
            "kind": "emulator",
            "provider": "official_virtual",
            "platforms": ["android"],
            "status": "available",
            "e2e_capable": True,
            "inventory_source": "emulator -list-avds",
        }
        for name in raw.splitlines()
        if name.strip()
    ]


def _probe_third_party_virtualization() -> list[dict[str, Any]]:
    probes = (
        ("prlctl", ["prlctl", "list", "--all", "--no-header", "-o", "uuid,name"], "parallels"),
        ("VBoxManage", ["VBoxManage", "list", "vms"], "virtualbox"),
        ("vmrun", ["vmrun", "list"], "vmware"),
        ("utmctl", ["utmctl", "list"], "utm"),
    )
    rows: list[dict[str, Any]] = []
    for binary, command, provider_name in probes:
        if shutil.which(binary) is None:
            continue
        raw = _run(command)
        if raw is None:
            continue
        for index, line in enumerate(raw.splitlines()):
            label = line.strip()
            if not label or label.lower().startswith("total running"):
                continue
            rows.append(
                {
                    "id": f"{provider_name}_{index}_{_slug(label)}",
                    "label": label,
                    "kind": "other",
                    "provider": "third_party_virtual",
                    "platforms": [],
                    "status": "available",
                    "e2e_capable": False,
                    "inventory_source": " ".join(command),
                    "note": (
                        "Installed third-party VM detected. Set platforms and "
                        "e2e_capable only after confirming an app-driving path."
                    ),
                }
            )
    return rows


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "host"


def select_hosts(
    hosts: list[dict[str, Any]],
    *,
    project_platforms: list[str],
    primary_platform: str | None,
    mode: str,
    selected_host_ids: list[str],
    current: str,
) -> dict[str, Any]:
    available = {
        host["id"]: host
        for host in hosts
        if host.get("status") == "available" and host.get("e2e_capable") is True
    }
    unknown = sorted(set(selected_host_ids) - set(available))
    if unknown:
        raise ValueError("Selected hosts are not available and E2E-capable: " + ", ".join(unknown))

    current_host = next(
        (
            host
            for host in available.values()
            if host.get("provider") == "current_platform" and current in host.get("platforms", [])
        ),
        None,
    )
    project_includes_current = current in project_platforms
    if mode == "interactive" and selected_host_ids:
        chosen = selected_host_ids
        source = "user_selection"
    elif project_includes_current and current_host is not None:
        chosen = [current_host["id"]]
        source = "current_platform_default"
    else:
        order = [primary_platform] if primary_platform else []
        order.extend(item for item in project_platforms if item not in order)
        platform_rank = {name: index for index, name in enumerate(order)}
        candidates = [
            host
            for host in available.values()
            if set(host.get("platforms", [])) & set(project_platforms)
            and host.get("provider") != "current_platform"
        ]
        candidates.sort(
            key=lambda host: (
                min(platform_rank.get(p, len(platform_rank)) for p in host["platforms"]),
                PROVIDER_RANK.get(str(host.get("provider") or ""), 99),
                host["id"],
            )
        )
        if not candidates:
            raise ValueError("No available E2E-capable host matches the project platforms.")
        chosen = [candidates[0]["id"]]
        source = "ai_fallback"

    return {
        "mode": mode,
        "source": source,
        "current_platform": current,
        "current_host_id": current_host["id"] if current_host else f"{current}_current",
        "project_includes_current_platform": project_includes_current,
        "selected_host_ids": chosen,
    }


def build_matrix(
    *,
    hosts: list[dict[str, Any]],
    project_platforms: list[str],
    primary_platform: str | None,
    mode: str,
    selected_host_ids: list[str],
    current: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "derived_from": ["local_host_inventory", "scope.supported_platforms"],
        "concurrency": "parallel_when_capable",
        "primary_form_factors": [],
        "project_platforms": project_platforms,
        "hosts": hosts,
        "selection": select_hosts(
            hosts,
            project_platforms=project_platforms,
            primary_platform=primary_platform,
            mode=mode,
            selected_host_ids=selected_host_ids,
            current=current,
        ),
        "assignment_policy": "selected_hosts_only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-platform", action="append", dest="platforms", required=True)
    parser.add_argument("--primary-platform")
    parser.add_argument("--mode", choices=("interactive", "unattended"), default="interactive")
    parser.add_argument("--select-host", action="append", default=[])
    parser.add_argument("--inventory", type=Path)
    args = parser.parse_args()
    if args.inventory:
        payload = json.loads(args.inventory.read_text(encoding="utf-8"))
        hosts = payload["hosts"] if isinstance(payload, dict) else payload
    else:
        hosts = probe_hosts()
    matrix = build_matrix(
        hosts=hosts,
        project_platforms=args.platforms,
        primary_platform=args.primary_platform,
        mode=args.mode,
        selected_host_ids=args.select_host,
        current=current_platform(),
    )
    print(json.dumps(matrix, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
