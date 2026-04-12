"""NLL (NPC Ledger List) and NPC SituationData (SMC/NPC) scanners."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from ..scan_models import (
    FlagHit,
    REL_NPC_CHATTER,
    REL_NPC_FUNCTION,
    REL_NPC_STATE,
)
from ..scan_utils import (
    STAGE_CODE_PATTERN,
    extract_localized,
    match_target as _match_target,
    parse_code,
    to_int,
)


# ---------------------------------------------------------------------------
# Private helpers – NPC/SMC context
# ---------------------------------------------------------------------------

def _describe_smc_asset(rel: str) -> tuple[str, int]:
    name = Path(rel).name
    asset_name = name[:-9] if name.endswith(".smc.json") else Path(rel).stem
    normalized = rel.replace("\\", "/").lower()
    if "/pawn/" in normalized:
        prefix = "PawnChatter"
    elif "/npc/" in normalized:
        prefix = "NpcChatter"
    else:
        prefix = "SituationChatter"

    npc_id = 0
    if asset_name.startswith(("n", "p")) and asset_name[1:].isdigit():
        npc_id = int(asset_name[1:])
    return f"{prefix}={asset_name}", npc_id


def _quest_window_text(
    start_quest_id: int,
    end_quest_id: int,
    start_quest_name_en: str,
    start_quest_name_jp: str,
    end_quest_name_en: str,
    end_quest_name_jp: str,
) -> str:
    start_name = start_quest_name_en or start_quest_name_jp
    end_name = end_quest_name_en or end_quest_name_jp
    if start_quest_id and end_quest_id:
        if start_quest_id == end_quest_id:
            label = start_name or end_name or str(start_quest_id)
            return f"QuestWindow={start_quest_id} ({label})"
        start_label = start_name or str(start_quest_id)
        end_label = end_name or str(end_quest_id)
        return f"QuestWindow={start_quest_id}-{end_quest_id} ({start_label} -> {end_label})"
    if start_quest_id:
        label = start_name or str(start_quest_id)
        return f"QuestStart={start_quest_id} ({label})"
    if end_quest_id:
        label = end_name or str(end_quest_id)
        return f"QuestEnd={end_quest_id} ({label})"
    return ""


def _build_smc_context(
    rel: str,
    group_serial: int,
    start_quest_id: int,
    end_quest_id: int,
    start_quest_name_en: str,
    start_quest_name_jp: str,
    end_quest_name_en: str,
    end_quest_name_jp: str,
    start_is_start: bool,
    end_is_start: bool,
    range_start: int | None,
    range_end: int | None,
) -> tuple[str, str, int]:
    asset_label, npc_id = _describe_smc_asset(rel)
    quest_window = _quest_window_text(
        start_quest_id,
        end_quest_id,
        start_quest_name_en,
        start_quest_name_jp,
        end_quest_name_en,
        end_quest_name_jp,
    )

    comment_parts = [f"GroupSerial={group_serial}"]
    if quest_window:
        comment_parts.append(quest_window)
    comment_parts.append(f"IsStartQuestIdStart={start_is_start}")
    comment_parts.append(f"IsEndQuestIdStart={end_is_start}")

    context_parts = [asset_label, "Quest-gated NPC chatter"]
    if quest_window:
        context_parts.append(quest_window)
    if range_start not in (None, 0) or range_end not in (None, 0):
        context_parts.append(f"QuestFlagRange={range_start or '?'}-{range_end or '?'}")

    return ", ".join(comment_parts), " | ".join(context_parts), npc_id


# ---------------------------------------------------------------------------
# NLL scanner – NPC function unlocks via FunctionOpenList[].FlagNo
# ---------------------------------------------------------------------------

def scan_nll_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ni, npc in enumerate(payload.get("NpcLedgerList", [])):
        if not isinstance(npc, dict):
            continue

        npc_id = to_int(npc.get("NpcId")) or 0
        npc_name_en, npc_name_jp = extract_localized(npc.get("NpcName"))
        npc_class_name_en, _ = extract_localized(npc.get("NpcClassName"))

        for ii, institution in enumerate(npc.get("InstitutionList", [])):
            if not isinstance(institution, dict):
                continue

            function_name_en, function_name_jp = extract_localized(institution.get("FunctionName"))
            function_id_type = str(institution.get("FunctionIdType") or "")

            for oi, open_data in enumerate(institution.get("FunctionOpenList", [])):
                if not isinstance(open_data, dict):
                    continue

                flag_no = to_int(open_data.get("FlagNo"))
                if flag_no is None or flag_no == 0 or not _match_target(flag_no, targets):
                    continue

                type_name = str(open_data.get("TypeName") or "")
                comment_parts: list[str] = []
                if npc_id:
                    comment_parts.append(f"NpcId={npc_id}")
                if type_name:
                    comment_parts.append(type_name)

                context_parts: list[str] = []
                npc_label = npc_name_en or npc_name_jp or npc_class_name_en
                if npc_label:
                    context_parts.append(npc_label)
                function_label = function_name_en or function_name_jp or function_id_type
                if function_label:
                    context_parts.append(function_label)

                yield FlagHit(
                    source_type="nll", file_path=rel,
                    json_path=f"NpcLedgerList[{ni}].InstitutionList[{ii}].FunctionOpenList[{oi}].FlagNo",
                    field_name="FlagNo", flag_value=flag_no,
                    flag_kind="quest_flag", relationship=REL_NPC_FUNCTION,
                    npc_id=npc_id,
                    npc_name=npc_name_en,
                    npc_name_jp=npc_name_jp,
                    function_name=function_name_en,
                    function_name_jp=function_name_jp,
                    comment=", ".join(comment_parts),
                    context=" -> ".join(context_parts),
                )


# ---------------------------------------------------------------------------
# NPC SituationData scanner – RangeStartQuestFlag / RangeEndQuestFlag
# ---------------------------------------------------------------------------

def _iter_situation_data(node: Any) -> Iterator[dict[str, Any]]:
    """Recursively find all SituationData dicts within NPC data."""
    if isinstance(node, dict):
        # Check if this dict looks like SituationData
        if "GroupSerial" in node and ("StartQuestId" in node or "RangeStartQuestFlag" in node):
            yield node
        for v in node.values():
            yield from _iter_situation_data(v)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_situation_data(item)


def scan_npc_situation_data(_path: Path, payload: Any, rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)
    source_type = "smc" if rel.endswith(".smc.json") else "npc"
    relationship = REL_NPC_CHATTER if source_type == "smc" else REL_NPC_STATE

    for sd in _iter_situation_data(payload):
        group_serial = to_int(sd.get("GroupSerial")) or 0
        start_quest_id = to_int(sd.get("StartQuestId")) or 0
        end_quest_id = to_int(sd.get("EndQuestId")) or 0
        start_is_start = bool(sd.get("IsStartQuestIdStart"))
        end_is_start = bool(sd.get("IsEndQuestIdStart"))
        start_quest_name_en, start_quest_name_jp = extract_localized(sd.get("StartQuestName"))
        end_quest_name_en, end_quest_name_jp = extract_localized(sd.get("EndQuestName"))

        range_start = to_int(sd.get("RangeStartQuestFlag"))
        range_end = to_int(sd.get("RangeEndQuestFlag"))
        comment, context, npc_id = _build_smc_context(
            rel,
            group_serial,
            start_quest_id,
            end_quest_id,
            start_quest_name_en,
            start_quest_name_jp,
            end_quest_name_en,
            end_quest_name_jp,
            start_is_start,
            end_is_start,
            range_start,
            range_end,
        )

        if range_start is not None and range_start != 0 and _match_target(range_start, targets):
            yield FlagHit(
                source_type=source_type, file_path=rel,
                json_path="SituationData.RangeStartQuestFlag",
                field_name="RangeStartQuestFlag", flag_value=range_start,
                flag_kind="quest_flag", relationship=relationship,
                quest_id=start_quest_id,
                quest_name=start_quest_name_en, quest_name_jp=start_quest_name_jp,
                stage_code=stage_code,
                group_serial=group_serial,
                npc_id=npc_id,
                comment=f"{comment}, chatter flag range start",
                context=context,
            )

        if range_end is not None and range_end != 0 and _match_target(range_end, targets):
            yield FlagHit(
                source_type=source_type, file_path=rel,
                json_path="SituationData.RangeEndQuestFlag",
                field_name="RangeEndQuestFlag", flag_value=range_end,
                flag_kind="quest_flag", relationship=relationship,
                quest_id=end_quest_id,
                quest_name=end_quest_name_en, quest_name_jp=end_quest_name_jp,
                stage_code=stage_code,
                group_serial=group_serial,
                npc_id=npc_id,
                comment=f"{comment}, chatter flag range end",
                context=context,
            )

        # StartQuestId / EndQuestId as targets
        if start_quest_id and _match_target(start_quest_id, targets):
            yield FlagHit(
                source_type=source_type, file_path=rel,
                json_path="SituationData.StartQuestId",
                field_name="StartQuestId", flag_value=start_quest_id,
                flag_kind="quest_id", relationship=relationship,
                quest_id=start_quest_id,
                quest_name=start_quest_name_en, quest_name_jp=start_quest_name_jp,
                stage_code=stage_code,
                group_serial=group_serial,
                npc_id=npc_id,
                comment=f"{comment}, chatter window start",
                context=context,
            )
        if end_quest_id and _match_target(end_quest_id, targets):
            yield FlagHit(
                source_type=source_type, file_path=rel,
                json_path="SituationData.EndQuestId",
                field_name="EndQuestId", flag_value=end_quest_id,
                flag_kind="quest_id", relationship=relationship,
                quest_id=end_quest_id,
                quest_name=end_quest_name_en, quest_name_jp=end_quest_name_jp,
                stage_code=stage_code,
                group_serial=group_serial,
                npc_id=npc_id,
                comment=f"{comment}, chatter window end",
                context=context,
            )
