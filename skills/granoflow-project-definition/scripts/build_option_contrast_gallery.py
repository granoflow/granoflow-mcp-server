#!/usr/bin/env python3
"""Build a side-by-side Contrast Gallery for interactive prototype option sets.

Interactive dual/triple task ui_prototype batches Must present options in one
viewport with per-axis visible-diff captions. This script produces that page
from a JSON manifest so hosts do not emit separate links alone.

After Design Baseline lock, task options are **page expressions** (`expr_a` /
`expr_b`) inside the locked Design System—not a second Design Spec vote.

Example manifest (JSON):

    {
      "title": "M2 Page Expression Gallery",
      "recommendation": "Design System 已锁定。按页选择 expr_a 或 expr_b（可混选）。",
      "design_system_locked": "ai_challenger",
      "tasks": [
        {
          "id": "eacaf815-…",
          "title": "完善书架…",
          "screens": ["S-bookshelf"],
          "contrast_axes": ["information_hierarchy", "interaction_pattern"],
          "visible_diffs": [
            {"axis": "information_hierarchy", "caption": "续读顶栏条卡 vs 续读英雄大卡"},
            {"axis": "interaction_pattern", "caption": "搜索降噪常驻 vs 搜索收入菜单"}
          ],
          "options": [
            {
              "id": "expr_a",
              "summary": "续读顶栏条卡 + 搜索降噪",
              "relative_href": "packages/…/expr_a/index.html"
            },
            {
              "id": "expr_b",
              "summary": "续读英雄大卡 + 搜索常驻",
              "relative_href": "packages/…/expr_b/index.html"
            }
          ]
        }
      ]
    }

Fail closed (print JSON error + exit 2):
  - prototype_option_contrast_gallery_required (empty tasks / <2 options)
  - prototype_option_diff_unlabeled (missing per-axis captions)
  - prototype_option_contrast_insufficient (<2 axes)
  - prototype_option_design_system_reopened (task option ids reopen Spec)
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


class GalleryError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


WHITELIST_AXES = {
    "information_hierarchy",
    "density",
    "interaction_pattern",
    "state_emphasis",
    "progressive_disclosure",
    "secondary_nav_within_delta",
}

# Design Spec triad labels must not appear as task-level option ids after
# Baseline lock (page expressions use expr_a / expr_b instead).
FORBIDDEN_TASK_OPTION_IDS = {
    "delta_match",
    "ai_challenger",
    "ai_challenger_a",
    "ai_challenger_b",
    "spec_match",
    "shell_match",
}


def _validate_task(task: dict[str, Any]) -> None:
    tid = str(task.get("id") or "").strip() or "<unknown>"
    options = task.get("options") or []
    if not isinstance(options, list) or len(options) < 2:
        raise GalleryError(
            "prototype_option_contrast_gallery_required",
            f"task {tid}: need ≥2 options for a contrast gallery",
        )
    for opt in options:
        if not isinstance(opt, dict):
            continue
        oid = str(opt.get("id") or "").strip()
        if oid in FORBIDDEN_TASK_OPTION_IDS:
            raise GalleryError(
                "prototype_option_design_system_reopened",
                f"task {tid}: option id {oid!r} reopens Design Spec; "
                f"use expr_a / expr_b (page expressions) inside locked Design System",
            )
    axes = task.get("contrast_axes") or []
    if not isinstance(axes, list) or len(axes) < 2:
        raise GalleryError(
            "prototype_option_contrast_insufficient",
            f"task {tid}: need ≥2 contrast_axes",
        )
    for axis in axes:
        if axis not in WHITELIST_AXES:
            raise GalleryError(
                "prototype_option_contrast_insufficient",
                f"task {tid}: axis {axis!r} not in whitelist",
            )
    diffs = task.get("visible_diffs") or []
    if not isinstance(diffs, list) or not diffs:
        raise GalleryError(
            "prototype_option_diff_unlabeled",
            f"task {tid}: visible_diffs required (one caption per declared axis)",
        )
    covered = {str(item.get("axis") or "") for item in diffs if isinstance(item, dict)}
    missing = [axis for axis in axes if axis not in covered]
    if missing:
        raise GalleryError(
            "prototype_option_diff_unlabeled",
            f"task {tid}: missing visible_diffs for axes {missing}",
        )
    for item in diffs:
        if not isinstance(item, dict):
            continue
        caption = str(item.get("caption") or "").strip()
        if not caption or caption in WHITELIST_AXES:
            raise GalleryError(
                "prototype_option_diff_unlabeled",
                f"task {tid}: caption must be a screen-checkable difference, "
                f"not an empty string or bare axis name",
            )
        if " vs " not in caption.lower() and "→" not in caption and "->" not in caption:
            # Soft hint only encoded as requirement: prefer comparative wording.
            # Still accept Chinese 「与」「对比」 etc.
            comparative_tokens = (" vs ", "对比", "相对", "而非", " vs", "／", "/")
            if not any(tok in caption for tok in comparative_tokens):
                raise GalleryError(
                    "prototype_option_diff_unlabeled",
                    f"task {tid}: caption {caption!r} must compare both options "
                    f"(include 对比 / vs / 而非 / →)",
                )


def _validate_manifest(data: dict[str, Any]) -> None:
    tasks = data.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        raise GalleryError(
            "prototype_option_contrast_gallery_required",
            "manifest.tasks must be a non-empty list",
        )
    for task in tasks:
        if not isinstance(task, dict):
            raise GalleryError(
                "prototype_option_contrast_gallery_required",
                "each tasks[] entry must be an object",
            )
        _validate_task(task)


def _render_task(task: dict[str, Any]) -> str:
    tid = html.escape(str(task.get("id") or ""))
    title = html.escape(str(task.get("title") or tid))
    screens = ", ".join(str(s) for s in (task.get("screens") or []))
    screens_h = html.escape(screens)
    diffs = task.get("visible_diffs") or []
    diff_lis = "".join(
        f"<li><b>{html.escape(str(d.get('axis')))}</b> — "
        f"{html.escape(str(d.get('caption')))}</li>"
        for d in diffs
        if isinstance(d, dict)
    )
    option_cards = []
    for opt in task.get("options") or []:
        if not isinstance(opt, dict):
            continue
        oid = html.escape(str(opt.get("id") or ""))
        summary = html.escape(str(opt.get("summary") or ""))
        href = html.escape(str(opt.get("relative_href") or ""), quote=True)
        option_cards.append(
            f"""
      <article>
        <h3>{oid}</h3>
        <p>{summary}</p>
        <iframe src="{href}" title="{oid}" loading="lazy"></iframe>
        <p><a href="{href}" target="_blank" rel="noopener">单独打开</a></p>
      </article>"""
        )
    return f"""
  <section class="card" id="{tid[:8]}">
    <h2>{title}</h2>
    <p class="meta">task <code>{tid}</code> · {screens_h}</p>
    <div class="diffs"><b>可见差异（请在画面中核对）：</b><ul>{diff_lis}</ul></div>
    <div class="pair">
{''.join(option_cards)}
    </div>
  </section>"""


def build_html(data: dict[str, Any]) -> str:
    _validate_manifest(data)
    title = html.escape(str(data.get("title") or "Prototype Contrast Gallery"))
    recommendation = html.escape(
        str(
            data.get("recommendation")
            or "Design System 已锁定。按页选择 expr_a 或 expr_b（可混选）。"
        )
    )
    sections = "".join(_render_task(t) for t in data["tasks"])
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<style>
:root {{
  --bg:#fff; --ink:#1a2422; --muted:#667370; --primary:#2f6f68;
  --surface:#f4f8f7; --line:#d7e0de; --radius:14px;
}}
body {{ margin:0; font-family: system-ui, -apple-system, sans-serif;
  color:var(--ink); background:#eef3f2; }}
header {{ padding:28px 32px; background:var(--bg); border-bottom:1px solid var(--line); }}
h1 {{ margin:0 0 8px; font-size:28px; }}
header p {{ margin:0; color:var(--muted); max-width:72ch; }}
.banner {{ margin:16px 32px 0; padding:12px 14px; border-radius:var(--radius);
  background:color-mix(in srgb, var(--primary) 10%, white);
  border:1px solid var(--line); font-size:14px; }}
main {{ padding:24px 32px 80px; display:grid; gap:28px; }}
.card {{ background:var(--bg); border:1px solid var(--line);
  border-radius:var(--radius); padding:20px; }}
.card h2 {{ margin:0 0 6px; font-size:18px; }}
.meta {{ color:var(--muted); font-size:13px; margin:0 0 10px; }}
.diffs {{ font-size:13px; margin:0 0 14px; padding:10px 12px;
  background:var(--surface); border-radius:12px; border:1px solid var(--line); }}
.diffs ul {{ margin:8px 0 0; padding-left:1.2em; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
@media (max-width:900px) {{ .pair {{ grid-template-columns:1fr; }} }}
article {{ border:1px solid var(--line); border-radius:12px; padding:12px;
  background:var(--surface); }}
article h3 {{ margin:0 0 6px; color:var(--primary); }}
article p {{ font-size:13px; color:var(--muted); min-height:2.8em; }}
iframe {{ width:100%; height:640px; border:1px solid var(--line);
  border-radius:12px; background:#fff; }}
a {{ color:var(--primary); }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p>左右并排对比。差异须在画面上可辨；勿只读说明文字。</p>
</header>
<p class="banner">{recommendation}</p>
<main>
{sections}
</main>
</body>
</html>
"""


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("manifest", type=Path, help="JSON manifest path")
    value.add_argument(
        "output",
        type=Path,
        help="Destination index.html (or directory; writes index.html inside)",
    )
    value.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only; print ok JSON without writing",
    )
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise GalleryError(
                "prototype_option_contrast_gallery_required",
                "manifest root must be a JSON object",
            )
        html_out = build_html(data)
    except GalleryError as error:
        print(
            json.dumps(
                {"ok": False, "code": error.code, "error": error.message},
                ensure_ascii=False,
            )
        )
        return 2
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(
            json.dumps(
                {
                    "ok": False,
                    "code": "prototype_option_contrast_gallery_required",
                    "error": str(error),
                },
                ensure_ascii=False,
            )
        )
        return 2

    output = args.output
    if output.suffix.lower() != ".html":
        output = output / "index.html"
    if args.dry_run:
        print(
            json.dumps(
                {
                    "ok": True,
                    "dryRun": True,
                    "tasks": len(data["tasks"]),
                    "output": str(output.resolve()),
                },
                ensure_ascii=False,
            )
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_out, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "dryRun": False,
                "tasks": len(data["tasks"]),
                "output": str(output.resolve()),
                "bytes": output.stat().st_size,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
