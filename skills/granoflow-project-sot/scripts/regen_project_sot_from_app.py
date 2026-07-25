#!/usr/bin/env python3
"""Regenerate temp/project-sot.yaml from Granoflow App entities."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STAGE_IDS = (
    "project_init",
    "milestones_created",
    "milestone_analysis",
    "milestone_plan",
    "milestone_implement",
    "integration_campaign",
    "e2e_campaign",
    "project_complete",
)


class GranoflowApiError(RuntimeError):
    """Stable local API failure without response-body or credential leakage."""


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


def _unwrap_entity(payload: dict[str, Any], entity_id: str | None = None) -> dict[str, Any]:
    value: Any = payload
    while isinstance(value, dict):
        if isinstance(value.get("entity"), dict):
            return value["entity"]
        if isinstance(value.get("data"), dict):
            value = value["data"]
            continue
        if entity_id is None or value.get("id") == entity_id:
            return value
        break
    raise GranoflowApiError("Granoflow Local HTTP API returned unexpected entity shape")


class GranoflowApi:
    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        self.base_url = (
            base_url or os.environ.get("GRANOFLOW_API_BASE_URL") or "http://127.0.0.1:56789"
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

    def project(self, project_id: str) -> dict[str, Any]:
        payload = self.request("GET", f"/v1/projects/{urllib.parse.quote(project_id)}")
        return _unwrap_entity(payload, project_id)

    def project_attachments(self, project_id: str) -> list[dict[str, Any]]:
        payload = self.request("GET", f"/v1/projects/{urllib.parse.quote(project_id)}/attachments")
        return _find_list(payload, ("items",))

    def milestones(self, project_id: str) -> list[dict[str, Any]]:
        payload = self.request("GET", "/v1/milestones")
        return [
            item
            for item in _find_list(payload, ("items",))
            if item.get("projectId") == project_id and item.get("status") != "deleted"
        ]

    def tasks(self, project_id: str) -> list[dict[str, Any]]:
        payload = self.request("GET", "/v1/tasks")
        return [
            item
            for item in _find_list(payload, ("items",))
            if item.get("projectId") == project_id and item.get("status") != "deleted"
        ]


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dump_yaml(data: dict[str, Any]) -> str:
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    except ImportError:
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _load_yamlish(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end < 0:
                return None
            text = text[3:end].strip("\n")
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
    except Exception:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return data if isinstance(data, dict) else None


def _project_work_digest(attachments: list[dict[str, Any]]) -> tuple[str, bool]:
    current = [
        a
        for a in attachments
        if a.get("logicalSlot") == "project_work" and a.get("supersededAt") in (None, "")
    ]
    if not current:
        current = [a for a in attachments if a.get("logicalSlot") == "project_work"]
    if not current:
        return "", False
    row = sorted(current, key=lambda a: str(a.get("createdAt") or ""), reverse=True)[0]
    digest = str(row.get("confirmedContentSha256") or row.get("contentSha256") or "").strip()
    return digest, bool(digest)


def _is_feature_milestone(title: str) -> bool:
    lowered = title.lower()
    return not (re.search(r"\be2e\b", lowered) or "integration" in lowered)


def _milestone_label(index: int, title: str) -> str:
    m = re.match(r"^(M\d+)\b", title.strip(), re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return f"M{index}"


def _rel_if_under(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _collect_evidence(repo_root: Path) -> dict[str, list[str]]:
    it_refs: list[str] = []
    e2e_refs: list[str] = []
    it_dir = repo_root / "temp" / "integration-campaign"
    if it_dir.is_dir():
        for name in ("closing-summary.json", "suite-plan.json", "journey_derivation.md"):
            candidate = it_dir / name
            if candidate.is_file():
                it_refs.append(_rel_if_under(repo_root, candidate))
    e2e_root = repo_root / "temp" / "e2e-campaign"
    if e2e_root.is_dir():
        for path in sorted(e2e_root.rglob("closing-summary.json")):
            e2e_refs.append(_rel_if_under(repo_root, path))
        for path in sorted(e2e_root.rglob("coverage-matrix.json")):
            e2e_refs.append(_rel_if_under(repo_root, path))
        for path in sorted(e2e_root.rglob("suite-plan.json")):
            e2e_refs.append(_rel_if_under(repo_root, path))

    # de-dupe preserving order
    def uniq(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
        return out

    return {"integration": uniq(it_refs), "e2e": uniq(e2e_refs)}


def _probe_workspace(repo_root: Path) -> dict[str, Any]:
    notes: dict[str, Any] = {"probed": True, "commands": []}
    analyze = repo_root / "analysis_options.yaml"
    pubspec = repo_root / "pubspec.yaml"
    if pubspec.is_file():
        notes["flutter_project"] = True
        if analyze.is_file():
            notes["commands"].append(
                {
                    "id": "flutter_analyze",
                    "command": "flutter analyze",
                    "cwd": str(repo_root),
                    "status": "pointer_only",
                }
            )
        notes["commands"].append(
            {
                "id": "flutter_test",
                "command": "flutter test",
                "cwd": str(repo_root),
                "status": "pointer_only",
            }
        )
    else:
        notes["flutter_project"] = False
    return notes


def _stage(
    stage_id: str,
    status: str,
    evidence: str = "",
    *,
    evidence_missing: bool | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {"id": stage_id, "status": status, "evidence": evidence}
    if evidence_missing is not None:
        row["evidence_missing"] = evidence_missing
    return row


def build_project_sot(
    *,
    project: dict[str, Any],
    attachments: list[dict[str, Any]],
    milestones: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    repo_root: Path,
    probe_workspace: bool,
    legacy: dict[str, Any] | None,
) -> dict[str, Any]:
    project_id = str(project.get("id") or "")
    title = str(project.get("title") or "")
    pw_digest, pw_present = _project_work_digest(attachments)
    evidence = _collect_evidence(repo_root)

    feature_ms = [m for m in milestones if _is_feature_milestone(str(m.get("title") or ""))]
    tasks_by_ms: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        mid = str(task.get("milestoneId") or "")
        tasks_by_ms.setdefault(mid, []).append(task)

    work_items: list[dict[str, Any]] = []
    all_feature_tasks_done = True
    for index, milestone in enumerate(feature_ms, start=1):
        mid = str(milestone.get("id") or "")
        label = _milestone_label(index, str(milestone.get("title") or ""))
        ms_tasks = tasks_by_ms.get(mid, [])
        done = bool(ms_tasks) and all(t.get("status") == "done" for t in ms_tasks)
        if not done:
            all_feature_tasks_done = False
        work_items.append(
            {
                "id": f"{label}.implement",
                "stage_id": "milestone_implement",
                "skill": "granoflow-task-orchestrator",
                "status": "done" if done else ("pending" if ms_tasks else "pending"),
                "milestone_id": mid,
                "confirmation": "none",
                "evidence_ref": None,
            }
        )

    has_milestones = bool(milestones)
    has_feature_tasks = any(tasks_by_ms.get(str(m.get("id") or ""), []) for m in feature_ms)
    it_evidence = evidence["integration"]
    e2e_evidence = evidence["e2e"]

    stages = [
        _stage(
            "project_init",
            "done" if pw_present else ("in_progress" if project_id else "not_started"),
            (
                "Project Work hash from App attachments"
                if pw_present
                else "project_work attachment missing"
            ),
            evidence_missing=not pw_present,
        ),
        _stage(
            "milestones_created",
            "done" if has_milestones else "not_started",
            f"{len(milestones)} milestones in App" if has_milestones else "",
        ),
        _stage(
            "milestone_analysis",
            "done" if has_feature_tasks else ("in_progress" if has_milestones else "not_started"),
            "Inferred from App task portfolio (regen coarse)",
        ),
        _stage(
            "milestone_plan",
            "done" if has_feature_tasks else ("in_progress" if has_milestones else "not_started"),
            "Inferred from App task portfolio (regen coarse)",
        ),
        _stage(
            "milestone_implement",
            "done"
            if all_feature_tasks_done and feature_ms
            else ("in_progress" if has_feature_tasks else "not_started"),
            "Feature milestone child tasks from App",
        ),
        _stage(
            "integration_campaign",
            "done" if it_evidence else "not_started",
            it_evidence[0] if it_evidence else "no temp/integration-campaign closing summary",
            evidence_missing=not bool(it_evidence),
        ),
        _stage(
            "e2e_campaign",
            "done" if e2e_evidence else "not_started",
            e2e_evidence[0] if e2e_evidence else "no temp/e2e-campaign closing summary",
            evidence_missing=not bool(e2e_evidence),
        ),
        _stage(
            "project_complete",
            "done" if (all_feature_tasks_done and feature_ms and e2e_evidence) else "not_started",
            "Selected-host delivery inferred; do not claim user_final_acceptance",
        ),
    ]

    # Prefer legacy stage/thin-gate truth when migrating (still normalize enums).
    if legacy:
        legacy_stages = legacy.get("stages")
        if isinstance(legacy_stages, list):
            by_id = {
                str(row.get("id")): row
                for row in legacy_stages
                if isinstance(row, dict) and row.get("id") in STAGE_IDS
            }
            rebuilt: list[dict[str, Any]] = []
            for row in stages:
                old = by_id.get(str(row["id"]))
                if not old:
                    rebuilt.append(row)
                    continue
                status = old.get("status")
                if status in {
                    "not_started",
                    "in_progress",
                    "done",
                    "blocked",
                    "waived",
                }:
                    row = dict(row)
                    row["status"] = status
                    if isinstance(old.get("evidence"), str) and old.get("evidence"):
                        row["evidence"] = old["evidence"]
                rebuilt.append(row)
            stages = rebuilt
        # Legacy delivery close outranks stale App duplicate pending tasks.
        if any(
            row.get("id") == "project_complete" and row.get("status") == "done" for row in stages
        ):
            for item in work_items:
                if str(item.get("id") or "").endswith(".implement"):
                    item["status"] = "done"

    stage_by_id = {str(s["id"]): s for s in stages}
    project_complete_done = stage_by_id["project_complete"]["status"] == "done"

    unfinished = [item for item in work_items if item.get("status") not in {"done", "cancelled"}]
    if project_complete_done:
        status = "completed"
        next_step = {
            "work_item_id": "DONE",
            "summary": "project_complete — selected-host delivery with honest residuals only",
            "pinned_by": None,
            "override": None,
        }
    elif unfinished:
        status = "active"
        nxt = unfinished[0]
        next_step = {
            "work_item_id": nxt["id"],
            "summary": (
                f"Continue {nxt['id']} (regen projection); " "run lint_project_sot.py on resume"
            ),
            "pinned_by": "schedule",
            "override": None,
        }
    else:
        status = "active"
        next_step = {
            "work_item_id": "integration_campaign",
            "summary": (
                "Advance integration_campaign / e2e_campaign thin gates; " "lint_project_sot.py"
            ),
            "pinned_by": "schedule",
            "override": None,
        }

    cross = "not_applicable"
    if len(feature_ms) >= 2:
        cross = "planned" if not it_evidence else "pending"
    # normalize invalid legacy values
    if legacy and legacy.get("cross_milestone_integration") in {
        "pending",
        "planned",
        "not_applicable",
    }:
        cross = str(legacy["cross_milestone_integration"])

    it_path = "not_started"
    if it_evidence:
        it_path = "full_unit_and_it"
    elif len(feature_ms) == 1 and e2e_evidence:
        it_path = "waived_e2e_direct"
    it_check = "covered" if it_evidence else "not_applicable"
    e2e_check = "covered" if e2e_evidence else "not_applicable"

    if legacy:
        lit = legacy.get("integration_campaign")
        if isinstance(lit, dict):
            if lit.get("path") in {"full_unit_and_it", "waived_e2e_direct", "not_started"}:
                it_path = str(lit["path"])
            if lit.get("cross_milestone_journey_check") in {
                "not_applicable",
                "covered",
                "gap",
            }:
                it_check = str(lit["cross_milestone_journey_check"])
            refs = lit.get("evidence_ref")
            if isinstance(refs, list) and refs:
                it_evidence = [str(x) for x in refs if str(x).strip()]
        le2e = legacy.get("e2e_campaign")
        if isinstance(le2e, dict):
            check = le2e.get("coverage_matrix_check")
            if check in {"not_applicable", "covered", "gap"}:
                e2e_check = str(check)
            elif check and e2e_evidence:
                # Map informal legacy strings (e.g. complete_in_app_covered) → covered
                e2e_check = "covered"
            refs = le2e.get("evidence_ref")
            if isinstance(refs, list) and refs:
                e2e_evidence = [str(x) for x in refs if str(x).strip()]
        if legacy.get("interaction_mode") in {"interactive", "unattended"}:
            interaction_mode = str(legacy["interaction_mode"])
        else:
            interaction_mode = "unattended"
        if legacy.get("status") in {"active", "paused", "completed", "superseded"}:
            status = str(legacy["status"])
        elif project_complete_done:
            status = "completed"
    else:
        interaction_mode = "unattended"

    sot: dict[str, Any] = {
        "doc_type": "project_sot",
        "schema": "granoflow_project_sot_v1",
        "project_id": project_id,
        "project_title": title,
        "status": status,
        "interaction_mode": interaction_mode,
        "collaborative_planning_surface": "unknown",
        "host_wake_surface": "unknown",
        "host_wake_bound": False,
        "bound_sot_path": "temp/project-sot.yaml",
        "updated_at": _now_iso(),
        "source_digests": {
            "project_work": pw_digest if pw_digest else "unknown_missing_project_work",
            "milestone_work": "",
            "portfolio": "",
        },
        "source_digest_verification": {
            "project_work": {
                "recorded": pw_digest if pw_digest else "unknown_missing_project_work",
                "app_readback": pw_digest if pw_digest else "",
                "matched": bool(pw_digest),
            }
        },
        "cross_milestone_integration": cross,
        "stages": stages,
        "work_items": work_items,
        "next_step": next_step,
        "integration_campaign": {
            "path": it_path,
            "cross_milestone_journey_check": it_check,
            "evidence_ref": it_evidence,
        },
        "e2e_campaign": {
            "coverage_matrix_check": e2e_check,
            "evidence_ref": e2e_evidence,
        },
        "parallel_batches": [],
        "regen": {
            "source": "granoflow_app",
            "honesty": "coarse_projection_from_entities_and_temp_pointers",
            "project_work_present": pw_present,
        },
    }
    if probe_workspace:
        sot["workspace_verify"] = _probe_workspace(repo_root)
    return sot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--probe-workspace", action="store_true")
    parser.add_argument("--migrate-legacy", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    output = (args.output or (repo_root / "temp" / "project-sot.yaml")).resolve()

    def fail(code: str, detail: str) -> int:
        print(json.dumps({"ok": False, "code": code, "detail": detail}, ensure_ascii=False))
        return 1

    if output.exists() and not args.force:
        return fail("project_sot_exists", f"{output} exists; pass --force to overwrite")

    legacy: dict[str, Any] | None = None
    if args.migrate_legacy:
        legacy_paths = sorted((repo_root / "temp").glob("project-e2e-sot-v*.md"))
        for path in legacy_paths:
            legacy = _load_yamlish(path)
            if legacy:
                break

    api = GranoflowApi(base_url=args.base_url, token=args.token)
    try:
        project = api.project(args.project_id)
        attachments = api.project_attachments(args.project_id)
        milestones = api.milestones(args.project_id)
        tasks = api.tasks(args.project_id)
        sot = build_project_sot(
            project=project,
            attachments=attachments,
            milestones=milestones,
            tasks=tasks,
            repo_root=repo_root,
            probe_workspace=args.probe_workspace,
            legacy=legacy,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_dump_yaml(sot), encoding="utf-8")
    except GranoflowApiError as exc:
        return fail("project_sot_regen_failed", str(exc))
    except OSError as exc:
        return fail("project_sot_regen_failed", str(exc))

    lint_script = Path(__file__).resolve().parent / "lint_project_sot.py"
    lint_ok = True
    lint_payload: dict[str, Any] | None = None
    if lint_script.is_file():
        try:
            completed = subprocess.run(
                ["python3", str(lint_script), str(output)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            try:
                parsed: dict[str, Any] = json.loads(completed.stdout or "{}")
            except json.JSONDecodeError:
                parsed = {
                    "ok": False,
                    "code": "project_sot_lint_failed",
                    "detail": completed.stdout or completed.stderr,
                }
            lint_payload = parsed
            lint_ok = bool(parsed.get("ok"))
        except (OSError, subprocess.TimeoutExpired) as exc:
            lint_ok = False
            lint_payload = {"ok": False, "code": "project_sot_lint_failed", "detail": str(exc)}

    result = {
        "ok": True,
        "code": "ok",
        "path": str(output),
        "project_id": args.project_id,
        "lint": lint_payload,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if lint_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
