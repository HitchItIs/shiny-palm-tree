import unittest
from unittest.mock import Mock, patch

from gui import TrainerApp


class TestExamFlow(unittest.TestCase):
    def test_exam_starts_with_five_tasks(self) -> None:
        app = object.__new__(TrainerApp)
        app.generators = [object() for _ in range(6)]
        app._next_task = Mock()
        selected = app.generators[:5]

        with patch("gui.random.sample", return_value=selected) as sample:
            app.start_exam()

        sample.assert_called_once_with(app.generators, k=5)
        self.assertEqual(app.exam_generators, selected)
        self.assertEqual(app.exam_index, 0)
        self.assertEqual(app.exam_results, [])
        app._next_task.assert_called_once_with()

    def test_exam_finishes_after_fifth_task(self) -> None:
        app = object.__new__(TrainerApp)
        app.mode = "exam"
        app.exam_generators = [object() for _ in range(5)]
        app.exam_index = 3
        app._next_task = Mock()
        app._show_exam_summary = Mock()

        app._continue()
        self.assertEqual(app.exam_index, 4)
        app._next_task.assert_called_once_with()

        app._continue()
        self.assertEqual(app.exam_index, 4)
        app._next_task.assert_called_once_with()
        app._show_exam_summary.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
