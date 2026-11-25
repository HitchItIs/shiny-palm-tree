import unittest
from unittest.mock import patch
from core.evaluator import Evaluator
from generators.raid import RaidGenerator


class TestRaidGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = RaidGenerator()
        self.evaluator = Evaluator()

    def test_raid_0_fixed(self) -> None:
        with patch("random.choice", side_effect=[0, 4]), patch.object(self.gen, "_gauss_int", return_value=4):
            task = self.gen.generate()
            fields = {f.key: f.expected_value for f in task.fields}
            self.assertEqual(fields["gross_capacity"], 16)  # 4 * 4 TB
            self.assertEqual(fields["net_capacity"], 16)
            self.assertEqual(fields["max_failed_disks"], 0)
            self.assertEqual(fields["efficiency"], 100.0)

            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(result.is_correct)

    def test_raid_1_fixed(self) -> None:
        with patch("random.choice", side_effect=[1, 4]):
            task = self.gen.generate()
            fields = {f.key: f.expected_value for f in task.fields}
            self.assertEqual(fields["gross_capacity"], 8)  # 2 * 4 TB
            self.assertEqual(fields["net_capacity"], 4)
            self.assertEqual(fields["max_failed_disks"], 1)
            self.assertEqual(fields["efficiency"], 50.0)

            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(result.is_correct)

    def test_raid_5_fixed(self) -> None:
        with patch("random.choice", side_effect=[5, 4]), patch.object(self.gen, "_gauss_int", return_value=4):
            task = self.gen.generate()
            fields = {f.key: f.expected_value for f in task.fields}
            self.assertEqual(fields["gross_capacity"], 16)  # 4 * 4 TB
            self.assertEqual(fields["net_capacity"], 12)  # (4-1) * 4 TB
            self.assertEqual(fields["max_failed_disks"], 1)
            self.assertEqual(fields["efficiency"], 75.0)

            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(result.is_correct)

    def test_raid_6_fixed(self) -> None:
        with patch("random.choice", side_effect=[6, 4]), patch.object(self.gen, "_gauss_int", return_value=4):
            task = self.gen.generate()
            fields = {f.key: f.expected_value for f in task.fields}
            self.assertEqual(fields["gross_capacity"], 16)  # 4 * 4 TB
            self.assertEqual(fields["net_capacity"], 8)   # (4-2) * 4 TB
            self.assertEqual(fields["max_failed_disks"], 2)
            self.assertEqual(fields["efficiency"], 50.0)

            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(result.is_correct)

    def test_raid_10_fixed(self) -> None:
        with patch("random.choice", side_effect=[10, 4, 4]):
            task = self.gen.generate()
            fields = {f.key: f.expected_value for f in task.fields}
            self.assertEqual(fields["gross_capacity"], 16)  # 4 * 4 TB
            self.assertEqual(fields["net_capacity"], 8)   # (4//2) * 4 TB
            self.assertEqual(fields["max_failed_disks"], 1)
            self.assertEqual(fields["efficiency"], 50.0)

            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(result.is_correct)

    def test_100_random_tasks(self) -> None:
        for _ in range(100):
            task = self.gen.generate()
            self.assertEqual(task.category, "raid")
            self.assertEqual(len(task.fields), 4)
            self.assertTrue(len(task.solution_steps) >= 4)

            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(
                result.is_correct,
                f"Task failed: {task.title}, expected: {[f.expected_value for f in task.fields]}, answers: {answers}"
            )
            self.assertEqual(result.points_earned, result.max_points)


if __name__ == "__main__":
    unittest.main()
