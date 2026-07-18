from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import mimetypes
import re
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_acceptance_report_v1"
ALLOWED_STATUSES = {"passed", "failed", "planned_not_run", "not_required"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_REPORT_BYTES = 25 * 1024 * 1024
FORBIDDEN_HTML = re.compile(
    r"<(script|iframe|object|embed|form)\b|\b(?:src|href)\s*=\s*['\"]https?://",
    re.IGNORECASE,
)


def _require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a non-empty string")
    return value.strip()


def _require_string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{path} must be a string array")
    return [item.strip() for item in value if item.strip()]


def _status_block(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    status = _require_text(value.get("status"), f"{path}.status")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"{path}.status is unsupported")
    reason = _require_text(value.get("reason"), f"{path}.reason")
    return {**value, "status": status, "reason": reason}


def validate_manifest(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    changes = value.get("changes")
    verification = value.get("verification")
    if not isinstance(changes, dict) or not isinstance(verification, dict):
        raise ValueError("changes and verification must be objects")
    automated = verification.get("automated")
    if not isinstance(automated, list):
        raise ValueError("verification.automated must be an array")
    normalized_automated: list[dict[str, str]] = []
    for index, item in enumerate(automated):
        if not isinstance(item, dict):
            raise ValueError(f"verification.automated[{index}] must be an object")
        status = _require_text(item.get("status"), f"verification.automated[{index}].status")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"verification.automated[{index}].status is unsupported")
        normalized_automated.append(
            {
                "name": _require_text(item.get("name"), f"verification.automated[{index}].name"),
                "status": status,
                "evidence": _require_text(
                    item.get("evidence"), f"verification.automated[{index}].evidence"
                ),
            }
        )
    integration = _status_block(verification.get("integration"), "integration")
    screenshots = _status_block(verification.get("screenshots"), "screenshots")
    if not isinstance(integration.get("scripts", []), list):
        raise ValueError("integration.scripts must be an array")
    if not isinstance(screenshots.get("items", []), list):
        raise ValueError("screenshots.items must be an array")
    return {
        "schema": SCHEMA,
        "title": _require_text(value.get("title"), "title"),
        "generatedAt": _require_text(value.get("generatedAt"), "generatedAt"),
        "summary": _require_text(value.get("summary"), "summary"),
        "changes": {
            name: _require_string_list(changes.get(name), f"changes.{name}")
            for name in ("code", "database", "workflow")
        },
        "verification": {
            "automated": normalized_automated,
            "integration": integration,
            "screenshots": screenshots,
        },
    }


def _items(values: list[str]) -> str:
    if not values:
        return '<p class="muted">无变化</p>'
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in values) + "</ul>"


def _image_data(root: Path, relative_path: str) -> tuple[str, str]:
    candidate = (root / relative_path).resolve()
    if root.resolve() not in candidate.parents:
        raise ValueError("screenshot path escapes manifest directory")
    data = candidate.read_bytes()
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("screenshot exceeds 8 MiB")
    mime = mimetypes.guess_type(candidate.name)[0]
    if mime not in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        raise ValueError("screenshot type is unsupported")
    return mime, base64.b64encode(data).decode("ascii")


