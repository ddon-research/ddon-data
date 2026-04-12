"""Helpers for rendering clickable JSON file links in generated AsciiDoc reports."""
from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path

from ._paths import DDON_DATA_ROOT, GENERATED_DIR


ROOT_DIR = DDON_DATA_ROOT
DEFAULT_REPORT_DIR = GENERATED_DIR


class _JsonPathLineResolver:
    def __init__(self, text: str) -> None:
        self.text = text
        self.length = len(text)
        self.index = 0
        self.line = 1
        self.path_to_line: dict[str, int] = {}

    def parse(self) -> dict[str, int]:
        self._skip_whitespace()
        self._parse_value("")
        return self.path_to_line

    def _peek(self) -> str:
        return self.text[self.index] if self.index < self.length else ""

    def _advance(self) -> str:
        char = self.text[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
        return char

    def _skip_whitespace(self) -> None:
        while self.index < self.length and self.text[self.index].isspace():
            self._advance()

    def _record(self, path: str) -> None:
        if path and path not in self.path_to_line:
            self.path_to_line[path] = self.line

    def _parse_value(self, path: str) -> None:
        self._skip_whitespace()
        if path:
            self._record(path)

        char = self._peek()
        if char == "{":
            self._parse_object(path)
            return
        if char == "[":
            self._parse_array(path)
            return
        if char == '"':
            self._parse_string()
            return
        if char in "-0123456789":
            self._parse_number()
            return
        if self.text.startswith("true", self.index):
            self.index += 4
            return
        if self.text.startswith("false", self.index):
            self.index += 5
            return
        if self.text.startswith("null", self.index):
            self.index += 4
            return
        raise ValueError(f"Unexpected JSON token at index {self.index}: {char!r}")

    def _parse_object(self, path: str) -> None:
        self._advance()
        self._skip_whitespace()
        if self._peek() == "}":
            self._advance()
            return

        while True:
            self._skip_whitespace()
            key = self._parse_string()
            self._skip_whitespace()
            if self._advance() != ":":
                raise ValueError("Expected ':' after object key")
            child_path = f"{path}.{key}" if path else key
            self._parse_value(child_path)
            self._skip_whitespace()
            char = self._peek()
            if char == ",":
                self._advance()
                continue
            if char == "}":
                self._advance()
                break
            raise ValueError(f"Expected ',' or '}}' at index {self.index}, got {char!r}")

    def _parse_array(self, path: str) -> None:
        self._advance()
        self._skip_whitespace()
        if self._peek() == "]":
            self._advance()
            return

        item_index = 0
        while True:
            child_path = f"{path}[{item_index}]" if path else f"[{item_index}]"
            self._parse_value(child_path)
            item_index += 1
            self._skip_whitespace()
            char = self._peek()
            if char == ",":
                self._advance()
                continue
            if char == "]":
                self._advance()
                break
            raise ValueError(f"Expected ',' or ']' at index {self.index}, got {char!r}")

    def _parse_string(self) -> str:
        if self._advance() != '"':
            raise ValueError("Expected string opening quote")
        chars: list[str] = []
        while self.index < self.length:
            char = self._advance()
            if char == '"':
                return "".join(chars)
            if char == "\\":
                if self.index >= self.length:
                    raise ValueError("Unterminated escape sequence")
                escaped = self._advance()
                if escaped == "u":
                    hex_digits = self.text[self.index:self.index + 4]
                    if len(hex_digits) != 4:
                        raise ValueError("Incomplete unicode escape")
                    chars.append(chr(int(hex_digits, 16)))
                    self.index += 4
                    continue
                escape_map = {
                    '"': '"',
                    "\\": "\\",
                    "/": "/",
                    "b": "\b",
                    "f": "\f",
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                }
                chars.append(escape_map.get(escaped, escaped))
                continue
            chars.append(char)
        raise ValueError("Unterminated string literal")

    def _parse_number(self) -> None:
        while self.index < self.length and self.text[self.index] in "-+0123456789.eE":
            self._advance()


@lru_cache(maxsize=256)
def _load_json_path_line_map(path_str: str) -> dict[str, int]:
    path = Path(path_str)
    try:
        text = path.read_text(encoding="utf-8")
        return _JsonPathLineResolver(text).parse()
    except (FileNotFoundError, OSError, UnicodeDecodeError, ValueError):
        return {}


def resolve_json_line_number(relative_path: str, json_path: str) -> int | None:
    if not relative_path.endswith(".json") or not json_path:
        return None
    absolute_path = ROOT_DIR / Path(relative_path)
    line_map = _load_json_path_line_map(str(absolute_path))
    return line_map.get(json_path)


def _escape_label(value: str) -> str:
    return value.replace("[", r"\[").replace("]", r"\]")


def build_json_file_link(
    relative_path: str,
    *,
    report_dir: Path | None = None,
    json_path: str = "",
    fallback_line: int | None = None,
) -> str:
    if not relative_path.endswith(".json"):
        return relative_path

    report_dir = report_dir or DEFAULT_REPORT_DIR
    absolute_path = ROOT_DIR / Path(relative_path)
    relative_target = os.path.relpath(absolute_path, report_dir).replace("\\", "/")
    line_number = resolve_json_line_number(relative_path, json_path) or fallback_line
    label = relative_path
    if line_number is not None:
        relative_target += f"#L{line_number}"
        label += f"#L{line_number}"
    return f"link:{relative_target}[{_escape_label(label)}]"