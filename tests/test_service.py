from dataclasses import dataclass, field

from polaris_core.chat.context import StaticContextProvider
from polaris_core.chat.service import PolarisService
from polaris_core.llm.providers import MockLLMProvider
from polaris_core.models import AssistantContext, AssistantRequest, ChatMessage, MessageRole


@dataclass
class RecordingProvider(MockLLMProvider):
    messages: list[ChatMessage] = field(default_factory=list)

    def complete(self, messages: list[ChatMessage]):
        self.messages = messages
        return super().complete(messages)


def test_service_returns_response_and_records_conversation():
    service = PolarisService(
        provider=MockLLMProvider(),
        context_provider=StaticContextProvider(title="Unit Test"),
    )

    response = service.ask(AssistantRequest(message="What wells are loaded?"))

    assert response.model == "mock/polaris"
    assert "Polaris mock response" in response.content
    messages = service.conversation.messages()
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "What wells are loaded?"
    assert messages[1].role == MessageRole.ASSISTANT


def test_service_rejects_empty_message():
    service = PolarisService()

    try:
        service.ask(AssistantRequest(message="   "))
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_request_context_is_passed_as_parameter_to_system_prompt():
    provider = RecordingProvider()
    service = PolarisService(provider=provider)

    service.ask(
        AssistantRequest(
            message="Use the available context.",
            context=AssistantContext(
                title="Uploaded local study",
                facts={"survey": "3D seismic", "wells": ["A-1", "B-2"]},
            ),
        )
    )

    system_message = provider.messages[0]
    assert system_message.role == MessageRole.SYSTEM
    assert "Uploaded local study" in system_message.content
    assert "survey: 3D seismic" in system_message.content
    assert "wells: A-1, B-2" in system_message.content
    assert "Andromeda" not in system_message.content
