"""Keeps past scores in history.json so users can track improvement."""

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("history.json")


def load_history(path=HISTORY_FILE):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def last_score(path=HISTORY_FILE):
    history = load_history(path)
    return history[-1]["total"] if history else None


def save_score(result, path=HISTORY_FILE):
    history = load_history(path)
    history.append({
        "date": datetime.now().isoformat(timespec="seconds"),
        "total": result.total,
        "band": result.band,
        "categories": result.category_percent,
    })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
