"""
Unified flag/quest investigation script.

Takes either a single flag number (--flag) or a single quest number (--quest)
and produces a structured JSON report + human-readable AsciiDoc with all
direct hits and ranked candidates from the decoded client data.

IMPORTANT: Only decoded client resource files are sources of truth.
Arrowgene quest assets are NOT scanned — they are the outputs we are
building, not evidence. CData* packet structures are also excluded.

Data sources:
  1. ddon-data/client JSON (QST, GPL, LOT, FSM, EVSI, QMI/FMI, NPC) — primary
  2. DDO.exe immediate operand scan — secondary, optional

Investigation target catalog (user-curated, NOT data sources):
  - known_world_manage_quest_flags.txt / known_world_manage_layout_flags.txt
  - npc_ledger_flags.json (manually documented NPC function → flag mappings)
  - world_manage_state_quests.md (manually documented layout flag descriptions)

Usage examples:
    python investigate_flags.py --quest 70000001
    python investigate_flags.py --flag 1109
    python investigate_flags.py --quest 70000001 --skip-executable-scan
    python investigate_flags.py --all-quests --skip-executable-scan
    python investigate_flags.py --all-client-quests --skip-executable-scan
"""
from __future__ import annotations

import argparse
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from catalog_loader import (
    TargetFlag,
    build_flag_query_context,
    build_quest_query_context,
    dedupe_targets,
    load_known_targets,
)
from client_scanner import collect_client_json_hits
from corpus_index import CorpusIndex, build_corpus_index
from executable_scanner import (
    collect_contexts_and_following_calls,
    collect_immediate_hits,
    serialize_immediate_result,
)
from derivation import DerivationClass
from graph_expansion import build_quest_graph_expansion
from json_cache import JsonCache
from quest_families import classify_quest_family
from report_writer import write_json_report, write_asciidoc_report
from candidate_finder import collect_candidate_json_hits
from mss_enrichment import enrich_hit_dicts_with_mss
from manifest import AUTHORITATIVE_WORLD_MANAGE_QUEST_IDS, get_authoritative_targets_for_quest
from source_metadata import (
    build_quest_archive_context,
    build_family_relationship_context,
    build_owner_layout_catalog,
    build_q7_owner_layout_catalog,
    collect_stage_neighborhood_cues,
    build_stage_neighborhood_context,
    collect_quest_archive_qst_hits,
    enrich_hit_with_npc_ledger,
    get_ams_rows_for_quest,
    get_csi_rows_for_quest,
    get_esi_rows_for_quest,
    get_evd_rows_for_quest,
    get_jmc_rows_for_quest,
    get_jtq_rows_for_quest,
    get_tqg_rows_for_quest,
    quest_has_special_resource_refs,
)

DEFAULT_UPSTREAM_ROOT = Path(r"C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream")
DEFAULT_DDO_EXE_PATH = Path(r"D:\DDON_03040008\DDO.exe")
DEFAULT_OBJDUMP_PATH = Path(r"C:\msys64\usr\bin\objdump.exe")
REPORT_STEM_PREFIX = "client_investigation"
REPORT_FORMAT_VERSION = "client_investigation.v4"

DIRECT_SOURCE_EXPLANATIONS: dict[str, str] = {
    "ams": "Area Master spot block; QuestId here indicates the map spot is hidden or blocked by that quest.",
    "csi": "Repeatable sortie cycle metadata; CycleSubNo here ties a repeatable q5 sortie to its cycle content bucket and stage route.",
    "evsi": "Event Viewer reference; this flag is tied to a replayable cinematic/event state for the resolved stage and event.",
    "gpl": "Layout group guard; QuestNo and LayoutFlagNo here usually determine whether a stage group loads, including enemy or object visibility.",
    "esi": "Repeatable sortie registry; QuestId and Flag here define special q5 repeatable sortie entries and their gate flags.",
    "evd": "Evidence registry; this season 3 file ties investigation-style substory evidence items to a quest and the flag unlocked at each step.",
    "jmc": "Job master control; this resource links tutorial and master-visit quests to a vocation mentor, area, and onboarding flow.",
    "jtq": "Tutorial quest registry; q6 tutorial quests are listed directly in the job tutorial quest table.",
    "lot": "Layout placement reference; LOT hits usually gate warps, NPCs, or interactable objects in the stage layout.",
    "qst": "Quest-stage scripting reference; QuestGroup conditions and QuestSetInfo objects describe how doors, warps, levers, text points, and OM controls behave when the quest or flag state changes.",
    "qmi": "Marker reference; quest and layout values here usually gate marker visibility or jump-point behavior.",
    "nll": "NPC ledger reference; the flag controls when an NPC function becomes available.",
    "npc": "NPC state reference; the quest flag participates in NPC appearance or behavior ranges.",
    "smc": "NPC state reference; the quest flag participates in NPC appearance or behavior ranges.",
    "tqg": "Tutorial quest grouping; q6 tutorial quests are clustered into authored tutorial groups here.",
    "faa": "Area-transition reference; the flag participates in a field adjoin or stage-transition gate.",
}


