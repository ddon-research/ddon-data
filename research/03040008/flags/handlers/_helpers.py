"""Shared private helpers for the handler sub-package."""
from __future__ import annotations

from typing import Any, Iterator

from scan_utils import extract_localized, to_int
from source_metadata import resolve_item_name


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
