from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from polaris_core.config import ConfigStore, PolarisConfig
from polaris_core.exceptions import ConfigurationError, ProviderError
from polaris_core.models import ChatMessage, MessageRole, TokenUsage


@dataclass(frozen=True)
class LLMResult:
    content: str
    model: str
    usage: TokenUsage = TokenUsage()


class LLMProvider(Protocol):
    model: str

    def complete(self, messages: list[ChatMessage]) -> LLMResult:
        """Return a completion for the supplied conversation."""


@dataclass
class MockLLMProvider:
    model: str = "mock/polaris"

    def complete(self, messages: list[ChatMessage]) -> LLMResult:
        last_user = next(
            (message.content for message in reversed(messages) if message.role == MessageRole.USER),
            "",
        )
        content = (
            "<b>Polaris mock response</b><br>"
            "The core is wired correctly. Last user message:<br>"
            f"<code>{last_user[:500]}</code>"
        )
        return LLMResult(content=content, model=self.model)


@dataclass
class LiteLLMProvider:
    model: str
    api_key: str | None = None
    temperature: float = 0.2

    @classmethod
    def from_env(cls) -> "LiteLLMProvider":
        model = os.getenv("POLARIS_MODEL")
        if not model:
            raise ConfigurationError(
                "Set POLARIS_MODEL, run 'polaris configure', or use MockLLMProvider."
            )
        return cls(model=model)

    @classmethod
    def from_config(cls, config: PolarisConfig | None = None) -> "LiteLLMProvider":
        loaded = config or ConfigStore().load()
        model = os.getenv("POLARIS_MODEL") or loaded.model
        api_key = loaded.api_key_for()
        if not model:
            raise ConfigurationError("No model configured. Run 'polaris configure'.")
        if not api_key:
            raise ConfigurationError(
                "No API key configured. Run 'polaris configure' or set GEMINI_API_KEY."
            )
        return cls(model=model, api_key=api_key)

    def complete(self, messages: list[ChatMessage]) -> LLMResult:
        try:
            import litellm
        except ImportError as exc:
            raise ConfigurationError("Install PolarisCore with the 'llm' extra to use LiteLLM.") from exc

        payload = [{"role": message.role.value, "content": message.content} for message in messages]
        try:
            response = litellm.completion(
                model=self.model,
                messages=payload,
                api_key=self.api_key,
                temperature=self.temperature,
            )
        except Exception as exc:
            raise ProviderError(str(exc)) from exc

        choice = response.choices[0]
        content = choice.message.content or ""
        usage = getattr(response, "usage", None)
        token_usage = TokenUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            total_tokens=getattr(usage, "total_tokens", 0) if usage else 0,
        )
        return LLMResult(content=content, model=self.model, usage=token_usage)
