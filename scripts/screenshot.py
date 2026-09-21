"""Renders a sample dashboard to docs/dashboard.svg for the README."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rich.console import Console  # noqa: E402

from dashboard import render  # noqa: E402
from scoring import NO, NOT_SURE, YES, load_questions, score  # noqa: E402

questions = load_questions()
answers = {q["id"]: q["safe_answer"] for q in questions}
answers.update({"P2": NO, "P4": YES, "D3": NO, "R2": NO, "R3": NOT_SURE,
                "S1": NO, "S3": NOT_SURE, "D4": NOT_SURE})

console = Console(record=True, width=100, highlight=False, force_terminal=True)
render(console, score(questions, answers), previous=52)
console.save_svg(str(ROOT / "docs" / "dashboard.svg"), title="python main.py")
