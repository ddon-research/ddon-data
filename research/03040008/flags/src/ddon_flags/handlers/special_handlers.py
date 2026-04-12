"""Special-family scanners: FAA, EVP, EVD, CSI, ESI, JTQ, TQG, JMC, AMS."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from ..scan_models import (
    FlagHit,
    REL_EVIDENCE_FLAG,
    REL_EVENT_PARAM,
    REL_FIELD_ADJOIN,
    REL_JOB_MASTER,
    REL_REPEATABLE_SORTIE,
    REL_SPOT_BLOCK,
    REL_TUTORIAL_GROUP,
    REL_TUTORIAL_QUEST,
)
from ..scan_utils import (
    EVENT_CODE_PATTERN,
    extract_localized,
    match_target as _match_target,
    parse_code,
    to_int,
)

from ._helpers import (
    _build_ams_context,
    _build_evidence_context,
    _build_jmc_context,
    _build_repeatable_sortie_context,
    _build_stage_route_context,
    _iter_jmc_quest_fields,
    _resolve_stage_name_fields,
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
