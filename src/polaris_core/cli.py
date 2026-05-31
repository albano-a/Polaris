from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from polaris_core.config import ConfigStore, config_summary, configure_interactively
from polaris_core.context import StaticContextProvider, geophysics_profile
from polaris_core.model_registry import default_model_for, fetch_live_models, list_models
from polaris_core.models import AssistantRequest, ResponseFormat
from polaris_core.providers import LiteLLMProvider, MockLLMProvider
from polaris_core.retrieval import LocalRetriever
from polaris_core.service import PolarisService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="polaris",
        description="PolarisCore command line interface.",
    )
    subparsers = parser.add_subparsers(dest="command")

    ask = subparsers.add_parser("ask", help="Ask Polaris a question.")
    add_ask_arguments(ask)

    configure = subparsers.add_parser("configure", help="Save provider, model, and API key.")
    configure.add_argument(
        "--provider",
        default="google",
        help="Provider name: google, openai, anthropic, or deepseek. Default: google.",
    )
    configure.add_argument("--model", help="Model name. Default: provider default.")
    configure.add_argument("--api-key", help="API key. If omitted, Polaris asks securely.")
    configure.add_argument("--show-path", action="store_true", help="Print the config path after saving.")

    models = subparsers.add_parser("models", help="List known model names.")
    models.add_argument("--provider", help="Provider name. Omit to list all providers.")
    models.add_argument("--live", action="store_true", help="Fetch models from the provider API.")

    config = subparsers.add_parser("config", help="Show current non-secret configuration.")
    config.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    return parser


def add_ask_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("message", nargs="*", help="Message to send to Polaris.")
    parser.add_argument("--mock", action="store_true", help="Use the built-in mock provider.")
    parser.add_argument("--docs", type=Path, help="File or directory with .txt/.md/.rst files for retrieval.")
    parser.add_argument("--plain", action="store_true", help="Ask for plain text instead of HTML.")
    parser.add_argument("--context-title", default=None, help="Optional title for runtime context.")
    parser.add_argument("--context-summary", default=None, help="Optional summary for runtime context.")
    parser.add_argument("--verbose", action="store_true", help="Print retrieval diagnostics to stderr.")


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    commands = {"ask", "configure", "models", "config"}
    if not raw_args:
        raw_args.append("ask")
    elif raw_args[0] not in commands:
        raw_args.insert(0, "ask")
    args = build_parser().parse_args(raw_args)
    command = args.command or "ask"
    if command == "configure":
        return configure_command(args)
    if command == "models":
        return models_command(args)
    if command == "config":
        return config_command(args)
    return ask_command(args)


def configure_command(args: argparse.Namespace) -> int:
    provider = args.provider.lower().strip()
    model = args.model or default_model_for(provider)
    store = ConfigStore()
    if args.api_key:
        config = store.update(provider=provider, model=model, api_key=args.api_key.strip())
    else:
        config = configure_interactively(provider=provider, model=model, store=store)

    print(f"Saved provider: {config.provider}")
    print(f"Saved model: {config.model}")
    if args.show_path:
        print(f"Config path: {store.path}")
    return 0


def models_command(args: argparse.Namespace) -> int:
    if args.live:
        config = ConfigStore().load()
        api_key = config.api_key_for(args.provider)
        if not api_key:
            print("No API key configured. Run 'polaris configure' or set the provider API key env var.")
            return 1
        models = fetch_live_models(args.provider, api_key)
    else:
        models = list_models(args.provider)
    if not models:
        print(f"No known models for provider '{args.provider}'.")
        return 1
    for item in models:
        description = f" - {item.description}" if item.description else ""
        print(f"{item.model}{description}")
    return 0


def config_command(args: argparse.Namespace) -> int:
    config = ConfigStore().load()
    summary = config_summary(config)
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    print(f"Provider: {summary['provider']}")
    print(f"Model: {summary['model']}")
    print(f"Config path: {summary['config_path']}")
    print(f"API key: {summary['api_key_source']}")
    return 0


def ask_command(args: argparse.Namespace) -> int:
    message = " ".join(args.message).strip()
    if not message:
        message = sys.stdin.read().strip()
    if not message:
        raise SystemExit("Provide a message or pipe one through stdin.")

    provider = MockLLMProvider() if args.mock else LiteLLMProvider.from_config()
    retriever = LocalRetriever.from_path(args.docs) if args.docs else None
    if args.verbose and args.docs:
        count = len(retriever.documents) if retriever else 0
        print(f"Loaded {count} document(s) from {args.docs}", file=sys.stderr)
    service = PolarisService(
        provider=provider,
        profile=geophysics_profile(),
        context_provider=StaticContextProvider(
            title=args.context_title,
            summary=args.context_summary,
        ),
        retriever=retriever,
    )
    response = service.ask(
        AssistantRequest(
            message=message,
            response_format=ResponseFormat.PLAIN_TEXT if args.plain else ResponseFormat.HTML,
        )
    )
    print(response.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
