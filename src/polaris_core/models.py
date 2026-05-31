from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ResponseFormat(str, Enum):
    PLAIN_TEXT = "plain_text"
    HTML = "html"
    MARKDOWN = "markdown"


@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class AssistantRequest:
    message: str
    use_retrieval: bool = True
    response_format: ResponseFormat = ResponseFormat.HTML
    context: "AssistantContext | None" = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssistantResponse:
    content: str
    model: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    retrieved_chunks: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssistantProfile:
    name: str = "Polaris"
    role: str = "an AI assistant"
    domain: str | None = None
    instructions: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssistantContext:
    title: str | None = None
    summary: str | None = None
    facts: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Document:
    id: str
    name: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
