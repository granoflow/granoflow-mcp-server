#!/usr/bin/env python3
"""Build a safe, deterministic Granoflow HTML prototype ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

NORMALIZED_TIME = (1980, 1, 1, 0, 0, 0)


def collect_files(source: Path) -> list[tuple[Path, str]]:
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("source must be a directory")
    if not (source / "index.html").is_file():
        raise ValueError("source must contain root index.html")

    files: list[tuple[Path, str]] = []
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed: {path}")
        if not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(source).as_posix())
        if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
            raise ValueError(f"unsafe relative path: {relative}")
        if relative.as_posix() == "manifest.json":
            continue
        files.append((path, relative.as_posix()))
    return sorted(files, key=lambda item: item[1])


def build_zip(
    source: Path,
    output: Path,
    dry_run: bool = False,
    *,
    title: str | None = None,
    version: str = "1.0.0",
) -> dict[str, object]:
    files = collect_files(source)
    resolved_title = (title or source.resolve().name).strip()
    if not resolved_title:
        raise ValueError("prototype title must not be empty")
    if not version.strip():
        raise ValueError("prototype version must not be empty")
    prototype_manifest = {
        "schema": "granoflow.prototype",
        "schemaVersion": 1,
        "entry": "index.html",
        "title": resolved_title,
        "version": version.strip(),
        "metadata": {
            "generator": "granoflow-project-definition/package_prototype.py",
            "artifactRole": "project_design_baseline",
        },
    }
    manifest_bytes = (
        json.dumps(
            prototype_manifest,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    manifest = [
        {
            "path": relative,
            "sizeBytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path, relative in files
    ]
    manifest.append(
        {
            "path": "manifest.json",
            "sizeBytes": len(manifest_bytes),
            "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        }
    )
    manifest.sort(key=lambda item: str(item["path"]))
    if not dry_run:
        output = output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(
            output,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for path, relative in files:
                info = zipfile.ZipInfo(relative, NORMALIZED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, path.read_bytes())
            manifest_info = zipfile.ZipInfo("manifest.json", NORMALIZED_TIME)
            manifest_info.compress_type = zipfile.ZIP_DEFLATED
            manifest_info.create_system = 3
            manifest_info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(manifest_info, manifest_bytes)
    return {
        "ok": True,
        "dryRun": dry_run,
        "output": str(output.resolve()),
        "entries": manifest,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("source", type=Path, help="Directory containing root index.html")
    value.add_argument("output", type=Path, help="Destination .zip path")
    value.add_argument("--dry-run", action="store_true", help="Validate and print manifest only")
    value.add_argument("--title", help="Prototype title stored in manifest.json")
    value.add_argument("--version", default="1.0.0", help="Immutable prototype version label")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        result = build_zip(
            args.source,
            args.output,
            args.dry_run,
            title=args.title,
            version=args.version,
        )
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
