# ─────────────────────────────────────────────
#  tests/test_chatbot.py — Chatbot Unit Tests
# ─────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from ai.chatbot import ChatSession, build_system_prompt, SUBJECT_PROMPTS, simple_ask


class TestBuildSystemPrompt:
    def test_default_subject(self):
        prompt = build_system_prompt("General")
        assert "tutor" in prompt.lower() or "knowledge" in prompt.lower()
        assert "Markdown" in prompt

    def test_math_subject(self):
        prompt = build_system_prompt("Mathematics")
        assert "Mathematics" in prompt or "step-by-step" in prompt.lower()

    def test_teacher_mode_prepends(self):
        prompt = build_system_prompt("Physics", teacher_mode=True)
        assert "Socratic" in prompt or "teacher" in prompt.lower()

    def test_all_subjects_covered(self):
        for subj in SUBJECT_PROMPTS:
            p = build_system_prompt(subj)
            assert len(p) > 50


class TestChatSession:
    @patch("ai.chatbot.get_llm")
    def test_ask_returns_dict(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is a test answer."
        mock_response.usage_metadata = {"total_tokens": 42}
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        session = ChatSession(subject="General")
        result = session.ask("What is 2+2?")

        assert isinstance(result, dict)
        assert "answer" in result
        assert "tokens" in result
        assert "success" in result
        assert result["success"] is True
        assert result["answer"] == "This is a test answer."

    @patch("ai.chatbot.get_llm")
    def test_ask_with_history(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Continued conversation."
        mock_response.usage_metadata = {}
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        session = ChatSession(subject="Mathematics")
        history = [
            {"role": "user", "content": "What is algebra?"},
            {"role": "assistant", "content": "Algebra is a branch of mathematics."},
        ]
        result = session.ask("Give me an example.", history=history)
        assert result["success"] is True

    @patch("ai.chatbot.get_llm")
    def test_ask_handles_exception(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API error")
        mock_get_llm.return_value = mock_llm

        session = ChatSession()
        result = session.ask("test question")
        assert result["success"] is False
        assert "Error" in result["answer"]

    @patch("ai.chatbot.get_llm")
    def test_teacher_mode(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let me teach you..."
        mock_response.usage_metadata = {}
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        session = ChatSession(subject="Physics", teacher_mode=True)
        result = session.ask("Explain gravity")
        assert result["success"] is True


class TestSimpleAsk:
    @patch("ai.chatbot.get_llm")
    def test_simple_ask_returns_string(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Simple answer"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = simple_ask("What is Python?")
        assert isinstance(result, str)
        assert len(result) > 0
