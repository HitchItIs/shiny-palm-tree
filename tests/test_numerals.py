import unittest
from unittest.mock import patch

from core.evaluator import Evaluator
from generators.numerals import NumeralGenerator


class TestNumeralGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = NumeralGenerator()
        self.evaluator = Evaluator()

    def test_fixed_decimal_conversion(self) -> None:
        with patch("random.choice", return_value="Dezimalzahl"), patch("random.randint", return_value=255):
            task = self.gen.generate()

        fields = {field.key: field.expected_value for field in task.fields}
        self.assertEqual(fields, {"binary": "11111111", "hexadecimal": "FF"})
        answers = {"binary": "11111111", "hexadecimal": "ff"}
        self.assertTrue(self.evaluator.evaluate(task, answers).is_correct)
        self.assertGreaterEqual(len(task.solution_steps), 3)

    def test_fixed_binary_conversion(self) -> None:
        with patch("random.choice", return_value="Binärzahl"), patch("random.randint", return_value=42):
            task = self.gen.generate()
        self.assertEqual(
            {field.key: field.expected_value for field in task.fields},
            {"decimal": "42", "hexadecimal": "2A"},
        )

    def test_fixed_hexadecimal_conversion(self) -> None:
        with patch("random.choice", return_value="Hexadezimalzahl"), patch("random.randint", return_value=4095):
            task = self.gen.generate()
        self.assertEqual(
            {field.key: field.expected_value for field in task.fields},
            {"decimal": "4095", "binary": "111111111111"},
        )

    def test_100_random_tasks(self) -> None:
        for _ in range(100):
            task = self.gen.generate()
            self.assertEqual(task.category, "numerals")
            self.assertEqual(len(task.fields), 2)
            parsed_values = []
            for field in task.fields:
                if field.key == "decimal":
                    parsed_values.append(int(field.expected_value, 10))
                elif field.key == "binary":
                    parsed_values.append(int(field.expected_value, 2))
                else:
                    parsed_values.append(int(field.expected_value, 16))
            self.assertEqual(parsed_values[0], parsed_values[1])
            answers = {field.key: str(field.expected_value) for field in task.fields}
            self.assertTrue(self.evaluator.evaluate(task, answers).is_correct)


if __name__ == "__main__":
    unittest.main()
