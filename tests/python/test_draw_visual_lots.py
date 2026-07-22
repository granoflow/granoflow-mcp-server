from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-project-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from draw_visual_lots import (  # noqa: E402
    VisualLotError,
    append_ledger,
    draw_shell_chrome,
    draw_spec_seeds,
    load_ledger,
    load_shell_deck,
    load_spec_deck,
    main,
)


class DrawVisualLotsTest(unittest.TestCase):
    def test_spec_draw_returns_distinct_true_random_seeds(self) -> None:
        seeds = draw_spec_seeds(count=3, ledger=None, dedupe=False)
        self.assertEqual(len(seeds), 3)
        self.assertEqual(len(set(seeds)), 3)
        self.assertTrue(set(seeds).issubset(set(load_spec_deck())))

    def test_shell_draw_returns_distinct_cards(self) -> None:
        cards = draw_shell_chrome(count=3, ledger=None, dedupe=False)
        ids = [card["id"] for card in cards]
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue(set(ids).issubset({card["id"] for card in load_shell_deck()}))

    def test_ledger_dedupe_excludes_historical_spec_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.json"
            blocked = load_spec_deck()[:5]
            append_ledger(ledger_path, kind="spec_seed", ids=blocked)
            drawn = draw_spec_seeds(
                count=3,
                ledger=load_ledger(ledger_path),
                dedupe=True,
            )
            self.assertTrue(set(drawn).isdisjoint(set(blocked)))

    def test_exhausted_pool_raises_visual_lot_exhausted(self) -> None:
        tiny = ["seed-a", "seed-b"]
        ledger = {
            "schema": "granoflow.visual_lot_ledger",
            "entries": [
                {"kind": "spec_seed", "id": "seed-a", "at": "t"},
                {"kind": "spec_seed", "id": "seed-b", "at": "t"},
            ],
        }
        with self.assertRaises(VisualLotError) as ctx:
            draw_spec_seeds(count=1, ledger=ledger, dedupe=True, deck=tiny)
        self.assertEqual(ctx.exception.code, "visual_lot_exhausted")

    def test_cli_rejects_classroom_salt_and_from(self) -> None:
        for args in (
            ["--kind", "spec", "--count", "1", "--from", "student-1"],
            ["--kind", "spec", "--count", "1", "--salt", "cohort-a"],
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(args)
            self.assertEqual(code, 2)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["code"], "visual_lot_classroom_salt_forbidden")

    def test_cli_json_ok_and_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(
                    [
                        "--kind",
                        "shell",
                        "--count",
                        "2",
                        "--ledger",
                        str(ledger_path),
                        "--record",
                    ]
                )
            self.assertEqual(code, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["entropy"], "true_random")
            self.assertEqual(len(payload["ids"]), 2)
            ledger = load_ledger(ledger_path)
            self.assertEqual(len(ledger["entries"]), 2)
            self.assertEqual(ledger["entries"][0]["kind"], "shell_chrome")


if __name__ == "__main__":
    unittest.main()
