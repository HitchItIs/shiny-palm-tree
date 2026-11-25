from dataclasses import dataclass

@dataclass 
class InputField:
    key: str
    label: str
    expected_value: str | float | int
    unit: str = ""
    tolerance: float = 0.0
    
@dataclass
class Task:
    category: str
    title: str
    description: str
    fields: list[InputField]
    solution_steps: list[str]

@dataclass
class EvaluationResult:
    is_correct: bool
    field_results: dict[str, bool]
    points_earned: int
    max_points: int