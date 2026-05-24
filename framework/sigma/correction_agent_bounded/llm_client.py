"""Wrapper minimo sobre anthropic SDK para generacion de patches."""

from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    """Interface para generacion de patches — provider-agnostic."""

    def generate_patch(self, prompt: str, max_tokens: int = 1000) -> str: ...


class AnthropicClient:
    """Implementacion concreta usando anthropic SDK."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", timeout: float = 30.0):
        """Initialize with model name and timeout for API calls."""
        self._model = model
        self._timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError as e:
                raise ImportError(
                    "anthropic SDK not installed. "
                    "Install with: pip install anthropic"
                ) from e
            self._client = anthropic.Anthropic(timeout=self._timeout)
        return self._client

    def generate_patch(self, prompt: str, max_tokens: int = 1000) -> str:
        """Send prompt to Claude and return the patch text. Raises ValueError if empty."""
        client = self._get_client()
        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            # Convert provider-specific exceptions (APIError, RateLimitError,
            # APIConnectionError) to RuntimeError so the orchestrator's
            # catch tuple handles them without importing anthropic.
            raise RuntimeError(f"Anthropic API error: {exc}") from exc
        text = response.content[0].text.strip()
        if not text:
            raise ValueError("LLM returned empty response")
        return text


class MockLLMClient:
    """Mock para tests — retorna respuestas predefinidas."""

    def __init__(self, responses: dict[str, str] | None = None, default: str = ""):
        self._responses = responses or {}
        self._default = default
        self.calls: list[str] = []

    def generate_patch(self, prompt: str, max_tokens: int = 1000) -> str:
        """Return a predefined response matching a keyword in the prompt."""
        self.calls.append(prompt)
        for key, response in self._responses.items():
            if key in prompt:
                return response
        if self._default:
            return self._default
        raise ValueError("MockLLMClient: no matching response for prompt and no default set")
