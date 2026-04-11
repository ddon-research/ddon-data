"""QST (Quest Stage Data) scanner."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from scan_models import (
    FlagHit,
    REL_DOOR_GATE,
    REL_LAYOUT_GUARD,
    REL_QUEST_CONDITION,
    REL_QUEST_ERASE,
    REL_QUEST_OM,
    REL_TEXT_QUEST,
    REL_WARP_GATE,
)
from scan_utils import (
    STAGE_CODE_PATTERN,
    extract_localized,
    match_target as _match_target,
    parse_code,
    parse_quest_id_from_path,
    to_int,
)
from source_metadata import resolve_stage

from handlers._helpers import (
    _append_item_part,
    _append_nonzero_part,
    _build_qst_info_om_summary,
    _strip_class_name,
)


def _build_qst_comment(group_no: int, group_comment: str, set_comment: str = "") -> str:
    parts = [f"QuestGroup {group_no}"] if group_no else []
    if group_comment:
        parts.append(group_comment)
    if set_comment and set_comment != group_comment:
        parts.append(set_comment)
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
# QST scanner -- QuestStageList -> QuestGrp -> Condition/EraseCondition
#                                            -> QuestSet deep scan
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
