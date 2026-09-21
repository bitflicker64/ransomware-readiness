"""Asks the questions one at a time and collects answers."""

import questionary
from questionary import Choice
from rich.console import Console

from scoring import NO, NOT_SURE, YES

CHOICES = [
    Choice("Yes", value=YES),
    Choice("No", value=NO),
    Choice("Not sure", value=NOT_SURE),
]

STYLE = questionary.Style([
    ("qmark", "fg:#e5484d bold"),
    ("question", "bold"),
    ("pointer", "fg:#e5484d bold"),
    ("highlighted", "fg:#e5484d bold"),
    ("answer", "fg:#46a758 bold"),
])


def run_quiz(questions, console: Console):
    """Return {question id: answer}, or None if the user cancels with Ctrl+C."""
    answers = {}
    total = len(questions)
    for i, q in enumerate(questions, start=1):
        console.print(f"\n[dim]Q {i}/{total} · {q['category']}[/dim]")
        answer = questionary.select(
            q["text"],
            choices=CHOICES,
            qmark="?",
            instruction="(use arrow keys)",
            style=STYLE,
        ).ask()
        if answer is None:
            return None
        answers[q["id"]] = answer
    return answers
