"""Rich dashboard and recommendations.

The same renderables are printed to the terminal and written to report.txt,
so the report always matches what the user saw.
"""

from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scoring import CATEGORIES, band_for

BAR_WIDTH = 20
DISCLAIMER = "Score bands are this tool's own, not an official standard or certification."


def _bar(percent):
    filled = round(percent / 100 * BAR_WIDTH)
    _, colour = band_for(percent)
    bar = Text("█" * filled, style=colour)
    bar.append("░" * (BAR_WIDTH - filled), style="grey42")
    return bar


def build_dashboard(result, previous=None):
    summary = Text()
    summary.append("Readiness score  ", style="bold")
    summary.append(f"{result.total}/100", style=f"bold {result.colour}")
    summary.append("   Band  ", style="bold")
    summary.append(result.band, style=f"bold {result.colour}")
    if previous is not None:
        diff = result.total - previous
        sign = "+" if diff > 0 else ""
        summary.append(f"   (last time {previous}, {sign}{diff})", style="dim")

    categories = Table(box=None, show_header=False, padding=(0, 1))
    categories.add_column("Category", width=11)
    categories.add_column("Bar")
    categories.add_column("Percent", justify="right", width=5)
    categories.add_column("Points", style="dim")
    for cat in CATEGORIES:
        pct = result.category_percent[cat]
        _, colour = band_for(pct)
        categories.add_row(
            cat, _bar(pct), Text(f"{pct}%", style=colour),
            f"{result.category_points[cat]}/25",
        )

    weaknesses = Text()
    top = result.top_weaknesses(3)
    if top:
        weaknesses.append("Top weaknesses\n", style="bold")
        for i, q in enumerate(top, start=1):
            tag = " (not sure)" if q in result.not_sure else ""
            weaknesses.append(f"{i}. [{q['id']}] {q['text']}{tag}")
            if i < len(top):
                weaknesses.append("\n")
    else:
        weaknesses.append("No weaknesses found. Keep testing and reviewing.", style="green")

    return Panel(
        Group(summary, Text(""), categories, Text(""), weaknesses),
        title="[bold]Ransomware Readiness Dashboard[/bold]",
        subtitle=f"[dim]{DISCLAIMER}[/dim]",
        border_style=result.colour,
        box=box.ROUNDED,
        padding=(1, 2),
    )
