"""Tests para llm_client.py — S-3 (mock, no LLM real)."""

import pytest

from sigma.correction_agent_bounded.llm_client import MockLLMClient


class TestMockLLMClient:
    def test_returns_matching_response(self):
        client = MockLLMClient(responses={"silent_catch": "logger.warn({err})"})
        result = client.generate_patch("Fix the silent_catch block")
        assert result == "logger.warn({err})"

    def test_records_calls(self):
        client = MockLLMClient(default="patch")
        client.generate_patch("prompt 1")
        client.generate_patch("prompt 2")
        assert len(client.calls) == 2
        assert "prompt 1" in client.calls[0]

    def test_default_response(self):
        client = MockLLMClient(default="default patch")
        result = client.generate_patch("anything")
        assert result == "default patch"

    def test_empty_response_raises(self):
        client = MockLLMClient()
        with pytest.raises(ValueError, match="no matching response"):
            client.generate_patch("no match")

    def test_multiple_responses(self):
        client = MockLLMClient(responses={
            "catch": "logger.warn(err)",
            "auth": "getUser()",
        })
        assert "logger" in client.generate_patch("fix catch block")
        assert "getUser" in client.generate_patch("add auth check")
