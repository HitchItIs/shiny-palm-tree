import unittest

from core.grading import exam_grade


class TestExamGrade(unittest.TestCase):
    def test_grade_thresholds(self):
        self.assertEqual(exam_grade(92), "1 – sehr gut")
        self.assertEqual(exam_grade(81), "2 – gut")
        self.assertEqual(exam_grade(67), "3 – befriedigend")
        self.assertEqual(exam_grade(50), "4 – ausreichend")
        self.assertEqual(exam_grade(30), "5 – mangelhaft")
        self.assertEqual(exam_grade(29.9), "6 – ungenügend")


if __name__ == "__main__":
    unittest.main()
