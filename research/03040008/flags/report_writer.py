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

from asciidoc_links import build_json_file_link
from derivation import derivation_label


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


def _build_hits_table(lines: list[str], hits: list[dict[str, Any]], report_dir: Path) -> None:
    lines.append('[cols="1,1,1,3,3,2,3,3",options="header"]')
    lines.append("|===")
    lines.append("| Family | Derivation | Confidence | File | JSON Path | Field | Context | Why")
    lines.append("")
    for hit in hits:
        fp = _escape_cell(
            build_json_file_link(
                str(hit.get("file_path", "") or ""),
                report_dir=report_dir,
                json_path=str(hit.get("json_path", "") or ""),
            )
        )
        jp = _escape_cell(hit.get("json_path", ""))
        fn = _escape_cell(hit.get("field_name", ""))
        ctx = _escape_cell(_format_context(hit))
        why = _escape_cell(hit.get("why", ""))
        family = _escape_cell(hit.get("resource_family", hit.get("source_type", "")))
        derivation = _escape_cell(derivation_label(str(hit.get("derivation_class") or "")))
        confidence = str(hit.get("confidence", ""))
        lines.append(f"| {family} | {derivation} | {confidence} | {fp} | {jp} | {fn} | {ctx} | {why}")
    lines.append("|===")
    lines.append("")


def _build_candidate_table(lines: list[str], hits: list[dict[str, Any]], report_dir: Path) -> None:
    lines.append('[cols="1,1,1,2,3,3,3",options="header"]')
    lines.append("|===")
    lines.append("| Tier | Derivation | Confidence | Field | File | Context | Why")
    lines.append("")
    for hit in hits:
        field_name = _escape_cell(hit.get("field_name", ""))
        file_path = _escape_cell(
            build_json_file_link(
                str(hit.get("file_path", "") or ""),
                report_dir=report_dir,
                json_path=str(hit.get("json_path", "") or ""),
            )
        )
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
            f"| {_escape_cell(str(hit.get('evidence_tier', 'candidate')))} | {_escape_cell(derivation_label(str(hit.get('derivation_class') or '')))} | {hit.get('confidence', '')} | {field_name} | {file_path} | {context} | {_escape_cell(hit.get('why', ''))}"
        )
    lines.append("|===")
    lines.append("")


def _mermaid_safe_id(node_id: str) -> str:
    characters = [character if character.isalnum() else "_" for character in node_id]
    sanitized = "".join(characters).strip("_")
    return f"node_{sanitized or 'root'}"


def _mermaid_escape(value: str, *, limit: int = 64) -> str:
    compact = " ".join(value.split())
    if len(compact) > limit:
        compact = compact[: limit - 3].rstrip() + "..."
    return compact.replace('"', r'\"')


def _short_edge_label(edge_type: str) -> str:
    return edge_type.replace("family_context:", "family:")


