from __future__ import annotations

from html import unescape
from html.parser import HTMLParser

_BOLD = "\033[1m"
_ITALIC = "\033[3m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


class _HTMLToTerminal(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._list_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("b", "strong"):
            self._parts.append(_BOLD)
        elif tag in ("i", "em"):
            self._parts.append(_ITALIC)
        elif tag in ("code", "pre"):
            self._parts.append(_CYAN)
        elif tag == "br":
            self._parts.append("\n")
        elif tag == "li":
            self._parts.append("  " * max(self._list_depth, 1) + "- ")
        elif tag in ("ul", "ol"):
            self._list_depth += 1
        elif tag == "p":
            if self._parts:
                self._parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("b", "strong", "i", "em", "code", "pre"):
            self._parts.append(_RESET)
        elif tag == "li":
            self._parts.append("\n")
        elif tag in ("ul", "ol"):
            self._list_depth = max(self._list_depth - 1, 0)
        elif tag == "p":
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self._parts.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self._parts.append(unescape(f"&#{name};"))

    def get_text(self) -> str:
        text = "".join(self._parts)
        lines = [line.rstrip() for line in text.splitlines()]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        collapsed: list[str] = []
        for line in lines:
            if line == "" and collapsed and collapsed[-1] == "":
                continue
            collapsed.append(line)
        return "\n".join(collapsed)


def html_to_terminal(html: str) -> str:
    parser = _HTMLToTerminal()
    parser.feed(html)
    parser.close()
    return parser.get_text()