def _localized_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("En") or value.get("Jp") or "")
    return str(value or "")


def _make_quest_id_target(quest_id: int, doc_comment: str, origin: str) -> TargetFlag:
    return TargetFlag(
        quest_id=quest_id,
        flag_type="quest_id",
        flag_value=quest_id,
        doc_comment=doc_comment,
        origin=origin,
    )


def _collect_esi_targets(quest_id: int) -> list[TargetFlag]:
    targets: list[TargetFlag] = []
    for row in get_esi_rows_for_quest(quest_id):
        flag_value = int(row.get("Flag") or 0)
        if flag_value > 0:
            targets.append(
                TargetFlag(
                    quest_id=quest_id,
                    flag_type="quest_flag",
                    flag_value=flag_value,
                    doc_comment="Repeatable sortie gate flag",
                    origin="derived_esi",
                )
            )
    return targets


def _collect_csi_targets(quest_id: int) -> list[TargetFlag]:
    targets: list[TargetFlag] = []
    for row in get_csi_rows_for_quest(quest_id):
        cycle_sub_no = int(row.get("CycleSubNo") or 0)
        cycle_no = int(row.get("CycleNo") or 0)
        if cycle_sub_no > 0:
            targets.append(
                TargetFlag(
                    quest_id=quest_id,
                    flag_type="cycle_sub_no",
                    flag_value=cycle_sub_no,
                    doc_comment=f"Repeatable cycle {cycle_no}/{cycle_sub_no}",
                    origin="derived_csi",
                )
            )
    return targets


def _collect_evd_targets(quest_id: int) -> list[TargetFlag]:
    targets: list[TargetFlag] = []
    for row in get_evd_rows_for_quest(quest_id):
        flag_value = int(row.get("Flag") or 0)
        if flag_value > 0:
            evidence_name = _localized_text(row.get("EvidenceName")) or "Evidence entry"
            targets.append(
                TargetFlag(
                    quest_id=quest_id,
                    flag_type="quest_flag",
                    flag_value=flag_value,
                    doc_comment=f"EVD: {evidence_name}",
                    origin="derived_evd",
                )
            )
    return targets


def _collect_local_qst_targets(quest_id: int) -> list[TargetFlag]:
    targets: list[TargetFlag] = []
    for hit in collect_quest_archive_qst_hits(quest_id):
        flag_type = hit.flag_kind or "quest_flag"
        if flag_type not in {"quest_flag", "layout_flag"}:
            continue

        stage_label = hit.stage_code or (f"st{hit.stage_no:04d}" if hit.stage_no else "")
        comment_parts = [part for part in (stage_label, hit.comment or hit.field_name) if part]
        doc_comment = "QST local: " + " | ".join(comment_parts) if comment_parts else "QST local quest-stage flag"
        targets.append(
            TargetFlag(
                quest_id=quest_id,
                flag_type=flag_type,
                flag_value=hit.flag_value,
                doc_comment=doc_comment,
                origin="derived_qst_local",
            )
        )
    return dedupe_targets(targets)


def _build_special_quest_targets(quest_id: int, include_fallback: bool) -> list[TargetFlag]:
    targets = [
        *_collect_esi_targets(quest_id),
        *_collect_csi_targets(quest_id),
        *_collect_evd_targets(quest_id),
    ]

    if quest_id not in AUTHORITATIVE_WORLD_MANAGE_QUEST_IDS:
        targets = [*targets, *_collect_local_qst_targets(quest_id)]

    if include_fallback or quest_has_special_resource_refs(quest_id):
        targets.append(_make_quest_id_target(quest_id, "Derived quest-wide association scan", "derived_special_query"))

    tutorial_refs = get_jtq_rows_for_quest(quest_id) or get_tqg_rows_for_quest(quest_id) or get_jmc_rows_for_quest(quest_id)
    if tutorial_refs and not any(target.flag_type == "quest_id" for target in targets):
        targets.append(_make_quest_id_target(quest_id, "Tutorial quest association scan", "derived_tutorial"))

    if get_ams_rows_for_quest(quest_id) and not any(target.flag_type == "quest_id" for target in targets):
        targets.append(_make_quest_id_target(quest_id, "Blocked spot association scan", "derived_ams"))

    return dedupe_targets(targets)


