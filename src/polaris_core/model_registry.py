from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass(frozen=True)
class ModelInfo:
    provider: str
    model: str
    description: str = ""


DEFAULT_MODELS: tuple[ModelInfo, ...] = (
    ModelInfo(
        provider="google",
        model="gemini/gemini-2.5-flash",
        description="Fast, balanced Google Gemini model for most chat and analysis workflows.",
    ),
    ModelInfo(
        provider="google",
        model="gemini/gemini-2.5-pro",
        description="Stronger Google Gemini reasoning model for complex geophysical analysis.",
    ),
    ModelInfo(
        provider="google",
        model="gemini/gemini-2.5-flash-lite",
        description="Lower-latency, cost-conscious Google Gemini model when available for your API key.",
    ),
    ModelInfo(
        provider="openai",
        model="openai/gpt-4o-mini",
        description="Fast OpenAI model for general chat and lightweight analysis.",
    ),
    ModelInfo(
        provider="openai",
        model="openai/gpt-4.1",
        description="Stronger OpenAI model for technical reasoning and code-heavy workflows.",
    ),
    ModelInfo(
        provider="anthropic",
        model="anthropic/claude-sonnet-4-5",
        description="Balanced Anthropic Claude model for high-quality reasoning.",
    ),
    ModelInfo(
        provider="anthropic",
        model="anthropic/claude-opus-4-1",
        description="Stronger Anthropic Claude model for complex analysis.",
    ),
    ModelInfo(
        provider="deepseek",
        model="deepseek/deepseek-chat",
        description="DeepSeek chat model for general assistant workflows.",
    ),
    ModelInfo(
        provider="deepseek",
        model="deepseek/deepseek-reasoner",
        description="DeepSeek reasoning model for complex technical tasks.",
    ),
)


def list_models(provider: str | None = None) -> tuple[ModelInfo, ...]:
    if provider is None:
        return DEFAULT_MODELS
    provider_key = normalize_provider(provider)
    return tuple(model for model in DEFAULT_MODELS if model.provider == provider_key)


def default_model_for(provider: str) -> str:
    models = list_models(provider)
    if not models:
        raise ValueError(f"Unknown provider: {provider}")
    return models[0].model


def fetch_live_models(provider: str, api_key: str) -> tuple[ModelInfo, ...]:
    provider_key = normalize_provider(provider)
    if provider_key != "google":
        raise ValueError(f"Live model listing is not implemented for provider: {provider}")
    return fetch_gemini_models(api_key)


def fetch_gemini_models(api_key: str) -> tuple[ModelInfo, ...]:
    query = urlencode({"key": api_key})
    url = f"https://generativelanguage.googleapis.com/v1beta/models?{query}"
    with urlopen(url, timeout=20) as response:  # nosec: user-supplied API key targets Google endpoint.
        payload = json.loads(response.read().decode("utf-8"))

    models: list[ModelInfo] = []
    for item in payload.get("models", []):
        raw_name = item.get("name", "")
        short_name = raw_name.removeprefix("models/")
        if not short_name.startswith("gemini-"):
            continue
        methods = item.get("supportedGenerationMethods", [])
        if methods and "generateContent" not in methods:
            continue
        models.append(
            ModelInfo(
                provider="google",
                model=f"gemini/{short_name}",
                description=item.get("displayName", ""),
            )
        )
    return tuple(models)


def normalize_provider(provider: str) -> str:
    provider_key = provider.lower().strip()
    aliases = {
        "gemini": "google",
        "google-ai": "google",
        "google_ai": "google",
        "google": "google",
        "openai": "openai",
        "anthropic": "anthropic",
        "claude": "anthropic",
        "deepseek": "deepseek",
    }
    return aliases.get(provider_key, provider_key)
