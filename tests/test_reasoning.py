"""
Tests for the reasoning subsystem.

Tests hypothesis generator parsing and critic evaluator parsing
without requiring live LLM or memory connections.
"""


import pytest

from backend.models.hypothesis import HypothesisStatus
from backend.reasoning.critic_evaluator import CriticEvaluator
from backend.reasoning.hypothesis_generator import HypothesisGenerator


class TestHypothesisGeneratorParsing:
    def test_parse_valid_response(self):
        response = (
            "HYPOTHESIS: Gravity is caused by mass.\n"
            "RATIONALE: Einstein's field equations."
        )
        statement, rationale = HypothesisGenerator._parse_response(response)
        assert statement == "Gravity is caused by mass."
        assert rationale == "Einstein's field equations."

    def test_parse_missing_rationale(self):
        response = "HYPOTHESIS: Stars are hot.\n"
        statement, rationale = HypothesisGenerator._parse_response(response)
        assert statement == "Stars are hot."
        assert rationale == ""

    def test_parse_empty_falls_back_to_full_text(self):
        response = "Some random text with no prefix."
        statement, rationale = HypothesisGenerator._parse_response(response)
        assert statement == response.strip()
        assert rationale == ""


class TestCriticEvaluatorParsing:
    def test_parse_accepted_response(self):
        response = (
            "SCORE: 0.85\n"
            "VERDICT: accepted\n"
            "REASONING: Strong evidence supports the claim."
        )
        score, verdict, reasoning = CriticEvaluator._parse_response(response)
        assert abs(score - 0.85) < 1e-6
        assert verdict == HypothesisStatus.ACCEPTED
        assert "evidence" in reasoning

    def test_parse_rejected_response(self):
        response = (
            "SCORE: 0.1\n"
            "VERDICT: rejected\n"
            "REASONING: Contradicts known data."
        )
        score, verdict, reasoning = CriticEvaluator._parse_response(response)
        assert score == pytest.approx(0.1)
        assert verdict == HypothesisStatus.REJECTED

    def test_parse_unknown_verdict_defaults_to_uncertain(self):
        response = (
            "SCORE: 0.5\n"
            "VERDICT: maybe\n"
            "REASONING: Unclear."
        )
        score, verdict, reasoning = CriticEvaluator._parse_response(response)
        assert verdict == HypothesisStatus.UNCERTAIN

    def test_parse_invalid_score_uses_default(self):
        response = (
            "SCORE: not-a-number\n"
            "VERDICT: uncertain\n"
            "REASONING: N/A"
        )
        score, verdict, reasoning = CriticEvaluator._parse_response(response)
        assert score == 0.5
