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

List known Gemini models:

```powershell
polaris models
```

List models from the Gemini API using your configured key:

```powershell
polaris models --live
```

Save your Gemini API key and model:

```powershell
polaris configure --provider gemini --model gemini/gemini-2.5-flash
```

You can also pass the key directly, although interactive entry is safer:

```powershell
polaris configure --provider gemini --model gemini/gemini-2.5-flash --api-key "YOUR_KEY"
```

Ask a question:

```powershell
polaris ask "What is acoustic impedance?"
```

The short form still works:

```powershell
polaris "How do checkshots help seismic well ties?"
```

Use local uploaded context:

```powershell
polaris ask --docs "C:\path\to\docs" "Summarize the uploaded reports."
```

Show non-secret config:

```powershell
polaris config
```

## Environment Variables

Environment variables override stored API keys:

```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
$env:POLARIS_MODEL="gemini/gemini-2.5-flash"
polaris ask "Explain seismic inversion."
```

## Library Usage

Create a model explicitly:

```python
from polaris_core import create_model

model = create_model(
    model="gemini/gemini-2.5-flash",
    api_key="YOUR_GEMINI_API_KEY",
)
```

Or use the Gemini convenience helper:

```python
from polaris_core import create_gemini_model

model = create_gemini_model(api_key="YOUR_GEMINI_API_KEY")
```

Persist model configuration for later use:

```python
from polaris_core import save_model_config

save_model_config(
    model="gemini/gemini-2.5-flash",
    api_key="YOUR_GEMINI_API_KEY",
)
```

Create a ready-to-use service:

```python
from polaris_core import AssistantContext, AssistantRequest, create_service

service = create_service(model="gemini/gemini-2.5-flash", api_key="YOUR_GEMINI_API_KEY")

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

for model in list_available_models("gemini"):
    print(model.model, model.description)
```

## Build And Upload

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
