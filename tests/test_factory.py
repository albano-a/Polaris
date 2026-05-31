from polaris_core import (
    AssistantRequest,
    create_gemini_model,
    create_model,
    create_service,
    list_available_models,
    save_model_config,
)
from polaris_core.providers import MockLLMProvider


def test_create_model_returns_litellm_provider():
    provider = create_model("gemini/gemini-2.5-flash", api_key="secret", temperature=0.1)

    assert provider.model == "gemini/gemini-2.5-flash"
    assert provider.api_key == "secret"
    assert provider.temperature == 0.1


def test_create_gemini_model_has_default_model():
    provider = create_gemini_model(api_key="secret")

    assert provider.model == "gemini/gemini-2.5-flash"
    assert provider.api_key == "secret"


def test_save_model_config_uses_custom_path(tmp_path):
    config = save_model_config(
        model="gemini/gemini-2.5-pro",
        api_key="secret",
        config_path=tmp_path / "config.json",
    )

    assert config.provider == "gemini"
    assert config.model == "gemini/gemini-2.5-pro"
    assert config.api_key_for("gemini") == "secret"


def test_create_service_accepts_explicit_provider():
    service = create_service(provider=MockLLMProvider())

    response = service.ask(AssistantRequest(message="Hello"))

    assert response.model == "mock/polaris"


def test_list_available_models_returns_gemini_suggestions():
    models = list_available_models()

    assert models
    assert models[0].model.startswith("gemini/")
