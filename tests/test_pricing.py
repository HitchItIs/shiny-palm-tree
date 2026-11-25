import unittest
from unittest.mock import patch

from core.evaluator import Evaluator
from generators.pricing import PricingGenerator


class TestPricingGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = PricingGenerator()
        self.evaluator = Evaluator()

    def test_fixed_calculation(self) -> None:
        with patch("random.choice", side_effect=[1299.99, 10, 2, 49.90]):
            task = self.gen.generate()

        fields = {field.key: field.expected_value for field in task.fields}
        self.assertEqual(fields["target_purchase_price"], 1169.99)
        self.assertEqual(fields["cash_purchase_price"], 1146.59)
        self.assertEqual(fields["landed_price"], 1196.49)
        self.assertTrue(self.evaluator.evaluate(
            task, {field.key: str(field.expected_value) for field in task.fields}
        ).is_correct)

    def test_fields_use_euro_and_tolerance(self) -> None:
        task = self.gen.generate()
        self.assertEqual(len(task.fields), 3)
        for field in task.fields:
            self.assertEqual(field.unit, "€")
            self.assertEqual(field.tolerance, 0.05)

    def test_100_random_tasks(self) -> None:
        for _ in range(100):
            task = self.gen.generate()
            self.assertEqual(task.category, "pricing")
            self.assertEqual(len(task.fields), 3)
            self.assertTrue(len(task.solution_steps) >= 5)
            answers = {field.key: str(field.expected_value) for field in task.fields}
            self.assertTrue(self.evaluator.evaluate(task, answers).is_correct)


if __name__ == "__main__":
    unittest.main()
