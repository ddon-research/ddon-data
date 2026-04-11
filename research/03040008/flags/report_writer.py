"""
Evidence report generator for flag/quest investigation results.

Produces structured JSON and human-readable AsciiDoc reports with
enriched metadata (quest names, stage names, comments, relationship types).
Includes a flag summary matrix and per-relationship grouped sections.
"""
from __future__ import annotations

import orjson
from pathlib import Path
from typing import Any


def write_json_report(output_path: Path, payload: dict[str, Any]) -> None:
    output_path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))


def _escape_cell(value: str) -> str:
    """Escape pipe characters inside AsciiDoc table cells."""
    return value.replace("|", "\\|")


RELATIONSHIP_LABELS: dict[str, str] = {
    "layout_guard":     "🏗️ Layout Guard",
    "door_gate":        "🚪 Door/Gate",
    "warp_gate":        "🌀 Warp Gate",
    "quest_condition":  "⚡ Quest Condition",
    "quest_erase":      "❌ Quest Erase",
    "event_state":      "🎬 Event State",
    "fsm_check":        "🔍 FSM Check",
    "fsm_set":          "✏️ FSM Set",
    "fsm_free_flag":    "🔧 FSM Local",
    "npc_state":        "👤 NPC State",
    "npc_chatter":      "🗣️ NPC Chatter",
    "npc_function":     "🏪 NPC Function",
    "marker_gate":      "📍 Marker Gate",
    "block_quest":      "🛡️ Block Quest",
    "quest_om":         "📦 Quest OM",
    "text_quest":       "💬 Text Quest",
    "field_adjoin":     "🧭 Field Adjoin",
    "event_param":      "🎞️ Event Param",
    "evidence_flag":    "🧾 Evidence Flag",
    "repeatable_sortie": "🔁 Repeatable Sortie",
    "tutorial_quest":   "🎓 Tutorial Quest",
    "tutorial_group":   "🧩 Tutorial Group",
    "job_master":       "🧑‍🏫 Job Master",
    "spot_block":       "🗺️ Spot Block",
    "server_command":   "🖥️ Server Cmd",
}

SOURCE_LABELS: dict[str, str] = {
    "qst":   "QST (Quest Stage Data)",
    "gpl":   "GPL (Layout Group Params)",
    "lot":   "LOT (Stage Layout)",
    "fsm":   "FSM (State Machine)",
    "evsi":  "EVSI (Event Viewer Set Info)",
    "qmi":   "QMI/FMI (Marker Info)",
    "npc":   "NPC (Situation Data)",
    "smc":   "SMC (Situation Message Control)",
    "nll":   "NLL (NPC Ledger)",
    "faa":   "FAA (Field Area Adjoin)",
    "evp":   "EVP (Event Param)",
    "evd":   "EVD (Evidence List)",
    "csi":   "CSI (Cycle Contents Sortie)",
    "esi":   "ESI (End Contents Sortie)",
    "jtq":   "JTQ (Job Tutorial Quest)",
    "tqg":   "TQG (Tutorial Quest Group)",
    "jmc":   "JMC (Job Master Ctrl)",
    "ams":   "AMS (Area Master Spot)",
}


def _target_value_label(flag_value: Any, flag_type: str) -> str:
    value_text = str(flag_value)
    if flag_type == "quest_id":
        return f"Quest ID {value_text}"
    if flag_type == "cycle_sub_no":
        return f"Cycle SubNo {value_text}"
    return f"Flag {value_text}"


def _origin_badge(origin: str) -> str:
    return {
        "npc_ledger": " [NPC Ledger]",
        "docs_world_manage": " [Docs]",
        "authoritative_manifest": " [Manifest]",
        "derived_special_query": " [Derived]",
        "derived_esi": " [ESI]",
        "derived_csi": " [CSI]",
        "derived_evd": " [EVD]",
        "derived_tutorial": " [Tutorial]",
        "derived_ams": " [AMS]",
    }.get(origin, "")


def _format_context(hit: dict[str, Any]) -> str:
    """Build a one-line context string from hit metadata."""
    parts: list[str] = []
    if hit.get("quest_id"):
        q = f"quest {hit['quest_id']}"
        if hit.get("quest_name"):
            q += f" ({hit['quest_name']})"
        parts.append(q)
    if hit.get("stage_name"):
        parts.append(hit["stage_name"])
    elif hit.get("stage_code"):
        parts.append(hit["stage_code"])
    if hit.get("area_name"):
        parts.append(hit["area_name"])
    if hit.get("npc_name"):
        parts.append(hit["npc_name"])
    if hit.get("function_name"):
        parts.append(hit["function_name"])
    if hit.get("group_serial"):
        parts.append(f"GroupSerial={hit['group_serial']}")
    if hit.get("comment"):
        parts.append(f'"{hit["comment"]}"')
    if hit.get("context"):
        parts.append(hit["context"])
    mss_matches = hit.get("mss_matches") or []
    if mss_matches:
        first = mss_matches[0]
        match_parts = []
        if first.get("npc_name"):
            match_parts.append(first["npc_name"])
        if first.get("message_excerpt"):
            match_parts.append(first["message_excerpt"])
        if match_parts:
            parts.append("MSS: " + " / ".join(match_parts))
    return " / ".join(parts)


