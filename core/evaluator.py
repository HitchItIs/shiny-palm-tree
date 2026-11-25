from core.models import EvaluationResult, InputField, Task


class Evaluator:
    def evaluate(self, task: Task, user_answers: dict[str, str]) -> EvaluationResult:
        field_results: dict[str, bool] = {}

        for field in task.fields:
            raw_answer = user_answers.get(field.key, "")
            field_results[field.key] = self._check_field(field, raw_answer)

        points_earned = sum(field_results.values())
        max_points = len(task.fields)

        return EvaluationResult(
            is_correct=(points_earned == max_points),
            field_results=field_results,
            points_earned=points_earned,
            max_points=max_points,
        )

    def _check_field(self, field: InputField, raw_answer: str) -> bool:
        cleaned = raw_answer.strip()
        if not cleaned:
            return False

        expected = field.expected_value
        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            try:
                user_val = float(cleaned.replace(",", "."))
            except ValueError:
                return False
            return abs(user_val - float(expected)) <= field.tolerance + 1e-9

        return cleaned.lower() == str(expected).strip().lower()