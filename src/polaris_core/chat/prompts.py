from __future__ import annotations

from typing import Any

from polaris_core.models import AssistantContext, AssistantProfile, ResponseFormat


class PromptBuilder:
    def build_system_prompt(
        self,
        profile: AssistantProfile,
        context: AssistantContext | None = None,
        response_format: ResponseFormat = ResponseFormat.HTML,
    ) -> str:
        format_rules = self._format_rules(response_format)
        sections = [
            f"You are {profile.name}, {profile.role}.",
            self._section("Domain", [profile.domain] if profile.domain else []),
            self._section("Instructions", profile.instructions),
            self._section("Capabilities", profile.capabilities),
            f"Response format:\n{format_rules}",
        ]
        if context is not None:
            context_lines = self._context_lines(context)
            if context_lines:
                sections.append(self._section("Runtime context", context_lines))
        return "\n\n".join(section for section in sections if section.strip())

    def build_user_prompt(self, message: str, retrieved_chunks: list[str] | None = None) -> str:
        chunks = retrieved_chunks or []
        if not chunks:
            return message

        context_block = "\n\n".join(f"[Context {idx + 1}]\n{chunk}" for idx, chunk in enumerate(chunks))
        return f"""Use the retrieved context when it is relevant. If the context is insufficient, say so briefly.

Retrieved context:
{context_block}

User question:
{message}
"""

    def _format_rules(self, response_format: ResponseFormat) -> str:
        if response_format == ResponseFormat.HTML:
            return (
                "- Return valid, compact HTML for rich text display.\n"
                "- Use <b>, <i>, <code>, <ul>, <li>, <br>, and <pre> when helpful.\n"
                "- Do not wrap the whole response in <html> or <body>."
            )
        if response_format == ResponseFormat.MARKDOWN:
            return "- Return concise GitHub-flavored Markdown."
        return "- Return plain text."

    def _context_lines(self, context: AssistantContext) -> list[str]:
        lines: list[str] = []
        if context.title:
            lines.append(f"Title: {context.title}")
        if context.summary:
            lines.append(f"Summary: {context.summary}")
        for key, value in context.facts.items():
            lines.append(f"{key}: {self._format_value(value)}")
        for key, value in context.extra.items():
            lines.append(f"{key}: {self._format_value(value)}")
        return lines

    def _section(self, title: str, items: tuple[str, ...] | list[str]) -> str:
        if not items:
            return ""
        body = "\n".join(f"- {item}" for item in items)
        return f"{title}:\n{body}"

    def _format_value(self, value: Any) -> str:
        if isinstance(value, (list, tuple, set)):
            return ", ".join(str(item) for item in value) if value else "none"
        return str(value)
