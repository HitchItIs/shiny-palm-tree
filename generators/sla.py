import random

from core.models import InputField, Task
from generators.base import BaseGenerator


class SlaGenerator(BaseGenerator):
    HOURS_PER_YEAR = 365 * 24
    AVAILABILITY_OPTIONS = (99.0, 99.5, 99.9, 99.95, 99.99)

    @property
    def category_id(self) -> str:
        return "sla"

    @property
    def name(self) -> str:
        return "SLA & Verfügbarkeit"

    def generate(self) -> Task:
        availability = random.choice(self.AVAILABILITY_OPTIONS)
        downtime_hours_exact = self.HOURS_PER_YEAR * (1 - availability / 100)
        downtime_hours = round(downtime_hours_exact, 2)
        downtime_minutes = round(downtime_hours_exact * 60, 1)

        fields = [
            InputField(
                "downtime_hours",
                "Maximale Ausfallzeit pro Jahr",
                downtime_hours,
                unit="h",
                tolerance=0.01,
            ),
            InputField(
                "downtime_minutes",
                "Maximale Ausfallzeit pro Jahr",
                downtime_minutes,
                unit="min",
                tolerance=0.1,
            ),
        ]
        solution_steps = [
            f"Jahreszeit: 365 Tage × 24 Stunden = {self.HOURS_PER_YEAR} Stunden.",
            f"Erlaubte Nichtverfügbarkeit: 100 % − {availability:g} % = "
            f"{100 - availability:g} % = {(100 - availability) / 100:g}.",
            f"Ausfallzeit in Stunden: {self.HOURS_PER_YEAR} h × "
            f"{(100 - availability) / 100:g} = {downtime_hours:.2f} h.",
            f"Ausfallzeit in Minuten: {self.HOURS_PER_YEAR} h × 60 × "
            f"{(100 - availability) / 100:g} = {downtime_minutes:.1f} min.",
        ]

        return Task(
            category=self.category_id,
            title=f"{self.name}: {availability:g} % Verfügbarkeit",
            description=(
                f"Ein IT-Service garantiert eine Verfügbarkeit von {availability:g} % pro Jahr. "
                "Berechne die maximal erlaubte Ausfallzeit bei 365 Tagen in Stunden "
                "(auf 2 Nachkommastellen) und Minuten (auf 1 Nachkommastelle)."
            ),
            fields=fields,
            solution_steps=solution_steps,
        )
