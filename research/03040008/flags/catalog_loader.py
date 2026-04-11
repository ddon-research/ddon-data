"""
Catalog of user-curated investigation targets for flag → quest mapping.

These files define WHAT to look for, not WHERE the data comes from.
They are manually documented observations, NOT server reconstructions
or Arrowgene quest asset data (which would be circular).

Sources of investigation targets:
  1. known_world_manage_quest_flags.txt   — manually documented quest flags
  2. known_world_manage_layout_flags.txt  — manually documented layout flags
  3. npc_ledger_flags.json                — NPC function → quest flag mappings
                                            (observed from live game client)
  4. world_manage_state_quests.md         — documented layout flag descriptions
                                            (observed from live game client)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


QUEST_ID_PATTERN = re.compile(r"^\d{8}$")
FLAG_LINE_PATTERN = re.compile(r"^\s+(\d+)(?:\s*//\s*(.*))?$")


@dataclass(frozen=True)
class TargetFlag:
    quest_id: int | None
    flag_type: str | None
    flag_value: int
    doc_comment: str = ""
    origin: str = "catalog"


def parse_known_flag_file(path: Path, flag_type: str) -> list[TargetFlag]:
    targets: list[TargetFlag] = []
    current_quest_id: int | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if QUEST_ID_PATTERN.fullmatch(stripped):
            current_quest_id = int(stripped)
            continue
        match = FLAG_LINE_PATTERN.match(line)
        if match and current_quest_id is not None:
            targets.append(
                TargetFlag(
                    quest_id=current_quest_id,
                    flag_type=flag_type,
                    flag_value=int(match.group(1)),
                    doc_comment=(match.group(2) or "").strip(),
                    origin="catalog",
                )
            )
    return targets


def dedupe_targets(targets: Iterable[TargetFlag]) -> list[TargetFlag]:
    deduped: dict[tuple[int | None, str | None, int], TargetFlag] = {}
    for target in targets:
        key = (target.quest_id, target.flag_type, target.flag_value)
        existing = deduped.get(key)
        if existing is None:
            deduped[key] = target
            continue
        if not existing.doc_comment and target.doc_comment:
            deduped[key] = target
    return sorted(deduped.values(), key=lambda item: (item.quest_id or 0, item.flag_type or "", item.flag_value, item.origin))


# ---------------------------------------------------------------------------
# NPC Ledger Flags loader (npc_ledger_flags.json)
# ---------------------------------------------------------------------------

def load_npc_ledger_flags(upstream_root: Path) -> list[TargetFlag]:
    """
    Parse docs/quests/npc_ledger_flags.json and return TargetFlags.

    Each entry maps an NPC → list of functions each gated by a quest flag.
    Flag value 0 means "no flag required" and is skipped.

    Returns TargetFlags with origin="npc_ledger" and doc_comment="NPC: <name> → <function>".
    """
    ledger_path = upstream_root / "docs" / "quests" / "npc_ledger_flags.json"
    if not ledger_path.exists():
        return []

    targets: list[TargetFlag] = []
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, dict):
        return []

    for npc_key, npc_data in data.items():
        if not isinstance(npc_data, dict):
            continue
        npc_name = npc_data.get("npc_name", f"NPC_{npc_key}")
        for func in npc_data.get("functions", []):
            if not isinstance(func, dict):
                continue
            flag_val = func.get("flag")
            if not isinstance(flag_val, int) or flag_val == 0:
                continue
            func_name = func.get("name", "Unknown")
            targets.append(
                TargetFlag(
                    quest_id=None,
                    flag_type="quest_flag",
                    flag_value=flag_val,
                    doc_comment=f"NPC: {npc_name} → {func_name}",
                    origin="npc_ledger",
                )
            )

    return targets


# ---------------------------------------------------------------------------
# World Manage State Quests loader (world_manage_state_quests.md)
# ---------------------------------------------------------------------------

_WM_QUEST_HEADER = re.compile(r"^###\s+q(\d{8})")
# 4-column: | Type | StageNo | Value | Comment  (trailing | is optional)
_WM_TABLE_ROW = re.compile(
    r"\|\s*(\w+)\s*\|\s*(?:st)?(\w+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|?\s*$"
)
# 3-column: | Type | Value | Comment  (no StageNo, trailing | is optional)
_WM_TABLE_ROW_3COL = re.compile(
    r"\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|?\s*$"
)


def _build_docs_target(quest_id: int, flag_value: int, comment: str, stage_str: str = "") -> TargetFlag | None:
    if flag_value == 0:
        return None
    stage_note = f"st{stage_str}" if stage_str else ""
    doc_comment = f"{comment} [{stage_note}]" if stage_note else comment
    return TargetFlag(
        quest_id=quest_id,
        flag_type="layout_flag",
        flag_value=flag_value,
        doc_comment=doc_comment,
        origin="docs_world_manage",
    )


def load_world_manage_docs(upstream_root: Path) -> list[TargetFlag]:
    """
    Parse docs/quests/world_manage_state_quests.md and return TargetFlags.

    Each documented row maps a layout flag value → quest with a human comment.
    Returns TargetFlags with origin="docs_world_manage".
    """
    doc_path = upstream_root / "docs" / "quests" / "world_manage_state_quests.md"
    if not doc_path.exists():
        return []

    targets: list[TargetFlag] = []
    current_quest_id: int | None = None

    for line in doc_path.read_text(encoding="utf-8").splitlines():
        # Check for quest header
        header_match = _WM_QUEST_HEADER.match(line)
        if header_match:
            current_quest_id = int(header_match.group(1))
            continue

        if current_quest_id is None:
            continue

        # Skip table headers and separators
        if line.strip().startswith("|:") or line.strip().startswith("| Type"):
            continue

        # Try 4-column match first (Type | StageNo | Value | Comment)
        match = _WM_TABLE_ROW.match(line)
        if match:
            target = _build_docs_target(
                current_quest_id,
                int(match.group(3)),
                match.group(4).strip(),
                match.group(2).strip(),
            )
            if target is not None:
                targets.append(target)
            continue

        # Try 3-column match (Type | Value | Comment) — some rows omit StageNo
        match3 = _WM_TABLE_ROW_3COL.match(line)
        if match3:
            target = _build_docs_target(current_quest_id, int(match3.group(2)), match3.group(3).strip())
            if target is not None:
                targets.append(target)

    return targets


# ---------------------------------------------------------------------------
# Combined loader
# ---------------------------------------------------------------------------

def load_known_targets(upstream_root: Path) -> list[TargetFlag]:
    """Load all known targets from all upstream documentation sources."""
    quest_flags_path = upstream_root / "docs" / "quests" / "known_world_manage_quest_flags.txt"
    layout_flags_path = upstream_root / "docs" / "quests" / "known_world_manage_layout_flags.txt"
    
    targets: list[TargetFlag] = []
    if quest_flags_path.exists():
        targets.extend(parse_known_flag_file(quest_flags_path, "quest_flag"))
    if layout_flags_path.exists():
        targets.extend(parse_known_flag_file(layout_flags_path, "layout_flag"))

    targets.extend(load_npc_ledger_flags(upstream_root))
    targets.extend(load_world_manage_docs(upstream_root))

    return sorted(targets, key=lambda item: (item.quest_id or 0, item.flag_type or "", item.flag_value, item.origin))


def build_flag_query_context(catalog: list[TargetFlag], flag_value: int) -> tuple[list[TargetFlag], list[TargetFlag]]:
    documented_targets = [target for target in catalog if target.flag_value == flag_value]
    query_targets = [TargetFlag(quest_id=None, flag_type=None, flag_value=flag_value, origin="flag_query")]
    return query_targets, documented_targets


def build_quest_query_context(catalog: list[TargetFlag], quest_id: int) -> tuple[list[TargetFlag], list[TargetFlag]]:
    documented_targets = [target for target in catalog if target.quest_id == quest_id]
    # We remove asset parsing from this module to keep things focused on the text catalog.
    return documented_targets, documented_targets