def _build_graph_mermaid(lines: list[str], graph_expansion: dict[str, Any]) -> None:
    nodes = {str(node.get("node_id") or ""): node for node in (graph_expansion.get("nodes") or []) if isinstance(node, dict)}
    edges = [edge for edge in (graph_expansion.get("edges") or []) if isinstance(edge, dict)]
    if not nodes or not edges:
        return

    selected_edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for depth_limit in (1, 2, 3):
        for edge in edges:
            if int(edge.get("depth") or 0) != depth_limit:
                continue
            edge_key = (str(edge.get("from") or ""), str(edge.get("to") or ""), str(edge.get("edge_type") or ""))
            if edge_key in seen_edges:
                continue
            selected_edges.append(edge)
            seen_edges.add(edge_key)
            if len(selected_edges) >= 24:
                break
        if len(selected_edges) >= 24:
            break

    if not selected_edges:
        return

    selected_node_ids = {str(edge.get("from") or "") for edge in selected_edges}
    selected_node_ids.update(str(edge.get("to") or "") for edge in selected_edges)
    selected_node_ids = {node_id for node_id in selected_node_ids if node_id in nodes}
    selected_nodes = sorted(
        (nodes[node_id] for node_id in selected_node_ids),
        key=lambda item: (int(item.get("depth") or 0), str(item.get("kind") or ""), str(item.get("label") or "")),
    )

    lines.append("=== Mermaid Graph Slice")
    lines.append("")
    lines.append("_This Mermaid flowchart shows a capped slice of the bounded graph so large quest reports stay readable while still exposing the graph structure._")
    lines.append("")
    lines.append("[mermaid]")
    lines.append("....")
    lines.append("flowchart TD")
    for node in selected_nodes:
        node_id = _mermaid_safe_id(str(node.get("node_id") or ""))
        label = _mermaid_escape(str(node.get("label") or node.get("node_id") or ""))
        lines.append(f'    {node_id}["{label}"]')
    for edge in selected_edges:
        from_id = _mermaid_safe_id(str(edge.get("from") or ""))
        to_id = _mermaid_safe_id(str(edge.get("to") or ""))
        edge_label = _mermaid_escape(_short_edge_label(str(edge.get("edge_type") or "")), limit=28)
        lines.append(f"    {from_id} -->|{edge_label}| {to_id}")

    class_to_nodes: dict[str, list[str]] = {
        "direct_deterministic": [],
        "owner_index": [],
        "dependency_inferred": [],
        "graph_expanded": [],
        "lower_confidence": [],
        "binary_auxiliary": [],
    }
    for node in selected_nodes:
        derivation = str(node.get("derivation_class") or "")
        if derivation in class_to_nodes:
            class_to_nodes[derivation].append(_mermaid_safe_id(str(node.get("node_id") or "")))

    lines.append("    classDef direct_deterministic fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px")
    lines.append("    classDef owner_index fill:#e3f2fd,stroke:#1565c0,stroke-width:1px")
    lines.append("    classDef dependency_inferred fill:#fff3e0,stroke:#ef6c00,stroke-width:1px")
    lines.append("    classDef graph_expanded fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px")
    lines.append("    classDef lower_confidence fill:#fbe9e7,stroke:#d84315,stroke-width:1px")
    lines.append("    classDef binary_auxiliary fill:#eceff1,stroke:#455a64,stroke-width:1px")
    for derivation, node_ids in class_to_nodes.items():
        if node_ids:
            lines.append(f"    class {','.join(node_ids)} {derivation}")
    lines.append("....")
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


