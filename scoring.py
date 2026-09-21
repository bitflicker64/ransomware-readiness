"""Scoring: points per answer, category percentages, band and weaknesses."""

import json
from dataclasses import dataclass, field
from pathlib import Path

QUESTIONS_FILE = Path(__file__).with_name("questions.json")

CATEGORIES = ["Prevention", "Detection", "Recovery", "Response"]
QUESTIONS_PER_CATEGORY = 5
POINTS_SAFE = 5
POINTS_NOT_SURE = 2
POINTS_RISKY = 0
CATEGORY_MAX = QUESTIONS_PER_CATEGORY * POINTS_SAFE  # 25

YES, NO, NOT_SURE = "yes", "no", "not_sure"
ANSWERS = (YES, NO, NOT_SURE)

# (minimum score, band name, rich colour)
BANDS = [
    (80, "Strong", "green"),
    (60, "Good", "yellow"),
    (40, "Basic", "dark_orange"),
    (0, "Poor", "red"),
]


def load_questions(path=QUESTIONS_FILE):
    with open(path, encoding="utf-8") as f:
        questions = json.load(f)
    validate_questions(questions)
    return questions


def validate_questions(questions):
    """Fail early if questions.json breaks the 4 x 5 layout the scoring relies on."""
    required = {"id", "category", "text", "safe_answer", "weight", "why", "fix"}
    ids = set()
    for q in questions:
        missing = required - q.keys()
        if missing:
            raise ValueError(f"Question {q.get('id', '?')} is missing {sorted(missing)}")
        if q["category"] not in CATEGORIES:
            raise ValueError(f"Question {q['id']} has unknown category {q['category']!r}")
        if q["safe_answer"] not in (YES, NO):
            raise ValueError(f"Question {q['id']} safe_answer must be 'yes' or 'no'")
        if q["id"] in ids:
            raise ValueError(f"Duplicate question id {q['id']}")
        ids.add(q["id"])
    for cat in CATEGORIES:
        count = sum(1 for q in questions if q["category"] == cat)
        if count != QUESTIONS_PER_CATEGORY:
            raise ValueError(f"{cat} has {count} questions, expected {QUESTIONS_PER_CATEGORY}")
