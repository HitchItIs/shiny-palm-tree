import random

from core.models import InputField, Task
from generators.base import BaseGenerator


class SlaGenerator(BaseGenerator):
    HOURS_PER_YEAR = 365 * 24
    HOURS_PER_MONTH = 30 * 24
    AVAILABILITY_OPTIONS = (99.0, 99.5, 99.9, 99.95, 99.99)
    TASK_TYPES = ("annual_downtime", "annual_availability", "monthly_downtime")

    @property
    def category_id(self) -> str:
        return "sla"

    @property
    def name(self) -> str:
        return "SLA & Verfügbarkeit"

    def generate(self) -> Task:
        task_type = random.choice(self.TASK_TYPES)
        if task_type == "annual_availability":
            return self._generate_annual_availability()
        if task_type == "monthly_downtime":
            return self._generate_monthly_downtime()
        if task_type == "annual_downtime":
            return self._generate_annual_downtime()
        raise ValueError(f"Unknown SLA task type: {task_type}")

    def _generate_annual_downtime(self) -> Task:
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

    def _generate_annual_availability(self) -> Task:
        downtime_hours = random.choice((1, 4, 8, 24, 48, 72))
        availability = round(
            (1 - downtime_hours / self.HOURS_PER_YEAR) * 100,
            2,
        )
        return Task(
            category=self.category_id,
            title=f"{self.name}: Verfügbarkeit bei {downtime_hours} h Ausfall",
            description=(
                f"Ein IT-Service war innerhalb eines Jahres mit 365 Tagen insgesamt "
                f"{downtime_hours} Stunden nicht verfügbar. Berechne die Verfügbarkeit "
                "in Prozent (auf 2 Nachkommastellen gerundet)."
            ),
            fields=[
                InputField(
                    "availability",
                    "Verfügbarkeit",
                    availability,
                    unit="%",
                    tolerance=0.01,
                )
            ],
            solution_steps=[
                f"Jahreszeit: 365 Tage × 24 Stunden = {self.HOURS_PER_YEAR} Stunden.",
                f"Verfügbare Zeit: {self.HOURS_PER_YEAR} h − {downtime_hours} h = "
                f"{self.HOURS_PER_YEAR - downtime_hours} h.",
                f"Verfügbarkeit: ({self.HOURS_PER_YEAR - downtime_hours} h ÷ "
                f"{self.HOURS_PER_YEAR} h) × 100 = {availability:.2f} %.",
            ],
        )

    def _generate_monthly_downtime(self) -> Task:
        availability = random.choice(self.AVAILABILITY_OPTIONS)
        downtime_hours_exact = self.HOURS_PER_MONTH * (1 - availability / 100)
        downtime_hours = round(downtime_hours_exact, 2)
        downtime_minutes = round(downtime_hours_exact * 60, 1)
        return Task(
            category=self.category_id,
            title=f"{self.name}: {availability:g} % Verfügbarkeit im Monat",
            description=(
                f"Ein IT-Service garantiert eine Verfügbarkeit von {availability:g} % "
                "pro 30-Tage-Monat. Berechne die maximal erlaubte Ausfallzeit in Stunden "
                "(auf 2 Nachkommastellen) und Minuten (auf 1 Nachkommastelle)."
            ),
            fields=[
                InputField(
                    "downtime_hours",
                    "Maximale Ausfallzeit pro Monat",
                    downtime_hours,
                    unit="h",
                    tolerance=0.01,
                ),
                InputField(
                    "downtime_minutes",
                    "Maximale Ausfallzeit pro Monat",
                    downtime_minutes,
                    unit="min",
                    tolerance=0.1,
                ),
            ],
            solution_steps=[
                f"Monatszeit: 30 Tage × 24 Stunden = {self.HOURS_PER_MONTH} Stunden.",
                f"Erlaubte Nichtverfügbarkeit: 100 % − {availability:g} % = "
                f"{100 - availability:g} % = {(100 - availability) / 100:g}.",
                f"Ausfallzeit in Stunden: {self.HOURS_PER_MONTH} h × "
                f"{(100 - availability) / 100:g} = {downtime_hours:.2f} h.",
                f"Ausfallzeit in Minuten: {self.HOURS_PER_MONTH} h × 60 × "
                f"{(100 - availability) / 100:g} = {downtime_minutes:.1f} min.",
            ],
        )
