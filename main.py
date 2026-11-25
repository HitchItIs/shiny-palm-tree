import random
import time
import argparse

from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from core.evaluator import Evaluator
from core.grading import exam_grade
from core.models import Task
from core.stats import StatsStorage
from generators.base import BaseGenerator
from generators.numerals import NumeralGenerator
from generators.pricing import PricingGenerator
from generators.raid import RaidGenerator
from generators.sla import SlaGenerator
from generators.subnet import SubnetGenerator
from generators.transfer import TransferGenerator


console = Console()

GENERATORS: list[BaseGenerator] = [
    SubnetGenerator(),
    TransferGenerator(),
    RaidGenerator(),
    NumeralGenerator(),
    PricingGenerator(),
    SlaGenerator(),
]


def _progress_display(percent: float) -> str:
    filled = round(percent / 100 * 8)
    bar = "█" * filled + "░" * (8 - filled)
    color = "green" if percent >= 80 else "yellow" if percent >= 50 else "red"
    return f"[{color}]{bar} {percent:.0f}%[/{color}]"


def choose_generator(stats: StatsStorage) -> BaseGenerator | str | None:
    console.clear()
    console.print(
        Panel(
            "[bold white]IHK AP1 Trainer[/bold white]\n"
            "[cyan]FIAE · Wissen üben, sicher in die Prüfung[/cyan]\n"
            "[dim]⌨  Rechnen · Verstehen · Wiederholen[/dim]",
            title="[bold cyan]◆ SHINY PALM TREE ◆[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE,
            expand=False,
            padding=(1, 3),
        )
    )

    table = Table(
        title="Themen",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Nr.", style="bold yellow", justify="center", width=5)
    table.add_column("Thema", style="bold white")
    table.add_column("Fortschritt", min_width=18)

    for idx, gen in enumerate(GENERATORS, start=1):
        table.add_row(str(idx), gen.name, _progress_display(stats.progress(gen.category_id)))

    console.print(table)
    console.print(
        "[bold yellow][r][/bold yellow] Zufällige Aufgabe    "
        "[bold yellow][p][/bold yellow] Prüfungs-Simulation (5 Aufgaben)    "
        "[bold yellow][q][/bold yellow] Beenden\n"
    )
    valid_choices = [str(i) for i in range(1, len(GENERATORS) + 1)] + ["r", "p", "q"]
    choice = Prompt.ask(
        "[bold cyan]Auswahl[/bold cyan]",
        choices=valid_choices,
        show_choices=False,
    )

    if choice == "q":
        return None
    if choice in {"r", "p"}:
        return choice
    return GENERATORS[int(choice) - 1]


def run_task(
    task: Task,
    evaluator: Evaluator,
    context: str | None = None,
) -> tuple[int, int] | None:
    console.clear()
    title = f"{task.title} · {context}" if context else task.title
    console.print(
        Panel(
            f"[bold white]{task.description}[/bold white]\n\n"
            "[dim]Tippe 'q' zum Abbrechen.[/dim]",
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    answers: dict[str, str] = {}
    for field in task.fields:
        unit_hint = f" [dim]({field.unit})[/dim]" if field.unit else ""
        raw = Prompt.ask(f"  [bold]{field.label}[/bold]{unit_hint}").strip()
        if raw.lower() == "q":
            return None
        answers[field.key] = raw

    result = evaluator.evaluate(task, answers)
    res_table = Table(
        title="Auswertung",
        box=box.SIMPLE_HEAVY,
        header_style="bold",
    )
    res_table.add_column("Status", justify="center", width=8)
    res_table.add_column("Feld", style="bold")
    res_table.add_column("Deine Antwort")
    res_table.add_column("Lösung", style="cyan")

    for field in task.fields:
        ok = result.field_results[field.key]
        unit = f" {field.unit}" if field.unit else ""
        status = "[bold green]OK[/bold green]" if ok else "[bold red]FALSCH[/bold red]"
        user_val = escape(answers[field.key]) if answers[field.key] else "[dim]–[/dim]"
        expected_val = f"{field.expected_value}{unit}"
        res_table.add_row(status, field.label, f"{user_val}{unit if answers[field.key] else ''}", expected_val)

    console.print()
    console.print(res_table)

    pct = (result.points_earned / result.max_points) * 100 if result.max_points else 0
    score_color = "green" if pct >= 80 else "yellow" if pct >= 50 else "red"
    console.print(
        f"[bold {score_color}]Punkte: {result.points_earned}/{result.max_points} "
        f"({pct:.0f}%)[/bold {score_color}]"
    )

    if task.solution_steps:
        steps_text = "\n".join(
            f"[bold cyan]{i}.[/bold cyan] {step}"
            for i, step in enumerate(task.solution_steps, start=1)
        )
        console.print()
        console.print(
            Panel(
                steps_text,
                title="[bold yellow]Lösungsweg[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    return result.points_earned, result.max_points


def _record_result(
    task: Task,
    outcome: tuple[int, int],
    stats: StatsStorage,
    session_totals: dict[str, int],
    streak: int,
) -> int:
    earned, possible = outcome
    stats.record(task.category, earned, possible)
    session_totals["earned"] += earned
    session_totals["possible"] += possible
    if possible > 0 and earned == possible:
        streak += 1
        console.print(f"[bold yellow]🔥 Serie: {streak} perfekte Aufgaben in Folge[/bold yellow]")
    else:
        if streak:
            console.print("[dim]Serie beendet – die nächste perfekte Aufgabe startet eine neue.[/dim]")
        streak = 0
    return streak


def run_exam(
    evaluator: Evaluator,
    stats: StatsStorage,
    session_totals: dict[str, int],
    streak: int,
) -> int:
    records: list[tuple[str, int, int]] = []
    completed = True
    started_at = time.perf_counter()
    for index, gen in enumerate(random.sample(GENERATORS, k=5), start=1):
        task = gen.generate()
        outcome = run_task(task, evaluator, context=f"Prüfung {index}/5")
        if outcome is None:
            console.print("[yellow]Prüfung vorzeitig abgebrochen.[/yellow]")
            completed = False
            break
        streak = _record_result(
            task,
            outcome,
            stats,
            session_totals,
            streak,
        )
        records.append((gen.name, outcome[0], outcome[1]))

    elapsed = time.perf_counter() - started_at
    earned = sum(record[1] for record in records)
    possible = sum(record[2] for record in records)
    percent = earned / possible * 100 if possible else 0

    table = Table(title="Prüfungsauswertung", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Thema")
    table.add_column("Punkte", justify="right")
    for name, points, max_points in records:
        table.add_row(name, f"{points}/{max_points}")
    table.add_section()
    table.add_row("Gesamt", f"{earned}/{possible}")
    console.print(table)
    if completed:
        console.print(
            f"Ergebnis: [bold]{percent:.1f}%[/bold] · "
            f"Note: [bold]{exam_grade(percent)}[/bold] · "
            f"{'[bold green]Bestanden[/bold green]' if percent >= 50 else '[bold red]Nicht bestanden[/bold red]'}"
        )
        console.print(
            "[dim]IHK-Schlüssel: 1 ab 92 % · 2 ab 81 % · 3 ab 67 % · "
            "4 ab 50 % · 5 ab 30 % · 6 unter 30 %[/dim]"
        )
    else:
        console.print(
            f"Zwischenergebnis: [bold]{percent:.1f}%[/bold] · "
            f"Prüfung nicht vollständig ({len(records)}/5 Aufgaben)"
        )
    console.print(f"Gesamtzeit: [cyan]{elapsed:.1f} Sekunden[/cyan]")
    return streak


def main() -> None:
    evaluator = Evaluator()
    stats = StatsStorage()
    session_totals = {"earned": 0, "possible": 0}
    streak = 0

    try:
        while True:
            selection = choose_generator(stats)
            if selection is None:
                break
            if selection == "p":
                streak = run_exam(evaluator, stats, session_totals, streak)
                continue
            random_mode = selection == "r"
            gen = None if random_mode else selection

            while True:
                if random_mode:
                    gen = random.choice(GENERATORS)
                if gen is None:
                    break
                task = gen.generate()
                outcome = run_task(task, evaluator)
                if outcome is None:
                    break
                streak = _record_result(task, outcome, stats, session_totals, streak)

                continue_label = "Neue zufällige Aufgabe" if random_mode else "Neue Aufgabe"
                again = Prompt.ask(
                    f"\n[bold]Weiter?[/bold] "
                    f"[dim][Enter = {continue_label} | m = Menü | q = Beenden][/dim]",
                    default="",
                    show_default=False,
                ).strip().lower()
                if again == "m":
                    break
                if again == "q":
                    gen = None
                    break

            if gen is None:
                break
    except KeyboardInterrupt:
        console.print("\n[yellow]Abgebrochen.[/yellow]")

    if session_totals["possible"] > 0:
        pct = session_totals["earned"] / session_totals["possible"] * 100
        console.print(
            Panel(
                f"[bold]Gesamtergebnis:[/bold] "
                f"{session_totals['earned']}/{session_totals['possible']} Punkte "
                f"([bold cyan]{pct:.1f}%[/bold cyan])",
                border_style="green",
                expand=False,
            )
        )
    console.print("[dim]Bis zum nächsten Mal![/dim]")


def launch_gui() -> None:
    import tkinter as tk

    from gui import TrainerApp

    root = tk.Tk()
    TrainerApp(root, GENERATORS)
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IHK AP1 Trainer")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Start the terminal version instead of the desktop app.",
    )
    arguments = parser.parse_args()
    if arguments.cli:
        main()
    else:
        launch_gui()
