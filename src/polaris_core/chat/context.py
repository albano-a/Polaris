from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from polaris_core.models import AssistantContext


class ContextProvider(Protocol):
    def get_context(self) -> AssistantContext:
        """Return dynamic context for the current request/session."""


@dataclass
class StaticContextProvider:
    title: str | None = None
    summary: str | None = None
    facts: dict[str, Any] | None = None
    extra: dict[str, Any] | None = None

    def get_context(self) -> AssistantContext:
        return AssistantContext(
            title=self.title,
            summary=self.summary,
            facts=self.facts or {},
            extra=self.extra or {},
        )
