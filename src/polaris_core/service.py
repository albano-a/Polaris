from __future__ import annotations

from dataclasses import dataclass, field

from polaris_core.context import ContextProvider, PromptBuilder, StaticContextProvider, geophysics_profile
from polaris_core.conversation import Conversation
from polaris_core.models import (
    AssistantContext,
    AssistantProfile,
    AssistantRequest,
    AssistantResponse,
    ChatMessage,
    MessageRole,
)
from polaris_core.providers import LLMProvider, MockLLMProvider
from polaris_core.retrieval import LocalRetriever


@dataclass
class PolarisService:
    provider: LLMProvider = field(default_factory=MockLLMProvider)
    profile: AssistantProfile = field(default_factory=geophysics_profile)
    context_provider: ContextProvider = field(default_factory=StaticContextProvider)
    retriever: LocalRetriever | None = None
    conversation: Conversation = field(default_factory=Conversation)
    prompt_builder: PromptBuilder = field(default_factory=PromptBuilder)

    def ask(self, request: AssistantRequest) -> AssistantResponse:
        message = request.message.strip()
        if not message:
            raise ValueError("AssistantRequest.message cannot be empty.")

        context = self._resolve_context(request.context)
        system_prompt = self.prompt_builder.build_system_prompt(
            self.profile,
            context,
            request.response_format,
        )
        retrieved = self._retrieve(message, request.use_retrieval)
        user_prompt = self.prompt_builder.build_user_prompt(
            message,
            [result.chunk for result in retrieved],
        )

        messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)]
        messages.extend(self.conversation.messages())
        messages.append(ChatMessage(role=MessageRole.USER, content=user_prompt))

        result = self.provider.complete(messages)

        self.conversation.add(MessageRole.USER, message)
        self.conversation.add(MessageRole.ASSISTANT, result.content)

        return AssistantResponse(
            content=result.content,
            model=result.model,
            usage=result.usage,
            retrieved_chunks=tuple(item.chunk for item in retrieved),
            metadata={
                "retrieved_documents": [
                    {
                        "id": item.document_id,
                        "name": item.document_name,
                        "score": item.score,
                    }
                    for item in retrieved
                ]
            },
        )

    def _retrieve(self, message: str, enabled: bool):
        if not enabled or self.retriever is None:
            return []
        return self.retriever.search(message)

    def _resolve_context(self, request_context: AssistantContext | None) -> AssistantContext:
        if request_context is not None:
            return request_context
        return self.context_provider.get_context()
