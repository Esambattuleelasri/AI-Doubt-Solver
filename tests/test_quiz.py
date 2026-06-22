# ─────────────────────────────────────────────
#  tests/test_quiz.py — Quiz Generator Tests
# ─────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
import json
from ai.quiz_generator import generate_quiz, grade_quiz, _letter_grade, _fallback_questions


class TestLetterGrade:
    def test_a_plus(self):   assert _letter_grade(95) == "A+"
    def test_a(self):        assert _letter_grade(85) == "A"
    def test_b(self):        assert _letter_grade(75) == "B"
    def test_c(self):        assert _letter_grade(65) == "C"
    def test_d(self):        assert _letter_grade(55) == "D"
    def test_f(self):        assert _letter_grade(40) == "F"
    def test_boundary_90(self): assert _letter_grade(90) == "A+"
    def test_boundary_80(self): assert _letter_grade(80) == "A"


class TestFallbackQuestions:
    def test_returns_correct_count(self):
        q = _fallback_questions("Python", "mcq", 5)
        assert len(q) == 5

    def test_structure(self):
        q = _fallback_questions("Math", "mcq", 3)
        for item in q:
            assert "question" in item
            assert "correct_answer" in item
            assert "options" in item

    def test_truefalse_options(self):
        q = _fallback_questions("History", "truefalse", 2)
        for item in q:
            assert "True" in item["options"]
            assert "False" in item["options"]


class TestGenerateQuiz:
    @patch("ai.quiz_generator.get_llm")
    def test_mcq_generation(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A) A language", "B) A snake", "C) A library", "D) A framework"],
                    "correct_answer": "A) A language",
                    "explanation": "Python is a programming language."
                }
            ]
        })
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = generate_quiz("Python", "mcq", "easy", 1)
        assert len(result) == 1
        assert result[0]["question"] == "What is Python?"
        assert len(result[0]["options"]) == 4

    @patch("ai.quiz_generator.get_llm")
    def test_handles_json_parse_error(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is not valid JSON at all!!!"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = generate_quiz("Biology", "mcq", "medium", 3)
        # Should return fallback questions, not crash
        assert isinstance(result, list)
        assert len(result) > 0

    @patch("ai.quiz_generator.get_llm")
    def test_handles_llm_exception(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("Network error")
        mock_get_llm.return_value = mock_llm

        result = generate_quiz("Chemistry", "truefalse", "hard", 5)
        assert isinstance(result, list)


class TestGradeQuiz:
    def _make_questions(self):
        return [
            {"question": "Q1?", "options": ["A) 1", "B) 2"], "correct_answer": "A) 1", "explanation": "Exp 1"},
            {"question": "Q2?", "options": ["A) X", "B) Y"], "correct_answer": "B) Y", "explanation": "Exp 2"},
            {"question": "Q3?", "options": None, "correct_answer": "photosynthesis", "explanation": "Exp 3"},
        ]

    def test_all_correct(self):
        q = self._make_questions()
        answers = {0: "A) 1", 1: "B) Y", 2: "photosynthesis"}
        result = grade_quiz(q, answers)
        assert result["score"] == 3
        assert result["percentage"] == 100
        assert result["grade"] == "A+"

    def test_all_wrong(self):
        q = self._make_questions()
        answers = {0: "B) 2", 1: "A) X", 2: "osmosis"}
        result = grade_quiz(q, answers)
        assert result["score"] == 0
        assert result["percentage"] == 0
        assert result["grade"] == "F"

    def test_partial_score(self):
        q = self._make_questions()
        answers = {0: "A) 1", 1: "A) X", 2: "osmosis"}
        result = grade_quiz(q, answers)
        assert result["score"] == 1
        assert result["total"] == 3

    def test_case_insensitive(self):
        q = self._make_questions()
        answers = {2: "PHOTOSYNTHESIS"}
        result = grade_quiz(q, answers)
        # correct_answer is "photosynthesis", user said "PHOTOSYNTHESIS" -> .lower() matches
        assert result["results"][2]["is_correct"] is True

    def test_unanswered_questions(self):
        q = self._make_questions()
        result = grade_quiz(q, {})
        assert result["score"] == 0

    def test_result_structure(self):
        q = self._make_questions()
        result = grade_quiz(q, {0: "A) 1"})
        assert "score" in result
        assert "total" in result
        assert "percentage" in result
        assert "grade" in result
        assert "results" in result
        assert len(result["results"]) == 3
