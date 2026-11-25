import unittest
from core.evaluator import Evaluator
from generators.transfer import TransferGenerator


class TestTransferGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = TransferGenerator()
        self.evaluator = Evaluator()

    def test_fixed_example_gb_decimal(self) -> None:
        task = self.gen.generate()
        self.assertEqual(task.category, "transfer")
        self.assertTrue(len(task.fields) == 3)
        self.assertTrue(len(task.solution_steps) >= 4)

    def test_random_tasks_evaluation(self) -> None:
        for _ in range(100):
            task = self.gen.generate()
            answers = {f.key: str(f.expected_value) for f in task.fields}
            result = self.evaluator.evaluate(task, answers)
            self.assertTrue(
                result.is_correct,
                f"Task failed validation: {task.title}, expected: {[f.expected_value for f in task.fields]}, got answers: {answers}"
            )
            self.assertEqual(result.points_earned, result.max_points)

    def test_specific_calculation_logic(self) -> None:
        task = self.gen.generate()
        fields_dict = {f.key: f for f in task.fields}
        
        self.assertIn("transfer_rate_mb", fields_dict)
        self.assertIn("duration_seconds", fields_dict)
        self.assertIn("duration_minutes", fields_dict)

        rate_field = fields_dict["transfer_rate_mb"]
        self.assertEqual(rate_field.unit, "MB/s")
        self.assertEqual(rate_field.tolerance, 0.1)

        sec_field = fields_dict["duration_seconds"]
        self.assertEqual(sec_field.unit, "s")
        self.assertEqual(sec_field.tolerance, 1.0)

        min_field = fields_dict["duration_minutes"]
        self.assertEqual(min_field.unit, "min")
        self.assertEqual(min_field.tolerance, 0.1)


if __name__ == "__main__":
    unittest.main()
