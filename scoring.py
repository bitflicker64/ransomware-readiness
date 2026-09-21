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


def points_for(question, answer):
    if answer == NOT_SURE:
        return POINTS_NOT_SURE
    if answer == question["safe_answer"]:
        return POINTS_SAFE
    return POINTS_RISKY


def is_risky(question, answer):
    return answer in (YES, NO) and answer != question["safe_answer"]


def band_for(score):
    for minimum, name, colour in BANDS:
        if score >= minimum:
            return name, colour
    return BANDS[-1][1], BANDS[-1][2]


@dataclass
class Result:
    total: int
    band: str
    colour: str
    category_points: dict
    category_percent: dict
    risky: list = field(default_factory=list)      # questions answered the risky way
    not_sure: list = field(default_factory=list)   # questions answered "not sure"

    @property
    def weak(self):
        """Every question that needs a recommendation: risky first, then not sure."""
        return self.risky + self.not_sure

    def top_weaknesses(self, n=3):
        """Risky answers by weight; not-sure answers fill any remaining slots."""
        return self.weak[:n]


def _by_weight(questions):
    # Highest weight first; ties keep questionnaire order.
    return sorted(questions, key=lambda q: -q["weight"])


def score(questions, answers):
    """answers maps question id -> 'yes' | 'no' | 'not_sure'."""
    category_points = {cat: 0 for cat in CATEGORIES}
    risky, not_sure = [], []
    for q in questions:
        answer = answers[q["id"]]
        if answer not in ANSWERS:
            raise ValueError(f"Invalid answer {answer!r} for {q['id']}")
        category_points[q["category"]] += points_for(q, answer)
        if answer == NOT_SURE:
            not_sure.append(q)
        elif is_risky(q, answer):
            risky.append(q)

    total = sum(category_points.values())
    category_percent = {
        cat: round(pts / CATEGORY_MAX * 100) for cat, pts in category_points.items()
    }
    band, colour = band_for(total)
    return Result(
        total=total,
        band=band,
        colour=colour,
        category_points=category_points,
        category_percent=category_percent,
        risky=_by_weight(risky),
        not_sure=_by_weight(not_sure),
    )
