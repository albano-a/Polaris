from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from polaris_core.models import ChatMessage, MessageRole


@dataclass
class Conversation:
    max_messages: int = 20
    _messages: deque[ChatMessage] = field(default_factory=deque)

    def add(self, role: MessageRole, content: str) -> None:
        self._messages.append(ChatMessage(role=role, content=content))
        while len(self._messages) > self.max_messages:
            self._messages.popleft()

    def messages(self) -> tuple[ChatMessage, ...]:
        return tuple(self._messages)

    def clear(self) -> None:
        self._messages.clear()
