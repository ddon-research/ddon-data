"""FSM (Finite State Machine) scanner."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from ..scan_models import (
    FlagHit,
    REL_FSM_CHECK,
    REL_FSM_FREE_FLAG,
    REL_FSM_SET,
)
from ..scan_utils import (
    EVENT_CODE_PATTERN,
    STAGE_CODE_PATTERN,
    extract_localized,
    match_target as _match_target,
    parse_code,
    parse_quest_id_from_path,
    to_int,
)
from ..source_metadata import describe_fsm_asset


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
