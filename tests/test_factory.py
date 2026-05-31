from polaris_core import (
    AssistantRequest,
    create_anthropic_model,
    create_deepseek_model,
    create_google_model,
    create_model,
    create_openai_model,
    create_service,
    list_available_models,
    save_model_config,
)
from polaris_core.providers import MockLLMProvider


def test_create_model_returns_litellm_provider():
    provider = create_model(
        model="gemini/gemini-2.5-flash",
        api_key="secret",
        provider="google",
        temperature=0.1,
    )

    assert provider.model == "gemini/gemini-2.5-flash"
    assert provider.api_key == "secret"
    assert provider.temperature == 0.1


def test_provider_convenience_helpers_have_defaults():
    google = create_google_model(api_key="secret")
    openai = create_openai_model(api_key="secret")
    anthropic = create_anthropic_model(api_key="secret")
    deepseek = create_deepseek_model(api_key="secret")

    assert google.model == "gemini/gemini-2.5-flash"
    assert openai.model == "openai/gpt-4o-mini"
    assert anthropic.model == "anthropic/claude-sonnet-4-5"
    assert deepseek.model == "deepseek/deepseek-chat"


def test_save_model_config_uses_custom_path(tmp_path):
    config = save_model_config(
        model="gemini/gemini-2.5-pro",
        api_key="secret",
        provider="google",
        config_path=tmp_path / "config.json",
    )

    assert config.provider == "google"
    assert config.model == "gemini/gemini-2.5-pro"
    assert config.api_key_for("google") == "secret"


def test_create_service_accepts_explicit_provider():
    service = create_service(provider=MockLLMProvider())

    response = service.ask(AssistantRequest(message="Hello"))

    assert response.model == "mock/polaris"


def test_list_available_models_returns_all_provider_suggestions():
    models = list_available_models()

    assert models
    assert {model.provider for model in models} >= {"google", "openai", "anthropic", "deepseek"}
