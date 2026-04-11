"""Shared scanner utilities for decoded client JSON traversal."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Final


QUEST_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"q(\d{8})")
STAGE_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"st(\d{4})")
EVENT_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"ev(\d{3})")


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def to_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def extract_localized(value: Any) -> tuple[str, str]:
    if isinstance(value, dict):
        return str(value.get("En") or ""), str(value.get("Jp") or "")
    if isinstance(value, str):
        return value, ""
    return "", ""


def parse_code(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(0) if match else ""


def parse_quest_id_from_path(path: str) -> int:
    match = QUEST_CODE_PATTERN.search(path.replace("\\", "/"))
    return int(match.group(1)) if match else 0


def match_target(value: int, targets: set[int] | None) -> bool:
    return targets is None or value in targets


def build_location_context(
    *,
    stage_no: int = 0,
    stage_name: str = "",
    stage_name_jp: str = "",
    area_name: str = "",
    area_name_jp: str = "",
    stage_code: str = "",
    event_code: str = "",
) -> dict[str, Any]:
    return {
        "stage_no": stage_no,
        "stage_name": stage_name,
        "stage_name_jp": stage_name_jp,
        "area_name": area_name,
        "area_name_jp": area_name_jp,
        "stage_code": stage_code,
        "event_code": event_code,
    }