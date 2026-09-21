"""Writes the dashboard and recommendations to report.txt."""

from datetime import datetime
from pathlib import Path

from rich.console import Console

from dashboard import render

REPORT_WIDTH = 100


def write_report(result, path="report.txt", previous=None):
    path = Path(path)
    with open(path, "w", encoding="utf-8") as f:
        console = Console(file=f, width=REPORT_WIDTH, color_system=None,
                          force_terminal=False, emoji=False)
        console.print(f"Ransomware Readiness Report  ·  {datetime.now():%Y-%m-%d %H:%M}\n")
        render(console, result, previous)
    return path
