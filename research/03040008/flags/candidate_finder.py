"""Residual decoded-data candidate search for unresolved target values."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from derivation import DerivationClass
from scan_utils import extract_localized, load_json, relative_path, to_int

if TYPE_CHECKING:
    from corpus_index import CorpusIndex
    from json_cache import JsonCache


FLAG_KEYS = {
    "Flag",
    "FlagId",
    "FlagNo",
    "QuestFlag",
    "BlockQuestFlag",
    "RangeStartQuestFlag",
    "RangeEndQuestFlag",
}
LAYOUT_KEYS = {"LayoutFlagId", "LayoutFlagNo", "Condition", "EraseCondition"}
QUEST_KEYS = {"QuestId", "QuestID", "QuestNo", "TextQuestNo", "BlockQuestID", "StartQuestId", "EndQuestId"}
SERIAL_KEYS = {"GroupSerial", "MsgSerial", "JumpGroupSerial", "GroupNameSerial"}
COLLISION_KEYS = {"NpcId", "UniqueId", "GroupNo", "EvidenceId", "FunctionParam"}


def _is_numeric_target(value: Any, targets: set[int]) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value in targets:
        return value
    if isinstance(value, float) and value.is_integer() and int(value) in targets:
        return int(value)
    return None


def _extract_context(node: dict[str, Any]) -> dict[str, Any]:
    quest_id = node.get("QuestId") if isinstance(node.get("QuestId"), int) else node.get("QuestID")
    if not isinstance(quest_id, int):
        quest_id = node.get("QuestNo") if isinstance(node.get("QuestNo"), int) else 0
    quest_name_en, quest_name_jp = extract_localized(node.get("QuestName"))
    stage_name_en, stage_name_jp = extract_localized(node.get("StageName"))
    npc_name_en, npc_name_jp = extract_localized(node.get("NpcName"))
    function_name_en, function_name_jp = extract_localized(node.get("FunctionName"))
    evidence_name_en, evidence_name_jp = extract_localized(node.get("EvidenceName"))
    comment = str(node.get("Comment") or "")
    group_serial = node.get("GroupSerial") if isinstance(node.get("GroupSerial"), int) else 0
    msg_serial = node.get("MsgSerial") if isinstance(node.get("MsgSerial"), int) else 0
    message_en, message_jp = extract_localized(node.get("Message"))
    return {
        "quest_id": quest_id or 0,
        "quest_name": quest_name_en,
        "quest_name_jp": quest_name_jp,
        "stage_name": stage_name_en,
        "stage_name_jp": stage_name_jp,
        "npc_name": npc_name_en,
        "npc_name_jp": npc_name_jp,
        "function_name": function_name_en,
        "function_name_jp": function_name_jp,
        "evidence_name": evidence_name_en,
        "evidence_name_jp": evidence_name_jp,
        "comment": comment,
        "group_serial": group_serial,
        "msg_serial": msg_serial,
        "message_excerpt": (message_en or message_jp).splitlines()[0] if (message_en or message_jp) else "",
        "class_name": str(node.get("@class") or ""),
    }


def _classify_candidate(field_name: str, file_path: str, target_kind: str) -> tuple[str, int, str]:
    lower_path = file_path.lower()
    if field_name in SERIAL_KEYS or field_name in COLLISION_KEYS:
        return "collision", 20, f"Matched a collision-prone numeric field ({field_name})."
    if lower_path.endswith(".fsm.json") and field_name in FLAG_KEYS | LAYOUT_KEYS:
        return "opaque_fsm", 65, "Matched a decoded FSM field, but authored semantics remain opaque without deeper correlation."
    if target_kind == "layout_flag" and field_name in LAYOUT_KEYS:
        return "candidate", 82, f"Matched a layout-oriented field ({field_name}) in decoded client JSON."
    if target_kind == "quest_flag" and field_name in FLAG_KEYS:
        return "candidate", 82, f"Matched a quest-flag-oriented field ({field_name}) in decoded client JSON."
    if field_name in FLAG_KEYS | LAYOUT_KEYS | QUEST_KEYS:
        return "context", 45, f"Matched a relevant decoded field ({field_name}), but not in the primary field family for this target type."
    return "context", 30, f"Matched decoded numeric data in field {field_name}."


def _walk_candidates(
    node: Any,
    targets: set[int],
    target_kinds: dict[int, str],
    file_path: str,
    json_path: str,
    current_context: dict[str, Any],
    results: list[dict[str, Any]],
) -> None:
    if isinstance(node, dict):
        next_context = dict(current_context)
        next_context.update({k: v for k, v in _extract_context(node).items() if v})
        for key, value in node.items():
            next_path = f"{json_path}.{key}" if json_path else key
            matched_value = _is_numeric_target(value, targets)
            if matched_value is not None:
                tier, score, why = _classify_candidate(key, file_path, target_kinds.get(matched_value, "quest_flag"))
                if tier == "context" and key not in FLAG_KEYS | LAYOUT_KEYS | QUEST_KEYS | SERIAL_KEYS | COLLISION_KEYS:
                    continue
                results.append(
                    {
                        "flag_value": matched_value,
                        "field_name": key,
                        "file_path": file_path,
                        "json_path": next_path,
                        "resource_family": Path(file_path).suffixes[-2] if len(Path(file_path).suffixes) >= 2 else Path(file_path).suffix,
                        "evidence_tier": tier,
                        "derivation_class": DerivationClass.LOWER_CONFIDENCE.value,
                        "confidence": score,
                        "why": why,
                        **next_context,
                    }
                )
            _walk_candidates(value, targets, target_kinds, file_path, next_path, next_context, results)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            next_path = f"{json_path}[{index}]"
            _walk_candidates(item, targets, target_kinds, file_path, next_path, current_context, results)


def collect_candidate_json_hits(
    ddon_data_root: Path,
    target_kinds: dict[int, str],
    *,
    corpus_index: "CorpusIndex | None" = None,
    json_cache: "JsonCache | None" = None,
) -> dict[int, list[dict[str, Any]]]:
    """Search decoded JSON for unresolved target values.

    When *corpus_index* and *json_cache* are provided, avoid repeated
    ``rglob`` and disk I/O.
    """
    client_root = ddon_data_root / "client" / "03040008"
    targets = set(target_kinds)
    by_value: dict[int, list[dict[str, Any]]] = {value: [] for value in sorted(targets)}
    if not client_root.exists() or not targets:
        return by_value

    # Determine which files to walk.
    if corpus_index is not None:
        json_paths = list(corpus_index.all_json_paths())
    else:
        json_paths = list(client_root.rglob("*.json"))

    for json_path in json_paths:
        if json_cache is not None:
            payload = json_cache.load(json_path)
        else:
            payload = load_json(json_path)
        if payload is None:
            continue
        rel = relative_path(json_path, ddon_data_root)
        hits: list[dict[str, Any]] = []
        _walk_candidates(payload, targets, target_kinds, rel, "", {}, hits)
        for hit in hits:
            value = int(hit["flag_value"])
            by_value.setdefault(value, []).append(hit)

    for value, hits in by_value.items():
        hits.sort(key=lambda item: (-int(item["confidence"]), str(item["file_path"]), str(item["json_path"])))
    return by_value
