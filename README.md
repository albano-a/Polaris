# PolarisCore

PolarisCore is a UI-independent Python library for building Polaris: an AI chatbot with a configurable geophysics profile, local document retrieval, and a simple CLI.

It is not tied to Andromeda. Any app can install the package, pass runtime context, and choose the UI.

## Install

```powershell
pip install polaris-core[llm]
```

For local development:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .[dev,llm]
```

## CLI

List known models for all supported providers:

```powershell
polaris models
```

Filter by provider:

```powershell
polaris models --provider openai
polaris models --provider anthropic
polaris models --provider deepseek
polaris models --provider google
```

List models from the Google Gemini API using your configured key:

```powershell
polaris models --provider google --live
```

Save an API key and model:

```powershell
polaris configure --provider google --model gemini/gemini-2.5-flash
polaris configure --provider openai --model openai/gpt-4o-mini
polaris configure --provider anthropic --model anthropic/claude-sonnet-4-5
polaris configure --provider deepseek --model deepseek/deepseek-chat
```

You can also pass the key directly, although interactive entry is safer:

```powershell
polaris configure --provider google --model gemini/gemini-2.5-flash --api-key "YOUR_KEY"
```

Ask a question:

```powershell
polaris ask "What is acoustic impedance?"
```

The short form still works:

```powershell
polaris "How do checkshots help seismic well ties?"
```

Use local uploaded context from text or PDF files:

```powershell
polaris ask --docs "C:\path\to\docs" "Summarize the uploaded reports."
```

Pass `--docs` without a path to use the geophysics documents packaged with PolarisCore:

```powershell
polaris ask "How does acoustic impedance relate to porosity?" --docs
```

Packaged references live in `src/polaris_core/docs` during development. PDFs, `.txt`, `.md`, and `.rst` files placed there are included in the installed package and used as retrieval context.

Show non-secret config:

```powershell
polaris config
```

## Environment Variables

Environment variables override stored API keys:

```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
$env:OPENAI_API_KEY="YOUR_KEY"
$env:ANTHROPIC_API_KEY="YOUR_KEY"
$env:DEEPSEEK_API_KEY="YOUR_KEY"
$env:POLARIS_MODEL="gemini/gemini-2.5-flash"
polaris ask "Explain seismic inversion."
```

## Library Usage

Create a model explicitly:

```python
from polaris_core import create_model

model = create_model(
    model="gemini/gemini-2.5-flash",
    api_key="YOUR_GOOGLE_API_KEY",
    provider="google",
)
```

Or use provider convenience helpers:

```python
from polaris_core import (
    create_anthropic_model,
    create_deepseek_model,
    create_google_model,
    create_openai_model,
)

model = create_google_model(api_key="YOUR_GOOGLE_API_KEY")
model = create_openai_model(api_key="YOUR_OPENAI_API_KEY")
model = create_anthropic_model(api_key="YOUR_ANTHROPIC_API_KEY")
model = create_deepseek_model(api_key="YOUR_DEEPSEEK_API_KEY")
```

Persist model configuration for later use:

```python
from polaris_core import save_model_config

save_model_config(
    model="gemini/gemini-2.5-flash",
    api_key="YOUR_GOOGLE_API_KEY",
    provider="google",
)
```

Create a ready-to-use service:

```python
from polaris_core import AssistantContext, AssistantRequest, create_service

service = create_service(
    model="gemini/gemini-2.5-flash",
    api_key="YOUR_GOOGLE_API_KEY",
    model_provider="google",
)

response = service.ask(
    AssistantRequest(
        message="Explain how checkshots help seismic well ties.",
        context=AssistantContext(
            title="Local study",
            facts={"basin": "Campos Basin", "available_logs": ["DT", "RHOB", "GR"]},
        ),
    )
)

print(response.content)
```

List suggested models from Python:

```python
from polaris_core import list_available_models

for model in list_available_models("google"):
    print(model.model, model.description)
```

## Build And Upload

This repository includes a GitHub Actions workflow at `.github/workflows/publish.yml`.

It builds and tests on pushes and pull requests. It publishes to PyPI when a GitHub Release is published.

Recommended PyPI setup:

1. Create the `polaris-core` project on PyPI.
2. Add a Trusted Publisher for this GitHub repository.
3. Use workflow file `.github/workflows/publish.yml`.
4. Use the GitHub environment name `pypi`.
5. Publish a GitHub Release to trigger the upload.

Build distributions:

```powershell
python -m build
```

Check them:

```powershell
python -m twine check dist/*
```

Upload to TestPyPI first:

```powershell
python -m twine upload --repository testpypi dist/*
```

Upload to PyPI:

```powershell
python -m twine upload dist/*
```
