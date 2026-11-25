from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from core.evaluator import Evaluator
from core.models import Task
from generators.base import BaseGenerator
from generators.subnet import SubnetGenerator
from generators.transfer import TransferGenerator


console = Console()

GENERATORS: list[BaseGenerator] = [
    SubnetGenerator(),
    TransferGenerator(),
]


def choose_generator() -> BaseGenerator | None:
    console.clear()
    table = Table(
        title="AP1 Trainer (FIAE)",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Nr.", style="bold yellow", justify="center", width=5)
    table.add_column("Thema", style="bold white")
    table.add_column("Kategorie", style="dim")

    for idx, gen in enumerate(GENERATORS, start=1):
        table.add_row(str(idx), gen.name, gen.category_id)

    console.print(table)
    console.print("[dim]Tippe eine Nummer zum Starten oder 'q' zum Beenden.[/dim]\n")

    valid_choices = [str(i) for i in range(1, len(GENERATORS) + 1)] + ["q"]
    choice = Prompt.ask(
        "[bold cyan]Auswahl[/bold cyan]",
        choices=valid_choices,
        show_choices=False,
    )

    if choice == "q":
        return None
    return GENERATORS[int(choice) - 1]


def run_task(task: Task, evaluator: Evaluator) -> tuple[int, int] | None:
    console.clear()
    console.print(
        Panel(
            f"[bold white]{task.description}[/bold white]\n\n"
            "[dim]Tippe 'q' zum Abbrechen.[/dim]",
            title=f"[bold cyan]{task.title}[/bold cyan]",
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

    # Ergebnistabelle
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
        f"[bold {score_color}]Punkte: {result.points_earned}/{result.max_points} ({pct:.0f}%)[/bold {score_color}]"
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


def main() -> None:
    evaluator = Evaluator()
    total_earned = 0
    total_possible = 0

    try:
        while True:
            gen = choose_generator()
            if gen is None:
                break

            while True:
                task = gen.generate()
                outcome = run_task(task, evaluator)
                if outcome is None:
                    break

                earned, possible = outcome
                total_earned += earned
                total_possible += possible

                again = Prompt.ask(
                    "\n[bold]Weiter?[/bold] [dim][Enter = Neue Aufgabe | m = Menü | q = Beenden][/dim]",
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

    console.print()
    if total_possible > 0:
        pct = (total_earned / total_possible) * 100
        console.print(
            Panel(
                f"[bold]Gesamtergebnis:[/bold] {total_earned}/{total_possible} Punkte ([bold cyan]{pct:.1f}%[/bold cyan])",
                border_style="green",
                expand=False,
            )
        )
    console.print("[dim]Bis zum nächsten Mal![/dim]")


if __name__ == "__main__":
    main()