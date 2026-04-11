"""GPL (Layout Group Params) and LOT (Stage Layout) scanners."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from scan_models import (
    FlagHit,
    REL_BLOCK_QUEST,
    REL_DOOR_GATE,
    REL_LAYOUT_GUARD,
    REL_QUEST_OM,
    REL_TEXT_QUEST,
    REL_WARP_GATE,
)
from scan_utils import (
    STAGE_CODE_PATTERN,
    build_location_context,
    extract_localized,
    match_target as _match_target,
    parse_code,
    to_int,
)
from source_metadata import resolve_lot_group_association, resolve_stage

from handlers._helpers import _build_qst_info_om_summary


# ---------------------------------------------------------------------------
# Private helpers – GPL
# ---------------------------------------------------------------------------

def _build_gpl_context(stage_code: str, group: dict[str, Any], group_index: int) -> str:
    parts = [f"GroupParam[{group_index}]"]
    data_common = group.get("DataCommon")
    group_no = None
    if isinstance(data_common, dict):
        group_no = to_int(data_common.get("Group"))
        if group_no is not None:
            parts.append(f"DataCommon.Group={group_no}")

    layout_areas: set[int] = set()
    layout_ref_count = 0
    for row in group.get("LayoutIdArray", []):
        if not isinstance(row, dict):
            continue
        layout_id = row.get("LayoutID")
        if not isinstance(layout_id, dict):
            continue
        area = to_int(layout_id.get("Area"))
        if area is not None:
            layout_areas.add(area)
        layout_ref_count += 1
    if layout_areas:
        preview = ", ".join(str(value) for value in sorted(layout_areas)[:3])
        if len(layout_areas) > 3:
            preview += f" +{len(layout_areas) - 3}"
        parts.append(f"LayoutAreas={preview}")
    if layout_ref_count:
        parts.append(f"LayoutRefs={layout_ref_count}")

    if group_no not in (None, 0):
        lot_association = resolve_lot_group_association(stage_code, group_no)
        if lot_association:
            lot_file_name = str(lot_association.get("file_name") or "")
            if lot_file_name:
                parts.append(f"LikelyLOT={lot_file_name}")
            elif lot_association.get("match_count"):
                parts.append(f"LikelyLOTMatches={lot_association['match_count']}")
            type_names = lot_association.get("type_names") or []
            if type_names:
                preview = ", ".join(type_names[:2])
                if len(type_names) > 2:
                    preview += f" +{len(type_names) - 2}"
                parts.append(f"LotTypes={preview}")
            warp_destinations = lot_association.get("warp_destinations") or []
            if warp_destinations:
                parts.append(f"WarpDest={warp_destinations[0].replace(' | ', ' / ')}")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Private helpers – LOT
# ---------------------------------------------------------------------------

def _lot_destination_context(info: dict[str, Any], index: int) -> str:
    parts: list[str] = []

    stage_numbers = info.get("StageNo")
    if isinstance(stage_numbers, list) and index < len(stage_numbers):
        destination_stage_no = to_int(stage_numbers[index]) or 0
        if destination_stage_no:
            _, stage_name_en, stage_name_jp = resolve_stage(stage_no=destination_stage_no)
            stage_names = info.get("StageNames")
            if isinstance(stage_names, list) and index < len(stage_names):
                local_stage_name_en, local_stage_name_jp = extract_localized(stage_names[index])
                stage_name_en = local_stage_name_en or stage_name_en
                stage_name_jp = local_stage_name_jp or stage_name_jp
            destination_label = stage_name_en or stage_name_jp or f"st{destination_stage_no:04d}"
            parts.append(f"Destination st{destination_stage_no:04d} {destination_label}".strip())

    spot_names = info.get("SpotNames")
    if isinstance(spot_names, list) and index < len(spot_names):
        spot_name_en, spot_name_jp = extract_localized(spot_names[index])
        spot_label = spot_name_en or spot_name_jp
        if spot_label:
            parts.append(f"Spot {spot_label}")

    start_positions = info.get("StartPosNo")
    if isinstance(start_positions, list) and index < len(start_positions):
        start_pos = to_int(start_positions[index])
        if start_pos is not None:
            parts.append(f"StartPos={start_pos}")

    return " | ".join(parts)


def _build_lot_object_context(type_name: str, info: dict[str, Any]) -> str:
    parts = [type_name] if type_name else []
    info_om = None
    if isinstance(info.get("InfoOm"), dict):
        info_om = info.get("InfoOm")
    elif isinstance(info.get("InfoCoord"), dict):
        info_om = info
    info_coord = info_om.get("InfoCoord") if isinstance(info_om, dict) else None
    if isinstance(info_coord, dict):
        om_name = str(info_coord.get("Name") or "")
        if om_name:
            parts.append(om_name)
    if isinstance(info_om, dict):
        info_om_summary = _build_qst_info_om_summary(info_om)
        if info_om_summary:
            parts.append(info_om_summary)
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# GPL scanner -- GroupParamBuff -> GuardData.LayoutFlagNo / DataLotFlag.LotFlagNo
# ---------------------------------------------------------------------------

def scan_gpl_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    stage_name_en, stage_name_jp = extract_localized(payload.get("StageName"))
    area_name_en, area_name_jp = extract_localized(payload.get("AreaName"))
    stage_no = to_int(payload.get("StageNo")) or 0
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)

    for gi, group in enumerate(payload.get("GroupParamBuff", [])):
        if not isinstance(group, dict):
            continue
        group_context = _build_gpl_context(stage_code, group, gi)
        guard = group.get("GuardData", {})
        if isinstance(guard, dict):
            layout_flag = to_int(guard.get("LayoutFlagNo"))
            quest_no = to_int(guard.get("QuestNo")) or 0
            quest_name_en, quest_name_jp = extract_localized(guard.get("QuestName"))
            if layout_flag and layout_flag != 0 and _match_target(layout_flag, targets):
                yield FlagHit(
                    source_type="gpl", file_path=rel,
                    json_path=f"GroupParamBuff[{gi}].GuardData.LayoutFlagNo",
                    field_name="LayoutFlagNo", flag_value=layout_flag,
                    flag_kind="layout_flag",
                    relationship=REL_LAYOUT_GUARD,
                    quest_id=quest_no,
                    quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                    stage_no=stage_no,
                    stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                    area_name=area_name_en, area_name_jp=area_name_jp,
                    stage_code=stage_code,
                    context=group_context,
                )
        lot_flag_data = group.get("DataLotFlag", {})
        if isinstance(lot_flag_data, dict):
            lot_flag = to_int(lot_flag_data.get("LotFlagNo"))
            quest_no = to_int((guard if isinstance(guard, dict) else {}).get("QuestNo")) or 0
            if lot_flag and lot_flag != 0 and _match_target(lot_flag, targets):
                yield FlagHit(
                    source_type="gpl", file_path=rel,
                    json_path=f"GroupParamBuff[{gi}].DataLotFlag.LotFlagNo",
                    field_name="LotFlagNo", flag_value=lot_flag,
                    flag_kind="quest_flag",
                    relationship=REL_LAYOUT_GUARD,
                    quest_id=quest_no,
                    stage_no=stage_no,
                    stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                    area_name=area_name_en, area_name_jp=area_name_jp,
                    stage_code=stage_code,
                    context=group_context,
                )


# ---------------------------------------------------------------------------
# LOT scanner -- deep scan of Array[].Info for ALL SetInfoOm* subtypes
# ---------------------------------------------------------------------------

def scan_lot_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    stage_no = to_int(payload.get("StageNo")) or 0
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)
    stage_name_en, stage_name_jp = extract_localized(payload.get("StageName"))
    area_name_en, area_name_jp = extract_localized(payload.get("AreaName"))

    common: dict[str, Any] = build_location_context(
        stage_no=stage_no,
        stage_name=stage_name_en,
        stage_name_jp=stage_name_jp,
        area_name=area_name_en,
        area_name_jp=area_name_jp,
        stage_code=stage_code,
    )

    for ai, entry in enumerate(payload.get("Array", [])):
        if not isinstance(entry, dict):
            continue
        info = entry.get("Info", {})
        if not isinstance(info, dict):
            continue
        type_name = entry.get("TypeName", "")
        context_str = _build_lot_object_context(type_name, info)

        # --- Scalar QuestFlag (SetInfoOmOld, SetInfoOmDoor, etc.) ---
        quest_flag = to_int(info.get("QuestFlag"))
        if quest_flag and quest_flag != 0 and _match_target(quest_flag, targets):
            quest_id = to_int(info.get("QuestID")) or to_int(info.get("QuestId")) or 0
            rel_type = REL_DOOR_GATE if "Door" in type_name else REL_QUEST_OM
            yield FlagHit(
                source_type="lot", file_path=rel,
                json_path=f"Array[{ai}].Info.QuestFlag",
                field_name="QuestFlag", flag_value=quest_flag,
                flag_kind="quest_flag", relationship=rel_type,
                quest_id=quest_id, context=context_str, **common,
            )

        # --- Scalar QuestId / QuestID (on doors, ctrls, bowl-of-life, etc.) ---
        for qf in ("QuestId", "QuestID"):
            q_val = to_int(info.get(qf))
            if q_val and q_val != 0 and _match_target(q_val, targets):
                rel_type = REL_DOOR_GATE if "Door" in type_name else REL_QUEST_OM
                yield FlagHit(
                    source_type="lot", file_path=rel,
                    json_path=f"Array[{ai}].Info.{qf}",
                    field_name=qf, flag_value=q_val,
                    flag_kind="quest_id", relationship=rel_type,
                    quest_id=q_val, context=context_str, **common,
                )

        # --- TextQuestNo (on warps, doors, text OMs) ---
        text_quest = to_int(info.get("TextQuestNo"))
        if text_quest and text_quest != 0 and _match_target(text_quest, targets):
            yield FlagHit(
                source_type="lot", file_path=rel,
                json_path=f"Array[{ai}].Info.TextQuestNo",
                field_name="TextQuestNo", flag_value=text_quest,
                flag_kind="quest_id", relationship=REL_TEXT_QUEST,
                quest_id=text_quest, context=context_str, **common,
            )

        # --- BlockQuestID / BlockQuestFlag (Volcano, HugeRimShl) ---
        block_quest_id = to_int(info.get("BlockQuestID"))
        block_quest_flag = to_int(info.get("BlockQuestFlag"))
        if block_quest_flag and block_quest_flag != 0 and _match_target(block_quest_flag, targets):
            yield FlagHit(
                source_type="lot", file_path=rel,
                json_path=f"Array[{ai}].Info.BlockQuestFlag",
                field_name="BlockQuestFlag", flag_value=block_quest_flag,
                flag_kind="quest_flag", relationship=REL_BLOCK_QUEST,
                quest_id=block_quest_id or 0, context=context_str, **common,
            )
        if block_quest_id and block_quest_id != 0 and _match_target(block_quest_id, targets):
            yield FlagHit(
                source_type="lot", file_path=rel,
                json_path=f"Array[{ai}].Info.BlockQuestID",
                field_name="BlockQuestID", flag_value=block_quest_id,
                flag_kind="quest_id", relationship=REL_BLOCK_QUEST,
                quest_id=block_quest_id, context=context_str, **common,
            )

        # --- OpenFlag (boolean, not a target but context marker) ---
        # We skip boolean fields as they are not numeric targets.

        # --- FlagNo[] array (warps of all kinds) ---
        flag_nos = info.get("FlagNo", [])
        quest_ids_list = info.get("QuestId", info.get("QuestID", []))
        if isinstance(flag_nos, list):
            if not isinstance(quest_ids_list, list):
                quest_ids_list = []
            for fi, fv_raw in enumerate(flag_nos):
                fv = to_int(fv_raw)
                if fv is None or fv == 0 or not _match_target(fv, targets):
                    continue
                q_id = to_int(quest_ids_list[fi]) if fi < len(quest_ids_list) else 0
                destination_context = _lot_destination_context(info, fi)
                context = context_str
                if destination_context:
                    context = f"{context_str} | {destination_context}" if context_str else destination_context
                yield FlagHit(
                    source_type="lot", file_path=rel,
                    json_path=f"Array[{ai}].Info.FlagNo[{fi}]",
                    field_name="FlagNo", flag_value=fv,
                    flag_kind="quest_flag", relationship=REL_WARP_GATE,
                    quest_id=q_id or 0, context=context, **common,
                )

        # --- QuestId[] array (paired with FlagNo[] on warps) ---
        if isinstance(quest_ids_list, list):
            for qi, q_raw in enumerate(quest_ids_list):
                q_val = to_int(q_raw)
                if q_val is None or q_val == 0 or not _match_target(q_val, targets):
                    continue
                destination_context = _lot_destination_context(info, qi)
                context = context_str
                if destination_context:
                    context = f"{context_str} | {destination_context}" if context_str else destination_context
                yield FlagHit(
                    source_type="lot", file_path=rel,
                    json_path=f"Array[{ai}].Info.QuestId[{qi}]",
                    field_name="QuestId", flag_value=q_val,
                    flag_kind="quest_id", relationship=REL_WARP_GATE,
                    quest_id=q_val, context=context, **common,
                )
