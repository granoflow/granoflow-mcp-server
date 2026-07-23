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

    def test_refresh_requires_recorded_ledger_dedupe(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(
                [
                    "--kind",
                    "spec",
                    "--request-type",
                    "refresh",
                ]
            )
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(buf.getvalue())["code"], "visual_lot_dedupe_required")

    def test_refresh_is_disjoint_and_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.json"
            receipt_path = Path(directory) / "receipt.json"
            first = io.StringIO()
            with redirect_stdout(first):
                self.assertEqual(
                    main(
                        [
                            "--kind",
                            "spec",
                            "--count",
                            "2",
                            "--ledger",
                            str(ledger_path),
                            "--record",
                        ]
                    ),
                    0,
                )
            prior_ids = set(json.loads(first.getvalue())["ids"])

            refreshed = io.StringIO()
            with redirect_stdout(refreshed):
                self.assertEqual(
                    main(
                        [
                            "--kind",
                            "spec",
                            "--count",
                            "2",
                            "--request-type",
                            "refresh",
                            "--ledger",
                            str(ledger_path),
                            "--dedupe",
                            "ledger",
                            "--record",
                            "--receipt-out",
                            str(receipt_path),
                        ]
                    ),
                    0,
                )
            payload = json.loads(refreshed.getvalue())
            self.assertTrue(prior_ids.isdisjoint(payload["ids"]))
            self.assertEqual(payload["receipt"]["request_type"], "refresh")
            self.assertNotEqual(
                payload["receipt"]["prior_ledger_sha256"],
                payload["receipt"]["ledger_after_sha256"],
            )
            self.assertEqual(
                json.loads(receipt_path.read_text())["visual_lot_receipt"]["ids"],
                payload["ids"],
            )

    def test_revise_preserves_recorded_seed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.json"
            seed_id = load_spec_deck()[0]
            append_ledger(ledger_path, kind="spec_seed", ids=[seed_id])
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(
                    [
                        "--kind",
                        "spec",
                        "--request-type",
                        "revise",
                        "--ledger",
                        str(ledger_path),
                        "--existing-id",
                        seed_id,
                    ]
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(payload["ids"], [seed_id])
            self.assertFalse(payload["receipt"]["redrawn"])

    def test_revise_rejects_unknown_seed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(
                    [
                        "--kind",
                        "spec",
                        "--request-type",
                        "revise",
                        "--ledger",
                        str(Path(directory) / "ledger.json"),
                        "--existing-id",
                        "seed-unknown",
                    ]
                )
            self.assertEqual(code, 1)
            self.assertEqual(
                json.loads(buf.getvalue())["code"],
                "visual_lot_revise_source_unknown",
            )


if __name__ == "__main__":
    unittest.main()