def build_asciidoc_lines(payload: dict[str, Any], report_dir: Path | None = None) -> list[str]:
    report_dir = report_dir or (Path(__file__).resolve().parent / "generated")
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

    quest_family = payload.get("quest_family")
    if isinstance(quest_family, dict):
        lines.append(f"Quest family:: {quest_family.get('key', '')} -- {quest_family.get('label', '')}")
        description = str(quest_family.get("description") or "")
        if description:
            lines.append(f"Quest family notes:: {description}")
        discovery_focus = str(quest_family.get("discovery_focus") or "")
        if discovery_focus:
            lines.append(f"Quest family focus:: {discovery_focus}")
        lines.append("")

    dependency_targets = payload.get("quest_dependency_targets")
    owner_indexes = payload.get("quest_owner_indexes")
    if isinstance(owner_indexes, list) and owner_indexes:
        lines.append("== External Owner Indexes")
        lines.append("")
        lines.append("_These are reusable external owner catalogs inferred from stage-neighborhood cues. They are broader than the subset of flags promoted into derived dependency targets._")
        lines.append("")
        lines.append('[cols="2,1,1,2,2,2,4",options="header"]')
        lines.append("|===")
        lines.append("| Owner Quest | Family | Catalog Count | Catalog Flags | Linked Cues | Cue Sources | Why")
        lines.append("")
        for owner in owner_indexes:
            owner_quest = str(owner.get("owner_quest_id") or "")
            owner_family = _escape_cell(str(owner.get("owner_family") or ""))
            catalog_flags = [str(value) for value in (owner.get("flag_values") or [])]
            preview_catalog = ", ".join(catalog_flags[:12])
            if len(catalog_flags) > 12:
                preview_catalog += f" +{len(catalog_flags) - 12} more"
            linked_flags = [str(value) for value in (owner.get("linked_flag_values") or [])]
            preview_linked = ", ".join(linked_flags[:8])
            if len(linked_flags) > 8:
                preview_linked += f" +{len(linked_flags) - 8} more"
            cue_sources = _escape_cell(", ".join(str(value) for value in (owner.get("linked_source_types") or [])))
            why = _escape_cell(str(owner.get("why") or ""))
            lines.append(
                f"| {owner_quest} | {owner_family} | {owner.get('flag_count', 0)} | {_escape_cell(preview_catalog)} | {_escape_cell(preview_linked)} | {cue_sources} | {why}"
            )
        lines.append("|===")
        lines.append("")

    if isinstance(dependency_targets, list) and dependency_targets:
        lines.append("== Derived External Dependency Targets")
        lines.append("")
        lines.append("_These are the promoted subset of external owner-index entries. A flag appears here only when it passes the current family-specific dependency promotion rules for this quest._")
        lines.append("")
        lines.append('[cols="2,1,1,2,2,4",options="header"]')
        lines.append("|===")
        lines.append("| Owner Quest | Family | Flag Count | Flags | Sources | Why")
        lines.append("")
        for target in dependency_targets:
            owner_quest = str(target.get("owner_quest_id") or "")
            owner_family = _escape_cell(str(target.get("owner_family") or ""))
            flag_values = [str(value) for value in (target.get("flag_values") or [])]
            preview_flags = ", ".join(flag_values[:12])
            if len(flag_values) > 12:
                preview_flags += f" +{len(flag_values) - 12} more"
            sources = _escape_cell(", ".join(str(value) for value in (target.get("source_types") or [])))
            why = _escape_cell(str(target.get("why") or ""))
            lines.append(
                f"| {owner_quest} | {owner_family} | {target.get('flag_count', 0)} | {_escape_cell(preview_flags)} | {sources} | {why}"
            )
        lines.append("|===")
        lines.append("")

    family_relationships = payload.get("quest_family_relationships")
    if isinstance(family_relationships, dict):
        sequence_context = family_relationships.get("quest_sequence")
        repeatable_sortie = family_relationships.get("repeatable_sortie")
        tutorial_scaffolding = family_relationships.get("tutorial_scaffolding")
        evidence_chain = family_relationships.get("evidence_chain")
        blocked_spots = family_relationships.get("blocked_spots")

        if any(item is not None for item in (sequence_context, repeatable_sortie, tutorial_scaffolding, evidence_chain, blocked_spots)):
            lines.append("== Family Relationship Context")
            lines.append("")
            lines.append("_These sections summarize deterministic client-side family metadata and reverse-index relationships. They are context for later owner/dependency inference, not direct quest-target promotion._")
            lines.append("")

            if isinstance(sequence_context, dict):
                lines.append("=== Quest Sequence")
                lines.append("")
                lines.append(f"* seq no: {sequence_context.get('seq_no', 0)}")
                previous = sequence_context.get("previous")
                if isinstance(previous, dict):
                    lines.append(f"* previous: {previous.get('quest_id', 0)} -- {previous.get('quest_name', '') or previous.get('quest_name_jp', '')}")
                next_entry = sequence_context.get("next")
                if isinstance(next_entry, dict):
                    lines.append(f"* next: {next_entry.get('quest_id', 0)} -- {next_entry.get('quest_name', '') or next_entry.get('quest_name_jp', '')}")
                lines.append("")

            if isinstance(repeatable_sortie, dict):
                lines.append("=== Repeatable Sortie")
                lines.append("")
                lines.append(f"* ESI rows: {repeatable_sortie.get('esi_count', 0)}")
                lines.append(f"* CSI rows: {repeatable_sortie.get('csi_count', 0)}")
                cycle_sub_nos = repeatable_sortie.get("cycle_sub_nos") or []
                if cycle_sub_nos:
                    lines.append(f"* cycle sub numbers: {', '.join(str(value) for value in cycle_sub_nos)}")
                cycle_nos = repeatable_sortie.get("cycle_nos") or []
                if cycle_nos:
                    lines.append(f"* cycle numbers: {', '.join(str(value) for value in cycle_nos)}")
                flags = repeatable_sortie.get("flags") or []
                if flags:
                    lines.append(f"* sortie flags: {', '.join(str(value) for value in flags)}")
                stage_tuples = repeatable_sortie.get("stage_tuples") or []
                for stage_tuple in stage_tuples[:5]:
                    lines.append(f"* stage tuple: {', '.join(str(value) for value in stage_tuple)}")
                lines.append("")

            if isinstance(tutorial_scaffolding, dict):
                lines.append("=== Tutorial Scaffolding")
                lines.append("")
                lines.append(f"* JTQ rows: {tutorial_scaffolding.get('jtq_count', 0)}")
                lines.append(f"* TQG rows: {tutorial_scaffolding.get('tqg_count', 0)}")
                lines.append(f"* JMC rows: {tutorial_scaffolding.get('jmc_count', 0)}")
                group_ids = tutorial_scaffolding.get("group_ids") or []
                if group_ids:
                    lines.append(f"* tutorial groups: {', '.join(str(value) for value in group_ids)}")
                tutorial_names = tutorial_scaffolding.get("tutorial_names") or []
                for tutorial_name in tutorial_names[:5]:
                    lines.append(f"* tutorial quest: {tutorial_name}")
                for job_link in (tutorial_scaffolding.get("job_links") or [])[:5]:
                    lines.append(
                        f"* job link: tutorial {job_link.get('job_tutorial_quest_id', 0)} / master {job_link.get('job_master_tutorial_quest_id', 0)}"
                    )
                lines.append("")

            if isinstance(evidence_chain, dict):
                lines.append("=== Evidence Chain")
                lines.append("")
                lines.append(f"* entries: {evidence_chain.get('entry_count', 0)}")
                flags = evidence_chain.get("flags") or []
                if flags:
                    lines.append(f"* evidence flags: {', '.join(str(value) for value in flags)}")
                lines.append("")

            if isinstance(blocked_spots, dict):
                lines.append("=== Blocked Spots")
                lines.append("")
                lines.append(f"* entries: {blocked_spots.get('entry_count', 0)}")
                spot_ids = blocked_spots.get("spot_ids") or []
                if spot_ids:
                    lines.append(f"* spot ids: {', '.join(str(value) for value in spot_ids)}")
                lines.append("")

    archive_context = payload.get("quest_archive_context")
    if isinstance(archive_context, dict):
        lines.append("== ARC Association Context")
        lines.append("")
        lines.append("_ARC associations are contextual only. They show which quest-stage and marker resources are bundled with this quest._")
        lines.append("")
        lines.append(
            f"* arc file: {build_json_file_link(str(archive_context.get('file_path', '') or ''), report_dir=report_dir, fallback_line=1)}"
        )
        lines.append(f"* resource count: {archive_context.get('resource_count', 0)}")
        stage_codes = archive_context.get("stage_codes") or []
        if stage_codes:
            lines.append(f"* stage codes: {', '.join(str(value) for value in stage_codes)}")
        resource_type_extensions = archive_context.get("resource_type_extensions") or []
        if resource_type_extensions:
            lines.append(f"* resource families: {', '.join(str(value) for value in resource_type_extensions)}")
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

    stage_neighborhood = payload.get("quest_stage_neighborhood")
    if isinstance(stage_neighborhood, dict):
        lines.append("== Stage Neighborhood Context")
        lines.append("")
        lines.append("_Stage-neighborhood context summarizes scanner-relevant client files that share the quest's archive stage codes. This is deterministic client topology, not inferred ownership._")
        lines.append("")
        lines.append(f"* scanner-relevant stage files: {stage_neighborhood.get('scanner_file_count', 0)}")
        stage_codes = stage_neighborhood.get("stage_codes") or []
        if stage_codes:
            lines.append(f"* indexed stage codes: {', '.join(str(value) for value in stage_codes)}")
        lines.append("")
        for stage in stage_neighborhood.get("stages", []):
            stage_label = str(stage.get("stage_code") or "unclassified")
            if stage.get("stage_name"):
                stage_label += f" -- {stage['stage_name']}"
            lines.append(f"=== {stage_label}")
            lines.append("")
            lines.append(f"* scanner files: {stage.get('scanner_file_count', 0)}")
            suffix_counts = stage.get("scanner_suffix_counts") or {}
            for suffix, count in sorted(suffix_counts.items()):
                lines.append(f"* {suffix}: {count}")
            lines.append("")

    stage_cues = payload.get("quest_stage_cues")
    if isinstance(stage_cues, dict):
        lines.append("== Stage Neighborhood External-State Cues")
        lines.append("")
        lines.append("_These cues are deterministic client-side observations from the quest's stage neighborhood. They are not promoted to direct quest targets yet; they highlight q6/q7-owned external state values co-located in the quest's archive stages._")
        lines.append("")
        lines.append(f"* cue count: {stage_cues.get('cue_count', 0)}")
        owner_families = stage_cues.get("owner_families") or []
        if owner_families:
            lines.append(f"* owner families: {', '.join(str(value) for value in owner_families)}")
        lines.append("")
        cues = stage_cues.get("cues") or []
        if cues:
            lines.append('[cols="1,1,1,2,2,2",options="header"]')
            lines.append("|===")
            lines.append("| Value | Kind | Hits | Sources | Owners | Stages")
            lines.append("")
            for cue in cues[:30]:
                value = _escape_cell(_target_value_label(cue.get("flag_value"), str(cue.get("flag_kind") or "")))
                kind = _escape_cell(str(cue.get("flag_kind") or ""))
                hit_count = str(cue.get("hit_count") or 0)
                sources = _escape_cell(", ".join(str(value) for value in (cue.get("source_types") or [])))
                owners = _escape_cell(", ".join(str(value) for value in (cue.get("owner_quests") or [])))
                stages = _escape_cell(", ".join(str(value) for value in (cue.get("stage_codes") or [])))
                lines.append(f"| {value} | {kind} | {hit_count} | {sources} | {owners} | {stages}")
            lines.append("|===")
            lines.append("")

    graph_expansion = payload.get("quest_graph_expansion")
    if isinstance(graph_expansion, dict):
        lines.append("== Bounded Graph Expansion")
        lines.append("")
        lines.append("_This graph summarizes bounded deterministic and inferred edges around the quest: quest archive stages, direct source families, stage-linked owner catalogs, promoted dependencies, reverse-index event/group links, and family-specific table edges._")
        lines.append("")
        lines.append(f"* max depth: {graph_expansion.get('max_depth', 0)}")
        lines.append(f"* node count: {graph_expansion.get('node_count', 0)}")
        lines.append(f"* edge count: {graph_expansion.get('edge_count', 0)}")
        node_kind_counts = graph_expansion.get("node_kind_counts") or {}
        if node_kind_counts:
            lines.append(f"* node kinds: {', '.join(f'{kind}={count}' for kind, count in sorted(node_kind_counts.items()))}")
        derivation_counts = graph_expansion.get("derivation_counts") or {}
        if derivation_counts:
            lines.append(f"* derivation: {', '.join(f'{derivation_label(str(kind))}={count}' for kind, count in sorted(derivation_counts.items()))}")
        lines.append("")
        _build_graph_mermaid(lines, graph_expansion)
        edges = graph_expansion.get("edges") or []
        if edges:
            lines.append('[cols="1,2,2,2,2,4",options="header"]')
            lines.append("|===")
            lines.append("| Depth | Edge | From | To | Derivation | Why")
            lines.append("")
            for edge in edges[:40]:
                lines.append(
                    f"| {edge.get('depth', 0)} | {_escape_cell(str(edge.get('edge_type') or ''))} | {_escape_cell(str(edge.get('from') or ''))} | {_escape_cell(str(edge.get('to') or ''))} | {_escape_cell(derivation_label(str(edge.get('derivation_class') or '')))} | {_escape_cell(str(edge.get('why') or ''))}"
                )
            lines.append("|===")
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
                _build_hits_table(lines, tier_hits, report_dir)
        else:
            lines.append("_No direct references found in decoded client data._")
            lines.append("")

        if candidate_hits:
            lines.append("=== Ranked Candidates")
            lines.append("")
            _build_candidate_table(lines, candidate_hits, report_dir)

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
    output_path.write_text("\n".join(build_asciidoc_lines(payload, output_path.parent)) + "\n", encoding="utf-8")
