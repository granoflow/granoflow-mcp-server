#!/usr/bin/env python3
"""Draw true-random Design Spec seeds and App Shell chrome lots.

Agents Must call this script instead of inventing seed-* / chrome ids.
Classroom salt / --from is rejected: every draw is true random.
Request-more batches Must pass --dedupe ledger (machine-local history).
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "granoflow.visual_lot_ledger"
DEFAULT_LEDGER = Path.home() / ".granoflow" / "visual-lot-ledger.json"
REFERENCES = Path(__file__).resolve().parents[1] / "references"


class VisualLotError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_spec_deck(path: Path | None = None) -> list[str]:
    deck_path = path or (REFERENCES / "spec-seed-deck.json")
    data = _load_json(deck_path)
    return [str(item["id"]) for item in data["seeds"]]


def load_shell_deck(path: Path | None = None) -> list[dict[str, Any]]:
    deck_path = path or (REFERENCES / "shell-chrome-deck.json")
    data = _load_json(deck_path)
    return list(data["cards"])


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schema": SCHEMA, "entries": []}
    data = _load_json(path)
    if data.get("schema") != SCHEMA:
        raise VisualLotError(
            "visual_lot_ledger_invalid",
            f"ledger schema must be {SCHEMA}",
        )
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise VisualLotError("visual_lot_ledger_invalid", "ledger.entries must be a list")
    return {"schema": SCHEMA, "entries": entries}


def used_ids(ledger: dict[str, Any], kind: str) -> set[str]:
    out: set[str] = set()
    for entry in ledger.get("entries", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("kind") == kind and isinstance(entry.get("id"), str):
            out.add(entry["id"])
    return out


def append_ledger(
    path: Path,
    *,
    kind: str,
    ids: list[str],
    project_id: str | None = None,
) -> None:
    ledger = load_ledger(path)
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    for lot_id in ids:
        entry: dict[str, Any] = {"kind": kind, "id": lot_id, "at": now}
        if project_id:
            entry["project_id"] = project_id
        ledger["entries"].append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def _pick_unique(pool: list[str], count: int, rng: secrets.SystemRandom) -> list[str]:
    if count > len(pool):
        raise VisualLotError(
            "visual_lot_exhausted",
            f"need {count} lots but only {len(pool)} remain after dedupe",
        )
    chosen = rng.sample(pool, count)
    return chosen


def draw_spec_seeds(
    *,
    count: int,
    ledger: dict[str, Any] | None,
    dedupe: bool,
    deck: list[str] | None = None,
    rng: secrets.SystemRandom | None = None,
) -> list[str]:
    rng = rng or secrets.SystemRandom()
    seeds = list(deck or load_spec_deck())
    if dedupe and ledger is not None:
        blocked = used_ids(ledger, "spec_seed")
        seeds = [s for s in seeds if s not in blocked]
    return _pick_unique(seeds, count, rng)


def draw_shell_chrome(
    *,
    count: int,
    ledger: dict[str, Any] | None,
    dedupe: bool,
    deck: list[dict[str, Any]] | None = None,
    rng: secrets.SystemRandom | None = None,
    max_attempts: int = 64,
) -> list[dict[str, Any]]:
    """Draw chrome cards; prefer distinct families when the pool allows."""
    rng = rng or secrets.SystemRandom()
    cards = list(deck or load_shell_deck())
    if dedupe and ledger is not None:
        blocked = used_ids(ledger, "shell_chrome")
        cards = [c for c in cards if c["id"] not in blocked]
    if count > len(cards):
        raise VisualLotError(
            "visual_lot_exhausted",
            f"need {count} chrome lots but only {len(cards)} remain after dedupe",
        )

    for _ in range(max_attempts):
        picked = rng.sample(cards, count)
        families = {str(card.get("family", card["id"])) for card in picked}
        # Soft diversity: if pool has enough families, require >1 family for count>=2
        available_families = {str(c.get("family", c["id"])) for c in cards}
        if count >= 2 and len(available_families) >= 2 and len(families) < 2:
            continue
        if (
            count >= 3
            and len(available_families) >= 3
            and len(families) < min(3, len(available_families))
        ):
            continue
        return picked
    # Fallback: accept last sample without family constraint (still unique ids)
    return rng.sample(cards, count)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        required=True,
        choices=("spec", "shell"),
        help="spec = Design Spec seeds; shell = App Shell chrome cards",
    )
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER,
        help="machine-local visual lot ledger (default: ~/.granoflow/visual-lot-ledger.json)",
    )
    parser.add_argument(
        "--dedupe",
        choices=("off", "ledger"),
        default="off",
        help="ledger = strong dedupe against machine-local history (use for request-more)",
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="append drawn lots to the ledger",
    )
    parser.add_argument("--project-id", default=None)
    parser.add_argument(
        "--from",
        dest="from_key",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--salt",
        default=None,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.from_key is not None or args.salt is not None:
        payload = {
            "ok": False,
            "code": "visual_lot_classroom_salt_forbidden",
            "error": "classroom salt / --from is forbidden; draws are true-random only",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 2

    if args.count < 1:
        payload = {
            "ok": False,
            "code": "visual_lot_invalid_count",
            "error": "count must be >= 1",
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 2

    dedupe = args.dedupe == "ledger"
    try:
        ledger = load_ledger(args.ledger) if dedupe or args.record else None
        if args.kind == "spec":
            ids = draw_spec_seeds(
                count=args.count,
                ledger=ledger if dedupe else None,
                dedupe=dedupe,
            )
            lots = [{"id": lot_id} for lot_id in ids]
            kind_key = "spec_seed"
        else:
            cards = draw_shell_chrome(
                count=args.count,
                ledger=ledger if dedupe else None,
                dedupe=dedupe,
            )
            lots = cards
            ids = [str(card["id"]) for card in cards]
            kind_key = "shell_chrome"

        if args.record:
            append_ledger(
                args.ledger,
                kind=kind_key,
                ids=ids,
                project_id=args.project_id,
            )

        payload = {
            "ok": True,
            "kind": args.kind,
            "entropy": "true_random",
            "dedupe": args.dedupe,
            "lots": lots,
            "ids": ids,
            "ledger": str(args.ledger) if args.record or dedupe else None,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except VisualLotError as exc:
        print(
            json.dumps(
                {"ok": False, "code": exc.code, "error": exc.message},
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
