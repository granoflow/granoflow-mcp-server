#!/usr/bin/env python3
"""Lint prototype HTML for user-visible copy-boundary leaks.

Fails closed when design rationale / filtering policy / reviewer pedagogy
appears inside simulated product UI.

Product UI scope:
  - elements matching .phone, [data-product-ui], .device-frame, .product-ui
  - if none exist, the entire <body> (fail-safe)

Reviewer-only regions (skipped):
  - [data-reviewer-only], .thesis, .reviewer-note, .gallery-caption
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PRODUCT_UI_CLASSES = frozenset(
    {"phone", "device-frame", "device_frame", "product-ui", "product_ui"}
)
REVIEWER_CLASSES = frozenset(
    {
        "thesis",
        "reviewer-note",
        "reviewer_note",
        "gallery-caption",
        "gallery_caption",
    }
)

LEAK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("zero_type_hidden", re.compile(r"0\s*本的类型不显示")),
    ("no_filenames_on_confirm", re.compile(r"不会在确认页|确认页列出文件名")),
    ("suffix_only_policy", re.compile(r"仅按.{0,12}后缀|只计后缀|不在导入前")),
    ("md5_design_timing", re.compile(r"不在导入前计算\s*MD5|MD5.{0,20}结束后汇总")),
    ("reviewer_debug", re.compile(r"便于排查|不混在同一列表|两组分栏查看")),
    ("design_rationale_zh", re.compile(r"设计理由|差异轴", re.I)),
    (
        "expr_axis_narration",
        re.compile(r"\bexpr_[ab]\b.{0,40}(hierarchy|interaction|置顶)", re.I),
    ),
    (
        "confidence_en",
        re.compile(
            r"high[- ]confidence|only reliable results|passed filtering",
            re.I,
        ),
    ),
    ("acceptance_leak", re.compile(r"验收\s*A\d+|acceptance\s+id", re.I)),
    (
        "for_reviewer",
        re.compile(r"for reviewers?|design rationale|filtering policy", re.I),
    ),
]


def _tokens(class_attr: str) -> set[str]:
    return {c for c in re.split(r"\s+", class_attr.strip()) if c}


def _marks_product(attrs: dict[str, str | None]) -> bool:
    if "data-product-ui" in attrs:
        return True
    return bool(_tokens(attrs.get("class") or "") & PRODUCT_UI_CLASSES)


def _marks_reviewer(attrs: dict[str, str | None]) -> bool:
    if "data-reviewer-only" in attrs:
        return True
    return bool(_tokens(attrs.get("class") or "") & REVIEWER_CLASSES)


class ProductTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict[str, bool]] = []
        self.product_chunks: list[str] = []
        self.body_chunks: list[str] = []
        self.in_body = False
        self.saw_product_frame = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: v for k, v in attrs}
        product = _marks_product(attr_map)
        reviewer = _marks_reviewer(attr_map)
        parent_product = self.stack[-1]["product"] if self.stack else False
        parent_reviewer = self.stack[-1]["reviewer"] if self.stack else False
        node = {
            "tag": tag.lower(),
            "product": parent_product or product,
            "reviewer": parent_reviewer or reviewer,
            "opens_product": product,
        }
        if product:
            self.saw_product_frame = True
        if tag.lower() == "body":
            self.in_body = True
        self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break
        if tag == "body":
            self.in_body = any(n["tag"] == "body" for n in self.stack)

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        reviewer = self.stack[-1]["reviewer"] if self.stack else False
        product = self.stack[-1]["product"] if self.stack else False
        if reviewer:
            return
        if product:
            self.product_chunks.append(data)
        elif self.in_body or not self.stack:
            self.body_chunks.append(data)


def extract_product_text(html: str) -> tuple[str, bool]:
    extractor = ProductTextExtractor()
    extractor.feed(html)
    if extractor.saw_product_frame:
        return ("\n".join(extractor.product_chunks), True)
    return ("\n".join(extractor.body_chunks), False)


def find_leaks(text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for code, pattern in LEAK_PATTERNS:
        for match in pattern.finditer(text):
            hits.append(
                {
                    "code": code,
                    "match": match.group(0)[:120],
                    "failCode": "user_visible_copy_boundary_violation",
                }
            )
    return hits


def lint_html(html: str, *, path: str | None = None) -> dict:
    text, used_frame = extract_product_text(html)
    hits = find_leaks(text)
    return {
        "ok": len(hits) == 0,
        "path": path,
        "productFrameScoped": used_frame,
        "failCode": None if not hits else "user_visible_copy_boundary_violation",
        "hits": hits,
        "scannedChars": len(text),
    }


def lint_path(path: Path) -> dict:
    return lint_html(path.read_text(encoding="utf-8"), path=str(path))


def expand_paths(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        path = path.resolve()
        if path.is_dir():
            index = path / "index.html"
            if index.is_file():
                out.append(index)
            else:
                out.extend(sorted(path.rglob("*.html")))
        elif path.is_file():
            out.append(path)
        else:
            raise FileNotFoundError(str(path))
    seen: set[str] = set()
    unique: list[Path] = []
    for item in out:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def lint_many(paths: list[Path]) -> dict:
    results = [lint_path(p) for p in paths]
    hits = [h for r in results for h in r["hits"]]
    return {
        "ok": all(r["ok"] for r in results),
        "failCode": None if not hits else "user_visible_copy_boundary_violation",
        "files": results,
        "hitCount": len(hits),
    }


def build_parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="HTML files or directories containing index.html",
    )
    return value


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        files = expand_paths(args.paths)
        if not files:
            raise ValueError("no HTML files found")
        result = lint_many(files)
    except (OSError, ValueError) as error:
        print(
            json.dumps(
                {
                    "ok": False,
                    "failCode": "user_visible_copy_lint_error",
                    "error": str(error),
                },
                ensure_ascii=False,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
