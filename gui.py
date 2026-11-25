import random
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from core.evaluator import Evaluator
from core.grading import exam_grade
from core.models import EvaluationResult, Task
from core.stats import StatsStorage
from generators.base import BaseGenerator


class TrainerApp:
    EXAM_TASK_COUNT = 5

    def __init__(
        self,
        root: tk.Tk,
        generators: list[BaseGenerator],
        stats: StatsStorage | None = None,
    ) -> None:
        self.root = root
        self.generators = generators
        self.stats = stats or StatsStorage(
            Path.home() / ".ihk-ap1-trainer" / "stats.json"
        )
        self.evaluator = Evaluator()
        self.mode = "topic"
        self.active_generator: BaseGenerator | None = None
        self.current_task: Task | None = None
        self.answer_fields: dict[str, ttk.Entry] = {}
        self.exam_generators: list[BaseGenerator] = []
        self.exam_results: list[tuple[str, int, int]] = []
        self.exam_index = 0

        self.root.title("IHK AP1 Trainer")
        self.root.geometry("920x720")
        self.root.minsize(720, 560)
        self.root.configure(background="#f3f6fb")
        self.root.option_add("*Font", ("Segoe UI", 11))

        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f3f6fb")
        style.configure("TLabel", background="#f3f6fb", foreground="#17233b")
        style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"), foreground="#173b70")
        style.configure("Subtitle.TLabel", foreground="#52627a")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", background="white", font=("Segoe UI", 13, "bold"))
        style.configure("CardText.TLabel", background="white", foreground="#52627a")
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            foreground="white",
            background="#2872c7",
            padding=(16, 10),
        )
        style.map(
            "Accent.TButton",
            foreground=[("disabled", "#f3f6fb"), ("pressed", "white"), ("active", "white")],
            background=[("disabled", "#9ab8da"), ("pressed", "#174b80"), ("active", "#1e5d9f")],
        )
        style.configure("Horizontal.TProgressbar", troughcolor="#e5eaf2", background="#2872c7")

        self._show_menu()

    def _clear(self) -> ttk.Frame:
        for child in self.root.winfo_children():
            child.destroy()
        frame = ttk.Frame(self.root, padding=32)
        frame.pack(fill="both", expand=True)
        return frame

    def _show_menu(self) -> None:
        frame = self._clear()
        ttk.Label(frame, text="IHK AP1 Trainer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text="Übe in deinem Tempo. Wähle ein Thema oder starte eine Prüfungssimulation.",
            style="Subtitle.TLabel",
            wraplength=800,
        ).pack(anchor="w", pady=(4, 22))

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(0, 20))
        ttk.Button(
            actions,
            text="Zufallsaufgabe starten",
            style="Accent.TButton",
            command=lambda: self.start_practice(),
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            actions,
            text=f"Prüfung starten · {self.EXAM_TASK_COUNT} Aufgaben",
            style="Accent.TButton",
            command=self.start_exam,
        ).pack(side="left")

        ttk.Label(frame, text="Themen", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        cards = ttk.Frame(frame)
        cards.pack(fill="both", expand=True)
        for index, generator in enumerate(self.generators):
            card = ttk.Frame(cards, style="Card.TFrame", padding=16)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)
            cards.columnconfigure(index % 2, weight=1)
            cards.rowconfigure(index // 2, weight=1)

            ttk.Label(card, text=generator.name, style="CardTitle.TLabel").pack(anchor="w")
            progress = self.stats.progress(generator.category_id)
            ttk.Label(
                card,
                text=f"Fortschritt: {progress:.0f}%",
                style="CardText.TLabel",
            ).pack(anchor="w", pady=(8, 4))
            ttk.Progressbar(card, maximum=100, value=progress).pack(fill="x", pady=(0, 12))
            ttk.Button(
                card,
                text="Thema starten",
                style="Accent.TButton",
                command=lambda selected=generator: self.start_practice(selected),
            ).pack(anchor="w")

    def start_practice(self, generator: BaseGenerator | None = None) -> None:
        self.mode = "random" if generator is None else "topic"
        self.active_generator = generator
        self._next_task()

    def start_exam(self) -> None:
        self.mode = "exam"
        self.exam_generators = random.sample(
            self.generators,
            k=min(self.EXAM_TASK_COUNT, len(self.generators)),
        )
        self.exam_results = []
        self.exam_index = 0
        self._next_task()

    def _next_task(self) -> None:
        if self.mode == "random":
            generator = random.choice(self.generators)
        elif self.mode == "exam":
            if self.exam_index >= len(self.exam_generators):
                self._show_exam_summary()
                return
            generator = self.exam_generators[self.exam_index]
        else:
            generator = self.active_generator
        if generator is None:
            self._show_menu()
            return
        self.active_generator = generator
        self.current_task = generator.generate()
        self._show_task()

    def _show_task(self) -> None:
        task = self.current_task
        if task is None:
            return
        frame = self._clear()
        heading = task.title
        if self.mode == "exam":
            heading = f"Prüfung · Aufgabe {self.exam_index + 1} von {len(self.exam_generators)}"
        elif self.mode == "random" and self.active_generator:
            heading = f"{task.title} · {self.active_generator.name}"
        ttk.Button(
            frame,
            text="← Hauptmenü",
            style="Accent.TButton",
            command=self._show_menu,
        ).pack(anchor="w")
        ttk.Label(frame, text=heading, style="Title.TLabel", wraplength=820).pack(
            anchor="w", pady=(18, 8)
        )
        ttk.Label(
            frame,
            text=task.description,
            style="Subtitle.TLabel",
            wraplength=820,
            justify="left",
        ).pack(anchor="w", pady=(0, 22))

        answers = ttk.Frame(frame, style="Card.TFrame", padding=18)
        answers.pack(fill="x", anchor="n")
        self.answer_fields = {}
        for row, field in enumerate(task.fields):
            label = f"{field.label} ({field.unit})" if field.unit else field.label
            ttk.Label(answers, text=label, style="CardTitle.TLabel").grid(
                row=row, column=0, sticky="w", padx=(0, 16), pady=8
            )
            entry = ttk.Entry(answers, width=34)
            entry.grid(row=row, column=1, sticky="ew", pady=8)
            self.answer_fields[field.key] = entry
            if row == 0:
                entry.focus_set()
        answers.columnconfigure(1, weight=1)
        ttk.Button(
            frame,
            text="Antwort prüfen",
            style="Accent.TButton",
            command=self._submit,
        ).pack(anchor="w", pady=18)

    def _submit(self) -> None:
        task = self.current_task
        if task is None:
            return
        answers = {key: entry.get().strip() for key, entry in self.answer_fields.items()}
        result = self.evaluator.evaluate(task, answers)
        self.stats.record(task.category, result.points_earned, result.max_points)
        if self.mode == "exam" and self.active_generator is not None:
            self.exam_results.append(
                (self.active_generator.name, result.points_earned, result.max_points)
            )
        self._show_result(task, result, answers)

    def _show_result(
        self,
        task: Task,
        result: EvaluationResult,
        answers: dict[str, str],
    ) -> None:
        frame = self._clear()
        ttk.Button(
            frame,
            text="← Hauptmenü",
            style="Accent.TButton",
            command=self._show_menu,
        ).pack(anchor="w")
        ttk.Label(frame, text="Auswertung", style="Title.TLabel").pack(anchor="w", pady=(18, 8))
        percent = result.points_earned / result.max_points * 100 if result.max_points else 0
        summary = f"{result.points_earned} von {result.max_points} Punkten · {percent:.0f}%"
        ttk.Label(
            frame,
            text=("Gut gemacht!" if result.is_correct else "Weiter üben – hier ist die Lösung.")
            + f"\n{summary}",
            font=("Segoe UI", 14, "bold"),
            justify="left",
        ).pack(anchor="w", pady=(0, 18))

        details = ttk.Frame(frame, style="Card.TFrame", padding=16)
        details.pack(fill="x", anchor="n")
        for row, field in enumerate(task.fields):
            status = "✓ Richtig" if result.field_results[field.key] else "✗ Noch nicht"
            answer = answers.get(field.key, "") or "–"
            unit = f" {field.unit}" if field.unit else ""
            ttk.Label(details, text=f"{status}  ·  {field.label}").grid(
                row=row, column=0, sticky="w", pady=3
            )
            ttk.Label(
                details,
                text=f"Deine Antwort: {answer}{unit}  |  Lösung: {field.expected_value}{unit}",
                style="CardText.TLabel",
                wraplength=680,
                justify="left",
            ).grid(row=row, column=1, sticky="w", padx=(18, 0), pady=3)

        ttk.Label(frame, text="Lösungsweg", font=("Segoe UI", 15, "bold")).pack(
            anchor="w", pady=(18, 6)
        )
        steps = "\n".join(f"{index}. {step}" for index, step in enumerate(task.solution_steps, 1))
        ttk.Label(frame, text=steps, wraplength=820, justify="left").pack(anchor="w")

        if self.mode == "exam" and self.exam_index + 1 >= len(self.exam_generators):
            next_text = "Prüfung abschließen · Ergebnis anzeigen"
        else:
            next_text = "Nächste Aufgabe"
        ttk.Button(
            frame,
            text=next_text,
            style="Accent.TButton",
            command=self._continue,
        ).pack(anchor="w", pady=(20, 0))

    def _continue(self) -> None:
        if self.mode == "exam":
            if self.exam_index + 1 >= len(self.exam_generators):
                self._show_exam_summary()
                return
            self.exam_index += 1
        self._next_task()

    def _show_exam_summary(self) -> None:
        frame = self._clear()
        ttk.Label(
            frame,
            text=f"Prüfung abgeschlossen · {len(self.exam_results)} von "
            f"{len(self.exam_generators)} Aufgaben",
            style="Title.TLabel",
        ).pack(anchor="w")
        earned = sum(result[1] for result in self.exam_results)
        possible = sum(result[2] for result in self.exam_results)
        percent = earned / possible * 100 if possible else 0
        ttk.Label(
            frame,
            text=f"{earned} von {possible} Punkten · {percent:.1f}%\n"
            f"Note: {exam_grade(percent)} · "
            f"{'Bestanden' if percent >= 50 else 'Noch nicht bestanden'}",
            font=("Segoe UI", 16, "bold"),
            justify="left",
        ).pack(anchor="w", pady=(12, 22))
        for name, points, maximum in self.exam_results:
            ttk.Label(frame, text=f"{name}: {points}/{maximum} Punkte").pack(anchor="w", pady=3)
        ttk.Button(
            frame,
            text="Zur Themenübersicht",
            style="Accent.TButton",
            command=self._show_menu,
        ).pack(anchor="w", pady=(24, 0))
