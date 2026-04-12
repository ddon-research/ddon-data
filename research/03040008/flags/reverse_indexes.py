"""Reusable reverse indexes for deterministic quest, stage, and flag relationships."""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any, Iterable

from scan_models import FlagHit
from source_metadata import (
    CLIENT_ROOT,
    _collect_stage_layout_hits,
    build_quest_archive_context,
    collect_quest_archive_qst_hits,
    resolve_lot_group_association,
)

GROUP_NO_PATTERN = re.compile(r"(?:^|\s\|\s)DataCommon\.Group=(?P<group>\d+)(?:$|\s\|)")
_REVERSE_INDEX_CACHE: dict[tuple[tuple[int, ...], tuple[str, ...]], dict[str, Any]] = {}


def _iter_all_client_quest_ids() -> tuple[int, ...]:
    quest_root = CLIENT_ROOT / "quest"
    quest_ids: list[int] = []
    for path in sorted(quest_root.glob("q*.arc.json")):
        name = path.name
        if not (name.startswith("q") and name.endswith(".arc.json")):
            continue
        raw_value = name[1:-9]
        if raw_value.isdigit():
            quest_ids.append(int(raw_value))
    return tuple(quest_ids)


def _normalize_quest_ids(quest_ids: Iterable[int] | None) -> tuple[int, ...]:
    if quest_ids is None:
        return _iter_all_client_quest_ids()
    values = {int(value) for value in quest_ids if int(value) > 0}
    return tuple(sorted(values))


def _normalize_stage_codes(stage_codes: Iterable[str] | None) -> tuple[str, ...]:
    values = {str(value) for value in (stage_codes or []) if str(value)}
    return tuple(sorted(values))


def _extract_group_no(context: str) -> int:
    match = GROUP_NO_PATTERN.search(context or "")
    return int(match.group("group")) if match else 0


def _append_event_viewer_reference(stage_to_event_viewers: dict[str, list[dict[str, Any]]], hit: FlagHit) -> None:
    if hit.source_type != "evsi" or not hit.stage_code or not hit.event_code:
        return

    stage_entries = stage_to_event_viewers.setdefault(hit.stage_code, [])
    entry = {
        "event_code": hit.event_code,
        "quest_id": int(hit.quest_id or 0),
        "file_path": hit.file_path,
        "event_key": hit.context.split(" | ")[1] if " | " in hit.context else "",
        "event_context": hit.context,
    }
    if entry not in stage_entries:
        stage_entries.append(entry)


def _append_stage_group_reference(stage_group_references: dict[str, dict[int, dict[str, Any]]], hit: FlagHit) -> None:
    if hit.source_type != "gpl" or not hit.stage_code:
        return

    group_no = _extract_group_no(hit.context)
    if group_no <= 0:
        return

    stage_bucket = stage_group_references.setdefault(hit.stage_code, {})
    group_bucket = stage_bucket.setdefault(
        group_no,
        {
            "gpl_refs": [],
            "lot_reference": None,
        },
    )

    gpl_ref = {
        "flag_value": int(hit.flag_value),
        "flag_kind": hit.flag_kind,
        "quest_id": int(hit.quest_id or 0),
        "file_path": hit.file_path,
        "json_path": hit.json_path,
        "context": hit.context,
    }
    if gpl_ref not in group_bucket["gpl_refs"]:
        group_bucket["gpl_refs"].append(gpl_ref)

    if group_bucket["lot_reference"] is None:
        lot_reference = resolve_lot_group_association(hit.stage_code, group_no)
        if lot_reference:
            group_bucket["lot_reference"] = dict(lot_reference)


