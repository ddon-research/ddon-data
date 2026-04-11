"""Cached metadata helpers for developer-facing report enrichment."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from scan_utils import extract_localized as _extract_localized
from scan_utils import load_json as _load_json
from scan_utils import relative_path as _relative_path_with_root


ROOT = Path(__file__).resolve().parents[3]
CLIENT_ROOT = ROOT / "client" / "03040008"
STAGE_CODE_PATTERN = re.compile(r"st(\d{4})")
NPC_FSM_PATTERN = re.compile(r"(?:^|/)(n\d{4})\.fsm\.json$")
ENEMY_FSM_PATTERN = re.compile(r"(?:^|/)(e\d{4})\.fsm\.json$")
MARKER_ASSET_PATTERN = re.compile(
    r"(?:^|/)(?P<asset>(?:st\d{4}|fa\d{3}|FieldArea\d+)_marker_(?P<kind>npc|om|sce|ect))\.(?P<ext>qmi|fmi)\.json$",
    re.IGNORECASE,
)
NPC_ASSET_ID_PATTERN = re.compile(r"(?:^|\D)n(?P<npc_id>\d{4})(?=\D|$)", re.IGNORECASE)


def _relative_path(path: Path) -> str:
    return _relative_path_with_root(path, ROOT)


def _iter_item_rows(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return
    for value in payload.values():
        if not isinstance(value, list):
            continue
        for row in value:
            if isinstance(row, dict) and isinstance(row.get("ItemId"), int):
                yield row


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


@lru_cache(maxsize=1)
def load_stage_lookup() -> dict[int, tuple[str, str]]:
    path = CLIENT_ROOT / "base" / "scr" / "stage_list.slt.json"
    payload = _load_json(path)
    if not isinstance(payload, dict):
        return {}

    lookup: dict[int, tuple[str, str]] = {}
    for row in payload.get("StageListInfoList", []):
        if not isinstance(row, dict):
            continue
        stage_no = row.get("StageNo")
        if not isinstance(stage_no, int):
            continue
        stage_name = row.get("StageName")
        if isinstance(stage_name, dict):
            lookup[stage_no] = (str(stage_name.get("En") or ""), str(stage_name.get("Jp") or ""))
        elif isinstance(stage_name, str):
            lookup[stage_no] = (stage_name, "")
    return lookup


@lru_cache(maxsize=1)
def load_event_name_lookup() -> dict[str, str]:
    path = CLIENT_ROOT / "EventViewRoom" / "ui" / "00_message" / "event" / "event_name.gmd.json"
    payload = _load_json(path)
    if not isinstance(payload, dict):
        return {}

    lookup: dict[str, str] = {}
    for row in payload.get("Indices", []):
        if not isinstance(row, dict):
            continue
        key = str(row.get("Key") or "")
        message = str(row.get("Message") or "")
        if key:
            lookup[key] = message
    return lookup


@lru_cache(maxsize=1)
def load_item_name_lookup() -> dict[int, tuple[str, str]]:
    path = CLIENT_ROOT / "base" / "etc" / "itemlist.ipa.json"
    payload = _load_json(path)
    lookup: dict[int, tuple[str, str]] = {}
    for row in _iter_item_rows(payload):
        item_id = row.get("ItemId")
        item_name_en, item_name_jp = _extract_localized(row.get("ItemName"))
        if isinstance(item_id, int) and (item_name_en or item_name_jp):
            lookup[item_id] = (item_name_en, item_name_jp)
    return lookup


def stage_no_from_code(stage_code: str) -> int:
    match = STAGE_CODE_PATTERN.fullmatch(stage_code or "")
    return int(match.group(1)) if match else 0


def resolve_stage(stage_no: int = 0, stage_code: str = "") -> tuple[int, str, str]:
    resolved_stage_no = stage_no or stage_no_from_code(stage_code)
    if not resolved_stage_no:
        return 0, "", ""
    stage_name_en, stage_name_jp = load_stage_lookup().get(resolved_stage_no, ("", ""))
    return resolved_stage_no, stage_name_en, stage_name_jp


def resolve_event_view(stage_code: str, event_code: str) -> tuple[str, str]:
    if not stage_code or not event_code:
        return "", ""
    event_key = f"EVENT_NAME_{stage_code}{event_code}"
    return event_key, load_event_name_lookup().get(event_key, "")


def resolve_item_name(item_id: int) -> tuple[str, str]:
    if item_id <= 0:
        return "", ""
    return load_item_name_lookup().get(item_id, ("", ""))


@lru_cache(maxsize=1)
def load_npc_name_lookup() -> dict[int, tuple[str, str]]:
    path = CLIENT_ROOT / "npc" / "npc_common" / "etc" / "npc" / "npc.nll.json"
    payload = _load_json(path)
    if not isinstance(payload, dict):
        return {}

    lookup: dict[int, tuple[str, str]] = {}
    for row in _as_list(payload.get("NpcLedgerList")):
        if not isinstance(row, dict):
            continue
        npc_id = row.get("NpcId")
        if not isinstance(npc_id, int) or npc_id <= 0:
            continue
        npc_name_en, npc_name_jp = _extract_localized(row.get("NpcName"))
        if npc_name_en or npc_name_jp:
            lookup[npc_id] = (npc_name_en, npc_name_jp)
    return lookup


def resolve_npc_name(npc_id: int) -> tuple[str, str]:
    if npc_id <= 0:
        return "", ""
    return load_npc_name_lookup().get(npc_id, ("", ""))


def infer_npc_id_from_text(*values: str) -> int:
    for value in values:
        if not value:
            continue
        match = NPC_ASSET_ID_PATTERN.search(value.replace("\\", "/"))
        if match:
            return int(match.group("npc_id"))
    return 0


def enrich_hit_with_npc_ledger(hit: dict[str, Any]) -> dict[str, Any]:
    cloned = dict(hit)
    raw_npc_id = cloned.get("npc_id")
    npc_id = raw_npc_id if isinstance(raw_npc_id, int) else 0
    if npc_id <= 0:
        npc_id = infer_npc_id_from_text(
            str(cloned.get("file_path") or ""),
            str(cloned.get("context") or ""),
            str(cloned.get("comment") or ""),
        )
    if npc_id <= 0:
        return cloned

    if not cloned.get("npc_id"):
        cloned["npc_id"] = npc_id

    npc_name_en, npc_name_jp = resolve_npc_name(npc_id)
    if npc_name_en and not cloned.get("npc_name"):
        cloned["npc_name"] = npc_name_en
    if npc_name_jp and not cloned.get("npc_name_jp"):
        cloned["npc_name_jp"] = npc_name_jp
    return cloned


def describe_fsm_asset(rel_path: str) -> str:
    normalized = rel_path.replace("\\", "/")
    npc_match = NPC_FSM_PATTERN.search(normalized)
    if npc_match:
        return f"NPCFSM={npc_match.group(1)}"
    enemy_match = ENEMY_FSM_PATTERN.search(normalized)
    if enemy_match:
        return f"EnemyFSM={enemy_match.group(1)}"
    return ""


def describe_marker_asset(rel_path: str) -> dict[str, str]:
    normalized = rel_path.replace("\\", "/")
    match = MARKER_ASSET_PATTERN.search(normalized)
    if not match:
        return {}

    marker_kind = match.group("kind").lower()
    extension = match.group("ext").lower()
    marker_type = {
        "npc": "NPCMarker",
        "om": "OMMarker",
        "sce": "SceneMarker",
        "ect": "ObjectiveMarker",
    }.get(marker_kind, "Marker")
    marker_scope = "Field" if extension == "fmi" else "Quest"
    return {
        "asset_name": match.group("asset"),
        "marker_kind": marker_kind,
        "marker_type": marker_type,
        "marker_scope": marker_scope,
        "source_extension": extension,
    }


def _extract_stage_code(path_text: str) -> str:
    match = STAGE_CODE_PATTERN.search(path_text)
    return match.group(0) if match else ""


def _format_lot_warp_destination(
    index: int,
    stage_no: int,
    stage_names: list[Any],
    spot_names: list[Any],
    start_positions: list[Any],
) -> str:
    _, stage_name_en, stage_name_jp = resolve_stage(stage_no=stage_no)
    if index < len(stage_names):
        local_stage_name_en, local_stage_name_jp = _extract_localized(stage_names[index])
        stage_name_en = local_stage_name_en or stage_name_en
        stage_name_jp = local_stage_name_jp or stage_name_jp

    destination = f"st{stage_no:04d}"
    destination_name = stage_name_en or stage_name_jp
    if destination_name:
        destination += f" {destination_name}"

    details = [destination]
    if index < len(spot_names):
        spot_name_en, spot_name_jp = _extract_localized(spot_names[index])
        spot_name = spot_name_en or spot_name_jp
        if spot_name:
            details.append(f"Spot {spot_name}")

    if index < len(start_positions):
        start_pos = start_positions[index]
        if isinstance(start_pos, int):
            details.append(f"StartPos={start_pos}")

    return " | ".join(details)


def _summarize_lot_warp(info: dict[str, Any]) -> list[str]:
    summaries: list[str] = []
    stage_numbers = _as_list(info.get("StageNo"))
    if not stage_numbers:
        return summaries

    stage_names = _as_list(info.get("StageNames"))
    spot_names = _as_list(info.get("SpotNames"))
    start_positions = _as_list(info.get("StartPosNo"))

    for index, raw_stage_no in enumerate(stage_numbers):
        stage_no = raw_stage_no if isinstance(raw_stage_no, int) else 0
        if stage_no == 0:
            continue
        summaries.append(
            _format_lot_warp_destination(index, stage_no, stage_names, spot_names, start_positions)
        )
    return summaries


def _find_lot_group_matches(stage_code: str, group_no: int) -> list[Path]:
    stage_lot_root = CLIENT_ROOT / "stage" / stage_code / "lot"
    if not stage_lot_root.exists():
        return []
    suffix = f"_p{group_no}.lot.json"
    return sorted(path for path in stage_lot_root.rglob(f"*{suffix}") if path.name.endswith(suffix))


def _find_prefixed_lot_matches(stage_code: str, prefix: str, group_no: int) -> list[Path]:
    stage_lot_root = CLIENT_ROOT / "stage" / stage_code / "lot"
    if not stage_lot_root.exists():
        return []

    suffixes = {f"_{prefix}{group_no:02d}.lot.json", f"_{prefix}{group_no}.lot.json"}
    matches: dict[str, Path] = {}
    for suffix in suffixes:
        for path in stage_lot_root.rglob(f"*{suffix}"):
            if path.name.endswith(suffix):
                matches[str(path)] = path
    return sorted(matches.values())


def _extract_position_tuple(value: Any) -> tuple[float, float, float] | None:
    if not isinstance(value, dict):
        return None
    x = value.get("X")
    y = value.get("Y")
    z = value.get("Z")
    if not all(isinstance(component, (int, float)) for component in (x, y, z)):
        return None
    assert isinstance(x, (int, float))
    assert isinstance(y, (int, float))
    assert isinstance(z, (int, float))
    return float(x), float(y), float(z)


def _distance_between(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _extract_lot_reference(entry: dict[str, Any]) -> tuple[tuple[float, float, float] | None, str]:
    type_name = str(entry.get("TypeName") or "")
    info = entry.get("Info")
    if not isinstance(info, dict):
        return None, type_name

    if isinstance(info.get("InfoCharacter"), dict):
        position = _extract_position_tuple(info["InfoCharacter"].get("Position"))
        npc_name_en, npc_name_jp = _extract_localized(info.get("NpcName"))
        label = npc_name_en or npc_name_jp or type_name or "LotEntry"
        return position, label

    info_om = None
    if isinstance(info.get("InfoOm"), dict):
        info_om = info.get("InfoOm")
    elif isinstance(info.get("InfoCoord"), dict):
        info_om = info
    if not isinstance(info_om, dict):
        return None, type_name or "LotEntry"

    info_coord = info_om.get("InfoCoord") if isinstance(info_om.get("InfoCoord"), dict) else info_om.get("InfoCharacter")
    position = _extract_position_tuple(info_coord.get("Position")) if isinstance(info_coord, dict) else None
    coord_name = str(info_coord.get("Name") or "") if isinstance(info_coord, dict) else ""
    label = coord_name or type_name or "LotEntry"
    return position, label


def _summarize_marker_lot_payload(
    payload: Any,
    marker_position: tuple[float, float, float] | None,
) -> dict[str, Any]:
    type_names, _ = _summarize_lot_payload(payload)
    nearest_label = ""
    nearest_distance: float | None = None
    if not isinstance(payload, dict) or marker_position is None:
        return {
            "type_names": type_names,
            "nearest_label": nearest_label,
            "nearest_distance": nearest_distance,
        }

    for entry in _as_list(payload.get("Array")):
        if not isinstance(entry, dict):
            continue
        entry_position, entry_label = _extract_lot_reference(entry)
        if entry_position is None:
            continue
        distance = _distance_between(marker_position, entry_position)
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_label = entry_label

    return {
        "type_names": type_names,
        "nearest_label": nearest_label,
        "nearest_distance": nearest_distance,
    }


@lru_cache(maxsize=512)
def _resolve_marker_lot_association_cached(stage_code: str, marker_kind: str, group_no: int) -> dict[str, Any] | None:
    prefix = {"npc": "n", "om": "p"}.get(marker_kind)
    if not stage_code or not prefix or group_no <= 0:
        return None

    matches = _find_prefixed_lot_matches(stage_code, prefix, group_no)
    if not matches:
        return None

    result: dict[str, Any] = {
        "match_count": len(matches),
        "file_names": [path.name for path in matches[:3]],
    }
    if len(matches) != 1:
        return result

    lot_path = matches[0]
    payload = _load_json(lot_path)
    lot_summary = _summarize_marker_lot_payload(payload, None)
    result.update(
        {
            "file_path": _relative_path(lot_path),
            "file_name": lot_path.name,
            "type_names": lot_summary.get("type_names", []),
        }
    )
    return result


def resolve_marker_lot_association(
    stage_code: str,
    marker_kind: str,
    group_no: int,
    marker_position: tuple[float, float, float] | None = None,
) -> dict[str, Any] | None:
    base_result = _resolve_marker_lot_association_cached(stage_code, marker_kind, group_no)
    if base_result is None or marker_position is None or not base_result.get("file_path"):
        return base_result

    lot_path = ROOT / str(base_result["file_path"])
    payload = _load_json(lot_path)
    if payload is None:
        return base_result

    lot_summary = _summarize_marker_lot_payload(payload, marker_position)
    enriched = dict(base_result)
    nearest_label = str(lot_summary.get("nearest_label") or "")
    nearest_distance = lot_summary.get("nearest_distance")
    if nearest_label:
        enriched["nearest_label"] = nearest_label
    if isinstance(nearest_distance, float):
        enriched["nearest_distance"] = round(nearest_distance, 2)
    return enriched


def _collect_lot_entry_summary(entry: dict[str, Any], type_names: list[str], warp_destinations: list[str]) -> None:
    type_name = str(entry.get("TypeName") or "")
    if type_name and type_name not in type_names:
        type_names.append(type_name)
    if type_name != "SetInfoOmWarp":
        return

    info = entry.get("Info")
    if not isinstance(info, dict):
        return

    for summary in _summarize_lot_warp(info):
        if summary not in warp_destinations:
            warp_destinations.append(summary)


def _summarize_lot_payload(payload: Any) -> tuple[list[str], list[str]]:
    type_names: list[str] = []
    warp_destinations: list[str] = []
    if not isinstance(payload, dict):
        return type_names, warp_destinations

    for entry in _as_list(payload.get("Array")):
        if not isinstance(entry, dict):
            continue
        _collect_lot_entry_summary(entry, type_names, warp_destinations)

    return type_names, warp_destinations


@lru_cache(maxsize=512)
def resolve_lot_group_association(stage_code: str, group_no: int) -> dict[str, Any] | None:
    if not stage_code or group_no <= 0:
        return None

    matches = _find_lot_group_matches(stage_code, group_no)
    if not matches:
        return None

    result: dict[str, Any] = {
        "match_count": len(matches),
        "file_names": [path.name for path in matches[:3]],
    }
    if len(matches) != 1:
        return result

    lot_path = matches[0]
    payload = _load_json(lot_path)
    type_names, warp_destinations = _summarize_lot_payload(payload)

    result.update(
        {
            "file_path": _relative_path(lot_path),
            "file_name": lot_path.name,
            "type_names": type_names,
            "warp_destinations": warp_destinations,
        }
    )
    return result


def build_quest_archive_context(quest_id: int) -> dict[str, Any] | None:
    archive_path = CLIENT_ROOT / "quest" / f"q{quest_id}.arc.json"
    payload = _load_json(archive_path)
    if not isinstance(payload, dict):
        return None

    grouped: dict[str, dict[str, Any]] = {}
    for row in payload.get("Resource", []):
        if not isinstance(row, dict):
            continue
        resource_path = str(row.get("Path") or "")
        stage_code = _extract_stage_code(resource_path)
        stage_no, stage_name_en, stage_name_jp = resolve_stage(stage_code=stage_code)
        bucket_key = stage_code or "unclassified"
        bucket = grouped.setdefault(
            bucket_key,
            {
                "stage_code": stage_code,
                "stage_no": stage_no,
                "stage_name": stage_name_en,
                "stage_name_jp": stage_name_jp,
                "resources": [],
            },
        )
        bucket["resources"].append(
            {
                "path": resource_path.replace("\\", "/"),
                "type_extension": str(row.get("TypeExtension") or ""),
                "type_name": str(row.get("TypeName") or ""),
            }
        )

    stages = sorted(grouped.values(), key=lambda item: (item["stage_code"] or "zzzz", item["stage_no"] or 0))
    return {
        "file_path": _relative_path(archive_path),
        "resource_count": int(payload.get("ResourceNum") or 0),
        "stages": stages,
    }


def _read_table(path: Path, key: str) -> list[dict[str, Any]]:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        return []
    return [row for row in _as_list(payload.get(key)) if isinstance(row, dict)]


def _as_positive_int(value: Any) -> int:
    return value if isinstance(value, int) and value > 0 else 0


def _stage_tuple(row: dict[str, Any]) -> tuple[int, int, int]:
    return (
        _as_positive_int(row.get("StageNo1")),
        _as_positive_int(row.get("StageNo2")),
        _as_positive_int(row.get("StageNo3")),
    )


@lru_cache(maxsize=1)
def load_esi_rows() -> list[dict[str, Any]]:
    return _read_table(CLIENT_ROOT / "game_common" / "quest" / "rEndContentsSortieInfo.esi.json", "EndContentsSortieInfoTable")


@lru_cache(maxsize=1)
def load_csi_rows() -> list[dict[str, Any]]:
    return _read_table(CLIENT_ROOT / "game_common" / "quest" / "rCycleContentsSortieInfo.csi.json", "CycleContentsSortieInfoTable")


@lru_cache(maxsize=1)
def load_evd_rows() -> list[dict[str, Any]]:
    return _read_table(CLIENT_ROOT / "ui" / "menu_evidence_list" / "ui" / "00_common" / "evidence" / "evidence.evd.json", "EvidenceList")


@lru_cache(maxsize=1)
def load_jtq_rows() -> list[dict[str, Any]]:
    return _read_table(CLIENT_ROOT / "game_common" / "quest" / "jobTutorialQuestList.jtq.json", "JobTutorialQuestList")


@lru_cache(maxsize=1)
def load_tqg_rows() -> list[dict[str, Any]]:
    return _read_table(CLIENT_ROOT / "game_common" / "quest" / "tutorialQuestGroup.tqg.json", "TutorialQuestGroupList")


@lru_cache(maxsize=1)
def load_jmc_rows() -> list[dict[str, Any]]:
    return _read_table(CLIENT_ROOT / "game_common" / "etc" / "jobMasterCtrl.jmc.json", "JobMasterCtrlList")


@lru_cache(maxsize=1)
def load_ams_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ams_root = CLIENT_ROOT / "ui" / "uGUIAreaMaster" / "ui" / "00_param" / "master"
    for path in sorted(ams_root.glob("*.ams.json")):
        rows.extend(_read_table(path, "AreaMasterSpotDataList"))
    return rows


@lru_cache(maxsize=1)
def _csi_by_stage_tuple() -> dict[tuple[int, int, int], list[dict[str, Any]]]:
    indexed: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    for row in load_csi_rows():
        indexed.setdefault(_stage_tuple(row), []).append(row)
    return indexed


def get_esi_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    return [row for row in load_esi_rows() if _as_positive_int(row.get("QuestId")) == quest_id]


def get_evd_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    return [row for row in load_evd_rows() if _as_positive_int(row.get("QuestId")) == quest_id]


def get_jtq_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    return [row for row in load_jtq_rows() if _as_positive_int(row.get("QuestId")) == quest_id]


def get_tqg_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for row in load_tqg_rows():
        quest_array = _as_list(row.get("QuestIdArray"))
        if any(_as_positive_int(entry.get("QuestId")) == quest_id for entry in quest_array if isinstance(entry, dict)):
            matches.append(row)
    return matches


def get_jmc_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for row in load_jmc_rows():
        tutorial_quest_id = _as_positive_int(row.get("JobTutorialQuestId"))
        master_quest_id = _as_positive_int(row.get("JobMasterTutorialQuestId"))
        if quest_id in {tutorial_quest_id, master_quest_id}:
            matches.append(row)
    return matches


def get_ams_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    return [row for row in load_ams_rows() if _as_positive_int(row.get("QuestId")) == quest_id]


def get_csi_rows_for_quest(quest_id: int) -> list[dict[str, Any]]:
    matches: dict[int, dict[str, Any]] = {}
    for row in get_esi_rows_for_quest(quest_id):
        for csi_row in _csi_by_stage_tuple().get(_stage_tuple(row), []):
            cycle_sub_no = _as_positive_int(csi_row.get("CycleSubNo"))
            if cycle_sub_no:
                matches[cycle_sub_no] = csi_row
    return [matches[key] for key in sorted(matches)]


def quest_has_special_resource_refs(quest_id: int) -> bool:
    return bool(
        get_esi_rows_for_quest(quest_id)
        or get_evd_rows_for_quest(quest_id)
        or get_jtq_rows_for_quest(quest_id)
        or get_tqg_rows_for_quest(quest_id)
        or get_jmc_rows_for_quest(quest_id)
        or get_ams_rows_for_quest(quest_id)
    )