# PolarisCore

UI-independent Python library for building Polaris: an AI chatbot with a configurable geophysics profile, local document retrieval (RAG), and a CLI.

Not tied to any specific frontend. Any app can install the package, pass runtime context, and choose its own UI.

## Install

```bash
pip install polaris-core[llm]
```

For local development:

```bash
pip install -e ".[dev,llm]"
```

## Quick Start

```bash
polaris configure --provider google --model gemini/gemini-2.5-flash
polaris ask "What is acoustic impedance?"
```

## CLI Reference

### `polaris configure` — save provider and API key

```bash
polaris configure --provider google --model gemini/gemini-2.5-flash
polaris configure --provider openai --model openai/gpt-4o-mini
polaris configure --provider anthropic --model anthropic/claude-sonnet-4-5
polaris configure --provider deepseek --model deepseek/deepseek-chat
```

Omit `--api-key` to enter it securely at the prompt. Or pass it directly:

```bash
polaris configure --provider google --api-key "YOUR_KEY"
```

### `polaris ask` — ask a question

```bash
polaris ask "How do checkshots help seismic well ties?"

# Short form — 'ask' can be omitted
polaris "Explain seismic inversion."
```

Use the built-in geophysics document store and your own uploaded docs for RAG:

```bash
polaris ask --docs "How does acoustic impedance relate to porosity?"
```

Use a specific file or directory instead:

```bash
polaris ask --docs "C:\path\to\reports" "Summarize the uploaded reports."
```

### `polaris docs` — manage the user document store

Documents added here are stored outside the repository and included automatically whenever `--docs` is used without a path.

```bash
# Add a file or an entire directory
polaris docs add relatorio.pdf
polaris docs add C:\meus-docs\geofisica\

# List stored documents
polaris docs list

# Remove a document
polaris docs remove relatorio.pdf

# Show where the store lives on disk
polaris docs path
```

Storage location:
- **Windows:** `%APPDATA%\PolarisCore\docs\`
- **Linux / macOS:** `~/.local/share/polaris-core/docs/`

### `polaris models` — list available models

```bash
polaris models
polaris models --provider google
polaris models --provider google --live   # query the provider API
```

### `polaris config` — show current configuration

```bash
polaris config
polaris config --json
```

## Environment Variables

Environment variables override stored API keys:

```bash
GEMINI_API_KEY=YOUR_KEY
OPENAI_API_KEY=YOUR_KEY
ANTHROPIC_API_KEY=YOUR_KEY
DEEPSEEK_API_KEY=YOUR_KEY
POLARIS_MODEL=gemini/gemini-2.5-flash
```

## Library Usage

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

Create a provider explicitly:

```python
from polaris_core import create_google_model, create_openai_model

model = create_google_model(api_key="YOUR_GOOGLE_API_KEY")
model = create_openai_model(api_key="YOUR_OPENAI_API_KEY")
```

Use the document store from Python:

```python
from polaris_core import LocalRetriever

retriever = LocalRetriever.from_user_docs()               # user store only
retriever = LocalRetriever.from_packaged_and_user_docs()  # bundled + user store
retriever = LocalRetriever.from_path("C:/path/to/docs")   # explicit path
```

List available models:

```python
from polaris_core import list_available_models

for model in list_available_models("google"):
    print(model.model, model.description)
```

## Publishing

This repository uses a GitHub Actions workflow at `.github/workflows/publish.yml`.

- **On push / PR:** builds, tests, and uploads artifacts.
- **On GitHub Release:** publishes automatically to PyPI via Trusted Publisher.

Setup:
1. Create `polaris-core` on PyPI and configure a Trusted Publisher for this repository.
2. Add a GitHub environment named `pypi`.
3. Publish a GitHub Release to trigger the upload.

To build and check locally:

```bash
python -m build
python -m twine check dist/*
```
