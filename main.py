"""Ransomware Readiness CLI: entry point, menu and flow."""

import sys

import questionary
from rich.console import Console

from dashboard import render, welcome_panel
from history import last_score, save_score
from quiz import STYLE, run_quiz
from report import write_report
from scoring import load_questions, score

console = Console(highlight=False)


def run_once(questions):
    """One full pass. Returns False if the user cancelled."""
    answers = run_quiz(questions, console)
    if answers is None:
        return False

    result = score(questions, answers)
    previous = last_score()

    console.print()
    render(console, result, previous)

    path = write_report(result, previous=previous)
    save_score(result)
    console.print(f"\n[green]Report saved to[/green] [bold]{path}[/bold]")
    return True


def main():
    try:
        questions = load_questions()
    except (OSError, ValueError) as e:
        console.print(f"[red]Could not load questions.json:[/red] {e}")
        return 1

    console.clear()
    console.print(welcome_panel(len(questions)))
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        console.print("\nBye.")
        return 0

    while True:
        if not run_once(questions):
            console.print("\n[yellow]Cancelled. No report written.[/yellow]")
            return 0
        choice = questionary.select(
            "What next?", choices=["Retake the quiz", "Quit"], style=STYLE,
        ).ask()
        if choice != "Retake the quiz":
            console.print("Bye.")
            return 0
        console.clear()


if __name__ == "__main__":
    sys.exit(main())
