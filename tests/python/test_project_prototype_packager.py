from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-project-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from package_prototype import build_zip, collect_files  # noqa: E402


class ProjectPrototypePackagerTest(unittest.TestCase):
    def test_build_is_deterministic_and_normalizes_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "index.html").write_text("<!doctype html>", encoding="utf-8")
            (source / "assets").mkdir()
            (source / "assets" / "app.css").write_text("body{}", encoding="utf-8")
            first = root / "first.zip"
            second = root / "second.zip"

            build_zip(source, first)
            build_zip(source, second)

            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            )
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(
                    archive.namelist(),
                    ["assets/app.css", "index.html", "manifest.json"],
                )
                self.assertTrue(
                    all(item.date_time == (1980, 1, 1, 0, 0, 0) for item in archive.infolist())
                )
                manifest = archive.read("manifest.json").decode("utf-8")
                self.assertIn('"schema":"granoflow.prototype"', manifest)
                self.assertIn('"artifactRole":"project_design_baseline"', manifest)

    def test_dry_run_does_not_write_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "index.html").write_text("ok", encoding="utf-8")
            output = root / "preview.zip"

            result = build_zip(source, output, dry_run=True)

            self.assertTrue(result["dryRun"])
            self.assertFalse(output.exists())

    def test_requires_root_index_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "prototype.html").write_text("no", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "root index.html"):
                collect_files(source)

    def test_lint_user_copy_flag_rejects_leaks(self) -> None:
        import json
        import subprocess

        script = SCRIPTS / "package_prototype.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "index.html").write_text(
                '<!doctype html><html><body><div class="phone">'
                "<p>0 本的类型不显示</p></div></body></html>",
                encoding="utf-8",
            )
            output = root / "out.granoprototype"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(source),
                    str(output),
                    "--lint-user-copy",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(
                payload.get("failCode"), "user_visible_copy_boundary_violation"
            )


if __name__ == "__main__":
    unittest.main()