def _build_external_dependency_targets(
    quest_id: int,
    *,
    corpus_index: CorpusIndex | None = None,
    json_cache: JsonCache | None = None,
    stage_cues: dict[str, Any] | None = None,
    owner_indexes: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if corpus_index is None or json_cache is None:
        return []

    current_family = classify_quest_family(quest_id).key
    if current_family == "q7":
        return []

    cues = stage_cues or collect_stage_neighborhood_cues(
        quest_id,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    if not isinstance(cues, dict):
        return []

    owners: dict[int, dict[str, Any]] = {}
    owner_catalog_cache: dict[int, dict[str, Any] | None] = {
        int(entry.get("owner_quest_id") or 0): entry
        for entry in (owner_indexes or [])
        if isinstance(entry, dict) and int(entry.get("owner_quest_id") or 0) > 0
    }
    for cue in cues.get("cues", []):
        if not isinstance(cue, dict):
            continue

        owner_quests = [int(value) for value in (cue.get("owner_quests") or []) if int(value) > 0]
        if len(owner_quests) != 1:
            continue

        owner_quest_id = owner_quests[0]
        if owner_quest_id == quest_id:
            continue

        owner_family = classify_quest_family(owner_quest_id).key
        if owner_family not in {"q6", "q7"}:
            continue

        source_types = set(str(value) for value in (cue.get("source_types") or []) if value)
        hit_count = int(cue.get("hit_count") or 0)
        if owner_family == "q7":
            if hit_count < 3 or hit_count >= 50:
                continue
        elif owner_family == "q6":
            if "gpl" not in source_types or hit_count >= 10:
                continue
        else:
            continue

        flag_value = int(cue.get("flag_value") or 0)
        if owner_quest_id not in owner_catalog_cache:
            owner_catalog_cache[owner_quest_id] = build_owner_layout_catalog(
                owner_quest_id,
                corpus_index=corpus_index,
                json_cache=json_cache,
            )
        owner_catalog = owner_catalog_cache[owner_quest_id]
        if owner_catalog is None:
            continue
        if flag_value not in set(owner_catalog.get("flag_values", [])):
            continue

        owner_entry = owners.setdefault(
            owner_quest_id,
            {
                "owner_quest_id": owner_quest_id,
                "owner_family": owner_family,
                "flag_values": set(),
                "source_types": set(),
                "stage_codes": set(),
                "why": (
                    "Filtered stage-neighborhood layout cues intersect the owner q7 quest's client-derived layout catalog built from self-owned stage cues and local q7 QST layout flags."
                    if owner_family == "q7"
                    else "Filtered GPL-backed q6 stage-neighborhood cues intersect the owner q6 quest's client-derived layout catalog built from self-owned client evidence."
                ),
            },
        )
        owner_entry["flag_values"].add(flag_value)
        owner_entry["source_types"].update(source_types)
        owner_entry["stage_codes"].update(str(value) for value in (cue.get("stage_codes") or []) if value)

    dependency_targets: list[dict[str, Any]] = []
    for owner_quest_id, owner_entry in sorted(owners.items()):
        flag_values = sorted(int(value) for value in owner_entry["flag_values"])
        sorted_source_types = sorted(str(value) for value in owner_entry["source_types"])
        stage_codes = sorted(str(value) for value in owner_entry["stage_codes"])
        dependency_targets.append(
            {
                "owner_quest_id": owner_quest_id,
                "owner_family": owner_entry["owner_family"],
                "derivation_class": DerivationClass.DEPENDENCY_INFERRED.value,
                "flag_values": flag_values,
                "flag_count": len(flag_values),
                "source_types": sorted_source_types,
                "stage_codes": stage_codes,
                "why": owner_entry["why"],
            }
        )

    return dependency_targets


def _build_owner_indexes(
    quest_id: int,
    *,
    corpus_index: CorpusIndex | None = None,
    json_cache: JsonCache | None = None,
    stage_cues: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if corpus_index is None or json_cache is None:
        return []

    cues = stage_cues or collect_stage_neighborhood_cues(
        quest_id,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    if not isinstance(cues, dict):
        return []

    linked_owners: dict[int, dict[str, Any]] = {}
    for cue in cues.get("cues", []):
        if not isinstance(cue, dict):
            continue

        owner_quests = [int(value) for value in (cue.get("owner_quests") or []) if int(value) > 0]
        if len(owner_quests) != 1:
            continue

        owner_quest_id = owner_quests[0]
        if owner_quest_id == quest_id:
            continue

        owner_family = classify_quest_family(owner_quest_id).key
        if owner_family not in {"q6", "q7"}:
            continue

        owner_entry = linked_owners.setdefault(
            owner_quest_id,
            {
                "owner_quest_id": owner_quest_id,
                "owner_family": owner_family,
                "linked_flag_values": set(),
                "linked_source_types": set(),
                "linked_stage_codes": set(),
            },
        )
        owner_entry["linked_flag_values"].add(int(cue.get("flag_value") or 0))
        owner_entry["linked_source_types"].update(str(value) for value in (cue.get("source_types") or []) if value)
        owner_entry["linked_stage_codes"].update(str(value) for value in (cue.get("stage_codes") or []) if value)

    owner_indexes: list[dict[str, Any]] = []
    for owner_quest_id, link_data in sorted(linked_owners.items()):
        owner_catalog = build_owner_layout_catalog(
            owner_quest_id,
            corpus_index=corpus_index,
            json_cache=json_cache,
        )
        if not isinstance(owner_catalog, dict):
            continue

        owner_indexes.append(
            {
                **owner_catalog,
                "derivation_class": DerivationClass.OWNER_INDEX.value,
                "linked_flag_values": sorted(int(value) for value in link_data["linked_flag_values"] if int(value) > 0),
                "linked_flag_count": len(link_data["linked_flag_values"]),
                "linked_source_types": sorted(str(value) for value in link_data["linked_source_types"]),
                "linked_stage_codes": sorted(str(value) for value in link_data["linked_stage_codes"]),
                "why": "Reusable owner catalog derived from the same stage-neighborhood cue set used for dependency inference.",
            }
        )

    return owner_indexes


def _explain_qmi_hit(context: str) -> str:
    if "MarkerType=NPCMarker" in context:
        return "Marker reference; this NPC marker likely appears on the map or above the associated NPC, and its group usually maps back to an NPC lot placement."
    if "MarkerType=OMMarker" in context:
        return "Marker reference; this OM marker likely points to an interactable object such as a door, lever, or device, and its group usually maps back to an OM lot placement."
    if "MarkerScope=Field" in context:
        return "Field marker reference; FMI data usually marks quest objective locations or field-side NPC and OM targets."
    return DIRECT_SOURCE_EXPLANATIONS["qmi"]


def _explain_fsm_hit(relationship: str, context: str) -> tuple[int, str]:
    if relationship == "fsm_free_flag":
        return 45, "Matched an FSM-local free flag, which is weaker evidence for world-manage authored data."
    if "QuestLocalNPCFSM" in context and "myquestflag" in context.lower():
        return 78, "Quest-local NPC FSM MyQuest check; these files usually describe NPC behavior for the same quest, so this flag likely controls that NPC's quest-specific presence or behavior."
    if "NPCFSM=" in context and "myquestflag" in context.lower():
        return 74, "NPC-related FSM MyQuest check; this flag likely controls NPC visibility, interaction, or behavior for the referenced quest."
    if "QuestLocalNPCFSM" in context:
        return 72, "Quest-local NPC FSM reference; these quest NPC FSM files usually define behavior for the same quest, such as joining fights or changing interactions."
    if "NPCFSM=" in context:
        return 70, "NPC-related FSM reference; this value likely participates in NPC visibility or interaction logic."
    return 64, "Matched decoded FSM state data; authored semantics remain indirect without deeper correlation."


def _explain_smc_hit(field_name: str) -> str:
    if field_name in {"StartQuestId", "EndQuestId"}:
        return "SituationMsgCtrl chatter reference; this NPC-specific .smc file gates which GroupSerial dialogue is available when speaking to that NPC, and StartQuestId/EndQuestId define the quest or quest-series window for that chatter."
    return "SituationMsgCtrl chatter-flag reference; this NPC-specific .smc file uses a quest-flag range to gate chatter groups that can stay available across follow-up quests in a series."


def _direct_source_explanation(source_type: str, field_name: str, context: str, family: str) -> str:
    if source_type == "qmi":
        return _explain_qmi_hit(context)
    if source_type == "smc":
        return _explain_smc_hit(field_name)
    return DIRECT_SOURCE_EXPLANATIONS.get(
        source_type,
        f"Matched an explicit decoded client field in {family}.",
    )

SEASON3_WORLD_MANAGE_QUESTS = list(AUTHORITATIVE_WORLD_MANAGE_QUEST_IDS)


def build_authoritative_quest_query_context(
    catalog: list[TargetFlag],
    quest_id: int,
) -> tuple[list[TargetFlag], list[TargetFlag]]:
    manifest = get_authoritative_targets_for_quest(quest_id)
    if manifest is None:
        return build_quest_query_context(catalog, quest_id)

    catalog_matches = {
        (target.quest_id, target.flag_type, target.flag_value): target
        for target in catalog
        if target.quest_id == quest_id
    }

    targets: list[TargetFlag] = []
    for manifest_key, flag_type in (("quest_flags", "quest_flag"), ("layout_flags", "layout_flag")):
        for flag_value in manifest[manifest_key]:
            catalog_match = catalog_matches.get((quest_id, flag_type, flag_value))
            targets.append(
                TargetFlag(
                    quest_id=quest_id,
                    flag_type=flag_type,
                    flag_value=flag_value,
                    doc_comment=(catalog_match.doc_comment if catalog_match else ""),
                    origin="authoritative_manifest",
                )
            )

    documented_targets = [target for target in catalog if target.quest_id == quest_id]
    return dedupe_targets(targets), dedupe_targets([*documented_targets, *targets])


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Investigate flag/quest relationships from decoded client data and produce evidence reports.",
    )
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--flag", type=int, help="Investigate a single flag value across all client data.")
    query_group.add_argument("--quest", type=int, help="Investigate all known flags for a quest ID.")
    query_group.add_argument("--all-quests", action="store_true",
                             help="Batch-run for the authoritative q7 world-manage quest set.")
    query_group.add_argument("--all-client-quests", action="store_true",
                             help="Batch-run for every quest folder found in the client corpus.")

    script_path = Path(__file__).resolve()
    ddon_data_root = script_path.parents[3]

    parser.add_argument("--ddon-data-root", type=Path, default=ddon_data_root,
                        help="Root path of the ddon-data repository.")
    parser.add_argument("--upstream-root", type=Path, default=DEFAULT_UPSTREAM_ROOT,
                        help="Root path of the Arrowgene upstream repository.")
    parser.add_argument("--ddo-exe-path", type=Path, default=DEFAULT_DDO_EXE_PATH,
                        help="Path to the unpacked PC DDO.exe executable.")
    parser.add_argument("--objdump-path", type=Path, default=DEFAULT_OBJDUMP_PATH,
                        help="Path to objdump for executable immediate scans.")
    parser.add_argument("--output-dir", type=Path, default=script_path.parent / "generated",
                        help="Directory for generated reports.")
    parser.add_argument("--skip-executable-scan", action="store_true",
                        help="Skip scanning DDO.exe for immediate-operand hits.")

    return parser.parse_args()


def build_target_report(
    target: TargetFlag,
    hits_by_value: dict[int, list[dict[str, Any]]],
    candidate_hits_by_value: dict[int, list[dict[str, Any]]],
    exe_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a report dict for a single target flag value."""
    matching_hits = hits_by_value.get(target.flag_value, [])
    candidate_hits = candidate_hits_by_value.get(target.flag_value, [])

    report: dict[str, Any] = {
        "target": {
            "flag_value": target.flag_value,
            "quest_id": target.quest_id,
            "flag_type": target.flag_type,
            "origin": target.origin,
            "doc_comment": target.doc_comment,
        },
        "hits": matching_hits,
        "candidate_hits": candidate_hits,
    }
    if exe_data:
        exe_data = dict(exe_data)
        exe_data["evidence_tier"] = "binary"
        exe_data["derivation_class"] = DerivationClass.BINARY_AUXILIARY.value
        report["executable_immediates"] = exe_data

    return report


def annotate_direct_hit(hit: dict[str, Any]) -> dict[str, Any]:
    cloned = dict(hit)
    source_type = str(cloned.get("source_type") or "")
    relationship = str(cloned.get("relationship") or "")
    quest_id = int(cloned.get("quest_id") or 0)
    family = source_type.upper()
    context = str(cloned.get("context") or "")

    evidence_tier = "candidate"
    confidence = 60
    why = f"Matched source family {family}."

    if source_type in {"qst", "gpl", "lot", "evsi", "nll", "evd", "faa", "npc", "smc", "qmi", "csi", "esi", "jtq", "tqg", "jmc", "ams"}:
        evidence_tier = "direct"
        confidence = 92
        why = _direct_source_explanation(source_type, str(cloned.get("field_name") or ""), context, family)
    elif source_type == "evp":
        if quest_id:
            evidence_tier = "direct"
            confidence = 85
            why = "Matched EventParam with explicit quest context."
        else:
            evidence_tier = "candidate"
            confidence = 68
            why = "Matched EventParam, but the entry is broad and needs surrounding context."
    elif source_type == "fsm":
        evidence_tier = "opaque_fsm"
        confidence, why = _explain_fsm_hit(relationship, context)

    if source_type == "gpl" and "LotTypes=SetInfoOmWarp" in context:
        why = "Layout group guard; the guarded GPL group resolves to a warp LOT, so the layout flag likely enables or reveals that warp object."

    cloned["resource_family"] = family
    cloned["evidence_tier"] = evidence_tier
    cloned["derivation_class"] = DerivationClass.DIRECT_DETERMINISTIC.value
    cloned["confidence"] = confidence
    cloned["why"] = why
    return cloned


def resolve_targets(catalog: list[TargetFlag], query_mode: str, query_value: int) -> tuple[list[TargetFlag], list[TargetFlag]]:
    if query_mode == "flag":
        return build_flag_query_context(catalog, query_value)
    base_targets, documented_targets = build_authoritative_quest_query_context(catalog, query_value)
    special_targets = _build_special_quest_targets(query_value, include_fallback=not base_targets)
    return (
        dedupe_targets([*base_targets, *special_targets]),
        dedupe_targets([*documented_targets, *special_targets]),
    )


def collect_direct_hits(
    ddon_data_root: Path,
    target_values: set[int],
    *,
    corpus_index: CorpusIndex | None = None,
    json_cache: JsonCache | None = None,
) -> tuple[list[Any], dict[int, list[dict[str, Any]]]]:
    print(f"Scanning ddon-data/client for {len(target_values)} target flag value(s)...")
    all_hits = collect_client_json_hits(
        ddon_data_root,
        target_values,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    print(f"  Found {len(all_hits)} total hits across all sources")
    serialized_hits: list[dict[str, Any]] = enrich_hit_dicts_with_mss(
        ddon_data_root,
        [annotate_direct_hit(hit.to_dict()) for hit in all_hits],
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    hits_by_value: dict[int, list[dict[str, Any]]] = {}
    source_counts: dict[str, int] = {}
    for hit in all_hits:
        source_counts[hit.source_type] = source_counts.get(hit.source_type, 0) + 1
    for source_type, count in sorted(source_counts.items()):
        print(f"    {source_type}: {count}")
    for hit_dict in serialized_hits:
        hits_by_value.setdefault(int(hit_dict["flag_value"]), []).append(hit_dict)
    return all_hits, hits_by_value


def collect_candidate_hits(
    ddon_data_root: Path,
    targets: list[TargetFlag],
    hits_by_value: dict[int, list[dict[str, Any]]],
    *,
    corpus_index: CorpusIndex | None = None,
    json_cache: JsonCache | None = None,
) -> dict[int, list[dict[str, Any]]]:
    unresolved_target_kinds = {
        target.flag_value: (target.flag_type or "quest_flag")
        for target in targets
        if target.flag_value not in hits_by_value
    }
    candidate_hits_by_value = collect_candidate_json_hits(
        ddon_data_root,
        unresolved_target_kinds,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    for flag_value, hits in candidate_hits_by_value.items():
        candidate_hits_by_value[flag_value] = [enrich_hit_with_npc_ledger(hit) for hit in hits]
    return candidate_hits_by_value


def collect_executable_hits(
    skip_exe: bool,
    ddo_exe: Path,
    objdump: Path,
    target_values: set[int],
) -> dict[int, dict[str, Any]]:
    exe_results: dict[int, dict[str, Any]] = {}
    if skip_exe:
        return exe_results

    ddo_exe_resolved = ddo_exe.resolve()
    objdump_resolved = objdump.resolve()
    if not ddo_exe_resolved.exists() or not objdump_resolved.exists():
        print("  Skipping executable scan (DDO.exe or objdump not found)")
        return exe_results

    print("Scanning DDO.exe for immediate operands...")
    immediate_hits = collect_immediate_hits(ddo_exe_resolved, objdump_resolved, target_values)
    analysis_addresses = {hit.address for hits in immediate_hits.values() for hit in hits}
    contexts_by_addr: dict[str, list[str]] = {}
    following_calls: dict[str, str] = {}
    if analysis_addresses:
        contexts_by_addr, following_calls = collect_contexts_and_following_calls(
            ddo_exe_resolved,
            objdump_resolved,
            analysis_addresses,
            context_padding=20,
            call_lookahead=6,
        )
    for flag_value, hits in immediate_hits.items():
        if hits:
            exe_results[flag_value] = serialize_immediate_result(
                flag_value,
                hits,
                contexts_by_addr,
                following_calls,
            )
    print(f"  Found immediate hits for {len(exe_results)} flag value(s)")
    return exe_results


def build_payload(
    query_mode: str,
    query_value: int,
    documented_targets: list[TargetFlag],
    targets: list[TargetFlag],
    hits_by_value: dict[int, list[dict[str, Any]]],
    candidate_hits_by_value: dict[int, list[dict[str, Any]]],
    exe_results: dict[int, dict[str, Any]],
    *,
    corpus_index: CorpusIndex | None = None,
    json_cache: JsonCache | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": REPORT_FORMAT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": {"mode": query_mode, "value": query_value},
        "documented_targets": [
            {
                "flag_value": target.flag_value,
                "quest_id": target.quest_id,
                "flag_type": target.flag_type,
                "doc_comment": target.doc_comment,
                "origin": target.origin,
            }
            for target in documented_targets
        ],
        "targets": [],
    }
    if query_mode == "quest":
        payload["quest_family"] = classify_quest_family(query_value).to_dict()
        payload["quest_family_relationships"] = build_family_relationship_context(query_value)
        stage_cues = collect_stage_neighborhood_cues(
            query_value,
            corpus_index=corpus_index,
            json_cache=json_cache,
        )
        owner_indexes = _build_owner_indexes(
            query_value,
            corpus_index=corpus_index,
            json_cache=json_cache,
            stage_cues=stage_cues,
        )
        payload["quest_owner_indexes"] = owner_indexes
        payload["quest_dependency_targets"] = _build_external_dependency_targets(
            query_value,
            corpus_index=corpus_index,
            json_cache=json_cache,
            stage_cues=stage_cues,
            owner_indexes=owner_indexes,
        )
        payload["quest_archive_context"] = build_quest_archive_context(query_value)
        payload["quest_stage_neighborhood"] = build_stage_neighborhood_context(query_value, corpus_index=corpus_index)
        payload["quest_stage_cues"] = stage_cues
        payload["quest_graph_expansion"] = build_quest_graph_expansion(
            query_value,
            targets=targets,
            hits_by_value=hits_by_value,
            family_relationships=payload["quest_family_relationships"],
            archive_context=payload["quest_archive_context"],
            owner_indexes=owner_indexes,
            dependency_targets=payload["quest_dependency_targets"],
            corpus_index=corpus_index,
            json_cache=json_cache,
        )
    for target in targets:
        payload["targets"].append(
            build_target_report(target, hits_by_value, candidate_hits_by_value, exe_results.get(target.flag_value))
        )
    return payload


def _format_elapsed(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remaining = seconds % 60
    return f"{minutes}m {remaining:.1f}s"


def run_investigation(
    query_mode: str,
    query_value: int,
    ddon_data_root: Path,
    upstream_root: Path,
    output_dir: Path,
    skip_exe: bool,
    ddo_exe: Path,
    objdump: Path,
    *,
    corpus_index: CorpusIndex | None = None,
    json_cache: JsonCache | None = None,
) -> None:
    """Run a single investigation for a flag or quest and write reports."""
    catalog = load_known_targets(upstream_root)
    targets, documented_targets = resolve_targets(catalog, query_mode, query_value)
    target_values = {t.flag_value for t in targets}
    _all_hits, hits_by_value = collect_direct_hits(
        ddon_data_root,
        target_values,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    candidate_hits_by_value = collect_candidate_hits(
        ddon_data_root,
        targets,
        hits_by_value,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    exe_results = collect_executable_hits(skip_exe, ddo_exe, objdump, target_values)
    payload = build_payload(
        query_mode,
        query_value,
        documented_targets,
        targets,
        hits_by_value,
        candidate_hits_by_value,
        exe_results,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )

    # ---------- Write output ----------
    stem = f"{REPORT_STEM_PREFIX}_{query_mode}_{query_value}"
    json_path = output_dir / f"{stem}.json"
    markdown_path = output_dir / f"{stem}.adoc"

    write_json_report(json_path, payload)
    write_asciidoc_report(markdown_path, payload)

    # Summary
    total_hits = sum(len(t.get("hits", [])) for t in payload["targets"])
    print(f"\nResults:")
    print(f"  Targets investigated: {len(targets)}")
    print(f"  Total flag references found: {total_hits}")
    print(f"  JSON report: {json_path}")
    print(f"  AsciiDoc report: {markdown_path}")


def _discover_client_quest_ids(ddon_data_root: Path) -> list[int]:
    """Discover all q######## quest folders in the client corpus."""
    quest_root = ddon_data_root / "client" / "03040008" / "quest"
    if not quest_root.exists():
        return []
    pattern = re.compile(r"^q(\d{8})$")
    quest_ids: list[int] = []
    for child in sorted(quest_root.iterdir()):
        if child.is_dir():
            match = pattern.match(child.name)
            if match:
                quest_ids.append(int(match.group(1)))
    return quest_ids


def _build_batch_infrastructure(
    ddon_data_root: Path,
) -> tuple[CorpusIndex, JsonCache]:
    """Build the corpus index and pre-load JSON cache for batch mode."""
    t0 = time.monotonic()
    print("Building corpus index...")
    index = build_corpus_index(ddon_data_root)
    t1 = time.monotonic()
    print(f"  Indexed {index.total_files} files ({index.scanner_file_count} scanner-relevant) in {_format_elapsed(t1 - t0)}")

    print("Pre-loading JSON cache...")
    cache = JsonCache()
    cache.preload(index, verbose=True)
    t2 = time.monotonic()
    print(f"  Cache loaded in {_format_elapsed(t2 - t1)}")

    return index, cache


def main() -> None:
    args = parse_arguments()

    ddon_data_root = args.ddon_data_root.resolve()
    upstream_root = args.upstream_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all_quests or args.all_client_quests:
        if args.all_client_quests:
            quest_ids = _discover_client_quest_ids(ddon_data_root)
            print(f"=== Batch mode: running {len(quest_ids)} client quest folders ===\n")
        else:
            quest_ids = SEASON3_WORLD_MANAGE_QUESTS
            print(f"=== Batch mode: running {len(quest_ids)} authoritative q7 world-manage quests ===\n")

        batch_start = time.monotonic()
        index, cache = _build_batch_infrastructure(ddon_data_root)

        # Phase 1: resolve all targets across every quest and collect the
        # combined set of flag values.  This lets us do a *single* corpus
        # scan instead of one per quest.
        catalog = load_known_targets(upstream_root)
        per_quest: list[tuple[int, list[TargetFlag], list[TargetFlag]]] = []
        all_target_values: set[int] = set()
        for quest_id in quest_ids:
            targets, documented_targets = resolve_targets(catalog, "quest", quest_id)
            per_quest.append((quest_id, targets, documented_targets))
            all_target_values.update(t.flag_value for t in targets)

        print(f"\nResolved {len(all_target_values)} unique target values across {len(quest_ids)} quests")

        # Phase 2: single-pass structured scan.
        t_scan = time.monotonic()
        print(f"Running single-pass structured scan for {len(all_target_values)} target values...")
        all_raw_hits = collect_client_json_hits(
            ddon_data_root,
            all_target_values,
            corpus_index=index,
            json_cache=cache,
        )
        print(f"  Found {len(all_raw_hits)} total hits in {_format_elapsed(time.monotonic() - t_scan)}")

        # Phase 3: annotate all hits and build a single MSS lookup.
        t_enrich = time.monotonic()
        all_annotated = [annotate_direct_hit(hit.to_dict()) for hit in all_raw_hits]
        all_enriched = enrich_hit_dicts_with_mss(
            ddon_data_root,
            all_annotated,
            corpus_index=index,
            json_cache=cache,
        )
        # Index enriched hits by flag value.
        global_hits_by_value: dict[int, list[dict[str, Any]]] = {}
        for hit_dict in all_enriched:
            global_hits_by_value.setdefault(int(hit_dict["flag_value"]), []).append(hit_dict)
        print(f"  Enriched and indexed in {_format_elapsed(time.monotonic() - t_enrich)}")

        # Phase 3.5: batched candidate search for all unresolved targets.
        t_cand = time.monotonic()
        all_unresolved_kinds: dict[int, str] = {}
        for _quest_id, targets, _documented_targets in per_quest:
            for target in targets:
                if target.flag_value not in global_hits_by_value or not global_hits_by_value[target.flag_value]:
                    all_unresolved_kinds[target.flag_value] = target.flag_type or "quest_flag"
        global_candidate_hits_by_value: dict[int, list[dict[str, Any]]] = {}
        if all_unresolved_kinds:
            print(f"Running batched candidate search for {len(all_unresolved_kinds)} unresolved target(s)...")
            global_candidate_hits_by_value = collect_candidate_json_hits(
                ddon_data_root,
                all_unresolved_kinds,
                corpus_index=index,
                json_cache=cache,
            )
            for flag_value, hits in global_candidate_hits_by_value.items():
                global_candidate_hits_by_value[flag_value] = [enrich_hit_with_npc_ledger(hit) for hit in hits]
            print(f"  Candidate search done in {_format_elapsed(time.monotonic() - t_cand)}")
        else:
            print("  No unresolved targets — skipping candidate search")

        # Phase 4: per-quest report generation.
        for qi, (quest_id, targets, documented_targets) in enumerate(per_quest, 1):
            quest_start = time.monotonic()
            print(f"\n{'='*60}")
            print(f"  [{qi}/{len(quest_ids)}] Quest {quest_id}")
            print(f"{'='*60}")

            target_values = {t.flag_value for t in targets}
            # Slice global hits for this quest's targets.
            hits_by_value: dict[int, list[dict[str, Any]]] = {
                v: global_hits_by_value.get(v, []) for v in target_values
            }

            # Slice global candidate hits for this quest's unresolved targets.
            candidate_hits_by_value: dict[int, list[dict[str, Any]]] = {
                v: global_candidate_hits_by_value.get(v, [])
                for v in target_values
                if v not in hits_by_value or not hits_by_value[v]
            }
            exe_results = collect_executable_hits(
                args.skip_executable_scan, args.ddo_exe_path, args.objdump_path, target_values,
            )
            payload_data = build_payload(
                "quest", quest_id, documented_targets, targets,
                hits_by_value, candidate_hits_by_value, exe_results,
                corpus_index=index,
                json_cache=cache,
            )

            stem = f"{REPORT_STEM_PREFIX}_quest_{quest_id}"
            json_path = output_dir / f"{stem}.json"
            markdown_path = output_dir / f"{stem}.adoc"
            write_json_report(json_path, payload_data)
            write_asciidoc_report(markdown_path, payload_data)

            total_hits = sum(len(t.get("hits", [])) for t in payload_data["targets"])
            quest_elapsed = time.monotonic() - quest_start
            print(f"  {len(targets)} targets, {total_hits} hits -> {json_path.name} ({_format_elapsed(quest_elapsed)})")

        batch_elapsed = time.monotonic() - batch_start
        print(f"\n{'='*60}")
        print(f"  Batch complete: {len(quest_ids)} quests in {_format_elapsed(batch_elapsed)}")
        print(f"  JSON cache stats: {cache.stats}")
        print(f"{'='*60}")
        return

    query_mode = "flag" if args.flag is not None else "quest"
    query_value = int(args.flag) if args.flag is not None else int(args.quest)
    index, cache = _build_batch_infrastructure(ddon_data_root)
    run_investigation(
        query_mode=query_mode,
        query_value=query_value,
        ddon_data_root=ddon_data_root,
        upstream_root=upstream_root,
        output_dir=output_dir,
        skip_exe=args.skip_executable_scan,
        ddo_exe=args.ddo_exe_path,
        objdump=args.objdump_path,
        corpus_index=index,
        json_cache=cache,
    )


if __name__ == "__main__":
    main()