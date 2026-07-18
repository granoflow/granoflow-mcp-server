from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-persistent-milestone-runner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from batch_gate import (  # noqa: E402
    freeze_batch,
    preparation_complete,
    prepared_task_ids,
    set_disposition,
)


class BatchGateTests(unittest.TestCase):
    def test_waiting_task_closes_preparation_without_entering_execution(self) -> None:
        batch = freeze_batch(
            "milestone-1",
            "batch-1",
            [{"id": "a", "status": "pending"}, {"id": "b", "status": "pending"}],
        )
        set_disposition(batch, "a", "prepared", "task_work_ready")
        self.assertFalse(preparation_complete(batch))
        set_disposition(batch, "b", "skipped_waiting", "needs_user_input", "user replies")
        self.assertTrue(preparation_complete(batch))
        self.assertEqual(prepared_task_ids(batch), {"a"})

    def test_unknown_task_cannot_be_classified(self) -> None:
        batch = freeze_batch("milestone-1", "batch-1", [{"id": "a"}])
        with self.assertRaises(KeyError):
            set_disposition(batch, "b", "prepared", "wrong_task")


if __name__ == "__main__":
    unittest.main()
