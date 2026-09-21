import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from report import write_report  # noqa: E402
from scoring import NO, NOT_SURE, YES, band_for, load_questions, score  # noqa: E402

QUESTIONS = load_questions()


def safe_answers():
    return {q["id"]: q["safe_answer"] for q in QUESTIONS}


def risky_answers():
    return {q["id"]: NO if q["safe_answer"] == YES else YES for q in QUESTIONS}


class ScoringTest(unittest.TestCase):
    def test_layout(self):
        self.assertEqual(len(QUESTIONS), 20)

    def test_all_safe_scores_100(self):
        r = score(QUESTIONS, safe_answers())
        self.assertEqual(r.total, 100)
        self.assertEqual(r.band, "Strong")
        self.assertEqual(r.weak, [])

    def test_all_risky_scores_0(self):
        r = score(QUESTIONS, risky_answers())
        self.assertEqual(r.total, 0)
        self.assertEqual(r.band, "Poor")
        self.assertEqual(len(r.risky), 20)

    def test_all_not_sure_scores_40(self):
        r = score(QUESTIONS, {q["id"]: NOT_SURE for q in QUESTIONS})
        self.assertEqual(r.total, 40)
        self.assertEqual(r.band, "Basic")

    def test_answering_yes_everywhere_penalises_reverse_question(self):
        # P4 (admin rights) is the reverse question: "yes" is the risky answer.
        r = score(QUESTIONS, {q["id"]: YES for q in QUESTIONS})
        self.assertEqual(r.total, 95)
        self.assertEqual([q["id"] for q in r.risky], ["P4"])
        self.assertEqual(r.category_percent["Prevention"], 80)

    def test_reverse_question_safe_answer_is_no(self):
        answers = safe_answers()
        self.assertEqual(answers["P4"], NO)

    def test_category_percentages_add_up_to_total(self):
        import random
        rng = random.Random(7)
        for _ in range(500):
            answers = {q["id"]: rng.choice([YES, NO, NOT_SURE]) for q in QUESTIONS}
            r = score(QUESTIONS, answers)
            self.assertEqual(sum(r.category_points.values()), r.total)
            self.assertEqual(sum(r.category_percent.values()) / 4, r.total)

    def test_every_weak_answer_has_a_recommendation(self):
        r = score(QUESTIONS, risky_answers())
        for q in r.weak:
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["fix"].strip())

    def test_top_weaknesses_ordered_by_weight(self):
        r = score(QUESTIONS, risky_answers())
        weights = [q["weight"] for q in r.risky]
        self.assertEqual(weights, sorted(weights, reverse=True))
        self.assertTrue(all(q["weight"] == 3 for q in r.top_weaknesses(3)))

    def test_bands(self):
        for s, band in [(100, "Strong"), (80, "Strong"), (79, "Good"), (60, "Good"),
                        (59, "Basic"), (40, "Basic"), (39, "Poor"), (0, "Poor")]:
            self.assertEqual(band_for(s)[0], band, s)

    def test_report_matches_dashboard(self):
        answers = safe_answers()
        answers["R2"] = NO
        answers["S3"] = NOT_SURE
        r = score(QUESTIONS, answers)
        with tempfile.TemporaryDirectory() as d:
            text = write_report(r, os.path.join(d, "report.txt")).read_text()
        self.assertIn(f"{r.total}/100", text)
        self.assertIn(r.band, text)
        for cat, pct in r.category_percent.items():
            self.assertRegex(text, rf"{cat}\s.*{pct}%")
        for q in r.weak:
            self.assertIn(f"[{q['id']}]", text)
        self.assertNotIn("\x1b[", text)  # plain text, no colour codes


if __name__ == "__main__":
    unittest.main()
