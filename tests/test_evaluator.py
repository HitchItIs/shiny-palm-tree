import unittest

from core.evaluator import Evaluator
from core.models import InputField, Task


class TestEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = Evaluator()
        self.sample_task = Task(
            category="test",
            title="Sample",
            description="Sample task",
            fields=[
                InputField("mask", "Subnetzmaske", "255.255.255.128"),
                InputField("hosts", "Hosts", 126),
                InputField("power", "Kosten", 12.45, unit="€", tolerance=0.1),
            ],
            solution_steps=[],
        )

    def test_all_correct_with_formatting(self) -> None:
        answers = {
            "mask": "  255.255.255.128 ",
            "hosts": "126",
            "power": "12,5",  # German decimal comma within 0.1 tolerance
        }
        result = self.evaluator.evaluate(self.sample_task, answers)
        self.assertTrue(result.is_correct)
        self.assertEqual(result.points_earned, 3)
        self.assertEqual(result.max_points, 3)

    def test_partial_and_invalid_answers(self) -> None:
        answers = {
            "mask": "255.255.255.0",  # wrong
            "hosts": "not a number",  # invalid int
            "power": "12.45",         # right
        }
        result = self.evaluator.evaluate(self.sample_task, answers)
        self.assertFalse(result.is_correct)
        self.assertEqual(result.points_earned, 1)
        self.assertEqual(
            result.field_results,
            {"mask": False, "hosts": False, "power": True},
        )

    def test_missing_answers_score_false(self) -> None:
        result = self.evaluator.evaluate(self.sample_task, {})
        self.assertFalse(result.is_correct)
        self.assertEqual(result.points_earned, 0)


if __name__ == "__main__":
    unittest.main()