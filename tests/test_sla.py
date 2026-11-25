import unittest
from unittest.mock import patch

from core.evaluator import Evaluator
from generators.sla import SlaGenerator


class TestSlaGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = SlaGenerator()
        self.evaluator = Evaluator()

    def test_fixed_99_9_percent(self) -> None:
        with patch("random.choice", return_value=99.9):
            task = self.gen.generate()

        fields = {field.key: field for field in task.fields}
        self.assertEqual(fields["downtime_hours"].expected_value, 8.76)
        self.assertEqual(fields["downtime_minutes"].expected_value, 525.6)
        self.assertEqual(fields["downtime_hours"].tolerance, 0.01)
        self.assertEqual(fields["downtime_minutes"].tolerance, 0.1)
        answers = {key: str(field.expected_value) for key, field in fields.items()}
        self.assertTrue(self.evaluator.evaluate(task, answers).is_correct)

    def test_fixed_99_99_percent(self) -> None:
        with patch("random.choice", return_value=99.99):
            task = self.gen.generate()
        fields = {field.key: field.expected_value for field in task.fields}
        self.assertEqual(fields["downtime_hours"], 0.88)
        self.assertEqual(fields["downtime_minutes"], 52.6)

    def test_100_random_tasks(self) -> None:
        for _ in range(100):
            task = self.gen.generate()
            self.assertEqual(task.category, "sla")
            self.assertEqual(len(task.fields), 2)
            answers = {field.key: str(field.expected_value) for field in task.fields}
            self.assertTrue(self.evaluator.evaluate(task, answers).is_correct)


if __name__ == "__main__":
    unittest.main()
