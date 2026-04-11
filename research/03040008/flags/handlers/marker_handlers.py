"""QMI/FMI (quest/field marker info) and EVSI (event state info) scanners."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from scan_models import (
    FlagHit,
    REL_EVENT_STATE,
    REL_MARKER_GATE,
)
from scan_utils import (
    EVENT_CODE_PATTERN,
    STAGE_CODE_PATTERN,
    extract_localized,
    match_target as _match_target,
    parse_code,
    to_int,
)
from source_metadata import (
    describe_marker_asset,
    resolve_event_view,
    resolve_marker_lot_association,
    resolve_stage,
)


# ---------------------------------------------------------------------------
# Private helpers – marker context
# ---------------------------------------------------------------------------

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
