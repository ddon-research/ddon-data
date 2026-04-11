"""Family-specific handlers for decoded client JSON scanning."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from scan_models import (
    FlagHit,
    REL_BLOCK_QUEST,
    REL_DOOR_GATE,
    REL_EVIDENCE_FLAG,
    REL_EVENT_PARAM,
    REL_EVENT_STATE,
    REL_FIELD_ADJOIN,
    REL_FSM_CHECK,
    REL_FSM_FREE_FLAG,
    REL_FSM_SET,
    REL_JOB_MASTER,
    REL_LAYOUT_GUARD,
    REL_MARKER_GATE,
    REL_NPC_CHATTER,
    REL_NPC_FUNCTION,
    REL_NPC_STATE,
    REL_QUEST_CONDITION,
    REL_QUEST_ERASE,
    REL_QUEST_OM,
    REL_REPEATABLE_SORTIE,
    REL_SPOT_BLOCK,
    REL_TEXT_QUEST,
    REL_TUTORIAL_GROUP,
    REL_TUTORIAL_QUEST,
    REL_WARP_GATE,
)
from scan_utils import (
    EVENT_CODE_PATTERN,
    STAGE_CODE_PATTERN,
    build_location_context,
    extract_localized,
    match_target as _match_target,
    parse_code,
    parse_quest_id_from_path,
    to_int,
)
from source_metadata import (
    describe_marker_asset,
    describe_fsm_asset,
    resolve_event_view,
    resolve_item_name,
    resolve_lot_group_association,
    resolve_marker_lot_association,
    resolve_stage,
)


def _append_item_part(parts: list[str], label: str, value: Any) -> None:
    item_id = to_int(value)
    if item_id in (None, 0):
        return
    assert item_id is not None
    item_name_en, item_name_jp = resolve_item_name(item_id)
    item_name = item_name_en or item_name_jp
    if item_name:
        parts.append(f"{label}={item_id} ({item_name})")
    else:
        parts.append(f"{label}={item_id}")


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


def _extract_marker_position(info: dict[str, Any]) -> tuple[float, float, float] | None:
    pos = info.get("Pos")
    if not isinstance(pos, dict):
        return None
    x = pos.get("X")
    y = pos.get("Y")
    z = pos.get("Z")
    if not all(isinstance(component, (int, float)) for component in (x, y, z)):
        return None
    assert isinstance(x, (int, float))
    assert isinstance(y, (int, float))
    assert isinstance(z, (int, float))
    return float(x), float(y), float(z)


def _format_marker_position(position: tuple[float, float, float]) -> str:
    return f"({position[0]:.1f},{position[1]:.1f},{position[2]:.1f})"


def _build_marker_context(stage_code: str, info: dict[str, Any], marker_meta: dict[str, str]) -> str:
    parts: list[str] = []
    marker_type = marker_meta.get("marker_type")
    if marker_type:
        parts.append(f"MarkerType={marker_type}")
    marker_scope = marker_meta.get("marker_scope")
    if marker_scope:
        parts.append(f"MarkerScope={marker_scope}")
    asset_name = marker_meta.get("asset_name")
    if asset_name:
        parts.append(f"MarkerAsset={asset_name}")

    group_no = to_int(info.get("GroupNo"))
    if group_no not in (None, 0):
        parts.append(f"MarkerGroup={group_no}")

    marker_position = _extract_marker_position(info)
    if marker_position is not None:
        parts.append(f"MarkerPos={_format_marker_position(marker_position)}")

    unique_id = to_int(info.get("UniqueId"))
    if unique_id not in (None, 0):
        parts.append(f"MarkerUniqueId={unique_id}")

    marker_kind = marker_meta.get("marker_kind") or ""
    if stage_code and marker_kind and group_no not in (None, 0):
        assert group_no is not None
        marker_lot = resolve_marker_lot_association(stage_code, marker_kind, group_no, marker_position)
        if marker_lot:
            lot_file_name = str(marker_lot.get("file_name") or "")
            if lot_file_name:
                parts.append(f"LikelyLOT={lot_file_name}")
            type_names = marker_lot.get("type_names") or []
            if type_names:
                preview = ", ".join(type_names[:2])
                if len(type_names) > 2:
                    preview += f" +{len(type_names) - 2}"
                parts.append(f"LotTypes={preview}")
            nearest_label = str(marker_lot.get("nearest_label") or "")
            if nearest_label:
                nearest_distance = marker_lot.get("nearest_distance")
                if isinstance(nearest_distance, (int, float)):
                    parts.append(f"NearestLot={nearest_label} d={nearest_distance:.1f}")
                else:
                    parts.append(f"NearestLot={nearest_label}")
    return " | ".join(parts)


def _strip_class_name(value: Any) -> str:
    text = str(value or "")
    return text.rsplit(".", 1)[-1] if text else ""


def _append_nonzero_part(parts: list[str], label: str, value: Any) -> None:
    numeric_value = to_int(value)
    if numeric_value not in (None, 0):
        parts.append(f"{label}={numeric_value}")


def _resolve_stage_name_fields(row: dict[str, Any]) -> tuple[int, str, str]:
    for suffix in ("3", "1", "2"):
        stage_no = to_int(row.get(f"StageNo{suffix}")) or 0
        stage_name_en, stage_name_jp = extract_localized(row.get(f"StageName{suffix}"))
        if stage_no or stage_name_en or stage_name_jp:
            return stage_no, stage_name_en, stage_name_jp
    return 0, "", ""


def _build_stage_route_context(row: dict[str, Any]) -> str:
    route_parts: list[str] = []
    for suffix in ("1", "2", "3"):
        stage_no = to_int(row.get(f"StageNo{suffix}")) or 0
        stage_name_en, stage_name_jp = extract_localized(row.get(f"StageName{suffix}"))
        if stage_no == 0 and not stage_name_en and not stage_name_jp:
            continue
        stage_label = stage_name_en or stage_name_jp or f"st{stage_no:04d}"
        route_parts.append(f"st{stage_no:04d} {stage_label}" if stage_no else stage_label)
    return " -> ".join(route_parts)


def _build_repeatable_sortie_context(row: dict[str, Any]) -> str:
    parts: list[str] = []
    stage_route = _build_stage_route_context(row)
    if stage_route:
        parts.append(f"SortieRoute={stage_route}")
    unknown1 = to_int(row.get("Unknown1"))
    unknown2 = to_int(row.get("Unknown2"))
    if unknown1 not in (None, 0):
        parts.append(f"Unknown1={unknown1}")
    if unknown2 not in (None, 0):
        parts.append(f"Unknown2={unknown2}")
    if row.get("Unknown3"):
        parts.append("Unknown3=True")
    cycle_no = to_int(row.get("CycleNo"))
    cycle_sub_no = to_int(row.get("CycleSubNo"))
    if cycle_no not in (None, 0):
        parts.append(f"CycleNo={cycle_no}")
    if cycle_sub_no not in (None, 0):
        parts.append(f"CycleSubNo={cycle_sub_no}")
    return " | ".join(parts)


def _build_evidence_context(evidence: dict[str, Any]) -> tuple[str, str]:
    step = to_int(evidence.get("Step")) or 0
    evidence_id = to_int(evidence.get("EvidenceId")) or 0
    evidence_type = str(evidence.get("EvidenceType") or "")
    evidence_name_en, evidence_name_jp = extract_localized(evidence.get("EvidenceName"))
    evidence_info_en, evidence_info_jp = extract_localized(evidence.get("EvidenceInfo"))
    evidence_name = evidence_name_en or evidence_name_jp
    evidence_info = evidence_info_en or evidence_info_jp
    context_parts = [evidence_name or "Evidence entry", "Season3SubstoryEvidence"]
    if evidence_type:
        context_parts.append(f"EvidenceType={evidence_type}")
    if evidence_info:
        context_parts.append(evidence_info.splitlines()[0])
    step_comment = f"Step={step}"
    if evidence_id:
        step_comment += f", EvidenceId={evidence_id}"
    return " | ".join(part for part in context_parts if part), step_comment


def _build_jmc_context(row: dict[str, Any]) -> tuple[str, str, str, str]:
    job_name_en, job_name_jp = extract_localized(row.get("JobName"))
    area_name_en, area_name_jp = extract_localized(row.get("AreaName"))
    start_job_level = to_int(row.get("StartJobLevel")) or 0
    context_parts = []
    if job_name_en or job_name_jp:
        context_parts.append(job_name_en or job_name_jp)
    if area_name_en or area_name_jp:
        context_parts.append(area_name_en or area_name_jp)
    if start_job_level:
        context_parts.append(f"StartJobLevel={start_job_level}")
    return " | ".join(context_parts), area_name_en, area_name_jp, f"JobId={to_int(row.get('JobId')) or 0}"


def _iter_jmc_quest_fields(row: dict[str, Any]) -> Iterator[tuple[str, str, int, str, str]]:
    for field_name, kind_label in (
        ("JobTutorialQuestId", "Job tutorial quest"),
        ("JobMasterTutorialQuestId", "Job master tutorial quest"),
    ):
        quest_id = to_int(row.get(field_name)) or 0
        if quest_id == 0:
            continue
        quest_name_en, quest_name_jp = extract_localized(row.get(field_name.replace("Id", "Name")))
        yield field_name, kind_label, quest_id, quest_name_en, quest_name_jp


def _build_ams_context(row: dict[str, Any]) -> tuple[str, int]:
    spot_name_en, spot_name_jp = extract_localized(row.get("SpotName"))
    category_name_en, category_name_jp = extract_localized(row.get("CategoryName"))
    spot_id = to_int(row.get("SpotId")) or 0
    recommend_level = to_int(row.get("RecommendLevel")) or 0
    context_parts = ["QuestBlockedSpot"]
    if spot_name_en or spot_name_jp:
        context_parts.append(spot_name_en or spot_name_jp)
    if category_name_en or category_name_jp:
        context_parts.append(category_name_en or category_name_jp)
    if recommend_level:
        context_parts.append(f"RecommendLevel={recommend_level}")
    return " | ".join(context_parts), spot_id


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


def _build_qst_comment(group_no: int, group_comment: str, set_comment: str = "") -> str:
    parts = [f"QuestGroup {group_no}"] if group_no else []
    if group_comment:
        parts.append(group_comment)
    if set_comment and set_comment != group_comment:
        parts.append(set_comment)
    return " | ".join(parts)


def _build_qst_info_om_summary(info_om: dict[str, Any]) -> str:
    parts: list[str] = []
    info_coord = info_om.get("InfoCoord")
    if isinstance(info_coord, dict):
        unit_id_type = str(info_coord.get("UnitIDType") or "")
        info_name = str(info_coord.get("Name") or "")
        if unit_id_type:
            parts.append(unit_id_type)
        elif info_name:
            parts.append(info_name)
        else:
            _append_nonzero_part(parts, "UnitID", info_coord.get("UnitID"))

    for field_name, label in (
        ("IsMyQuest", "MyQuestOnly"),
        ("OpenFlag", "OpenOnCondition"),
        ("EnableZone", "EnableZone"),
        ("IsBreakLink", "BreakLink"),
        ("IsBreakQuest", "BreakQuest"),
        ("DisableEffect", "DisableEffect"),
        ("DisableOnlyEffect", "DisableOnlyEffect"),
    ):
        if info_om.get(field_name):
            parts.append(label)

    _append_item_part(parts, "KeyNo", info_om.get("KeyNo"))
    _append_nonzero_part(parts, "QuestFlag", info_om.get("QuestFlag"))
    _append_nonzero_part(parts, "WarpPointId", info_om.get("WarpPointId"))

    break_group = to_int(info_om.get("BreakGroup"))
    break_id = to_int(info_om.get("BreakID"))
    if break_group not in (None, 0) or break_id not in (None, 0):
        break_kind = to_int(info_om.get("BreakKind")) or 0
        parts.append(f"BreakTarget=kind{break_kind}/group{break_group or 0}/id{break_id or 0}")

    return " | ".join(parts)


def _format_qst_link_kind(link: dict[str, Any]) -> str:
    kind_text = str(link.get("KindType") or "")
    if kind_text.startswith("U_"):
        return kind_text[2:]
    if kind_text:
        return kind_text
    kind_value = to_int(link.get("Kind"))
    if kind_value is not None:
        return f"KIND_{kind_value}"
    return "UNKNOWN"


def _build_qst_ctrl_link_summary(set_info: dict[str, Any]) -> str:
    link_details: list[str] = []
    link_pattern: list[str] = []
    for link in set_info.get("LinkParam", []):
        if not isinstance(link, dict):
            continue
        kind = _format_qst_link_kind(link)
        if kind in {"NONE", "KIND_0"}:
            continue
        detail_parts: list[str] = []
        group_no = to_int(link.get("Group"))
        link_id = to_int(link.get("Id"))
        if group_no not in (None, 0):
            detail_parts.append(f"G{group_no}")
        if link_id not in (None, 0):
            detail_parts.append(f"I{link_id}")
        state = to_int(link.get("State"))
        transition = to_int(link.get("Transition"))
        if state not in (None, 0):
            detail_parts.append(f"S{state}")
        if transition not in (None, 0):
            detail_parts.append(f"T{transition}")
        cam_ev_no = to_int(link.get("CamEvNo"))
        if cam_ev_no is not None and cam_ev_no > 0:
            detail_parts.append(f"CamEvNo={cam_ev_no}")
        fsm_name = str(link.get("Fsm") or "")
        if fsm_name:
            detail_parts.append(f"FSM={fsm_name}")
        link_pattern.append(kind)
        detail = kind
        if detail_parts:
            detail += f"({','.join(detail_parts)})"
        link_details.append(detail)

    parts: list[str] = []
    if link_pattern:
        parts.append(f"LinkPattern={' -> '.join(link_pattern)}")
    if link_details:
        preview = "; ".join(link_details[:3])
        if len(link_details) > 3:
            preview += f" +{len(link_details) - 3}"
        parts.append(f"Links={preview}")
    return " | ".join(parts)


def _build_qst_set_specific_summary(set_info: dict[str, Any], class_name: str) -> str:
    parts: list[str] = []
    if class_name == "QuestSetInfoOmCtrl":
        _append_item_part(parts, "KeyItemNo", set_info.get("KeyItemNo"))
        _append_nonzero_part(parts, "QuestId", set_info.get("QuestId"))
        _append_nonzero_part(parts, "EmHpRate", set_info.get("EmHpRate"))
        add_group_no = to_int(set_info.get("AddGroupNo"))
        if add_group_no not in (None, -1):
            parts.append(f"AddGroupNo={add_group_no}")
        add_sub_group_no = to_int(set_info.get("AddSubGroupNo"))
        if add_sub_group_no not in (None, -1):
            parts.append(f"AddSubGroupNo={add_sub_group_no}")
        if set_info.get("IsQuest"):
            parts.append("QuestScopedCtrl")
        link_summary = _build_qst_ctrl_link_summary(set_info)
        if link_summary:
            parts.append(link_summary)
    elif class_name == "QuestSetInfoOmLever":
        if set_info.get("ReqLever"):
            parts.append("ReqLever")
        cam_ev_no = to_int(set_info.get("CamEvNo"))
        if cam_ev_no is not None and cam_ev_no >= 0:
            parts.append(f"CamEvNo={cam_ev_no}")
        fsm_name = str(set_info.get("Fsm") or set_info.get("FSM") or "")
        if fsm_name:
            parts.append(f"FSM={fsm_name}")
    elif class_name == "QuestSetInfoOmDoor":
        if set_info.get("Prt"):
            parts.append("PRT")
        _append_nonzero_part(parts, "TextNo", set_info.get("TextNo"))
        _append_nonzero_part(parts, "TextType", set_info.get("TextType"))
        _append_nonzero_part(parts, "TextQuestNo", set_info.get("TextQuestNo"))
        _append_nonzero_part(parts, "QuestID", set_info.get("QuestID"))
        _append_nonzero_part(parts, "QuestFlag", set_info.get("QuestFlag"))
    elif class_name in {"QuestSetInfoOmText", "QuestSetInfoOmActText", "QuestSetInfoOmWarp"}:
        _append_nonzero_part(parts, "TextNo", set_info.get("TextNo"))
        _append_nonzero_part(parts, "TextType", set_info.get("TextType"))
        _append_nonzero_part(parts, "TextQuestNo", set_info.get("TextQuestNo"))
        if set_info.get("NoWarp"):
            parts.append("NoWarp")
    return " | ".join(parts)


def _build_qst_set_context(group_no: int, quest_set: dict[str, Any], set_info: dict[str, Any], class_name: str) -> str:
    parts = [f"QuestSet={class_name or 'QuestSet'}"]
    om_id = to_int(quest_set.get("OmID"))
    if om_id not in (None, 0):
        parts.append(f"OmID={om_id}")
    info_om = set_info.get("InfoOm") if isinstance(set_info.get("InfoOm"), dict) else set_info
    if isinstance(info_om, dict):
        info_om_summary = _build_qst_info_om_summary(info_om)
        if info_om_summary:
            parts.append(info_om_summary)
    set_specific = _build_qst_set_specific_summary(set_info, class_name)
    if set_specific:
        parts.append(set_specific)
    if group_no:
        parts.append(f"GroupNo={group_no}")
    return " | ".join(parts)


def _build_qst_group_context(group: dict[str, Any]) -> str:
    group_no = to_int(group.get("GroupNo")) or 0
    summaries: list[str] = []
    for quest_set in group.get("QuestSet", []):
        if not isinstance(quest_set, dict):
            continue
        set_info = quest_set.get("SetInfo")
        if not isinstance(set_info, dict):
            continue
        class_name = _strip_class_name(set_info.get("@class"))
        summaries.append(_build_qst_set_context(group_no, quest_set, set_info, class_name))
    preview = " || ".join(summaries[:2])
    if len(summaries) > 2:
        preview += f" || +{len(summaries) - 2} more"
    return preview


def _build_qst_warp_destination_context(set_info: dict[str, Any], index: int) -> str:
    parts: list[str] = []
    stage_numbers = set_info.get("StageNo")
    if isinstance(stage_numbers, list) and index < len(stage_numbers):
        destination_stage_no = to_int(stage_numbers[index]) or 0
        if destination_stage_no:
            _, stage_name_en, stage_name_jp = resolve_stage(stage_no=destination_stage_no)
            stage_names = set_info.get("StageNames")
            if isinstance(stage_names, list) and index < len(stage_names):
                local_stage_name_en, local_stage_name_jp = extract_localized(stage_names[index])
                stage_name_en = local_stage_name_en or stage_name_en
                stage_name_jp = local_stage_name_jp or stage_name_jp
            destination_label = stage_name_en or stage_name_jp or f"st{destination_stage_no:04d}"
            parts.append(f"Destination st{destination_stage_no:04d} {destination_label}".strip())

    spot_names = set_info.get("SpotNames")
    if isinstance(spot_names, list) and index < len(spot_names):
        spot_name_en, spot_name_jp = extract_localized(spot_names[index])
        spot_label = spot_name_en or spot_name_jp
        if spot_label:
            parts.append(f"Spot {spot_label}")

    start_positions = set_info.get("StartPosNo")
    if isinstance(start_positions, list) and index < len(start_positions):
        start_pos = to_int(start_positions[index])
        if start_pos is not None:
            parts.append(f"StartPos={start_pos}")

    if set_info.get("NoWarp"):
        parts.append("NoWarp")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# QST scanner – QuestStageList → QuestGrp → Condition/EraseCondition
#                                          → QuestSet deep scan
# ---------------------------------------------------------------------------

# Fields on QuestSet sub-objects that contain flag values
_QST_SET_FLAG_FIELDS = {
    "QuestFlag":    ("quest_flag", REL_QUEST_OM),
    "FlagNo":       ("quest_flag", REL_QUEST_OM),
    "LayoutFlagNo": ("layout_flag", REL_LAYOUT_GUARD),
}

# Fields on QuestSet sub-objects that contain quest IDs
_QST_SET_QUEST_FIELDS = {"QuestID", "QuestId", "TextQuestNo"}


def _build_qst_hit_base(
    rel: str,
    quest_id: int,
    stage_no: int,
    stage_name: str,
    stage_name_jp: str,
    stage_code: str,
    comment: str,
    context: str,
) -> dict[str, Any]:
    return {
        "file_path": rel,
        "quest_id": quest_id,
        "stage_no": stage_no,
        "stage_name": stage_name,
        "stage_name_jp": stage_name_jp,
        "stage_code": stage_code,
        "comment": comment,
        "context": context,
    }


def scan_qst_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    quest_id = parse_quest_id_from_path(rel)
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)
    for stage in payload.get("QuestStageList", []):
        if not isinstance(stage, dict):
            continue
        stage_no = to_int(stage.get("StageNo")) or 0
        stage_name_en, stage_name_jp = extract_localized(stage.get("StageName"))
        if not stage_name_en and not stage_name_jp:
            _, stage_name_en, stage_name_jp = resolve_stage(stage_no=stage_no, stage_code=stage_code)
        for gi, group in enumerate(stage.get("QuestGrp", [])):
            if not isinstance(group, dict):
                continue
            group_no = to_int(group.get("GroupNo")) or 0
            comment = (group.get("Comment") or "").strip()
            group_context = _build_qst_group_context(group)

            # ----- Group-level: Condition = layout flag guard -----
            val = to_int(group.get("Condition"))
            if val is not None and val != 0 and _match_target(val, targets):
                yield FlagHit(
                    source_type="qst", file_path=rel,
                    json_path=f"QuestStageList[].QuestGrp[{gi}].Condition",
                    field_name="Condition", flag_value=val,
                    flag_kind="layout_flag", relationship=REL_QUEST_CONDITION,
                    quest_id=quest_id,
                    stage_no=stage_no,
                    stage_name=stage_name_en,
                    stage_name_jp=stage_name_jp,
                    stage_code=stage_code,
                    comment=_build_qst_comment(group_no, comment),
                    context=group_context,
                )

            # ----- Group-level: EraseCondition = erase layout flag -----
            val = to_int(group.get("EraseCondition"))
            if val is not None and val != 0 and _match_target(val, targets):
                yield FlagHit(
                    source_type="qst", file_path=rel,
                    json_path=f"QuestStageList[].QuestGrp[{gi}].EraseCondition",
                    field_name="EraseCondition", flag_value=val,
                    flag_kind="layout_flag", relationship=REL_QUEST_ERASE,
                    quest_id=quest_id,
                    stage_no=stage_no,
                    stage_name=stage_name_en,
                    stage_name_jp=stage_name_jp,
                    stage_code=stage_code,
                    comment=_build_qst_comment(group_no, comment),
                    context=group_context,
                )

            # ----- QuestSet deep scan -----
            for si, qs in enumerate(group.get("QuestSet", [])):
                if not isinstance(qs, dict):
                    continue
                qs_comment = (qs.get("Comment") or "").strip()
                set_info = qs.get("SetInfo")
                if not isinstance(set_info, dict):
                    continue
                class_name = _strip_class_name(set_info.get("@class"))
                combined_comment = _build_qst_comment(group_no, comment, qs_comment)
                qst_context = _build_qst_set_context(group_no, qs, set_info, class_name)

                # Determine relationship from class name
                qs_rel = REL_QUEST_OM
                if "Door" in class_name:
                    qs_rel = REL_DOOR_GATE
                elif "Warp" in class_name:
                    qs_rel = REL_WARP_GATE

                qst_hit_base = _build_qst_hit_base(
                    rel,
                    quest_id,
                    stage_no,
                    stage_name_en,
                    stage_name_jp,
                    stage_code,
                    combined_comment,
                    qst_context,
                )

                # Scan all known fields on the nested SetInfo object.
                yield from _scan_qst_set_entry(
                    set_info,
                    gi,
                    si,
                    qst_hit_base,
                    qs_rel,
                    targets,
                )

                # Also scan nested InfoOm if present (QuestSetInfoOm is embedded under SetInfo)
                info_om = set_info.get("InfoOm")
                if isinstance(info_om, dict):
                    yield from _scan_qst_set_entry(
                        info_om,
                        gi,
                        si,
                        qst_hit_base,
                        qs_rel,
                        targets,
                        json_prefix="InfoOm.",
                    )

                # Scan FlagNo arrays (warp entries)
                flag_nos = set_info.get("FlagNo", [])
                quest_ids_list = set_info.get("QuestId", set_info.get("QuestID", []))
                if isinstance(flag_nos, list):
                    if not isinstance(quest_ids_list, list):
                        quest_ids_list = []
                    for fi, fv_raw in enumerate(flag_nos):
                        fv = to_int(fv_raw)
                        if fv is None or fv == 0 or not _match_target(fv, targets):
                            continue
                        q_id = to_int(quest_ids_list[fi]) if fi < len(quest_ids_list) else 0
                        warp_context = _build_qst_warp_destination_context(set_info, fi)
                        combined_context = qst_context
                        if warp_context:
                            combined_context = f"{qst_context} | {warp_context}" if qst_context else warp_context
                        yield FlagHit(
                            source_type="qst", file_path=rel,
                            json_path=f"QuestStageList[].QuestGrp[{gi}].QuestSet[{si}].SetInfo.FlagNo[{fi}]",
                            field_name="FlagNo", flag_value=fv,
                            flag_kind="quest_flag", relationship=REL_WARP_GATE,
                            quest_id=q_id or quest_id,
                            stage_no=stage_no,
                            stage_name=stage_name_en,
                            stage_name_jp=stage_name_jp,
                            stage_code=stage_code,
                            comment=combined_comment,
                            context=combined_context,
                        )


def _scan_qst_set_entry(
    obj: dict,
    gi: int,
    si: int,
    hit_base: dict[str, Any],
    relationship: str,
    targets: set[int] | None,
    json_prefix: str = "",
) -> Iterator[FlagHit]:
    """Scan a QuestSet entry dict (or its InfoOm sub-dict) for flag/quest fields."""
    quest_name_en, quest_name_jp = extract_localized(obj.get("QuestName"))
    # Scalar flag fields
    for fn, (kind, default_rel) in _QST_SET_FLAG_FIELDS.items():
        val = to_int(obj.get(fn))
        if val is not None and val != 0 and _match_target(val, targets):
            yield FlagHit(
                source_type="qst",
                json_path=f"QuestStageList[].QuestGrp[{gi}].QuestSet[{si}].{json_prefix}{fn}",
                field_name=fn, flag_value=val, flag_kind=kind,
                relationship=relationship if relationship != REL_QUEST_OM else default_rel,
                quest_name=quest_name_en,
                quest_name_jp=quest_name_jp,
                **hit_base,
            )

    # Quest ID fields (treated as quest-id hits, not flag hits)
    for fn in _QST_SET_QUEST_FIELDS:
        val = to_int(obj.get(fn))
        if val is not None and val != 0 and _match_target(val, targets):
            q_rel = REL_TEXT_QUEST if fn == "TextQuestNo" else relationship
            yield FlagHit(
                source_type="qst",
                json_path=f"QuestStageList[].QuestGrp[{gi}].QuestSet[{si}].{json_prefix}{fn}",
                field_name=fn, flag_value=val,
                flag_kind="quest_id",
                relationship=q_rel,
                quest_id=val,
                quest_name=quest_name_en,
                quest_name_jp=quest_name_jp,
                **{k: v for k, v in hit_base.items() if k != "quest_id"},
            )


# ---------------------------------------------------------------------------
# GPL scanner – GroupParamBuff → GuardData.LayoutFlagNo / DataLotFlag.LotFlagNo
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
# LOT scanner – deep scan of Array[].Info for ALL SetInfoOm* subtypes
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


# ---------------------------------------------------------------------------
# FSM scanner – ContainerName-filtered, distinguishes world manage from
#               FSM-local free flags
# ---------------------------------------------------------------------------

# ContainerName → (flag_field, flag_kind, relationship)
_FSM_WORLD_MANAGE_CONTAINERS: dict[str, tuple[str | None, str | None, str]] = {
    "mainqstflagon":     ("FlagNo",       "quest_flag",  REL_FSM_SET),
    "mainqstflagoff":    ("FlagNo",       "quest_flag",  REL_FSM_SET),
    "myqstflagon":       ("FlagNo",       "quest_flag",  REL_FSM_SET),
    "myqstflagoff":      ("FlagNo",       "quest_flag",  REL_FSM_SET),
    "flagquest":         ("FlagNo",       "quest_flag",  REL_FSM_CHECK),
    "ismyquestflag":     ("FlagNo",       "quest_flag",  REL_FSM_CHECK),
    "checkmyquestflag":  ("FlagNo",       "quest_flag",  REL_FSM_CHECK),
    "checklayoutflag":   ("LayoutFlagNo", "layout_flag", REL_FSM_CHECK),
    "setlayout":         ("FlagNo",       "layout_flag", REL_FSM_SET),
    "questinfo":         (None,            None,          REL_FSM_CHECK),
    "setopendoor":       (None,            None,          REL_FSM_SET),
    "callannounce":      (None,            None,          REL_FSM_SET),
    "setdispunit":       (None,            None,          REL_FSM_SET),
    "callmessage":       (None,            None,          REL_FSM_SET),
    "callnpcmessage":    (None,            None,          REL_FSM_SET),
}

# Free flag containers — tracked as fsm_free_flag with low priority
_FSM_FREE_FLAG_CONTAINERS = {"SetFSMFreeFlagOn", "SetFSMFreeFlagOff"}


def _iter_fsm_processes(node: Any) -> Iterator[dict[str, Any]]:
    """Recursively yield all process dicts within the FSM tree."""
    if isinstance(node, dict):
        # If this dict has ContainerName + Parameter, it's a process
        if "ContainerName" in node and "Parameter" in node:
            yield node
        for v in node.values():
            yield from _iter_fsm_processes(v)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_fsm_processes(item)


def scan_fsm_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)
    event_code = parse_code(EVENT_CODE_PATTERN, rel)
    quest_id_from_path = parse_quest_id_from_path(rel)
    fsm_asset_label = describe_fsm_asset(rel)

    for process in _iter_fsm_processes(payload):
        container_name = process.get("ContainerName", "") or ""
        container_key = container_name.lower()
        param = process.get("Parameter")
        if not isinstance(param, dict):
            continue

        quest_id = to_int(param.get("QuestId")) or quest_id_from_path
        quest_name_en, quest_name_jp = extract_localized(param.get("QuestName"))
        context = container_name
        if fsm_asset_label:
            context = f"{context} | {fsm_asset_label}"
        if "NPCFSM=" in fsm_asset_label and quest_id and quest_id == quest_id_from_path:
            context = f"{context} | QuestLocalNPCFSM"

        # --- World-manage flag containers ---
        if container_key in _FSM_WORLD_MANAGE_CONTAINERS:
            flag_field, flag_kind, rel_type = _FSM_WORLD_MANAGE_CONTAINERS[container_key]
            resolved_flag_kind = flag_kind or ""

            # Emit flag hit if the container has a flag field
            if flag_field:
                val = to_int(param.get(flag_field))
                if val is not None and val != 0 and _match_target(val, targets):
                    yield FlagHit(
                        source_type="fsm", file_path=rel,
                        json_path=f"Process.Parameter.{flag_field}",
                        field_name=flag_field, flag_value=val,
                        flag_kind=resolved_flag_kind, relationship=rel_type,
                        quest_id=quest_id,
                        quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                        stage_code=stage_code, event_code=event_code,
                        context=context,
                    )

            # Also emit QuestId as a target if it matches
            q_id_val = to_int(param.get("QuestId"))
            if q_id_val and q_id_val != 0 and _match_target(q_id_val, targets):
                yield FlagHit(
                    source_type="fsm", file_path=rel,
                    json_path="Process.Parameter.QuestId",
                    field_name="QuestId", flag_value=q_id_val,
                    flag_kind="quest_id", relationship=rel_type,
                    quest_id=q_id_val,
                    quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                    stage_code=stage_code, event_code=event_code,
                    context=context,
                )

        # --- Free flag containers (FSM-local, low priority) ---
        elif container_name in _FSM_FREE_FLAG_CONTAINERS:
            val = to_int(param.get("FlagNo"))
            if val is not None and val != 0 and _match_target(val, targets):
                yield FlagHit(
                    source_type="fsm", file_path=rel,
                    json_path="Process.Parameter.FlagNo",
                    field_name="FlagNo", flag_value=val,
                    flag_kind="fsm_free_flag", relationship=REL_FSM_FREE_FLAG,
                    quest_id=quest_id,
                    stage_code=stage_code, event_code=event_code,
                    context=context,
                    comment="FSM-local free flag (not a world manage flag)",
                )

        # --- Unknown containers: still check for LayoutFlagNo / FlagNo with QuestId ---
        else:
            for fn, kind, rel_type in (
                ("FlagNo", "quest_flag", REL_FSM_CHECK),
                ("LayoutFlagNo", "layout_flag", REL_FSM_CHECK),
            ):
                val = to_int(param.get(fn))
                if val is not None and val != 0 and _match_target(val, targets):
                    # Only emit if we also have a QuestId (avoids FSM free flags)
                    pq = to_int(param.get("QuestId"))
                    if pq and pq != 0:
                        yield FlagHit(
                            source_type="fsm", file_path=rel,
                            json_path=f"Process.Parameter.{fn}",
                            field_name=fn, flag_value=val,
                            flag_kind=kind, relationship=rel_type,
                            quest_id=pq,
                            quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                            stage_code=stage_code, event_code=event_code,
                            context=context,
                        )


# ---------------------------------------------------------------------------
# EVSI scanner – FlagArray[].FlagNo / LayoutFlagArray[].FlagNo
# ---------------------------------------------------------------------------

def scan_evsi_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)
    event_code = parse_code(EVENT_CODE_PATTERN, rel)
    stage_no, stage_name_en, stage_name_jp = resolve_stage(stage_code=stage_code)
    event_key, event_name = resolve_event_view(stage_code, event_code)
    context_parts = ["Event Viewer"]
    if event_key:
        context_parts.append(event_key)
    if event_name:
        context_parts.append(event_name)
    event_context = " | ".join(context_parts)

    for array_name, kind in (("FlagArray", "quest_flag"), ("LayoutFlagArray", "layout_flag")):
        entries = payload.get(array_name)
        if not isinstance(entries, list):
            continue
        for ei, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            flag_no = to_int(entry.get("FlagNo"))
            if flag_no is None or not _match_target(flag_no, targets):
                continue
            quest_id = to_int(entry.get("QuestId")) or 0
            quest_name_en, quest_name_jp = extract_localized(entry.get("QuestName"))
            yield FlagHit(
                source_type="evsi", file_path=rel,
                json_path=f"{array_name}[{ei}].FlagNo",
                field_name="FlagNo", flag_value=flag_no, flag_kind=kind,
                relationship=REL_EVENT_STATE,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                stage_no=stage_no,
                stage_name=stage_name_en,
                stage_name_jp=stage_name_jp,
                stage_code=stage_code,
                event_code=event_code,
                context=event_context,
            )


# ---------------------------------------------------------------------------
# QMI/FMI scanner – JumpPosition.FlagId / LayoutFlagId / QuestId
# ---------------------------------------------------------------------------

def scan_qmi_fmi_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    stage_code = parse_code(STAGE_CODE_PATTERN, rel)
    stage_no = to_int(payload.get("StageNo")) or 0
    stage_name_en, stage_name_jp = extract_localized(payload.get("StageName"))
    marker_meta = describe_marker_asset(rel)

    info_list = payload.get("InfoList", [])
    if not isinstance(info_list, list):
        return

    for ii, info in enumerate(info_list):
        if not isinstance(info, dict):
            continue
        marker_context = _build_marker_context(stage_code, info, marker_meta)
        # JumpPosition entries are often nested — scan recursively
        for jp_key in ("JumpPosition", "JumpPosition2"):
            jp_list = info.get(jp_key, [])
            if isinstance(jp_list, dict):
                jp_list = [jp_list]
            if not isinstance(jp_list, list):
                continue
            for ji, jp in enumerate(jp_list):
                if not isinstance(jp, dict):
                    continue
                quest_id = to_int(jp.get("QuestId")) or 0
                quest_name_en, quest_name_jp = extract_localized(jp.get("QuestName"))

                flag_id = to_int(jp.get("FlagId"))
                if flag_id and flag_id != 0 and _match_target(flag_id, targets):
                    yield FlagHit(
                        source_type="qmi", file_path=rel,
                        json_path=f"InfoList[{ii}].{jp_key}[{ji}].FlagId",
                        field_name="FlagId", flag_value=flag_id,
                        flag_kind="quest_flag", relationship=REL_MARKER_GATE,
                        quest_id=quest_id,
                        quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                        stage_no=stage_no, stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                        stage_code=stage_code,
                        context=marker_context,
                    )

                layout_flag_id = to_int(jp.get("LayoutFlagId"))
                if layout_flag_id and layout_flag_id != 0 and _match_target(layout_flag_id, targets):
                    yield FlagHit(
                        source_type="qmi", file_path=rel,
                        json_path=f"InfoList[{ii}].{jp_key}[{ji}].LayoutFlagId",
                        field_name="LayoutFlagId", flag_value=layout_flag_id,
                        flag_kind="layout_flag", relationship=REL_MARKER_GATE,
                        quest_id=quest_id,
                        quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                        stage_no=stage_no, stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                        stage_code=stage_code,
                        context=marker_context,
                    )

                # QuestId itself as a target
                if quest_id and quest_id != 0 and _match_target(quest_id, targets):
                    yield FlagHit(
                        source_type="qmi", file_path=rel,
                        json_path=f"InfoList[{ii}].{jp_key}[{ji}].QuestId",
                        field_name="QuestId", flag_value=quest_id,
                        flag_kind="quest_id", relationship=REL_MARKER_GATE,
                        quest_id=quest_id,
                        quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                        stage_no=stage_no, stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                        stage_code=stage_code,
                        context=marker_context,
                    )


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




# ---------------------------------------------------------------------------
# FAA scanner – AdjoinInfoVector3.FlagId / QuestId with stage context
# ---------------------------------------------------------------------------

def scan_faa_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ai, adjoin_info in enumerate(payload.get("Array", [])):
        if not isinstance(adjoin_info, dict):
            continue

        destination_stage_no = to_int(adjoin_info.get("DestinationStageNo")) or 0
        destination_stage_en, destination_stage_jp = extract_localized(adjoin_info.get("DestinationStageName"))
        next_stage_no = to_int(adjoin_info.get("NextStageNo")) or 0
        next_stage_en, next_stage_jp = extract_localized(adjoin_info.get("NextStageName"))

        for pi, position in enumerate(adjoin_info.get("Positions", [])):
            if not isinstance(position, dict):
                continue

            quest_id = to_int(position.get("QuestId")) or 0
            quest_name_en, quest_name_jp = extract_localized(position.get("QuestName"))
            flag_id = to_int(position.get("FlagId"))
            context = f"Next stage: {next_stage_en or next_stage_jp or next_stage_no or '?'}"

            if flag_id is not None and flag_id != 0 and _match_target(flag_id, targets):
                yield FlagHit(
                    source_type="faa", file_path=rel,
                    json_path=f"Array[{ai}].Positions[{pi}].FlagId",
                    field_name="FlagId", flag_value=flag_id,
                    flag_kind="layout_flag", relationship=REL_FIELD_ADJOIN,
                    quest_id=quest_id,
                    quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                    stage_no=destination_stage_no,
                    stage_name=destination_stage_en, stage_name_jp=destination_stage_jp,
                    comment=f"DestinationStageNo={destination_stage_no}",
                    context=context,
                )

            if quest_id and _match_target(quest_id, targets):
                yield FlagHit(
                    source_type="faa", file_path=rel,
                    json_path=f"Array[{ai}].Positions[{pi}].QuestId",
                    field_name="QuestId", flag_value=quest_id,
                    flag_kind="quest_id", relationship=REL_FIELD_ADJOIN,
                    quest_id=quest_id,
                    quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                    stage_no=destination_stage_no,
                    stage_name=destination_stage_en, stage_name_jp=destination_stage_jp,
                    comment=f"DestinationStageNo={destination_stage_no}",
                    context=context,
                )


# ---------------------------------------------------------------------------
# EVP scanner – EventParam.Flag / QuestId with stage and event context
# ---------------------------------------------------------------------------

def scan_evp_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ei, event_param in enumerate(payload.get("EventParamList", [])):
        if not isinstance(event_param, dict):
            continue

        stage_no = to_int(event_param.get("Stage")) or 0
        stage_name_en, stage_name_jp = extract_localized(event_param.get("StageName"))
        event_no = to_int(event_param.get("EvNo")) or 0
        event_name_en, event_name_jp = extract_localized(event_param.get("EventName"))
        quest_id = to_int(event_param.get("QuestId")) or 0
        quest_name_en, quest_name_jp = extract_localized(event_param.get("QuestName"))
        flag_value = to_int(event_param.get("Flag"))
        file_name = str(event_param.get("FileName") or "")
        flag_types = event_param.get("FlagTypes") or []
        flag_type_text = ", ".join(str(value) for value in flag_types if value)
        event_code = f"ev{event_no:03d}" if event_no else parse_code(EVENT_CODE_PATTERN, rel)
        context_parts = []
        if event_name_en or event_name_jp:
            context_parts.append(event_name_en or event_name_jp)
        if file_name:
            context_parts.append(file_name.replace("\\", "/"))
        if flag_type_text:
            context_parts.append(f"FlagTypes={flag_type_text}")
        context = " | ".join(context_parts)

        if flag_value is not None and flag_value != 0 and _match_target(flag_value, targets):
            yield FlagHit(
                source_type="evp", file_path=rel,
                json_path=f"EventParamList[{ei}].Flag",
                field_name="Flag", flag_value=flag_value,
                flag_kind="quest_flag", relationship=REL_EVENT_PARAM,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                stage_no=stage_no,
                stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                event_code=event_code,
                comment=f"EvNo={event_no}",
                context=context,
            )

        if quest_id and _match_target(quest_id, targets):
            yield FlagHit(
                source_type="evp", file_path=rel,
                json_path=f"EventParamList[{ei}].QuestId",
                field_name="QuestId", flag_value=quest_id,
                flag_kind="quest_id", relationship=REL_EVENT_PARAM,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                stage_no=stage_no,
                stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                event_code=event_code,
                comment=f"EvNo={event_no}",
                context=context,
            )


# ---------------------------------------------------------------------------
# EVD scanner – Evidence.Flag / QuestId with step and evidence context
# ---------------------------------------------------------------------------

def scan_evd_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ei, evidence in enumerate(payload.get("EvidenceList", [])):
        if not isinstance(evidence, dict):
            continue

        flag_value = to_int(evidence.get("Flag"))
        quest_id = to_int(evidence.get("QuestId")) or 0
        quest_name_en, quest_name_jp = extract_localized(evidence.get("QuestName"))
        context, step_comment = _build_evidence_context(evidence)

        if flag_value is not None and flag_value != 0 and _match_target(flag_value, targets):
            yield FlagHit(
                source_type="evd", file_path=rel,
                json_path=f"EvidenceList[{ei}].Flag",
                field_name="Flag", flag_value=flag_value,
                flag_kind="quest_flag", relationship=REL_EVIDENCE_FLAG,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                comment=step_comment,
                context=context,
            )

        if quest_id and _match_target(quest_id, targets):
            yield FlagHit(
                source_type="evd", file_path=rel,
                json_path=f"EvidenceList[{ei}].QuestId",
                field_name="QuestId", flag_value=quest_id,
                flag_kind="quest_id", relationship=REL_EVIDENCE_FLAG,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                comment=f"{step_comment}, Flag={flag_value or 0}",
                context=context,
            )


# ---------------------------------------------------------------------------
# Repeatable sortie scanners – CSI / ESI
# ---------------------------------------------------------------------------

def scan_csi_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ci, row in enumerate(payload.get("CycleContentsSortieInfoTable", [])):
        if not isinstance(row, dict):
            continue

        cycle_sub_no = to_int(row.get("CycleSubNo")) or 0
        if cycle_sub_no == 0 or not _match_target(cycle_sub_no, targets):
            continue

        cycle_no = to_int(row.get("CycleNo")) or 0
        stage_no, stage_name_en, stage_name_jp = _resolve_stage_name_fields(row)
        context = _build_repeatable_sortie_context(row)

        yield FlagHit(
            source_type="csi", file_path=rel,
            json_path=f"CycleContentsSortieInfoTable[{ci}].CycleSubNo",
            field_name="CycleSubNo", flag_value=cycle_sub_no,
            flag_kind="cycle_sub_no", relationship=REL_REPEATABLE_SORTIE,
            stage_no=stage_no,
            stage_name=stage_name_en, stage_name_jp=stage_name_jp,
            comment=f"CycleNo={cycle_no}",
            context=context,
        )


def scan_esi_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ei, row in enumerate(payload.get("EndContentsSortieInfoTable", [])):
        if not isinstance(row, dict):
            continue

        quest_id = to_int(row.get("QuestId")) or 0
        quest_name_en, quest_name_jp = extract_localized(row.get("QuestName"))
        flag_value = to_int(row.get("Flag"))
        stage_no, stage_name_en, stage_name_jp = _resolve_stage_name_fields(row)
        context = _build_repeatable_sortie_context(row)
        unknown_comment = f"Unknown1={to_int(row.get('Unknown1')) or 0}, Unknown2={to_int(row.get('Unknown2')) or 0}"

        if flag_value is not None and flag_value != 0 and _match_target(flag_value, targets):
            yield FlagHit(
                source_type="esi", file_path=rel,
                json_path=f"EndContentsSortieInfoTable[{ei}].Flag",
                field_name="Flag", flag_value=flag_value,
                flag_kind="quest_flag", relationship=REL_REPEATABLE_SORTIE,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                stage_no=stage_no,
                stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                comment=unknown_comment,
                context=context,
            )

        if quest_id and _match_target(quest_id, targets):
            yield FlagHit(
                source_type="esi", file_path=rel,
                json_path=f"EndContentsSortieInfoTable[{ei}].QuestId",
                field_name="QuestId", flag_value=quest_id,
                flag_kind="quest_id", relationship=REL_REPEATABLE_SORTIE,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                stage_no=stage_no,
                stage_name=stage_name_en, stage_name_jp=stage_name_jp,
                comment=f"{unknown_comment}, Flag={flag_value or 0}",
                context=context,
            )


# ---------------------------------------------------------------------------
# Tutorial / job master scanners – JTQ / TQG / JMC
# ---------------------------------------------------------------------------

def scan_jtq_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for qi, quest_entry in enumerate(payload.get("JobTutorialQuestList", [])):
        if not isinstance(quest_entry, dict):
            continue

        quest_id = to_int(quest_entry.get("QuestId")) or 0
        if quest_id == 0 or not _match_target(quest_id, targets):
            continue

        quest_name_en, quest_name_jp = extract_localized(quest_entry.get("QuestName"))
        yield FlagHit(
            source_type="jtq", file_path=rel,
            json_path=f"JobTutorialQuestList[{qi}].QuestId",
            field_name="QuestId", flag_value=quest_id,
            flag_kind="quest_id", relationship=REL_TUTORIAL_QUEST,
            quest_id=quest_id,
            quest_name=quest_name_en, quest_name_jp=quest_name_jp,
            context="Job tutorial quest registry",
        )


def scan_tqg_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for gi, group in enumerate(payload.get("TutorialQuestGroupList", [])):
        if not isinstance(group, dict):
            continue

        group_id = to_int(group.get("GroupId")) or 0
        for qi, quest_entry in enumerate(group.get("QuestIdArray", [])):
            if not isinstance(quest_entry, dict):
                continue

            quest_id = to_int(quest_entry.get("QuestId")) or 0
            if quest_id == 0 or not _match_target(quest_id, targets):
                continue

            quest_name_en, quest_name_jp = extract_localized(quest_entry.get("QuestName"))
            yield FlagHit(
                source_type="tqg", file_path=rel,
                json_path=f"TutorialQuestGroupList[{gi}].QuestIdArray[{qi}].QuestId",
                field_name="QuestId", flag_value=quest_id,
                flag_kind="quest_id", relationship=REL_TUTORIAL_GROUP,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                comment=f"GroupId={group_id}",
                context="Tutorial quest group membership",
            )


def scan_jmc_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for ji, row in enumerate(payload.get("JobMasterCtrlList", [])):
        if not isinstance(row, dict):
            continue

        context, area_name_en, area_name_jp, job_comment = _build_jmc_context(row)
        for field_name, kind_label, quest_id, quest_name_en, quest_name_jp in _iter_jmc_quest_fields(row):
            if not _match_target(quest_id, targets):
                continue
            yield FlagHit(
                source_type="jmc", file_path=rel,
                json_path=f"JobMasterCtrlList[{ji}].{field_name}",
                field_name=field_name, flag_value=quest_id,
                flag_kind="quest_id", relationship=REL_JOB_MASTER,
                quest_id=quest_id,
                quest_name=quest_name_en, quest_name_jp=quest_name_jp,
                area_name=area_name_en, area_name_jp=area_name_jp,
                comment=job_comment,
                context=f"{kind_label} | {context}" if context else kind_label,
            )


# ---------------------------------------------------------------------------
# AMS scanner – AreaMasterSpotData.QuestId marks quest-blocked spots
# ---------------------------------------------------------------------------

def scan_ams_file(_path: Path, payload: dict[str, Any], rel: str, targets: set[int] | None) -> Iterator[FlagHit]:
    for si, row in enumerate(payload.get("AreaMasterSpotDataList", [])):
        if not isinstance(row, dict):
            continue

        quest_id = to_int(row.get("QuestId")) or 0
        if quest_id == 0 or not _match_target(quest_id, targets):
            continue

        quest_name_en, quest_name_jp = extract_localized(row.get("QuestName"))
        stage_no = to_int(row.get("StageNoMap")) or 0
        stage_name_en, stage_name_jp = extract_localized(row.get("StageName"))
        area_name_en, area_name_jp = extract_localized(row.get("AreaName"))
        context, spot_id = _build_ams_context(row)
        yield FlagHit(
            source_type="ams", file_path=rel,
            json_path=f"AreaMasterSpotDataList[{si}].QuestId",
            field_name="QuestId", flag_value=quest_id,
            flag_kind="quest_id", relationship=REL_SPOT_BLOCK,
            quest_id=quest_id,
            quest_name=quest_name_en, quest_name_jp=quest_name_jp,
            stage_no=stage_no,
            stage_name=stage_name_en, stage_name_jp=stage_name_jp,
            area_name=area_name_en, area_name_jp=area_name_jp,
            comment=f"SpotId={spot_id}",
            context=context,
        )