def build_reverse_indexes(
    *,
    quest_ids: Iterable[int] | None = None,
    stage_codes: Iterable[str] | None = None,
    corpus_index: Any | None = None,
    json_cache: Any | None = None,
) -> dict[str, Any]:
    normalized_quest_ids = _normalize_quest_ids(quest_ids)
    requested_stage_codes = set(_normalize_stage_codes(stage_codes))

    stage_to_quests: dict[str, set[int]] = {}
    quest_stage_codes: dict[int, tuple[str, ...]] = {}
    for quest_id in normalized_quest_ids:
        archive_context = build_quest_archive_context(quest_id)
        if not isinstance(archive_context, dict):
            continue
        current_stage_codes = tuple(
            sorted(str(stage_code) for stage_code in archive_context.get("stage_codes", []) if stage_code)
        )
        quest_stage_codes[quest_id] = current_stage_codes
        for stage_code in current_stage_codes:
            requested_stage_codes.add(stage_code)
            stage_to_quests.setdefault(stage_code, set()).add(quest_id)

    normalized_stage_codes = tuple(sorted(requested_stage_codes))
    cache_key = (normalized_quest_ids, normalized_stage_codes)
    if corpus_index is not None and json_cache is not None and cache_key in _REVERSE_INDEX_CACHE:
        return copy.deepcopy(_REVERSE_INDEX_CACHE[cache_key])

    flag_to_quests: dict[int, set[int]] = {}
    flag_to_stages: dict[int, set[str]] = {}
    flag_to_kinds: dict[int, set[str]] = {}
    stage_to_event_viewers: dict[str, list[dict[str, Any]]] = {}
    stage_group_references: dict[str, dict[int, dict[str, Any]]] = {}

    for quest_id, current_stage_codes in quest_stage_codes.items():
        for hit in collect_quest_archive_qst_hits(quest_id):
            flag_value = int(hit.flag_value)
            if flag_value <= 0:
                continue
            flag_to_quests.setdefault(flag_value, set()).add(quest_id)
            if hit.flag_kind:
                flag_to_kinds.setdefault(flag_value, set()).add(hit.flag_kind)
            hit_stage_code = str(hit.stage_code or "")
            if hit_stage_code:
                flag_to_stages.setdefault(flag_value, set()).add(hit_stage_code)

    if corpus_index is not None and json_cache is not None:
        for stage_code in normalized_stage_codes:
            for hit in _collect_stage_layout_hits(stage_code, corpus_index=corpus_index, json_cache=json_cache):
                flag_value = int(hit.flag_value)
                if flag_value <= 0:
                    continue
                if int(hit.quest_id or 0) > 0:
                    flag_to_quests.setdefault(flag_value, set()).add(int(hit.quest_id))
                if hit.flag_kind:
                    flag_to_kinds.setdefault(flag_value, set()).add(hit.flag_kind)
                if hit.stage_code:
                    flag_to_stages.setdefault(flag_value, set()).add(hit.stage_code)
                _append_event_viewer_reference(stage_to_event_viewers, hit)
                _append_stage_group_reference(stage_group_references, hit)

    result = {
        "quest_ids": list(normalized_quest_ids),
        "stage_codes": list(normalized_stage_codes),
        "flag_to_quests": {flag_value: sorted(values) for flag_value, values in sorted(flag_to_quests.items())},
        "flag_to_stages": {flag_value: sorted(values) for flag_value, values in sorted(flag_to_stages.items())},
        "flag_to_kinds": {flag_value: sorted(values) for flag_value, values in sorted(flag_to_kinds.items())},
        "stage_to_quests": {stage_code: sorted(values) for stage_code, values in sorted(stage_to_quests.items())},
        "stage_to_event_viewers": {
            stage_code: sorted(entries, key=lambda item: (item.get("event_code", ""), int(item.get("quest_id") or 0), item.get("file_path", "")))
            for stage_code, entries in sorted(stage_to_event_viewers.items())
        },
        "stage_group_references": {
            stage_code: {
                group_no: {
                    "gpl_refs": sorted(group_entry["gpl_refs"], key=lambda item: (int(item.get("flag_value") or 0), int(item.get("quest_id") or 0), item.get("file_path", ""))),
                    "lot_reference": dict(group_entry["lot_reference"]) if isinstance(group_entry.get("lot_reference"), dict) else None,
                }
                for group_no, group_entry in sorted(stage_groups.items())
            }
            for stage_code, stage_groups in sorted(stage_group_references.items())
        },
    }

    if corpus_index is not None and json_cache is not None:
        _REVERSE_INDEX_CACHE[cache_key] = copy.deepcopy(result)
    return result