def build_report(value: dict[str, Any], manifest_root: Path) -> str:
    screenshots = value["verification"]["screenshots"]
    figures: list[str] = []
    for item in screenshots.get("items", []):
        if not isinstance(item, dict):
            raise ValueError("screenshots.items entries must be objects")
        path = _require_text(item.get("path"), "screenshots.items.path")
        caption = _require_text(item.get("caption"), "screenshots.items.caption")
        mime, encoded = _image_data(manifest_root, path)
        figures.append(
            f'<figure><img alt="{html.escape(caption)}" src="data:{mime};base64,{encoded}">'
            f"<figcaption>{html.escape(caption)}</figcaption></figure>"
        )
    automated = "".join(
        "<tr>"
        f"<td>{html.escape(item['name'])}</td>"
        f"<td><code>{html.escape(item['status'])}</code></td>"
        f"<td>{html.escape(item['evidence'])}</td>"
        "</tr>"
        for item in value["verification"]["automated"]
    )
    scripts = integration_scripts(value["verification"]["integration"].get("scripts", []))
    css = "".join(
        (
            ":root{color-scheme:light dark;font-family:-apple-system,",
            'BlinkMacSystemFont,"Segoe UI",sans-serif}',
            "body{margin:0;background:#f4f6fa;color:#172033}",
            "main{max-width:980px;margin:auto;padding:32px 20px}",
            "section,header{background:white;border:1px solid #dce2eb;border-radius:16px;",
            "padding:24px;margin:16px 0;box-shadow:0 8px 24px #1d2a4412}",
            "h1{margin-top:0}h2{font-size:1.12rem}.muted{color:#647087}",
            "code{background:#edf1f7;border-radius:6px;padding:2px 6px}",
            "table{width:100%;border-collapse:collapse}",
            "th,td{text-align:left;border-bottom:1px solid #e3e7ee;padding:10px}",
            "img{display:block;max-width:100%;height:auto;border-radius:10px;",
            "border:1px solid #dce2eb}figcaption{margin-top:8px;color:#647087}",
            "@media(prefers-color-scheme:dark){body{background:#111722;color:#e8edf7}",
            "section,header{background:#1b2432;border-color:#344156}",
            "code{background:#283548}}",
        )
    )
    integration = value["verification"]["integration"]
    screenshot_content = "".join(figures) or '<p class="muted">本报告没有关键截图。</p>'
    document = "\n".join(
        (
            "<!doctype html>",
            '<html lang="zh-CN"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            f"<title>{html.escape(value['title'])}</title><style>{css}</style></head>",
            f'<body><main data-schema="{SCHEMA}">',
            '<header><p class="muted">Granoflow 验收报告 · '
            f"{html.escape(value['generatedAt'])}</p>",
            f"<h1>{html.escape(value['title'])}</h1>",
            f"<p>{html.escape(value['summary'])}</p></header>",
            f"<section><h2>代码变化</h2>{_items(value['changes']['code'])}",
            f"<h2>数据库变化</h2>{_items(value['changes']['database'])}",
            f"<h2>流程变化</h2>{_items(value['changes']['workflow'])}</section>",
            "<section><h2>自动化验证</h2><table><thead><tr>",
            "<th>检查</th><th>状态</th><th>证据</th></tr></thead>",
            f"<tbody>{automated}</tbody></table></section>",
            "<section><h2>集成测试</h2><p>",
            f"<code>{html.escape(integration['status'])}</code> ",
            f"{html.escape(integration['reason'])}</p>{scripts}</section>",
            "<section><h2>截图验证</h2><p>",
            f"<code>{html.escape(screenshots['status'])}</code> ",
            f"{html.escape(screenshots['reason'])}</p>{screenshot_content}</section>",
            "</main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_REPORT_BYTES:
        raise ValueError("acceptance report exceeds 25 MiB")
    if validate_report_html(document) != "ok":
        raise ValueError("generated acceptance report violates the safe HTML policy")
    return document


def integration_scripts(values: list[Any]) -> str:
    if not values:
        return '<p class="muted">没有编排脚本。</p>'
    rows: list[str] = []
    for item in values:
        if not isinstance(item, dict):
            raise ValueError("integration.scripts entries must be objects")
        path = _require_text(item.get("path"), "integration.scripts.path")
        check = _require_text(item.get("check"), "integration.scripts.check")
        rows.append(
            f"<tr><td><code>{html.escape(path)}</code></td>" f"<td>{html.escape(check)}</td></tr>"
        )
    return (
        "<table><thead><tr><th>脚本</th><th>静态检查</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def validate_report_html(document: str) -> str:
    if FORBIDDEN_HTML.search(document):
        return "forbidden_active_or_remote_content"
    if f'data-schema="{SCHEMA}"' not in document:
        return "schema_marker_missing"
    return "ok"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a self-contained Granoflow acceptance HTML."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    value = validate_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
    document = build_report(value, args.manifest.parent)
    args.output.write_text(document, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "schema": SCHEMA,
                "output": str(args.output.resolve()),
                "contentSha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
                "sizeBytes": len(document.encode("utf-8")),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