def _group_hits_by_tier(hits: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for hit in hits:
        tier = str(hit.get("evidence_tier") or "candidate")
        grouped.setdefault(tier, []).append(hit)
    return grouped


def _build_hits_table(lines: list[str], hits: list[dict[str, Any]]) -> None:
    lines.append('[cols="1,1,3,3,2,3,3",options="header"]')
    lines.append("|===")
    lines.append("| Family | Confidence | File | JSON Path | Field | Context | Why")
    lines.append("")
    for hit in hits:
        fp = _escape_cell(hit.get("file_path", ""))
        jp = _escape_cell(hit.get("json_path", ""))
        fn = _escape_cell(hit.get("field_name", ""))
        ctx = _escape_cell(_format_context(hit))
        why = _escape_cell(hit.get("why", ""))
        family = _escape_cell(hit.get("resource_family", hit.get("source_type", "")))
        confidence = str(hit.get("confidence", ""))
        lines.append(f"| {family} | {confidence} | {fp} | {jp} | {fn} | {ctx} | {why}")
    lines.append("|===")
    lines.append("")


def _build_candidate_table(lines: list[str], hits: list[dict[str, Any]]) -> None:
    lines.append('[cols="1,1,2,3,3,3",options="header"]')
    lines.append("|===")
    lines.append("| Tier | Confidence | Field | File | Context | Why")
    lines.append("")
    for hit in hits:
        field_name = _escape_cell(hit.get("field_name", ""))
        file_path = _escape_cell(hit.get("file_path", ""))
        context_parts = [
            hit.get("quest_name") or "",
            hit.get("stage_name") or "",
            hit.get("npc_name") or "",
            hit.get("function_name") or "",
            hit.get("message_excerpt") or "",
            hit.get("comment") or "",
        ]
        context = _escape_cell(" / ".join(part for part in context_parts if part))
        lines.append(
            f"| {_escape_cell(str(hit.get('evidence_tier', 'candidate')))} | {hit.get('confidence', '')} | {field_name} | {file_path} | {context} | {_escape_cell(hit.get('why', ''))}"
        )
    lines.append("|===")
    lines.append("")


def _format_npc_function_label(npc_name: str, function_name: str) -> str:
    if npc_name and function_name:
        return f"NPC: {npc_name} -> {function_name}"
    return f"NPC: {npc_name or function_name}"


def _build_npc_function_description(hits: list[dict[str, Any]]) -> str:
    labels: list[str] = []
    seen: set[tuple[str, str]] = set()
    for hit in hits:
        if hit.get("relationship") != "npc_function":
            continue
        npc_name = str(hit.get("npc_name") or hit.get("npc_name_jp") or "")
        function_name = str(hit.get("function_name") or hit.get("function_name_jp") or "")
        if not npc_name and not function_name:
            continue
        key = (npc_name, function_name)
        if key in seen:
            continue
        seen.add(key)
        labels.append(_format_npc_function_label(npc_name, function_name))

    if not labels:
        return ""

    preview = "; ".join(labels[:2])
    if len(labels) > 2:
        preview += f" +{len(labels) - 2} more"
    return preview


def _build_description(doc_comment: str, hits: list[dict[str, Any]]) -> str:
    npc_description = _build_npc_function_description(hits)
    if doc_comment and npc_description:
        return f"{doc_comment} | {npc_description}"
    return doc_comment or npc_description


def _build_flag_summary(all_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a deduplicated flag summary from all target reports."""
    summaries: list[dict[str, Any]] = []

    for target_report in all_targets:
        target = target_report["target"]
        hits = target_report.get("hits", [])

        # Collect unique stages, relationships, and quest IDs
        stages: set[str] = set()
        relationships: set[str] = set()
        quest_ids: set[int] = set()
        sources: set[str] = set()

        for h in hits:
            if h.get("stage_code"):
                stages.add(h["stage_code"])
            if h.get("relationship"):
                relationships.add(h["relationship"])
            if h.get("quest_id"):
                quest_ids.add(h["quest_id"])
            if h.get("source_type"):
                sources.add(h["source_type"])

        summaries.append({
            "flag_value": target.get("flag_value"),
            "flag_type": target.get("flag_type", ""),
            "hit_count": len(hits),
            "sources": sorted(sources),
            "stages": sorted(stages),
            "quest_ids": sorted(quest_ids),
            "relationships": sorted(relationships),
            "doc_comment": _build_description(str(target.get("doc_comment", "")), hits),
        })

    return summaries


def build_asciidoc_lines(payload: dict[str, Any]) -> list[str]:
    query = payload["query"]
    lines = [
        "= Client Flag/Quest Investigation",
        ":toc: macro",
        ":toclevels: 3",
        ":toc-title: Contents",
        "",
        f"Query mode:: {query['mode']}",
        f"Query value:: {query['value']}",
        f"Generated at:: {payload['generated_at']}",
        "",
        "toc::[]",
        "",
    ]

    archive_context = payload.get("quest_archive_context")
    if isinstance(archive_context, dict):
        lines.append("== ARC Association Context")
        lines.append("")
        lines.append("_ARC associations are contextual only. They show which quest-stage and marker resources are bundled with this quest._")
        lines.append("")
        lines.append(f"* arc file: {archive_context.get('file_path', '')}")
        lines.append(f"* resource count: {archive_context.get('resource_count', 0)}")
        lines.append("")
        for stage in archive_context.get("stages", []):
            stage_label = str(stage.get("stage_code") or "unclassified")
            if stage.get("stage_name"):
                stage_label += f" -- {stage['stage_name']}"
            lines.append(f"=== {stage_label}")
            lines.append("")
            for resource in stage.get("resources", []):
                type_name = resource.get("type_name") or resource.get("type_extension") or "resource"
                lines.append(f"* {type_name}: {resource.get('path', '')}")
            lines.append("")

    # ---------- Flag Summary Matrix ----------
    targets = payload.get("targets", [])
    if targets:
        summaries = _build_flag_summary(targets)

        lines.append("== Flag Summary Matrix")
        lines.append("")
        lines.append('[cols="2,1,1,2,2,3,3",options="header"]')
        lines.append("|===")
        lines.append("| Target | Kind | Hits | Sources | Stages | Relationships | Description")
        lines.append("")
        for s in summaries:
            flag = _escape_cell(_target_value_label(s["flag_value"], str(s.get("flag_type") or "")))
            kind = _escape_cell(s.get("flag_type", "") or "")
            hits_str = str(s["hit_count"])
            sources = _escape_cell(", ".join(s["sources"]))
            stages = _escape_cell(", ".join(s["stages"][:5]))
            if len(s["stages"]) > 5:
                stages += f" +{len(s['stages'])-5}"
            rels = ", ".join(
                str(RELATIONSHIP_LABELS.get(r, r) or r) for r in s["relationships"][:3]
            )
            if len(s["relationships"]) > 3:
                rels += f" +{len(s['relationships'])-3}"
            rels = _escape_cell(rels)
            desc = _escape_cell(s.get("doc_comment", ""))
            lines.append(f"| {flag} | {kind} | {hits_str} | {sources} | {stages} | {rels} | {desc}")
        lines.append("|===")
        lines.append("")

    # ---------- Documented targets from catalog ----------
    if payload.get("documented_targets"):
        lines.append("== Known Documented Targets")
        lines.append("")
        for t in payload["documented_targets"]:
            flag_type = str(t.get("flag_type") or "")
            label = _target_value_label(t.get("flag_value"), flag_type)
            if t.get("quest_id") and flag_type != "quest_id":
                label = f"quest {t['quest_id']} -- {label}"
            origin = t.get("origin", "")
            origin_badge = _origin_badge(str(origin))
            c = f" -- {t['doc_comment']}" if t.get("doc_comment") else ""
            lines.append(f"* {label}{c}{origin_badge}")
        lines.append("")

    # ---------- Per-target reports ----------
    for target_report in targets:
        target = target_report["target"]
        flag_type = str(target.get("flag_type") or "")
        label = _target_value_label(target.get("flag_value"), flag_type)
        if target.get("quest_id") and flag_type != "quest_id":
            label += f" -- Quest {target['quest_id']}"

        lines.append(f"== {label}")
        lines.append("")
        lines.append(f"origin:: {target.get('origin', 'unknown')}")

        hits = target_report.get("hits", [])
        candidate_hits = target_report.get("candidate_hits", [])
        lines.append(f"direct hits:: *{len(hits)}*")
        lines.append(f"ranked candidates:: *{len(candidate_hits)}*")
        lines.append("")

        if hits:
            by_tier = _group_hits_by_tier(hits)
            lines.append("=== Direct Hits")
            lines.append("")
            for tier, tier_hits in sorted(by_tier.items()):
                lines.append(f"==== {tier} -- {len(tier_hits)} hit(s)")
                lines.append("")
                _build_hits_table(lines, tier_hits)
        else:
            lines.append("_No direct references found in decoded client data._")
            lines.append("")

        if candidate_hits:
            lines.append("=== Ranked Candidates")
            lines.append("")
            _build_candidate_table(lines, candidate_hits)

        # Executable immediates if present
        exe_data = target_report.get("executable_immediates", {})
        if exe_data and exe_data.get("references"):
            lines.append(f"=== Binary Fallback -- {exe_data.get('hit_count', 0)} hit(s)")
            lines.append("")
            if exe_data.get("dominant_following_calls"):
                lines.append(f"* dominant following calls: {exe_data['dominant_following_calls']}")
                lines.append("")
            lines.append('[cols="1,3",options="header"]')
            lines.append("|===")
            lines.append("| Address | Instruction")
            lines.append("")
            for ref in exe_data["references"]:
                lines.append(f"| `{ref['address']}` | `{ref['mnemonic']} {ref['operands']}`")
            lines.append("|===")
            lines.append("")

    return lines


def write_asciidoc_report(output_path: Path, payload: dict[str, Any]) -> None:
    output_path.write_text("\n".join(build_asciidoc_lines(payload)) + "\n", encoding="utf-8")
