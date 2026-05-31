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
        provider="gemini",
        model="gemini/gemini-2.5-flash",
        description="Fast, balanced Gemini model for most chat and analysis workflows.",
    ),
    ModelInfo(
        provider="gemini",
        model="gemini/gemini-2.5-pro",
        description="Stronger Gemini reasoning model for complex geophysical analysis.",
    ),
    ModelInfo(
        provider="gemini",
        model="gemini/gemini-2.5-flash-lite",
        description="Lower-latency, cost-conscious Gemini model when available for your API key.",
    ),
)


def list_models(provider: str | None = None) -> tuple[ModelInfo, ...]:
    if provider is None:
        return DEFAULT_MODELS
    provider_key = provider.lower().strip()
    return tuple(model for model in DEFAULT_MODELS if model.provider == provider_key)


def default_model_for(provider: str) -> str:
    models = list_models(provider)
    if not models:
        raise ValueError(f"Unknown provider: {provider}")
    return models[0].model


def fetch_live_models(provider: str, api_key: str) -> tuple[ModelInfo, ...]:
    provider_key = provider.lower().strip()
    if provider_key != "gemini":
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
                provider="gemini",
                model=f"gemini/{short_name}",
                description=item.get("displayName", ""),
            )
        )
    return tuple(models)
