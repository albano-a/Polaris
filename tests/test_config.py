from polaris_core.config import ConfigStore
from polaris_core.model_registry import default_model_for, list_models
from polaris_core.providers import LiteLLMProvider


def test_model_registry_lists_gemini_models():
    models = list_models("gemini")

    assert models
    assert models[0].model == "gemini/gemini-2.5-flash"
    assert default_model_for("gemini") == "gemini/gemini-2.5-flash"


def test_config_store_saves_provider_model_and_key(tmp_path):
    store = ConfigStore(tmp_path / "config.json")

    saved = store.update(
        provider="gemini",
        model="gemini/gemini-2.5-pro",
        api_key="secret",
    )
    loaded = store.load()

    assert saved.model == "gemini/gemini-2.5-pro"
    assert loaded.provider == "gemini"
    assert loaded.api_key_for("gemini") == "secret"


def test_litellm_provider_can_be_built_from_config(tmp_path):
    store = ConfigStore(tmp_path / "config.json")
    config = store.update(
        provider="gemini",
        model="gemini/gemini-2.5-flash",
        api_key="secret",
    )

    provider = LiteLLMProvider.from_config(config)

    assert provider.model == "gemini/gemini-2.5-flash"
    assert provider.api_key == "secret"
